import asyncio
import ccxt.async_support as ccxt

async def test():
    print("Testing CCXT")
    b = ccxt.binance()
    y = ccxt.bybit()
    try:
        bin = await b.fetch_ticker('BTC/USDT')
        print(f"BINANCE REAL: {bin['last']}")
    except Exception as e:
        print(f"BINANCE ERROR: {e}")
        
    try:
        byb = await y.fetch_ticker('BTC/USDT')
        print(f"BYBIT REAL: {byb['last']}")
    except Exception as e:
        print(f"BYBIT ERROR: {e}")
        
    await b.close()
    await y.close()

asyncio.run(test())
