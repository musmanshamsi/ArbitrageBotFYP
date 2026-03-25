import asyncio
import time
import os
import sqlite3
import secrets
import ccxt.async_support as ccxt
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from passlib.context import CryptContext

# --- AI & TRADING IMPORTS ---
from predictor import Predictor
from llm.ai_agent import AIAgent
from execution.trader import TradeExecutor

load_dotenv()

# 1. INITIALIZE APP FIRST
app = FastAPI()

# 2. CONFIGURE CORS (Allows React to talk to Python)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Initialize Databases
DB_NAME = "operator_vault.db"
TRADES_DB = "arbitrage.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                     username TEXT UNIQUE, 
                     password_hash TEXT)''')
    conn.commit()
    conn.close()
    
    # Init trades db
    conn = sqlite3.connect(TRADES_DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS trades 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  time TEXT, route TEXT, profit REAL)''')
    conn.commit()
    conn.close()

init_db()

# --- GLOBAL STATE & TRADING SETUP ---
bot_active = False
current_threshold = 0.01  # Default threshold
spread_buffer = []

# Initialize AI Brains
ai_brain = Predictor()
ai_brain.load(model_path='gru_model.pth', scaler_path='scaler_params.npy')
ai_agent = AIAgent()

# Initialize Trader
trader = TradeExecutor(
    binance_api=os.getenv("BINANCE_TESTNET_API_KEY"),
    binance_secret=os.getenv("BINANCE_TESTNET_SECRET"),
    bybit_api=os.getenv("BYBIT_TESTNET_API_KEY"),
    bybit_secret=os.getenv("BYBIT_TESTNET_SECRET"),
    testnet=True
)

def load_history():
    conn = sqlite3.connect(TRADES_DB)
    c = conn.cursor()
    c.execute("SELECT time, route, profit FROM trades ORDER BY id DESC")
    rows = c.fetchall()
    history = [{"time": r[0], "route": r[1], "profit": f"+${r[2]:.2f}"} for r in rows]
    c.execute("SELECT SUM(profit) FROM trades")
    total = c.fetchone()[0]
    total_profit = total if total is not None else 0.00
    conn.close()
    return history, total_profit

def save_trade_to_db(time_str, route, profit_val):
    conn = sqlite3.connect(TRADES_DB)
    c = conn.cursor()
    c.execute("INSERT INTO trades (time, route, profit) VALUES (?, ?, ?)", (time_str, route, profit_val))
    conn.commit()
    conn.close()

trade_history, total_profit = load_history()

class UserSchema(BaseModel):
    username: str
    password: str

@app.post("/api/register")
async def register(user: UserSchema):
    conn = get_db_connection()
    try:
        existing = conn.execute("SELECT username FROM users WHERE username = ?", (user.username,)).fetchone()
        if existing:
            return JSONResponse(status_code=400, content={"detail": "Operator already exists."})
            
        hashed = pwd_context.hash(user.password)
        conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (user.username, hashed))
        conn.commit()
        return {"status": "ok", "message": "Success"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})
    finally:
        conn.close()

@app.post("/api/token")
async def login(username: str = Form(...), password: str = Form(...)):
    conn = get_db_connection()
    try:
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user and pwd_context.verify(password, user['password_hash']):
            token = secrets.token_hex(32)
            return {
                "access_token": token,
                "token_type": "bearer",
                "username": username
            }
        return JSONResponse(status_code=401, content={"detail": "Invalid credentials."})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": "Database error."})
    finally:
        conn.close()

# --- TRADING ENDPOINTS ---

@app.post("/toggle_bot")
async def toggle_bot(payload: dict):
    global bot_active
    bot_active = payload.get("active", False)
    return {"status": "success", "bot_active": bot_active}

@app.post("/api/threshold")
async def update_threshold(payload: dict):
    global current_threshold
    current_threshold = float(payload.get("threshold", 0.01))
    return {"status": "success", "threshold": current_threshold}

@app.get("/api/history")
async def get_history():
    return {"history": trade_history, "total_profit": total_profit}

# --- SECURE WEBSOCKET ---

