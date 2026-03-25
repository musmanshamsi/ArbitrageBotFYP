import asyncio
import os
import sqlite3
import ccxt.async_support as ccxt
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from predictor import Predictor  # Imports your AI brain

# --- SECURITY IMPORTS ---
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

# Load environment variables
load_dotenv()

app = FastAPI()

# Allow React frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SECURITY CONFIG & DEPENDENCIES ---
SECRET_KEY = "your_super_secret_fyp_key" # Tip: Move this to .env before going live!
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Tells FastAPI where to look for the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

class UserAuth(BaseModel):
    username: str
    password: str

# 🛡️ The "Bouncer": Validates the token for protected routes
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode and verify the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    return username # Returns the verified operator's username


# --- DATABASE SETUP ---
DB_FILE = "arbitrage.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Existing trades table
    c.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT,
            route TEXT,
            profit REAL
        )
    ''')
    # Users table for authentication
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

def load_history():
    conn = sqlite3.connect(DB_FILE)
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
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO trades (time, route, profit) VALUES (?, ?, ?)", (time_str, route, profit_val))
    conn.commit()
    conn.close()

init_db()


# --- PUBLIC AUTHENTICATION ENDPOINTS ---

@app.post("/api/register")
async def register(user: UserAuth):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        hashed_pw = pwd_context.hash(user.password)
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user.username, hashed_pw))
        conn.commit()
        return {"status": "success", "message": "User registered"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    finally:
        conn.close()

@app.post("/api/login")
async def login(user: UserAuth):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (user.username,))
    result = c.fetchone()
    conn.close()

    if result and pwd_context.verify(user.password, result[0]):
        token = jwt.encode({"sub": user.username}, SECRET_KEY, algorithm=ALGORITHM)
        return {"status": "success", "token": token, "username": user.username}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")


# --- GLOBAL STATE & AI SETUP ---
bot_active = False
current_threshold = 0.08  # Controlled by React UI slider
trade_history, total_profit = load_history()

# Initialize AI Predictor
ai_brain = Predictor()
ai_brain.load(model_path='gru_model.pth', scaler_path='scaler_params.npy')
spread_buffer = []  # Stores the last 10 spreads for the AI

# --- EXCHANGE SETUP (TESTNET API) ---
exchange_binance = ccxt.binance({
    'apiKey': os.getenv('BINANCE_TESTNET_API_KEY', ''),
    'secret': os.getenv('BINANCE_TESTNET_SECRET', ''),
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'} 
})
exchange_binance.set_sandbox_mode(True) 

exchange_bybit = ccxt.bybit({
    'apiKey': os.getenv('BYBIT_TESTNET_API_KEY', ''),
    'secret': os.getenv('BYBIT_TESTNET_SECRET', ''),
    'enableRateLimit': True,
    'options': {
        'defaultType': 'spot', 
        'adjustForTimeDifference': True, 
        'recvWindow': 10000 
    }
})
exchange_bybit.set_sandbox_mode(True)

SYMBOL = 'BTC/USDT'
TRADE_SIZE = 0.01 


# --- SECURE REST API ENDPOINTS ---
# Notice the `current_user` dependency added to these routes!

@app.post("/toggle_bot")
async def toggle_bot(payload: dict, current_user: str = Depends(get_current_user)):
    global bot_active
    bot_active = payload.get("active", False)
    print(f"🔐 Operator '{current_user}' changed bot status to: {bot_active}")
    return {"status": "success", "bot_active": bot_active}

@app.post("/api/threshold")
async def update_threshold(payload: dict, current_user: str = Depends(get_current_user)):
    global current_threshold
    current_threshold = float(payload.get("threshold", 0.08))
    print(f"🔐 Operator '{current_user}' updated threshold to: {current_threshold}")
    return {"status": "success", "threshold": current_threshold}

@app.get("/api/history")
async def get_history(current_user: str = Depends(get_current_user)):
    print(f"🔐 Operator '{current_user}' requested trade history.")
    return {"history": trade_history, "total_profit": total_profit}


# --- SECURE WEBSOCKET & ARBITRAGE ENGINE ---

@app.websocket("/ws/market")
async def market_websocket(websocket: WebSocket, token: str = None):
    # 🛡️ SECURITY: Reject if no token is provided
    if not token:
        print("⛔ WebSocket rejected: No token provided.")
        await websocket.close(code=1008) # 1008 is standard for policy violation
        return
        
    # 🛡️ SECURITY: Reject if token is invalid, expired, or forged
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        print("⛔ WebSocket rejected: Invalid token.")
        await websocket.close(code=1008)
        return

    # If they pass the checks, let them in
    await websocket.accept()
    print("✅ FRONTEND SECURELY CONNECTED TO WEBSOCKET!")
    
    global bot_active, total_profit, trade_history, current_threshold, spread_buffer
    
    try:
        while True:
            try:
                print("⏳ 1. Requesting Binance Data...")
                binance_ticker = await exchange_binance.fetch_ticker(SYMBOL)
                print("✅ 1. Binance Data Received!")

                print("⏳ 2. Requesting Bybit Data...")
                bybit_ticker = await exchange_bybit.fetch_ticker(SYMBOL)
                print("✅ 2. Bybit Data Received!")
                
                binance_price = binance_ticker['last']
                bybit_price = bybit_ticker['last']

                # Mocking balances for UI
                binance_bal = 1500.00 
                bybit_bal = 1500.00

                # 2. Arbitrage Logic & Spread Calculation
                spread = 0.0
                direction = "IDLE"
                
                if binance_price < bybit_price:
                    spread = ((bybit_price - binance_price) / binance_price) * 100
                    direction = "BINANCE ➔ BYBIT"
                elif bybit_price < binance_price:
                    spread = ((binance_price - bybit_price) / bybit_price) * 100
                    direction = "BYBIT ➔ BINANCE"

                # 3. Feed the AI Brain
                spread_buffer.append(spread)
                if len(spread_buffer) > 10:
                    spread_buffer.pop(0)

                ai_prediction = 0.0
                if len(spread_buffer) == 10:
                    raw_pred = ai_brain.predict(spread_buffer)
                    
                    if hasattr(raw_pred, 'item'):
                        ai_prediction = float(raw_pred.item())
                    elif isinstance(raw_pred, (list, tuple)) or hasattr(raw_pred, '__iter__'):
                        ai_prediction = float(raw_pred[0])
                    else:
                        ai_prediction = float(raw_pred)

                # 4. Opportunity Check
                opportunity = (spread >= current_threshold) and (ai_prediction >= current_threshold)

                # 5. Execute Trade
                if bot_active and opportunity:
                    trade_profit = round((spread / 100) * binance_price * TRADE_SIZE, 2)
                    total_profit += trade_profit
                    time_now = datetime.now().strftime("%H:%M:%S")
                    
                    save_trade_to_db(time_now, direction, trade_profit)
                    
                    trade_record = {"time": time_now, "route": direction, "profit": f"+${trade_profit:.2f}"}
                    trade_history.insert(0, trade_record)
                    
                    print(f"🚀 TRADE EXECUTED: {direction} | Profit: ${trade_profit}")
                    
                    await websocket.send_json({
                        "type": "trade",
                        "trade": trade_record,
                        "raw_profit": trade_profit
                    })
                    await asyncio.sleep(2) 

                # 6. Broadcast Data to React UI
                status_msg = f"MONITORING_{direction.replace(' ➔ ', '_')}" if opportunity else "SCANNING_MARKETS"
                if not bot_active:
                    status_msg = "SYSTEM_IDLE"

                print("📦 3. Sending Data to React UI...")
                await websocket.send_json({
                    "type": "market",
                    "binance": round(binance_price, 2),
                    "kraken": round(bybit_price, 2), 
                    "spread": spread,
                    "ai_prediction": ai_prediction if len(spread_buffer) == 10 else 0.0,
                    "status": status_msg,
                    "opportunity": opportunity,
                    "latency": 45,
                    "binance_bal": binance_bal,
                    "bybit_bal": bybit_bal
                })
                print("✅ 3. Data Sent! Restarting loop...\n")

            except Exception as api_err:
                print("\n" + "="*50)
                print(f"🚨 CRITICAL ERROR: {type(api_err).__name__}")
                print(f"🚨 DETAILS: {api_err}")
                print("="*50 + "\n")
                
                await websocket.send_json({
                    "type": "ai_msg",
                    "text": "Market data fetching... Please hold."
                })
            
            await asyncio.sleep(1.5) 
            
    except WebSocketDisconnect:
        print("❌ Frontend Client Disconnected.")
    except Exception as e:
        print(f"❌ WebSocket Error: {e}")
    finally:
        await exchange_binance.close()
        await exchange_bybit.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)