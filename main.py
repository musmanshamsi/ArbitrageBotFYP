import threading
import uvicorn
import time
import sys
import socket
from api import app
from core.server import run_arbitrage_bot

api_start_failure = threading.Event()

def is_port_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        try:
            sock.connect((host, port))
            return False
        except (ConnectionRefusedError, OSError):
            return True


def start_api():
    try:
        print("📡 Initializing API Gateway...")
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")
    except OSError as e:
        print(f"❌ API Gateway failed to bind on 127.0.0.1:8000 - {e}")
        api_start_failure.set()
    except Exception as e:
        print(f"❌ API Gateway failed: {e}")
        api_start_failure.set()


if __name__ == "__main__":
    print("\n" + "="*40)
    print("🚀 ARBPRO CORE SYSTEM STARTING")
    print("="*40)

    if not is_port_available("127.0.0.1", 8000):
        print("❌ Port 8000 is already in use. Please stop the existing server or change the port before restarting.")
        sys.exit(1)

    # 1. Start the API Server in a background thread
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()

    # Give the API a second to bind to the port
    time.sleep(1.5)

    if api_start_failure.is_set():
        print("❌ Backend startup failed. Check the API port and restart the application.")
        sys.exit(1)

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