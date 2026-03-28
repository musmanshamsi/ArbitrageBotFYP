import os
import asyncio
import torch
import numpy as np
from dotenv import load_dotenv
import ccxt.async_support as ccxt
from predictor import Predictor

load_dotenv()

async def verify_exchanges():
    print("\n--- [SEARCH] EXCHANGE CONNECTIVITY CHECK ---")
    
    # Check Binance
    binance = ccxt.binance({
        'apiKey': os.getenv("BINANCE_TESTNET_API_KEY"),
        'secret': os.getenv("BINANCE_TESTNET_SECRET"),
        'proxies': {}
    })
    binance.set_sandbox_mode(True)
    
    try:
        ticker = await asyncio.wait_for(binance.fetch_ticker('BTC/USDT'), timeout=5)
        print(f"[SUCCESS] Binance Ticker: {ticker['last']}")
        bal = await binance.fetch_balance()
        print(f"[SUCCESS] Binance Balance (USDT): {bal.get('USDT', {}).get('free', 0)}")
    except Exception as e:
        print(f"[ERROR] Binance Error: {e}")
    finally:
        await binance.close()

    # Check Bybit
    bybit_opts = {
        'apiKey': os.getenv("BYBIT_TESTNET_API_KEY"),
        'secret': os.getenv("BYBIT_TESTNET_SECRET"),
    }
    proxy = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
    if proxy:
        bybit_opts['proxies'] = {'http': proxy, 'https': proxy}
        print(f"[INFO] Using Proxy for Bybit: {proxy}")

    bybit = ccxt.bybit(bybit_opts)
    bybit.set_sandbox_mode(True)
    
    try:
        ticker = await asyncio.wait_for(bybit.fetch_ticker('BTC/USDT'), timeout=5)
        print(f"[SUCCESS] Bybit Ticker: {ticker['last']}")
        bal = await bybit.fetch_balance()
        print(f"[SUCCESS] Bybit Balance (USDT): {bal.get('USDT', {}).get('free', 0)}")
    except Exception as e:
        print(f"[ERROR] Bybit Error: {e}")
    finally:
        await bybit.close()

def verify_calculations():
    print("\n--- [CALC] CALCULATION LOGIC CHECK ---")
    binance_price = 65000.0
    bybit_price = 65650.0 # 1% spread
    
    spread = ((bybit_price - binance_price) / binance_price) * 100
    print(f"Spread Calculation: {spread}% (Expected: 1.0%)")
    
    FEE_RATE = 0.002
    SLIPPAGE_RATE = 0.0005
    total_costs = (FEE_RATE + SLIPPAGE_RATE) * 100
    net_spread = spread - total_costs
    print(f"Net Spread: {net_spread}% (Expected: 0.75%)")
    
    trade_size = 0.01
    est_profit = (spread / 100) * binance_price * trade_size
    print(f"Est Profit: ${est_profit:.2f} (Expected: $6.50)")

def verify_ai():
    print("\n--- [AI] AI CORE CHECK ---")
    try:
        p = Predictor()
        p.load()
        dummy_input = [0.1, 0.12, 0.15, 0.11, 0.13, 0.14, 0.16, 0.12, 0.11, 0.15]
        pred = p.predict(dummy_input)
        print(f"[SUCCESS] AI Prediction Successful: {pred:.4f}%")
    except Exception as e:
        print(f"[ERROR] AI Error: {e}")

if __name__ == "__main__":
    verify_calculations()
    verify_ai()
    asyncio.run(verify_exchanges())
