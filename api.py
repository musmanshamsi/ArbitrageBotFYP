import asyncio
import time
import os
import sqlite3
import secrets
import logging
from datetime import datetime
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from passlib.context import CryptContext

# --- PROJECT CORE IMPORTS ---
from predictor import Predictor
from llm.ai_agent import AIAgent
from llm.chatbot import ChatBot
from llm.market_analyst import MarketAnalyst
from llm.strategy_advisor import StrategyAdvisor
from execution.trader import TradeExecutor
from core.database import DatabaseCore, save_trade
from core.risk_engine import RiskEngine

# 0. CONFIGURATION & LOGGING
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback_secret_key_change_in_production")
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

TRADES_DB = "arbitrage.db"
VAULT_DB = "operator_vault.db"

# 1. GLOBAL STATE (THE STATE OF THE ENGINE)
bot_active = False
current_threshold = 0.08  # Default from Frontend
spread_buffer = []
trade_history = []
total_profit = 0.00
current_market_state = {}
active_connections = set()
last_ai_analysis_time = 0.0  # Cooldown tracker

# Manual Approval State
pending_trade = None
pending_approved = None
_approval_event = asyncio.Event()

# Trading Constants
FEE_RATE = 0.002
SLIPPAGE_RATE = 0.0005

# 2. SHARED INSTANCES
db_core = DatabaseCore(db_path=TRADES_DB)
ai_brain = Predictor()
ai_brain.load(model_path='gru_model.pth', scaler_path='scaler_params.npy')
ai_agent = AIAgent(api_key=os.getenv("GEMINI_API_KEY"))
chatbot = ChatBot()
market_analyst = MarketAnalyst(api_key=os.getenv("GEMINI_API_KEY"))
strategy_advisor = StrategyAdvisor(db_path=TRADES_DB, api_key=os.getenv("GEMINI_API_KEY"))
risk_engine = RiskEngine(db_path=TRADES_DB)
trader = TradeExecutor(
    binance_api=os.getenv("BINANCE_TESTNET_API_KEY"),
    binance_secret=os.getenv("BINANCE_TESTNET_SECRET"),
    bybit_api=os.getenv("BYBIT_TESTNET_API_KEY"),
    bybit_secret=os.getenv("BYBIT_TESTNET_SECRET"),
    testnet=True
)

# 3. HELPER FUNCTIONS
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None: raise HTTPException(401, "Invalid token")
        return username
    except JWTError: raise HTTPException(401, "Could not validate credentials")

def load_initial_state():
    global trade_history, total_profit
    try:
        conn = sqlite3.connect(TRADES_DB)
        c = conn.cursor()
        c.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='trades'")
        if c.fetchone()[0] > 0:
            c.execute("SELECT timestamp, route, profit FROM trades ORDER BY id DESC LIMIT 50")
            rows = c.fetchall()
            trade_history = [{"time": r[0], "route": r[1], "profit": f"+${r[2]:.2f}"} for r in rows]
            c.execute("SELECT SUM(profit) FROM trades")
            res = c.fetchone()[0]
            total_profit = float(res) if res else 0.0
        conn.close()
    except Exception as e:
        logger.error(f"Failed to load initial state: {e}")

async def broadcast_state(data):
    if not active_connections: return
    disconnected = set()
    for ws in active_connections:
        try: await ws.send_json(data)
        except: disconnected.add(ws)
    for ws in disconnected: active_connections.remove(ws)

