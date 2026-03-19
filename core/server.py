import sys
import os
import asyncio
import json
import websockets
import random
import sqlite3
import uvicorn
import io
import csv
import time
from fastapi import FastAPI, WebSocket, Request, Body  # Added Body here
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

# --- 1. PATH & IMPORT FIX ---
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# Import the analyst instance from your llm folder
try:
    from llm.chatbot import analyst
except ImportError:
    # Fallback if the file is missing during a quick test
    class MockAnalyst:
        def get_response(self, q): return "AI Module not found in llm/chatbot.py"
    analyst = MockAnalyst()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. DATABASE SETUP ---
def init_db():
    with sqlite3.connect('trades.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS trades 
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                          time TEXT, 
                          route TEXT, 
                          profit REAL)''')
        conn.commit()

init_db()

# Global State
config = {"threshold": 0.05, "trade_amount": 10000}
prices = {"binance": 0.0, "bybit": 0.0, "latency": 0}

# --- 3. MARKET DATA FETCHING ---
async def fetch_market_data():
    url = "wss://stream.binance.com:9443/ws/btcusdt@trade"
    while True:
        try:
            async with websockets.connect(url) as ws:
                while True:
                    raw_data = await ws.recv()
                    data = json.loads(raw_data)
                    
                    # Latency Calculation
                    event_time = data.get("E", 0)
                    current_time_ms = int(time.time() * 1000)
                    prices["latency"] = current_time_ms - event_time

                    prices["binance"] = float(data["p"])
                    # Simulate Bybit price
                    prices["bybit"] = prices["binance"] + random.uniform(-15.0, 15.0)
        except Exception as e:
            print(f"Connection error: {e}")
            await asyncio.sleep(2)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(fetch_market_data())

# --- 4. ENDPOINTS ---

@app.get("/get_trades")
async def get_trades():
    try:
        with sqlite3.connect('trades.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, time, route, profit FROM trades ORDER BY id DESC LIMIT 10")
            rows = cursor.fetchall()
            return [{"id": r[0], "time": r[1], "route": r[2], "profit": f"${r[3]:.2f}"} for r in rows]
    except Exception as e:
        return {"error": str(e)}

@app.get("/download_trades")
async def download_trades():
    try:
        with sqlite3.connect('trades.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trades ORDER BY id DESC")
            rows = cursor.fetchall()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Timestamp", "Route", "Profit ($)"])
        writer.writerows(rows)
        
        response_content = output.getvalue().encode('utf-8')
        return StreamingResponse(
            io.BytesIO(response_content),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=trade_history.csv"}
        )
    except Exception as e:
        return {"error": str(e)}

@app.websocket("/ws/market")
async def market_data(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await asyncio.sleep(1)
            b, by = prices["binance"], prices["bybit"]
            lat = prices.get("latency", 0)
            
            if b > 0:
                diff = abs(by - b)
                raw_spread = (diff / b) * 100
                net_profit = raw_spread - 0.15 
                direction = "BINANCE ➔ BYBIT" if b < by else "BYBIT ➔ BINANCE"
                is_op = net_profit > config["threshold"]

                if is_op:
                    with sqlite3.connect('trades.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO trades (time, route, profit) VALUES (datetime('now', 'localtime'), ?, ?)", 
                                       (direction, round(config["trade_amount"] * (net_profit/100), 2)))
                        conn.commit()

                await websocket.send_json({
                    "binance": round(b, 2), 
                    "kraken": round(by, 2), 
                    "spread": round(raw_spread, 3), 
                    "net_profit": round(net_profit, 3),
                    "direction": direction, 
                    "opportunity": is_op,
                    "threshold": config["threshold"],
                    "latency": lat
                })
    except:
        pass

# FIXED: Combined the two /ask_ai routes into one clean endpoint
@app.post("/ask_ai")
async def ask_ai(payload: dict = Body(...)):
    question = payload.get("question", "")
    # Call the response logic from your llm/chatbot.py file
    answer = analyst.get_response(question) 
    return {"answer": answer}

@app.post("/update_threshold/{value}")
async def update_threshold(value: float):
    config["threshold"] = value
    return {"status": "success"}

# --- SERVER LAUNCH ---
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)