import asyncio
import json
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
# Using your existing naming convention
from core.server import trader, ai_bot 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/market")
async def market_stream(websocket: WebSocket):
    await websocket.accept()
    while True:
        # Reusing the exact logic from your run_arbitrage_bot
        binance_ticker = trader.binance.fetch_ticker('BTC/USDT')
        b_price = binance_ticker['last']
        
        # Simulating Bybit as per your server.py logic
        bybit_price = b_price * (1 + 0.001) 
        spread = ((bybit_price - b_price) / b_price) * 100

        # Sending the data in the format your Index.tsx expects
        payload = {
            "binance": b_price,
            "kraken": bybit_price, # Mapped to your 'bybit' state in React
            "spread": spread,
            "opportunity": spread >= 1.0,
            "latency": 55,
            "risk": "LOW"
        }
        
        await websocket.send_text(json.dumps(payload))
        await asyncio.sleep(1) # Match your desired update frequency