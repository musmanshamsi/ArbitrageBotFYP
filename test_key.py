import os
import asyncio
import ccxt.async_support as ccxt
from dotenv import load_dotenv

load_dotenv()

async def test_bybit():
    print("Testing Bybit Testnet Connection...")
    exchange = ccxt.bybit({
        'apiKey': os.getenv('BYBIT_TESTNET_API_KEY', ''),
        'secret': os.getenv('BYBIT_TESTNET_SECRET', ''),
        'enableRateLimit': True,
        'options': {'defaultType': 'spot', 'adjustForTimeDifference': True}
    })
    exchange.set_sandbox_mode(True)

    try:
        # This forces the bot to use the API keys to check your balance
        balance = await exchange.fetch_balance()
        print("✅ SUCCESS! Your Bybit keys are valid. Balance:", balance['USDT']['free'], "USDT")
    except Exception as e:
        print("❌ FAILED! Bybit rejected the keys. Reason:", e)
    finally:
        await exchange.close()

asyncio.run(test_bybit())