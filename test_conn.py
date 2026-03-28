import requests
import os
from dotenv import load_dotenv

load_dotenv()

proxies = {
    'http': os.getenv('HTTP_PROXY'),
    'https': os.getenv('HTTPS_PROXY')
}

print(f"Testing connectivity with proxies: {proxies}")

try:
    r = requests.get("https://api.binance.com/api/v3/ping", timeout=5, proxies=proxies)
    print(f"Binance Ping (with proxy): {r.status_code}")
except Exception as e:
    print(f"Binance Ping (with proxy) failed: {e}")

try:
    r = requests.get("https://api.binance.com/api/v3/ping", timeout=5)
    print(f"Binance Ping (no proxy): {r.status_code}")
except Exception as e:
    print(f"Binance Ping (no proxy) failed: {e}")