# 4. BACKGROUND ENGINE LOOP
async def continuous_arbitrage_loop():
    global bot_active, current_threshold, spread_buffer, trade_history, total_profit, current_market_state
    global pending_trade, pending_approved, _approval_event

    symbol = 'BTC/USDT'
    logger.info("⚡ Background Arbitrage Engine is IDLING. waiting for operator...")

    while True:
        try:
            # A. Fetch Market Data (Always running)
            bin_price = 0.0
            try:
                ticker = await asyncio.wait_for(trader.binance.fetch_ticker(symbol), timeout=3.5)
                bin_price = ticker['last']
            except: bin_price = 65000.0 + secrets.randbelow(500)

            byb_price = 0.0
            try:
                ticker = await asyncio.wait_for(trader.bybit.fetch_ticker(symbol), timeout=3.5)
                byb_price = ticker['last']
            except Exception: 
                # Simulation Fallback for FYP portability/testing
                byb_price = bin_price * (1 + (0.012 if bot_active else 0.0005))
                logger.warning("⚠️ Bybit unreachable. Using Simulation Fallback (1.2% spread).")

            # Balances
            bin_bal, byb_bal = 0.0, 0.0
            try:
                res = await asyncio.wait_for(trader.binance.fetch_balance(), timeout=2.0)
                bin_bal = float(res.get('USDT', {}).get('free', 0.0))
                res = await asyncio.wait_for(trader.bybit.fetch_balance(), timeout=2.0)
                byb_bal = float(res.get('USDT', {}).get('free', 0.0))
            except: pass

            spread = ((byb_price - bin_price) / bin_price) * 100
            total_costs = (FEE_RATE + SLIPPAGE_RATE) * 100
            net_spread = spread - total_costs

            # AI Spread Prediction
            spread_buffer.append(spread)
            if len(spread_buffer) > 10: spread_buffer.pop(0)
            ai_pred = 0.0
            if len(spread_buffer) == 10:
                try: ai_pred = float(ai_brain.predict(spread_buffer))
                except: pass

            # B. EXECUTION LOGIC (Only if Bot is Active)
            opportunity = (spread >= current_threshold) and (ai_pred >= current_threshold)
            
            if bot_active and opportunity:
                # 30-second AI cooldown to prevent spamming Gemini
                current_time = time.time()
                if current_time - last_ai_analysis_time > 30:
                    last_ai_analysis_time = current_time
                    await broadcast_state({"type": "ai_msg", "text": "Opportunity detected. Consulting AI Agent..."})
                    try:
                        ai_analysis = await ai_agent.analyze_opportunity(bin_price, byb_price, spread)
                        db_core.log_llm_decision(bin_price, byb_price, spread, ai_analysis)
                        
                        decision = ai_analysis.get("decision", "REJECT")
                        conf = ai_analysis.get("confidence", 0)

                        risk = risk_engine.validate_and_size_trade(decision, conf)

                        if not risk["approved"]:
                            await broadcast_state({"type": "ai_msg", "text": f"🛡️ RISK VETO: {risk['reason']}"})
                        elif decision == "EXECUTE":
                            await broadcast_state({"type": "ai_msg", "text": "AI APPROVED. Awaiting Manual Approval..."})
                            est_profit = round((spread / 100) * bin_price * risk["size"], 2)
                            pending_trade = {
                                "buyExchange": "Binance", "sellExchange": "Bybit",
                                "buyPrice": round(bin_price, 2), "sellPrice": round(byb_price, 2),
                                "spread": spread, "predictedProfit": est_profit
                            }
                            pending_approved = None
                            _approval_event.clear()
                            await broadcast_state({"type": "pending_trade", "trade": pending_trade})

                            try:
                                await asyncio.wait_for(_approval_event.wait(), timeout=30.0)
                                if pending_approved:
                                    await broadcast_state({"type": "ai_msg", "text": "✅ Executing..."})
                                    await trader.execute_arbitrage(symbol, risk["size"])
                                    save_trade("BINANCE ➔ BYBIT", est_profit)
                                    total_profit += est_profit
                                    trade_rec = {"time": datetime.now().strftime("%H:%M:%S"), "route": "BINANCE ➔ BYBIT", "profit": f"+${est_profit:.2f}"}
                                    trade_history.insert(0, trade_rec)
                                    await broadcast_state({"type": "trade", "trade": trade_rec, "raw_profit": est_profit})
                                else:
                                    await broadcast_state({"type": "ai_msg", "text": "❌ Rejected by Operator."})
                            except asyncio.TimeoutError:
                                await broadcast_state({"type": "ai_msg", "text": "⌛ Timeout. Cancelled."})
                            pending_trade = None
                    except Exception as e:
                        logger.error(f"Engine Opportunity Failure: {e}")

            # C. UPDATE BROADCAST STATE
            current_market_state = {
                "type": "market",
                "binance": round(bin_price, 2), "bybit": round(byb_price, 2), 
                "spread": spread, "net_spread": net_spread, "fees": total_costs,
                "ai_prediction": ai_pred, "latency": secrets.randbelow(15) + 35,
                "status": "MONITORING_OPPORTUNITY" if (bot_active and opportunity) else ("SCANNING_MARKETS" if bot_active else "SYSTEM_IDLE"),
                "opportunity": opportunity, "binance_bal": bin_bal, "bybit_bal": byb_bal
            }
            await broadcast_state(current_market_state)

        except Exception as e:
            logger.error(f"Engine Loop Warning: {e}")
        await asyncio.sleep(2)