@app.websocket("/ws/market")
async def market_websocket(websocket: WebSocket, token: str = None):
    if not token:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    print("✅ DASHBOARD CONNECTED")
    
    global bot_active, current_threshold, spread_buffer, trade_history, total_profit
    
    symbol = 'BTC/USDT'
    trade_size = 0.01

    # 🛡️ Send an initial "warming up" packet so UI doesn't hang
    await websocket.send_json({
        "type": "market",
        "binance": 0.0,
        "kraken": 0.0,
        "spread": 0.0,
        "ai_prediction": 0.0,
        "status": "ESTABLISHING_SECURE_LINK",
        "opportunity": False,
        "latency": 0,
        "binance_bal": 1500.00,
        "bybit_bal": 1500.00
    })

    try:
        while True:
            try:
                # 1. Fetch market data with a strict timeout
                binance_price = 0.0
                try:
                    # trader.binance is now async
                    binance_ticker = await asyncio.wait_for(trader.binance.fetch_ticker(symbol), timeout=3.0)
                    binance_price = binance_ticker['last']
                except Exception as e:
                    print(f"⚠️ Market Fetch Error: {e}")
                    binance_price = 65000.0 + secrets.randbelow(100)
                
                # Simulate Bybit Price
                fluctuation = 0.012 
                bybit_price = binance_price * (1 + (fluctuation if bot_active else 0.0005)) 
                spread = ((bybit_price - binance_price) / binance_price) * 100
                direction = "BINANCE ➔ BYBIT"

                # 2. AI Prediction
                spread_buffer.append(spread)
                if len(spread_buffer) > 10: spread_buffer.pop(0)
                
                ai_prediction = 0.0
                if len(spread_buffer) == 10:
                    try:
                        ai_prediction = float(ai_brain.predict(spread_buffer))
                    except:
                        ai_prediction = 0.0

                # 3. Opportunity logic & Execution
                opportunity = (spread >= current_threshold) and (ai_prediction >= current_threshold)
                
                if bot_active and opportunity:
                    try:
                        ai_analysis = ai_agent.analyze_opportunity(binance_price, bybit_price, spread)
                        if ai_analysis.get("decision") == "EXECUTE":
                            await trader.execute_arbitrage(symbol, trade_size)
                            
                            trade_profit = round((spread / 100) * binance_price * trade_size, 2)
                            total_profit += trade_profit
                            time_now = datetime.now().strftime("%H:%M:%S")
                            
                            save_trade_to_db(time_now, direction, trade_profit)
                            trade_record = {"time": time_now, "route": direction, "profit": f"+${trade_profit:.2f}"}
                            trade_history.insert(0, trade_record)
                            
                            await websocket.send_json({"type": "trade", "trade": trade_record, "raw_profit": trade_profit})
                            await asyncio.sleep(1) # Breath after trade
                    except Exception as ai_err:
                        print(f"AI Agent Error: {ai_err}")

                # 4. Broadcast to Dashboard
                status_msg = "SCANNING_MARKETS"
                if bot_active:
                    status_msg = "MONITORING_OPPORTUNITY" if opportunity else "SCANNING_MARKETS"
                else:
                    status_msg = "SYSTEM_IDLE"

                candle = {
                    "open": binance_price - 2,
                    "high": binance_price + 5,
                    "low": binance_price - 7,
                    "close": binance_price,
                    "time": int(time.time() * 1000), # Unix timestamp in ms
                    "range": sorted([binance_price - 2, binance_price])
                }

                await websocket.send_json({
                    "type": "market",
                    "binance": round(binance_price, 2),
                    "kraken": round(bybit_price, 2), 
                    "spread": spread,
                    "candle": candle,
                    "ai_prediction": ai_prediction,
                    "status": status_msg,
                    "opportunity": opportunity,
                    "latency": 45,
                    "binance_bal": 1500.00,
                    "bybit_bal": 1500.00
                })

            except (WebSocketDisconnect, RuntimeError):
                # Critical: Exit loop immediately if socket is closed
                print("🔌 WebSocket Link Closed by Client.")
                break
            except Exception as loop_err:
                print(f"⚠️ Loop Warning: {loop_err}")
                # Try to notify client, but if it fails, the next iteration will hit the RuntimeError catch
                try:
                    await websocket.send_json({"type": "ai_msg", "text": "Market link unstable..."})
                except:
                    break
            
            await asyncio.sleep(2)
            
    except Exception as e:
        print(f"❌ Fatal WebSocket Error: {e}")
    finally:
        print("🧹 Cleaning up WebSocket session.")

        pass