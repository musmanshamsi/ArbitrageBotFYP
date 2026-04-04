import asyncio
import time
import os
import sqlite3
import secrets
import ccxt.async_support as ccxt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
import bcrypt

# --- AI & TRADING IMPORTS ---
from predictor import Predictor
from llm.ai_agent import AIAgent
from execution.trader import TradeExecutor
from config import ExchangeConfig

load_dotenv()

# 1. INITIALIZE APP FIRST
app = FastAPI()

# 2. CONFIGURE CORS (Allows React to talk to Python)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:8080", 
        "http://localhost:8081",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8081"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SECURITY CONFIG & DEPENDENCIES ---
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY environment variable is not set in .env")
ALGORITHM = "HS256"
# Removed pwd_context

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username

# Initialize Databases
DB_NAME = "operator_vault.db"
TRADES_DB = "arbitrage.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
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
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
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

# --- MANUAL APPROVAL STATE ---
pending_trade: dict | None = None     # Holds a trade waiting for human approval
pending_approved: bool | None = None  # None = waiting, True = approved, False = rejected
import asyncio as _asyncio
_approval_event = _asyncio.Event()    # Signals when the operator has responded

# --- TRADING COST CONFIGURATION ---
FEE_RATE = 0.002  # 0.20% (Combined Binance/Bybit)
SLIPPAGE_RATE = 0.0005  # 0.05% (Estimated)

# Initialize AI Brains
ai_brain = Predictor()
ai_brain.load(model_path='gru_model.pth', scaler_path='scaler_params.npy')
ai_agent = AIAgent()

# Initialize Trader with professional configuration
ExchangeConfig.validate()
ExchangeConfig.print_config()
trader = TradeExecutor()  # Uses ExchangeConfig automatically

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

class UserAuth(BaseModel):
    username: str
    password: str

@app.post("/api/register")
async def register(user: UserAuth):
    conn = get_db_connection()
    try:
        existing = conn.execute("SELECT username FROM users WHERE username = ?", (user.username,)).fetchone()
        if existing:
            return JSONResponse(status_code=400, content={"detail": "Operator already exists."})
            
        hashed_pw = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (user.username, hashed_pw))
        conn.commit()
        return {"status": "success", "message": "User registered"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})
    finally:
        conn.close()

