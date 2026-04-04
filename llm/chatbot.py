import os
import logging
import asyncio
from dotenv import load_dotenv
from google import genai
from llm.ai_agent import AIAgent

load_dotenv()
logger = logging.getLogger(__name__)

class ChatBot:
    def __init__(self, api_key: str = None):
        """
        Initializes the ChatBot with the Senior Arbitrage Analyst persona
        and connects it to the core AIAgent.
        """
        # 1. Secure Key Loading (No hardcoded placeholders)
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        # 2. Correctly instantiate the Agent and pass the key down
        self.agent = AIAgent(api_key=self.api_key)
        
        # 3. Setup the distinct Chat Client for the Q&A Sidebar
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
            self.model_id = 'gemini-2.0-flash'
        else:
            self.client = None
            logger.error("CRITICAL: ChatBot initialized without API key!")

        # 4. Strict Persona Definition
        self.system_prompt = (
            "You are ArbPro, a Senior Quantitative Cryptocurrency Arbitrage Analyst. "
            "Your job is to explain trading decisions, analyze spreads between Binance and Bybit, "
            "and evaluate market risk. Do not answer general knowledge or non-financial questions. "
            "Keep answers concise, professional, and focused on actionable quantitative metrics."
        )

    async def process_chat_query(self, user_query: str, market_context: dict = None) -> str:
        """
        Handles free-form text questions from the frontend Sidebar.
        """
        if not self.client:
            return "System Error: AI is offline due to missing API key."

        # Inject real-time market data so the bot knows what's happening *right now*
        context_str = f"\n[Current Market Context]: {market_context}" if market_context else "\n[Current Market Context]: None provided."
        
        full_prompt = f"{self.system_prompt}{context_str}\n\nUser Question: {user_query}"

        try:
            # Run the sync SDK call in an async thread to prevent blocking FastAPI WebSockets
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_id,
                contents=full_prompt
            )
            return response.text
            
        except Exception as e:
            logger.error(f"ChatBot Execution Error: {str(e)}")
            return "I am currently experiencing technical difficulties connecting to the market oracle."

    async def analyze_opportunity(self, binance_price: float, bybit_price: float, spread: float) -> dict:
        """
        Wrapper for the AI Agent's decision engine.
        FIXED: Renamed from analyze_trade() to match the underlying AIAgent API.
        """
        return await self.agent.analyze_opportunity(binance_price, bybit_price, spread)

# --- BACKWARD COMPATIBLE INITIALIZATION ---
# This instance will be imported by modules that need a ready-to-use analyst
analyst = ChatBot(api_key=os.getenv("GEMINI_API_KEY"))