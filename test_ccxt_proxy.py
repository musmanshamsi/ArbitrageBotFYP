import ccxt.async_support as ccxt
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_binance_no_proxy():
    # Force use of environment proxy if it's not already used
    # But here we want to TEST if we can EXPLICITLY disable it
    
    config = {
        'apiKey': os.getenv("BINANCE_TESTNET_API_KEY"),
        'secret': os.getenv("BINANCE_TESTNET_SECRET"),
    }
    
    # In CCXT, providing an empty proxies dict should override environment variables
    config['proxies'] = {} 
    
    exchange = ccxt.binance(config)
    exchange.set_sandbox_mode(True)
    
    print("Testing Binance ticker fetch with explicit empty proxies...")
    try:
        ticker = await asyncio.wait_for(exchange.fetch_ticker('BTC/USDT'), timeout=5)
        print(f"Success! Price: {ticker['last']}")
    except Exception as e:
        print(f"Failed: {type(e).__name__}: {e}")
    finally:
        await exchange.close()

if __name__ == "__main__":
    asyncio.run(test_binance_no_proxy())
