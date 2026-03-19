from llm.ai_agent import AIAgent

class ChatBot:
    def __init__(self, api_key):
        # Create an instance of the agent
        self.agent = AIAgent(api_key)

    def get_response(self, question):
        # Logic to pass dashboard queries to the agent
        return self.agent.analyze_trade(question)

# --- CONFIGURATION ---
# Replace with your actual OpenAI API Key
MY_API_KEY = "sk-proj-YOUR_REAL_KEY_HERE" 

# Create the instance that server.py will import
analyst = ChatBot(api_key=MY_API_KEY)