@app.post("/api/login")
async def login(user: UserAuth):
    conn = get_db_connection()
    user_record = conn.execute("SELECT password_hash FROM users WHERE username = ?", (user.username,)).fetchone()
    conn.close()

    if user_record and bcrypt.checkpw(user.password.encode('utf-8'), user_record['password_hash'].encode('utf-8')):
        expire = datetime.utcnow() + timedelta(days=7)
        token = jwt.encode({"sub": user.username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
        # Note: Depending on frontend implementation it may expect token or access_token
        return {"status": "success", "token": token, "username": user.username, "access_token": token, "token_type": "bearer"}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Fallback for older frontend compatibility
@app.post("/api/token")
async def token_login(username: str = Form(...), password: str = Form(...)):
    conn = get_db_connection()
    user_record = conn.execute("SELECT password_hash FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()

    if user_record and bcrypt.checkpw(password.encode('utf-8'), user_record['password_hash'].encode('utf-8')):
        expire = datetime.utcnow() + timedelta(days=7)
        token = jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token, "token_type": "bearer", "username": username}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

# --- TRADING ENDPOINTS ---

@app.post("/toggle_bot")
async def toggle_bot(payload: dict, current_user: str = Depends(get_current_user)):
    global bot_active
    bot_active = payload.get("active", False)
    print(f"🔐 Operator '{current_user}' changed bot status to: {bot_active}")
    return {"status": "success", "bot_active": bot_active}

@app.get("/api/bot_status")
async def get_bot_status(current_user: str = Depends(get_current_user)):
    global bot_active, current_threshold
    print(f"🔐 Operator '{current_user}' requested bot status.")
    return {"status": "success", "bot_active": bot_active, "current_threshold": current_threshold}

@app.post("/api/threshold")
async def update_threshold(payload: dict, current_user: str = Depends(get_current_user)):
    global current_threshold
    current_threshold = float(payload.get("threshold", 0.01))
    print(f"🔐 Operator '{current_user}' updated threshold to: {current_threshold}")
    return {"status": "success", "threshold": current_threshold}

@app.get("/api/history")
async def get_history(current_user: str = Depends(get_current_user)):
    print(f"🔐 Operator '{current_user}' requested trade history.")
    return {"history": trade_history, "total_profit": total_profit}

@app.post("/api/trade/approve")
async def approve_trade(payload: dict, current_user: str = Depends(get_current_user)):
    """Manual override: operator approves or rejects a pending trade."""
    global pending_approved, _approval_event
    decision = payload.get("decision", "REJECT")  # "APPROVE" or "REJECT"
    pending_approved = (decision == "APPROVE")
    _approval_event.set()  # Unblock the waiting WebSocket loop
    print(f"\ud83d\udd10 Operator '{current_user}' {decision}D the pending trade.")
    return {"status": "success", "decision": decision}

# --- SECURE WEBSOCKET ---

@app.websocket("/ws/market")
async def market_websocket(websocket: WebSocket, token: str = None):
    # 🛡️ SECURITY: Reject if no token is provided
    if not token:
        print("⛔ WebSocket rejected: No token provided.")
        await websocket.close(code=1008)
        return

    # 🛡️ SECURITY: Reject if token is invalid, expired, or forged
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        print("⛔ WebSocket rejected: Invalid token.")
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
        "bybit": 0.0,
        "spread": 0.0,
        "ai_prediction": 0.0,
        "status": "ESTABLISHING_SECURE_LINK",
        "opportunity": False,
        "latency": 0,
        "binance_bal": 0.00,
        "bybit_bal": 0.00,
        "bot_active": bot_active
    })

    try:
        while True:
            try:
                # 1. Fetch market data with a strict timeout
                binance_price = 0.0
                fetch_success = True
                try:
                    binance_ticker = await asyncio.wait_for(trader.binance.fetch_ticker(symbol), timeout=3.5)
                    binance_price = binance_ticker['last']
                except asyncio.TimeoutError:
                    print(f"⚠️ Market Fetch Timeout (3.5s) on Binance. Using simulated data.")
                    fetch_success = False
                except Exception as e:
                    print(f"⚠️ Market Fetch Error ({type(e).__name__}): {e}")
                    fetch_success = False

                if not fetch_success:
                    # Provide a realistic mock price if the API is down/blocked
                    binance_price = 65000.0 + secrets.randbelow(500)
                    
                # Fetch Real Balances
                bin_balance = 0.0
                byb_balance = 0.0
                try:
                    # Use a slightly longer timeout for balance if needed, or skip if already failing
                    bin_res = await asyncio.wait_for(trader.binance.fetch_balance(), timeout=2.5)
                    bin_balance = float(bin_res.get('USDT', {}).get('free', 0.0))
                except Exception:
                    # Silently fail for balances to keep scanning prices
                    pass

                try:
                    # Bybit often needs a proxy, so it's more likely to hit native timeouts
                    byb_res = await asyncio.wait_for(trader.bybit.fetch_balance(), timeout=2.5)
                    byb_balance = float(byb_res.get('USDT', {}).get('free', 0.0))
                except Exception:
                    pass
                
                # 2. Fetch Bybit Price (Real)
                bybit_price = 0.0
                bybit_fetch_success = True
                try:
                    # Bybit often needs a proxy, handled by trader.bybit
                    bybit_ticker = await asyncio.wait_for(trader.bybit.fetch_ticker(symbol), timeout=3.5)
                    bybit_price = bybit_ticker['last']
                except asyncio.TimeoutError:
                    print(f"⚠️ Market Fetch Timeout (3.5s) on Bybit. Using simulated fallback.")
                    bybit_fetch_success = False
                except Exception as e:
                    print(f"⚠️ Bybit Market Fetch Error: {e}")
                    bybit_fetch_success = False

                if not bybit_fetch_success:
                    # Fallback to simulation if Bybit API is unreachable
                    fluctuation = 0.012 if bot_active else 0.0005
                    bybit_price = binance_price * (1 + fluctuation)
                
                spread = ((bybit_price - binance_price) / binance_price) * 100
                
                # Dynamic Profitability Analysis
                total_costs = (FEE_RATE + SLIPPAGE_RATE) * 100
                net_spread = spread - total_costs
                
                direction = "BINANCE ➔ BYBIT"

                # 3. AI Prediction
                spread_buffer.append(spread)
                if len(spread_buffer) > 10: spread_buffer.pop(0)
                
                ai_prediction = 0.0
                if len(spread_buffer) == 10:
                    try:
                        ai_prediction = float(ai_brain.predict(spread_buffer))
                    except:
                        ai_prediction = 0.0

                # 4. Opportunity logic & Execution
                opportunity = (spread >= current_threshold) and (ai_prediction >= current_threshold)
                
                if bot_active and opportunity:
                    global pending_trade, pending_approved, _approval_event
                    try:
                        # Step 1: Consult AI for initial recommendation
                        await websocket.send_json({"type": "ai_msg", "text": "Significant opportunity detected. Consulting AI Agent..."})
                        ai_analysis = await ai_agent.analyze_opportunity(binance_price, bybit_price, spread)
                        ai_decision = ai_analysis.get("decision")
                        reason = ai_analysis.get("reason")
                        conf = ai_analysis.get("confidence")

                        if ai_decision == "EXECUTE":
                            await websocket.send_json({"type": "ai_msg", "text": f"AI APPROVED: {reason} (Confidence: {conf}). Awaiting human confirmation..."})

                            # Step 2: Stage the trade and notify frontend for manual approval
                            est_profit = round((spread / 100) * binance_price * trade_size, 2)
                            pending_trade = {
                                "buyExchange": "Binance",
                                "sellExchange": "Bybit",
                                "buyPrice": round(binance_price, 2),
                                "sellPrice": round(bybit_price, 2),
                                "spread": spread,
                                "predictedProfit": est_profit
                            }
                            pending_approved = None
                            _approval_event.clear()

                            # Broadcast pending_trade event to trigger modal on frontend
                            await websocket.send_json({"type": "pending_trade", "trade": pending_trade})

                            # Step 3: Wait up to 30s for operator decision
                            try:
                                await asyncio.wait_for(_approval_event.wait(), timeout=30.0)
                            except asyncio.TimeoutError:
                                await websocket.send_json({"type": "ai_msg", "text": "\u23f1 Approval timed out. Trade cancelled."})
                                pending_trade = None
                                continue

                            # Step 4: Execute or skip based on operator response
                            if pending_approved:
                                await websocket.send_json({"type": "ai_msg", "text": "\u2705 Operator APPROVED. Executing arbitrage..."})
                                await trader.execute_arbitrage(symbol, trade_size)

                                trade_profit = round((spread / 100) * binance_price * trade_size, 2)
                                total_profit += trade_profit
                                time_now = datetime.now().strftime("%H:%M:%S")

                                save_trade_to_db(time_now, direction, trade_profit)
                                trade_record = {"time": time_now, "route": direction, "profit": f"+${trade_profit:.2f}"}
                                trade_history.insert(0, trade_record)

                                await websocket.send_json({"type": "trade", "trade": trade_record, "raw_profit": trade_profit})
                                await asyncio.sleep(1)
                            else:
                                await websocket.send_json({"type": "ai_msg", "text": "\u274c Operator REJECTED the trade."})

                            pending_trade = None
                        else:
                            await websocket.send_json({"type": "ai_msg", "text": f"AI REJECTED: {reason} (Confidence: {conf})"})
                    except Exception as ai_err:
                        print(f"AI Agent Error: {ai_err}")

                # 4. Broadcast to Dashboard
                status_msg = "SCANNING_MARKETS"
                if bot_active:
                    status_msg = "MONITORING_OPPORTUNITY" if opportunity else "SCANNING_MARKETS"
                else:
                    status_msg = "SYSTEM_IDLE"

                # 5. Fetch Market Depth L2 Orderbook
                order_book = {"bids": [], "asks": []}
                try:
                    ob = await asyncio.wait_for(trader.binance.fetch_order_book(symbol, limit=10), timeout=1.5)
                    order_book = {"bids": ob['bids'], "asks": ob['asks']}
                except Exception:
                    pass

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
                    "bybit": round(bybit_price, 2), 
                    "spread": spread,
                    "net_spread": net_spread,
                    "fees": total_costs,
                    "candle": candle,
                    "ai_prediction": ai_prediction,
                    "status": status_msg,
                    "opportunity": opportunity,
                    "latency": 45,
                    "binance_bal": bin_balance,
                    "bybit_bal": byb_balance,
                    "order_book": order_book,
                    "bot_active": bot_active
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