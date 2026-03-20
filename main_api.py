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

# --- DATABASE SETUP ---
DB_FILE = "arbitrage_bot.db"

def init_db():
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
    print("✅ System Modules Loaded Successfully")
except ImportError as e:
    print(f"❌ Critical Import Error: {e}")
    sys.exit(1)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Initialize Exchange Connection
trader_logic = TradeExecutor(
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
    cooldown = 30 

state = BotState()

# --- HELPER FUNCTIONS ---
def save_trade_to_db(ts, route, profit):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO trades (timestamp, route, profit) VALUES (?, ?, ?)", (ts, route, profit))
    conn.commit()
    conn.close()

async def get_unified_balances(current_btc_price):
    """Calculates full account value across both exchanges."""
    try:
        # Fetch balances in parallel for speed
        b_task = asyncio.to_thread(trader_logic.binance.fetch_balance)
        y_task = asyncio.to_thread(trader_logic.bybit.fetch_balance)
        b_bal, y_bal = await asyncio.gather(b_task, y_task)

        def extract_assets(bal_obj):
            usdt = bal_obj.get('USDT', {}).get('total', 0.0)
            btc = bal_obj.get('BTC', {}).get('total', 0.0)
            return {
                "usdt": usdt,
                "btc": btc,
                "total_usd": usdt + (btc * current_btc_price)
            }

        binance_stats = extract_assets(b_bal)
        bybit_stats = extract_assets(y_bal)

        return {
            "binance": binance_stats,
            "bybit": bybit_stats,
            "grand_total": binance_stats['total_usd'] + bybit_stats['total_usd']
        }
    except Exception as e:
        print(f"Balance Sync Error: {e}")
        # Fallback to defaults if API fails
        return None

# --- BACKGROUND TRADE WORKFLOW ---
async def attempt_trade(b_price, bybit_price, spread, websocket: WebSocket):
    state.current_status = "CONSULTING_AI"
    await websocket.send_text(json.dumps({"type": "ai_msg", "text": f"🔍 Spread detected: {spread:.2f}%. AI is validating..."}))

    try:
        analysis = await asyncio.to_thread(ai_bot.analyze_opportunity, b_price, bybit_price, spread)
        if analysis.get("decision") == "EXECUTE":
            state.current_status = "EXECUTING_TRADE"
            await websocket.send_text(json.dumps({"type": "ai_msg", "text": "✅ AI APPROVED. Executing arbitrage..."}))
            
            # Real Execution Call
            await asyncio.to_thread(trader_logic.execute_arbitrage, 'BTC/USDT', 0.01)
            
            profit_est = (b_price * 0.01) * (spread / 100)
            ts = datetime.now().strftime("%H:%M:%S")
            
            await asyncio.to_thread(save_trade_to_db, ts, "BINANCE ➔ BYBIT", profit_est)
            
            await websocket.send_text(json.dumps({
                "type": "trade", 
                "trade": {"time": ts, "route": "BINANCE ➔ BYBIT", "profit": f"${profit_est:.2f}"},
                "raw_profit": profit_est
            }))
            state.last_trade_time = time.time()
        else:
            await websocket.send_text(json.dumps({"type": "ai_msg", "text": f"✋ AI REJECTED: {analysis.get('reason')}"}))
            state.last_trade_time = time.time()
    except Exception as e:
        print(f"Trade Error: {e}")
    finally:
        state.current_status = "SCANNING_MARKET" if state.is_running else "IDLE"

# --- API ROUTES ---
@app.post("/toggle_bot")
async def toggle_bot(data: dict):
    state.is_running = data.get("active", False)
    state.current_status = "SCANNING_MARKET" if state.is_running else "IDLE"
    return {"status": "success", "active": state.is_running}

@app.get("/api/history")
async def get_history():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, route, profit FROM trades ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
    total_profit = sum(row[2] for row in rows)
    history = [{"time": r[0], "route": r[1], "profit": f"${r[2]:.2f}"} for r in rows]
    return {"history": history, "total_profit": total_profit}

@app.post("/api/reset")
async def reset_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM trades")
    conn.commit()
    conn.close()
    return {"status": "success"}

# --- MAIN WEBSOCKET ---
@app.websocket("/ws/market")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # 1. Get Market Data
            ticker = await asyncio.to_thread(trader_logic.binance.fetch_ticker, 'BTC/USDT')
            b_price = ticker['last']
            
            # Simulated Spread Logic (Replace with real logic if preferred)
            fluctuation = random.uniform(-0.001, 0.011)
            bybit_price = b_price * (1 + fluctuation)
            spread = ((bybit_price - b_price) / b_price) * 100
            
            # 2. Get Unified Balances
            balances = await get_unified_balances(b_price)

            # 3. Check for Trades
            is_op = spread >= 1.0
            if state.is_running and is_op and (time.time() - state.last_trade_time) > state.cooldown:
                asyncio.create_task(attempt_trade(b_price, bybit_price, spread, websocket))

            # 4. Send Unified Payload
            payload = {
                "type": "market",
                "binance": b_price,
                "kraken": bybit_price, # Mapped to your UI component name
                "spread": spread,
                "opportunity": is_op,
                "status": state.current_status,
                "balances": balances, # New Complete Balance Object
                "latency": random.randint(30, 60),
                "risk": "LOW" if spread < 0.8 else "HIGH"
            }
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(1.5)

    except WebSocketDisconnect:
        print("❌ Frontend disconnected")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)