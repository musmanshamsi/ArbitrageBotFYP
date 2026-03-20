import os
import json
from google import genai
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class AIAgent:
    def __init__(self):
        # 1. SETUP PRIMARY AI (Google Gemini - New SDK)
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.gemini_client = None
        if self.gemini_key:
            # New 2026 Syntax for Gemini
            self.gemini_client = genai.Client(api_key=self.gemini_key)
        else:
            print("⚠️ Warning: GEMINI_API_KEY not found.")

        # 2. SETUP FALLBACK AI (Groq / LLaMA 3.1)
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_client = Groq(api_key=self.groq_api_key) if self.groq_api_key else None

    def analyze_opportunity(self, binance_price, bybit_price, spread):
        """Analyzes the spread using Gemini, with an automatic fallback to Groq."""
        
        prompt = f"""
        Arbitrage Opportunity Detected!
        Binance Price: ${binance_price}
        Bybit Price: ${bybit_price}
        Spread: {spread}%

        You are an expert crypto trading AI. Analyze this spread. Is it safe to trade?
        Respond ONLY in valid JSON format exactly like this, with no extra text:
        {{"decision": "EXECUTE" or "REJECT", "reason": "Short explanation under 10 words", "confidence": 0-100}}
        """

        # --- ATTEMPT 1: PRIMARY AI (GEMINI) ---
        if self.gemini_client:
            try:
                # Upgraded to the newest Flash model
                response = self.gemini_client.models.generate_content(
                    model='gemini-2.5-flash', 
                    contents=prompt
                )
                return self._parse_json(response.text)
            
            except Exception as e_gemini:
                print(f"\n⚠️ Gemini Failed: {e_gemini}")
                print("🔄 Switching to Fallback AI (Groq)...")
        else:
             print("\n⚠️ No Gemini Client configured. Switching to Fallback AI (Groq)...")

        # --- ATTEMPT 2: FALLBACK AI (GROQ) ---
        if self.groq_client:
            try:
                chat_completion = self.groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.1-8b-instant", 
                    response_format={"type": "json_object"} 
                )
                return json.loads(chat_completion.choices[0].message.content)
            except Exception as e_groq:
                print(f"❌ Fallback AI also failed: {e_groq}")
        else:
            print("❌ No GROQ_API_KEY found in .env. Cannot use fallback.")

        # --- ATTEMPT 3: FAIL-SAFE ABORT ---
        return {
            "decision": "REJECT", 
            "reason": "Both AI APIs unreachable. Safety abort.", 
            "confidence": 0
        }

    def _parse_json(self, text):
        """Helper function to clean up AI output and convert it to a Python dictionary."""
        try:
            clean_text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except json.JSONDecodeError:
            print(f"⚠️ Failed to parse AI response into JSON. Raw output: {text}")
            return {"decision": "REJECT", "reason": "AI returned invalid format", "confidence": 0}