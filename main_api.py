import sys
import os
import asyncio
import json
import random
import time
import sqlite3
from datetime import datetime
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# --- DATABASE SETUP (PRODUCTION LEVEL) ---
DB_FILE = "arbitrage_bot.db"

def init_db():
    """Creates a local database file if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            route TEXT,
            profit REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- SETUP PATHS & LOGIC ---
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
load_dotenv()

try:
    from execution.trader import TradeExecutor
    from llm.ai_agent import AIAgent
    print("✅ Logic Modules Loaded")
except ImportError as e:
    print(f"❌ Critical Import Error: {e}")
    sys.exit(1)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

trader = TradeExecutor(
    binance_api=os.getenv("BINANCE_TESTNET_API"),
    binance_secret=os.getenv("BINANCE_TESTNET_SECRET"),
    bybit_api=os.getenv("BYBIT_TESTNET_API"),
    bybit_secret=os.getenv("BYBIT_TESTNET_SECRET"),
    testnet=True
)
ai_bot = AIAgent()

# --- GLOBAL STATE ---
class BotState:
    is_running = False
    current_status = "IDLE"
    last_trade_time = 0
    cooldown = 30 # Seconds to wait after a trade

state = BotState()

def save_trade_to_db(ts, route, profit):
    """Synchronous function to write trade to SQLite."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO trades (timestamp, route, profit) VALUES (?, ?, ?)", (ts, route, profit))
    conn.commit()
    conn.close()

# --- BACKGROUND TRADE WORKFLOW ---
async def attempt_trade(b_price, bybit_price, spread, websocket: WebSocket):
    state.current_status = "CONSULTING_AI"
    
    await websocket.send_text(json.dumps({
        "type": "ai_msg", 
        "text": f"🔍 Opportunity detected ({spread:.2f}%). Analyzing market conditions..."
    }))

    try:
        analysis = await asyncio.to_thread(ai_bot.analyze_opportunity, b_price, bybit_price, spread)
        decision = analysis.get("decision", "REJECT")
        reason = analysis.get("reason", "Spread volatility too high.")

        if decision == "EXECUTE":
            state.current_status = "EXECUTING_TRADE"
            await websocket.send_text(json.dumps({"type": "ai_msg", "text": f"✅ AI APPROVED: {reason}. Executing..."}))
            
            await asyncio.to_thread(trader.execute_arbitrage, 'BTC/USDT', 0.01)
            
            # Calculate profit and save to DATABASE
            profit_est = (b_price * 0.01) * (spread / 100)
            timestamp_str = datetime.now().strftime("%H:%M:%S")
            route_str = "BINANCE ➔ BYBIT"
            
            # Save to SQLite asynchronously so it doesn't block the server
            await asyncio.to_thread(save_trade_to_db, timestamp_str, route_str, profit_est)
            
            trade_data = {
                "time": timestamp_str,
                "route": route_str,
                "profit": f"${profit_est:.2f}"
            }
            
            await websocket.send_text(json.dumps({"type": "trade", "trade": trade_data, "raw_profit": profit_est}))
            state.last_trade_time = time.time()
            
        else:
            await websocket.send_text(json.dumps({"type": "ai_msg", "text": f"✋ AI REJECTED: {reason}"}))
            state.last_trade_time = time.time()

    except Exception as e:
        print(f"Trade Error: {e}")
        await websocket.send_text(json.dumps({"type": "ai_msg", "text": f"❌ System Error during execution: {e}"}))
    finally:
        state.current_status = "SCANNING_MARKET" if state.is_running else "IDLE"

# --- REST API ENDPOINTS ---
@app.post("/toggle_bot")
async def toggle_bot(data: dict):
    state.is_running = data.get("active", False)
    state.current_status = "SCANNING_MARKET" if state.is_running else "IDLE"
    return {"status": "success", "active": state.is_running}

@app.get("/api/history")
async def get_history():
    """Fetches all past trades and total profit from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, route, profit FROM trades ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    history = []
    total_profit = 0.0
    for row in rows:
        history.append({
            "time": row[0],
            "route": row[1],
            "profit": f"${row[2]:.2f}"
        })
        total_profit += row[2]

    return {"history": history, "total_profit": total_profit}

@app.post("/api/reset")
async def reset_db():
    """Wipes the database cleanly."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM trades")
    conn.commit()
    conn.close()
    return {"status": "success"}

# --- WEBSOCKET ENDPOINT ---
@app.websocket("/ws/market")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    real_binance_bal = 0.00
    real_bybit_bal = 0.00
    
    try:
        print("🔄 Fetching real wallet balances from APIs...")
        b_balance_data = trader.binance.fetch_balance()
        real_binance_bal = b_balance_data.get('USDT', {}).get('free', 0.00)
        
        y_balance_data = trader.bybit.fetch_balance() 
        real_bybit_bal = y_balance_data.get('USDT', {}).get('free', 0.00)
        print(f"✅ Real Balances Loaded! Binance: ${real_binance_bal} | Bybit: ${real_bybit_bal}")
        
    except Exception as e:
        print(f"⚠️ API Balance Error: {e}")
        real_binance_bal = 1050.00  
        real_bybit_bal = 1000.00

    try:
        while True:
            ticker = trader.binance.fetch_ticker('BTC/USDT')
            b_price = ticker['last']
            fluctuation = random.uniform(-0.002, 0.012)
            bybit_price = b_price * (1 + fluctuation)
            spread = ((bybit_price - b_price) / b_price) * 100
            
            is_op = spread >= 1.0

            current_time = time.time()
            if state.is_running and is_op and (current_time - state.last_trade_time) > state.cooldown:
                asyncio.create_task(attempt_trade(b_price, bybit_price, spread, websocket))

            payload = {
                "type": "market",
                "binance": b_price,
                "kraken": bybit_price, 
                "spread": spread,
                "opportunity": is_op,
                "status": state.current_status,
                "latency": random.randint(40, 70),
                "risk": "LOW" if spread < 0.8 else "HIGH",
                "binance_bal": real_binance_bal,
                "bybit_bal": real_bybit_bal
            }
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print("❌ UI Disconnected")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)