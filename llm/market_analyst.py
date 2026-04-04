import os
import json
import asyncio
from datetime import datetime, timedelta, timezone
import pandas as pd
import numpy as np

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None
    print("WARNING: google-generativeai not installed. MarketAnalyst features disabled.")
    print("Install with: py -3.10 -m pip install google-generativeai")

from dotenv import load_dotenv

load_dotenv()

class MarketAnalyst:
    def __init__(self, api_key=None):
        """Initializes the Market Analyst with Gemini 2.0 Flash."""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = None
        if GENAI_AVAILABLE and self.api_key:
            try:
                # Try new API first (v0.4+)
                if hasattr(genai, 'Client'):
                    self.client = genai.Client(api_key=self.api_key)
                else:
                    # Use new API (genai.configure + GenerativeModel)
                    genai.configure(api_key=self.api_key)
                    self.client = genai.GenerativeModel('gemini-pro')
            except Exception as e:
                print(f"WARNING: Failed to initialize Gemini client: {e}")
                self.client = None
        
        if not self.client and GENAI_AVAILABLE:
            print("Warning: GEMINI_API_KEY not found. MarketAnalyst will return default states.")

        # Cache configuration: Prevents API spam by storing the LLM analysis for 5 minutes
        self.cache = {}
        self.cache_ttl = timedelta(minutes=5)

    async def update_market_context(self, ohlc_data: list) -> dict:
        """
        The master function. Feeds OHLC data to the LLM to get a comprehensive 
        market overview, caching the result to save API tokens and reduce latency.
        
        Expected ohlc_data format: [{'time': int, 'open': float, 'high': float, 'low': float, 'close': float, 'volume': float}, ...]
        """
        # Strict SDS Compliance: Using timezone-aware datetime to prevent server-drift bugs
        now = datetime.now(timezone.utc)
        
        # 1. Check Cache Validity
        if "market_state" in self.cache:
            timestamp, cached_data = self.cache["market_state"]
            if now - timestamp < self.cache_ttl:
                return cached_data

        # 2. Validate Data
        if not ohlc_data or len(ohlc_data) < 10:
            print("⚠️ MarketAnalyst: Insufficient OHLC data provided. Returning default state.")
            return self._default_market_state()

        if not self.client:
            return self._default_market_state()

        # 3. Pre-process data with Pandas to save LLM context window limits
        df = pd.DataFrame(ohlc_data)
        
        # Calculate some basic metrics so the LLM doesn't have to do raw math
        current_price = df['close'].iloc[-1]
        highest_high = df['high'].max()
        lowest_low = df['low'].min()
        price_change_pct = ((current_price - df['close'].iloc[0]) / df['close'].iloc[0]) * 100
        
        # Sample the dataframe to a manageable string (e.g., last 20 candles)
        recent_candles = df[['open', 'high', 'low', 'close', 'volume']].tail(20).to_dict(orient='records')

        prompt = f"""
        MARKET ANALYSIS REQUEST
        ═════════════════════════════════════════════════════════
        You are an elite quantitative crypto analyst. Analyze the following BTC/USDT data.

        [PRE-CALCULATED METRICS]
        • Current Price: ${current_price:.2f}
        • Period High: ${highest_high:.2f}
        • Period Low: ${lowest_low:.2f}
        • Period Price Change: {price_change_pct:.2f}%

        [RECENT OHLCV CANDLES (Last 20 periods)]
        {json.dumps(recent_candles, indent=2)}

        [ANALYSIS REQUIREMENTS]
        Based on price action, identify the market regime, estimate volatility, score the sentiment, and pinpoint key support/resistance levels.

        Respond ONLY in valid JSON format matching this exact schema:
        {{
            "regime": "trending_up" | "trending_down" | "ranging" | "volatile_chop",
            "regime_confidence": 0-100,
            "volatility_score": 0-10,  // 0 is dead flat, 10 is extreme erratic swings
            "sentiment": -1.0 to 1.0,  // -1.0 is extreme bear, 1.0 is extreme bull
            "support_levels": [float, float], // Two closest support prices below current price
            "resistance_levels": [float, float], // Two closest resistance prices above current price
            "reasoning": "Short 2 sentence technical justification."
        }}
        """

        try:
            # 4. Call Gemini Asynchronously without blocking the main event loop
            # Handle both old and new API formats
            if hasattr(self.client, 'models'):
                # Old API (genai.Client)
                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model='gemini-2.0-flash',
                    contents=prompt
                )
            else:
                # New API (genai.GenerativeModel)
                response = await asyncio.to_thread(
                    self.client.generate_content,
                    prompt
                )
            
            # 5. Parse and Cache Result
            analysis = self._parse_json(response.text)
            self.cache["market_state"] = (now, analysis)
            print(f"Market Context Updated: {analysis['regime']} (Vol: {analysis['volatility_score']}/10)")
            return analysis

        except Exception as e:
            print(f"WARNING: Market Analyst AI Call Failed: {e}")
            return self._default_market_state()

    # ==========================================
    # MODULAR ACCESS METHODS (Reads from Cache)
    # ==========================================

    async def detect_market_regime(self, ohlc_data: list) -> dict:
        """Returns {"regime": str, "confidence": int}"""
        state = await self.update_market_context(ohlc_data)
        return {
            "regime": state.get("regime", "UNKNOWN"),
            "confidence": state.get("regime_confidence", 0)
        }

    async def analyze_volatility(self, ohlc_data: list) -> dict:
        """Returns {"volatility_score": int, "forecast_duration": int}"""
        state = await self.update_market_context(ohlc_data)
        score = state.get("volatility_score", 5)
        # Higher volatility requires shorter trade duration windows (e.g., 30 secs)
        duration = 30 if score > 7 else (60 if score > 4 else 120)
        return {
            "volatility_score": score,
            "forecast_duration": duration
        }

    async def generate_sentiment(self, ohlc_data: list) -> dict:
        """Returns {"sentiment": float, "reason": str}"""
        state = await self.update_market_context(ohlc_data)
        return {
            "sentiment": state.get("sentiment", 0.0),
            "reason": state.get("reasoning", "No analysis available.")
        }

    async def identify_support_resistance(self, ohlc_data: list) -> dict:
        """Returns {"support": list, "resistance": list}"""
        state = await self.update_market_context(ohlc_data)
        return {
            "support": state.get("support_levels", []),
            "resistance": state.get("resistance_levels", [])
        }

    # ==========================================
    # INTERNAL HELPERS
    # ==========================================

    def _default_market_state(self) -> dict:
        """Failsafe output if the LLM or API fails."""
        return {
            "regime": "UNKNOWN",
            "regime_confidence": 0,
            "volatility_score": 5,
            "sentiment": 0.0,
            "support_levels": [],
            "resistance_levels": [],
            "reasoning": "Fallback to default state due to API or parsing error."
        }

    def _parse_json(self, text: str) -> dict:
        """Safely extracts dictionary from LLM text output."""
        try:
            clean_text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except json.JSONDecodeError:
            print(f"⚠️ Market Analyst failed to parse AI response. Raw output: {text}")
            return self._default_market_state()