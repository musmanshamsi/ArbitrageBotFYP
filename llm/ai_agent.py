from openai import OpenAI

class AIAgent:
    def __init__(self, api_key):
        # Initializing the modern OpenAI client
        self.client = OpenAI(api_key=api_key)

    def analyze_trade(self, context):
        prompt = f"""
        Analyze this live crypto arbitrage opportunity:
        {context}
        
        Instructions:
        1. Evaluate if the spread is worth the execution (consider 0.1% fees).
        2. Provide a 'DECISION' (EXECUTE or HOLD).
        3. Provide a brief 'REASONING' based on price and profitability.
        Keep the response concise for a terminal display.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini", # Using mini for faster/cheaper demo, or use "gpt-4"
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"AI Agent Error: {str(e)}"