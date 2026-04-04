import os
import json
import re
import logging
from google import genai
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Setup basic logging for this module
logger = logging.getLogger(__name__)

class AIAgent:
    def __init__(self, api_key: str, groq_api_key: str = None):
        """
        Initializes the AI Agent with the modern google-genai SDK.
        """
        if not api_key:
            logger.error("CRITICAL: Gemini API key is missing! AI features will fail.")
            
        # v1.0+ Syntax: Instantiate the Client directly
        self.client = genai.Client(api_key=api_key)
        self.model_id = 'gemini-2.0-flash'
        
        # Store Groq key for Tier 1 fallback (if used later)
        self.groq_api_key = groq_api_key

    def _clean_and_parse_json(self, raw_text: str) -> dict:
        """
        Strips markdown wrappers and enforces a strict fallback schema.
        """
        fallback_schema = {
            "decision": "WAIT",
            "confidence": 0,
            "position_size": 0.0,
            "reasoning": "Failsafe triggered: LLM output was unparsable or API failed."
        }

        if not raw_text:
            return fallback_schema

        try:
            # Regex to aggressively strip ```json and ``` tags
            cleaned_text = re.sub(r'```json\s*(.*?)\s*```', r'\1', raw_text, flags=re.DOTALL | re.IGNORECASE).strip()
            
            # If no 'json' tag was found but backticks remain, simple strip
            if "```" in cleaned_text:
                cleaned_text = cleaned_text.replace("```", "").strip()
            
            parsed_data = json.loads(cleaned_text)
            
            # Schema Validation: Ensure required keys exist
            for key in ["decision", "confidence", "reasoning"]:
                if key not in parsed_data:
                    logger.warning(f"Missing key '{key}' in LLM response. Using fallback.")
                    return fallback_schema
                    
            return parsed_data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON Parsing Error: {str(e)}. Raw text: {raw_text}")
            return fallback_schema
        except Exception as e:
            logger.error(f"Unexpected error in JSON parser: {str(e)}")
            return fallback_schema

    async def analyze_opportunity(self, binance_price: float, bybit_price: float, spread: float) -> dict:
        """Analyzes the spread using Gemini, with an automatic fallback to Groq."""
        
        prompt = f"""
        Arbitrage Opportunity Detected!
        Binance Price: ${binance_price}
        Bybit Price: ${bybit_price}
        Spread: {spread}%

        Analyze this spread. Is it safe to trade? 
        Consider fee/slippage overhead (~0.25%).
        
        Respond ONLY in valid JSON format:
        {{
            "decision": "EXECUTE" or "REJECT", 
            "reasoning": "Short explanation", 
            "confidence": 0-100,
            "position_size": 0.0
        }}
        """

        # --- ATTEMPT 1: PRIMARY AI (GEMINI) ---
        if self.client:
            try:
                # v1.0+ Syntax: generate_content is called on client.models
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=prompt
                )
                return self._clean_and_parse_json(response.text)
            
            except Exception as e_gemini:
                logger.error(f"❌ Gemini API Error: {e_gemini}")
                logger.info("🔄 Switching to Fallback AI (Groq)...")
        else:
            logger.warning("No Gemini Client configured. Switching to Fallback AI (Groq)...")

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
                logger.error(f"❌ Fallback AI Error: {e_groq}")
        else:
            logger.warning("No Groq client configured. Cannot use fallback.")

        # --- ATTEMPT 3: FAIL-SAFE ABORT ---
        return {
            "decision": "REJECT", 
            "reason": "All AI models unreachable. Safety abort.", 
            "confidence": 0
        }

    async def chat(self, question: str, system_prompt: str = "You are a helpful assistant.") -> str:
        """General chat interface for the dashboard assistant."""
        if not self.client:
            return "AI Agent is not configured. Please check your API keys."

        try:
            # v1.0+ Syntax for Chat
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[
                    {"role": "user", "parts": [{"text": f"System Instruction: {system_prompt}\n\nUser Question: {question}"}]}
                ]
            )
            return response.text
        except Exception as e:
            logger.error(f"Chat Error: {e}")
            return "I'm having trouble connecting to my brain right now. Please try again later."
