import threading
import uvicorn
import time
import sys
from api import app  
from core.server import run_arbitrage_bot

def start_api():
    print("📡 Initializing API Gateway...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

if __name__ == "__main__":
    print("\n" + "="*40)
    print("🚀 ARBPRO CORE SYSTEM STARTING")
    print("="*40)
    
    # 1. Start the API Server in a background thread
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()
    
    # Give the API a second to bind to the port
    time.sleep(1.5)
    print("✅ LOCAL VAULT ONLINE (Port 8080)")

    # 2. The Arbitrage Engine is now hosted within the API WebSocket
    print("🤖 BACKEND & ARBITRAGE ENGINE RUNNING ON PORT 8000...")
    try:
        # Keep the main thread alive so the daemon API thread can run
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 System shutdown requested by Operator.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ CRITICAL ENGINE ERROR: {e}")