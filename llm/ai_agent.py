import os
import json
import asyncio

# Try to import optional LLM libraries
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None
    print("WARNING: google-generativeai not installed. Gemini features disabled.")
    print("Install with: py -3.10 -m pip install google-generativeai")

try:
    from groq import AsyncGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    AsyncGroq = None
    print("WARNING: groq not installed. Groq features disabled.")
    print("Install with: py -3.10 -m pip install groq")

from dotenv import load_dotenv

load_dotenv()

class AIAgent:
    def __init__(self, gemini_key=None, groq_key=None, api_key=None):
        # Allow `api_key` as a kwarg since chatbot.py seems to be passing it that way
        self.gemini_key = gemini_key or api_key or os.getenv("GEMINI_API_KEY")
        self.gemini_client = None
        if GENAI_AVAILABLE and self.gemini_key:
            try:
                # Try new API first (v0.4+)
                if hasattr(genai, 'Client'):
                    self.gemini_client = genai.Client(api_key=self.gemini_key)
                else:
                    # Use new API (genai.configure + GenerativeModel)
                    genai.configure(api_key=self.gemini_key)
                    self.gemini_client = genai.GenerativeModel('gemini-pro')
            except Exception as e:
                print(f"WARNING: Failed to initialize Gemini client: {e}")
                self.gemini_client = None
        if not self.gemini_client and GENAI_AVAILABLE:
            print("WARNING: GEMINI_API_KEY not found or client initialization failed.")

        self.groq_api_key = groq_key or os.getenv("GROQ_API_KEY")
        self.groq_client = None
        if GROQ_AVAILABLE and self.groq_api_key:
            self.groq_client = AsyncGroq(api_key=self.groq_api_key)
        if not self.groq_client and GROQ_AVAILABLE:
            print("⚠️ Warning: GROQ_API_KEY not found.")

    # ==========================================
    # v6.0 LEGACY STRATEGY ENGINE 
    # ==========================================

    async def analyze_opportunity(self, binance_price, bybit_price, spread):
        """Legacy v6.0 analysis method. Preserved for backward compatibility."""
        prompt = f"""
        Arbitrage Opportunity Detected!
        Binance Price: ${binance_price}
        Bybit Price: ${bybit_price}
        Spread: {spread}%

        Analyze this spread. Is it safe to trade?
        Respond ONLY in valid JSON format:
        {{"decision": "EXECUTE" or "REJECT", "reason": "Short explanation", "confidence": 0-100}}
        """

        # Attempt Gemini
        gemini_result = await self._gemini_analyze(prompt)
        if gemini_result.get("decision") != "ERROR":
            # Map "reasoning" back to "reason" for legacy frontend
            if "reasoning" in gemini_result and "reason" not in gemini_result:
                gemini_result["reason"] = gemini_result.pop("reasoning")
            return gemini_result

        print("🔄 Switching to Fallback AI (Groq)...")
        
        # Attempt Groq
        groq_result = await self._groq_analyze(prompt)
        if groq_result.get("decision") != "ERROR":
            if "reasoning" in groq_result and "reason" not in groq_result:
                groq_result["reason"] = groq_result.pop("reasoning")
            return groq_result

        # Fail-safe
        return {
            "decision": "REJECT", 
            "reason": "Both AI APIs unreachable. Safety abort.", 
            "confidence": 0
        }

    # ==========================================
    # v7.0 ENHANCED STRATEGY ENGINE
    # ==========================================
    
    async def analyze_opportunity_v2(self, spread_data: dict, market_context: dict):
        """v7.0: Analyzes full market context using a concurrent Dual-LLM Ensemble approach."""
        
        binance_price = spread_data.get('binance_price', 0)
        bybit_price = spread_data.get('bybit_price', 0)
        spread = spread_data.get('spread', 0)

        ohlc_history = market_context.get('ohlc_history', "N/A")
        volatility = market_context.get('volatility', 5)
        regime = market_context.get('regime', "UNKNOWN")
        recent_profit = market_context.get('recent_profit', 0)
        total_risk = market_context.get('total_risk', 0)
        kelly_size = market_context.get('kelly_size', 0.01)

        prompt = f"""
        ARBITRAGE DECISION FRAMEWORK v7.0
        ═════════════════════════════════════════════════════════

        [MARKET CONDITIONS]
        • Binance: ${binance_price}
        • Bybit: ${bybit_price}
        • Spread: {spread}%
        • Volatility (0-10): {volatility}
        • Market Regime: {regime}
        • Recent Performance: +${recent_profit}

        [TECHNICAL ANALYSIS]
        • OHLC Summary: {ohlc_history}

        [RISK ASSESSMENT]
        • Current Cumulative Risk: {total_risk}%
        • Max Allowed Risk: 2%
        • Recommended Position Size (Kelly): {kelly_size} BTC

        [DECISION FRAMEWORK]
        Respond ONLY in valid JSON format matching this exact schema:
        {{
            "decision": "EXECUTE" | "EXECUTE_REDUCED" | "WAIT" | "REJECT",
            "confidence": 0-100,
            "position_size": {kelly_size},
            "reasoning": "2-3 sentence explanation",
            "risk_level": "LOW" | "MEDIUM" | "HIGH",
            "time_window": 30-300,
            "alternative_strategy": "If not this, consider X"
        }}
        """

        gemini_task = asyncio.create_task(self._gemini_analyze(prompt))
        groq_task = asyncio.create_task(self._groq_analyze(prompt))

        gemini_result, groq_result = await asyncio.gather(gemini_task, groq_task)

        return self._ensemble_decisions(gemini_result, groq_result)

    # ==========================================
    # INTERNAL HELPERS
    # ==========================================

    async def _gemini_analyze(self, prompt: str) -> dict:
        if not self.gemini_client:
            return {"decision": "ERROR", "confidence": 0, "reasoning": "Gemini not configured"}
        try:
            # Handle both old and new API formats
            if hasattr(self.gemini_client, 'models'):
                # Old API (genai.Client)
                response = await asyncio.to_thread(
                    self.gemini_client.models.generate_content,
                    model='gemini-2.0-flash',
                    contents=prompt
                )
            else:
                # New API (genai.GenerativeModel)
                response = await asyncio.to_thread(
                    self.gemini_client.generate_content,
                    prompt
                )
            return self._parse_json(response.text)
        except Exception as e:
            print(f"WARNING: Primary AI (Gemini) Failed: {e}")
            return {"decision": "ERROR", "confidence": 0, "reasoning": str(e)}

    async def _groq_analyze(self, prompt: str) -> dict:
        if not self.groq_client:
            return {"decision": "ERROR", "confidence": 0, "reasoning": "Groq not configured"}
        try:
            chat_completion = await self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                response_format={"type": "json_object"}
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            print(f"⚠️ Fallback AI (Groq) Failed: {e}")
            return {"decision": "ERROR", "confidence": 0, "reasoning": str(e)}

    def _ensemble_decisions(self, gemini_res: dict, groq_res: dict) -> dict:
        if gemini_res.get("decision") == "ERROR" and groq_res.get("decision") == "ERROR":
            return self._failsafe_abort("Both AI engines failed. System offline.")
            
        if gemini_res.get("decision") == "ERROR":
            return groq_res
        if groq_res.get("decision") == "ERROR":
            return gemini_res

        gemini_decision = gemini_res.get("decision", "REJECT")
        groq_decision = groq_res.get("decision", "REJECT")
        gemini_conf = gemini_res.get("confidence", 0)
        groq_conf = groq_res.get("confidence", 0)

        weighted_conf = (gemini_conf * 0.7) + (groq_conf * 0.3)

        if "REJECT" in [gemini_decision, groq_decision]:
            final_decision = "REJECT"
            reasoning = f"VETO TRIGGERED: Gemini voted {gemini_decision}, Groq voted {groq_decision}. Rejecting for safety."
            position_size = 0.0
        elif gemini_decision != groq_decision:
            final_decision = "EXECUTE_REDUCED"
            reasoning = "Models disagreed on execution strength. Downgrading position size to mitigate risk."
            g_size = float(gemini_res.get("position_size", 0) or 0)
            gr_size = float(groq_res.get("position_size", 0) or 0)
            position_size = min(g_size, gr_size)
        else:
            final_decision = gemini_decision
            reasoning = f"Consensus Achieved: {gemini_res.get('reasoning', 'Trade validated.')}"
            position_size = float(gemini_res.get("position_size", 0) or 0)

        return {
            "decision": final_decision,
            "confidence": round(weighted_conf, 2),
            "position_size": position_size,
            "reasoning": reasoning,
            "risk_level": gemini_res.get("risk_level", "HIGH"),
            "time_window": gemini_res.get("time_window", 60),
            "alternative_strategy": gemini_res.get("alternative_strategy", "Wait for next cycle.")
        }

    def _failsafe_abort(self, reason: str) -> dict:
        return {
            "decision": "REJECT",
            "confidence": 0,
            "position_size": 0.0,
            "reasoning": reason,
            "risk_level": "HIGH",
            "time_window": 0,
            "alternative_strategy": "Halt trading immediately."
        }

    def _parse_json(self, text: str) -> dict:
        try:
            clean_text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except json.JSONDecodeError:
            print(f"⚠️ Failed to parse AI response. Raw output: {text}")
            return self._failsafe_abort("AI returned malformed JSON structure.")