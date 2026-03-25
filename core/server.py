import sys
import os
import time
import random
from dotenv import load_dotenv

# --- THE FIX: Tell Python to look in the main folder ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
# -------------------------------------------------------

from execution.trader import TradeExecutor
from llm.ai_agent import AIAgent
from core.database import save_trade

# 1. Load the hidden keys securely
load_dotenv(os.path.join(parent_dir, '.env'))

bin_api = os.getenv("BINANCE_TESTNET_API_KEY")
bin_secret = os.getenv("BINANCE_TESTNET_SECRET")
byb_api = os.getenv("BYBIT_TESTNET_API_KEY")
byb_secret = os.getenv("BYBIT_TESTNET_SECRET")

# 2. Initialize the components
trader = TradeExecutor(
    binance_api=bin_api,
    binance_secret=bin_secret,
    bybit_api=byb_api,
    bybit_secret=byb_secret,
    testnet=True
)

ai_bot = AIAgent()

import asyncio

async def run_arbitrage_bot(ui_handle=None):
    """
    Main bot loop (Async version). 
    ui_handle: If provided, sends logs to the Tkinter GUI.
    """
    
    # Helper function to log to both Terminal and GUI
    def log_message(msg):
        print(msg)
        if ui_handle:
            ui_handle.log(msg)

    log_message("\n🧠 --- AI ARBITRAGE SYSTEM ONLINE --- 🧠")
    log_message("Monitoring Live Binance Data & Consulting Gemini AI...\n")
    
    last_ai_call = 0  
    ai_cooldown = 60  

    try:
        while True:
            try:
                # 1. Fetch Real Binance Price
                # Need to use await here because trader.binance is an async ccxt instance
                binance_ticker = await trader.binance.fetch_ticker('BTC/USDT')
                binance_price = binance_ticker['last']
                
                # 2. Simulate Bybit Price
                fluctuation = random.uniform(-0.005, 0.015) 
                bybit_price = binance_price * (1 + fluctuation)
                
                # 3. Calculate Spread
                spread_percent = ((bybit_price - binance_price) / binance_price) * 100
                
                # Live Output
                status_msg = f"📊 Binance: {binance_price:.2f} | Bybit (Sim): {bybit_price:.2f} | Spread: {spread_percent:.2f}%"
                log_message(status_msg)
                
                # 4. Smart AI-DRIVEN DECISION LOGIC
                current_time = time.time()
                
                if spread_percent >= 1.0:
                    if (current_time - last_ai_call) > ai_cooldown:
                        log_message(f"🔍 Significant Opportunity ({spread_percent:.2f}%). Consulting AI Agent...")
                        
                        # AIAgent analyze_opportunity is now async
                        ai_analysis = await ai_bot.analyze_opportunity(binance_price, bybit_price, spread_percent)
                        last_ai_call = time.time() 
                        
                        decision = ai_analysis.get("decision")
                        reason = ai_analysis.get("reason")
                        conf = ai_analysis.get("confidence")

                        if decision == "EXECUTE":
                            log_message(f"🤖 AI APPROVED: {reason} (Confidence: {conf})")
                            
                            # 🔥 EXECUTE THE TRADE (Async)
                            await trader.execute_arbitrage('BTC/USDT', 0.01)
                            
                            # Record the trade in the shared database
                            save_trade("BINANCE ➔ BYBIT", round((spread_percent / 100) * binance_price * 0.01, 2))
                            
                            log_message("⏳ Trade complete. Cooldown for 15 seconds...\n")
                            await asyncio.sleep(15)
                        else:
                            log_message(f"✋ AI REJECTED: {reason} (Confidence: {conf})")
                    else:
                        wait_remaining = int(ai_cooldown - (current_time - last_ai_call))
                        log_message(f"⏳ Spread is good ({spread_percent:.2f}%), but AI is on cooldown ({wait_remaining}s remaining).")
                
                await asyncio.sleep(3)
                
            except Exception as e:
                log_message(f"❌ Error in Brain Loop: {e}")
                await asyncio.sleep(10)
    finally:
        await trader.close()

if __name__ == "__main__":
    asyncio.run(run_arbitrage_bot())