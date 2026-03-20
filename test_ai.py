from dotenv import load_dotenv
import os
from llm.ai_agent import AIAgent

load_dotenv()

print("🚀 Initializing AI Arbitrage Agent...")
try:
    bot = AIAgent()
    
    print("\n📊 Simulating a profitable 1.5% spread...")
    # Simulating: Binance price = 70000, Bybit price = 71050, Spread = 1.5%
    response = bot.analyze_opportunity(70000, 71050, 1.5) 
    
    print("\n✅ FINAL AI DECISION:")
    print(response)

except Exception as e:
    print(f"\n❌ CRITICAL SYSTEM FAILURE: {str(e)}")