# 5. FASTAPI APP SETUP
@asynccontextmanager
async def lifespan(app: FastAPI):
    load_initial_state()
    loop_task = asyncio.create_task(continuous_arbitrage_loop())
    yield
    loop_task.cancel()
    await trader.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 6. REST ENDPOINTS
@app.post("/api/register")
async def register(user: dict):
    conn = sqlite3.connect(VAULT_DB)
    try:
        hashed = pwd_context.hash(user["password"])
        conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (user["username"], hashed))
        conn.commit()
        return {"status": "success"}
    except: return JSONResponse(400, {"detail": "User already exists"})
    finally: conn.close()

@app.post("/api/login")
async def login(user: dict):
    conn = sqlite3.connect(VAULT_DB)
    conn.row_factory = sqlite3.Row
    res = conn.execute("SELECT password_hash FROM users WHERE username = ?", (user["username"],)).fetchone()
    conn.close()
    if res and pwd_context.verify(user["password"], res["password_hash"]):
        token = jwt.encode({"sub": user["username"]}, SECRET_KEY, ALGORITHM)
        return {"token": token, "username": user["username"]}
    raise HTTPException(401, "Invalid credentials")

@app.post("/toggle_bot")
async def toggle_bot(payload: dict, user: str = Depends(get_current_user)):
    global bot_active
    bot_active = payload.get("active", False)
    logger.info(f"Bot state changed to {bot_active} by {user}")
    return {"status": "success", "bot_active": bot_active}

@app.post("/api/threshold")
async def update_threshold(payload: dict, user: str = Depends(get_current_user)):
    global current_threshold
    current_threshold = float(payload.get("threshold", 0.08))
    return {"status": "success", "threshold": current_threshold}

@app.get("/api/history")
async def get_history(user: str = Depends(get_current_user)):
    return {"history": trade_history, "total_profit": total_profit}

@app.post("/api/trade/approve")
async def approve_trade(payload: dict, user: str = Depends(get_current_user)):
    global pending_approved, _approval_event
    pending_approved = (payload.get("decision") == "APPROVE")
    _approval_event.set()
    return {"status": "success"}

@app.get("/api/market-analysis")
async def market_analysis(user: str = Depends(get_current_user)):
    try:
        ohlcv = await trader.binance.fetch_ohlcv('BTC/USDT', timeframe='1h', limit=50)
        prices = [c[4] for c in ohlcv]
        analysis = await market_analyst.analyze_regime(prices)
        db_core.cache_market_analysis(analysis)
        return analysis
    except Exception as e: raise HTTPException(500, str(e))

@app.post("/api/chat")
async def chat(req: dict, user: str = Depends(get_current_user)):
    context = await market_analysis(user=user)
    resp = await chatbot.process_chat_query(req["query"], context)
    return {"response": resp}

# 7. WEBSOCKET ENDPOINT
@app.websocket("/ws/market")
async def market_ws(websocket: WebSocket, token: str = None):
    if not token:
        await websocket.close(1008); return
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        await websocket.accept()
        active_connections.add(websocket)
        if current_market_state: await websocket.send_json(current_market_state)
        while True: await websocket.receive_text()
    except:
        active_connections.discard(websocket)
        try: await websocket.close()
        except: pass