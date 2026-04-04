import asyncio
from llm.ai_agent import AIAgent
from llm.chatbot import ChatBot
import json

def test_json_parsing():
    print("Running JSON Parsing tests...")
    agent = AIAgent()
    
    # Test 1: Clean JSON
    text1 = '{"decision": "EXECUTE", "reason": "High spread", "confidence": 95}'
    res1 = agent._clean_and_parse_json(text1)
    assert res1["decision"] == "EXECUTE"
    
    # Test 2: Markdown JSON
    text2 = '```json\n{"decision": "REJECT", "reason": "Low volume", "confidence": 80}\n```'
    res2 = agent._clean_and_parse_json(text2)
    assert res2["decision"] == "REJECT"
    
    # Test 3: Malformed JSON
    text3 = 'The decision is to EXECUTE because reasons.'
    res3 = agent._clean_and_parse_json(text3)
    assert res3["decision"] == "REJECT"
    assert "invalid format" in res3["reason"]
    
    # Test 4: Empty response
    res4 = agent._clean_and_parse_json("")
    assert res4["decision"] == "REJECT"
    
    print("JSON Parsing tests passed!")

async def test_ai_flow():
    # Note: Requires valid API keys in .env
    agent = AIAgent()
    if not agent.client:
        print("⚠️ Skipping live AI tests (no GEMINI_API_KEY).")
        return

    print("\nRunning Live AI Flow tests...")
    print("Testing analyze_opportunity...")
    res = await agent.analyze_opportunity(65000.0, 65500.0, 0.77)
    print(f"Result: {res}")
    assert "decision" in res
    assert "reason" in res

    print("\nTesting ChatBot persona...")
    bot = ChatBot()
    # Ask a question that should trigger the Senior Analyst persona
    response = await bot.get_response("Who are you and what is your role here?")
    print(f"ChatBot Response: {response}")
    
    # Check if the response sounds like an analyst
    keywords = ["analyst", "arbitrage", "market", "trading", "ArbPro"]
    found_keywords = [k for k in keywords if k.lower() in response.lower()]
    print(f"Found Keywords: {found_keywords}")
    assert len(found_keywords) > 0, "Response does not match Analyst persona"

    print("Live AI Flow tests passed!")

if __name__ == "__main__":
    try:
        test_json_parsing()
        asyncio.run(test_ai_flow())
        print("\nALL LLM TESTS PASSED!")
    except Exception as e:
        print(f"\nTEST FAILURE: {e}")
        import traceback
        traceback.print_exc()

