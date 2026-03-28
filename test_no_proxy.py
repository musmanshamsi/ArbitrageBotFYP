import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Clear proxy from environment for this process
if "HTTP_PROXY" in os.environ: del os.environ["HTTP_PROXY"]
if "HTTPS_PROXY" in os.environ: del os.environ["HTTPS_PROXY"]

print("Testing connectivity without any proxies in environment.")

try:
    r = requests.get("https://api.binance.com/api/v3/ping", timeout=5)
    print(f"Binance Ping (no proxy): {r.status_code}")
except Exception as e:
    print(f"Binance Ping (no proxy) failed: {e}")

try:
    r = requests.get("https://api.bybit.com/v5/market/time", timeout=5)
    print(f"Bybit Ping (no proxy): {r.status_code}")
except Exception as e:
    print(f"Bybit Ping (no proxy) failed: {e}")
