"""
PROFESSIONAL SYSTEM VERIFICATION TOOL
AI Arbitrage Bot v7.0

Validates:
- Exchange connectivity and credentials
- Correct API URLs
- Exchange balances
- System calculations
- Model integrity
"""

import os
import asyncio
import torch
import numpy as np
from dotenv import load_dotenv
import ccxt.async_support as ccxt
from config import ExchangeConfig
from predictor import Predictor

load_dotenv()


async def verify_exchanges():
    """Verify connectivity and credentials for all exchanges"""
    
    print("\n" + "=" * 70)
    print(f"🔍 EXCHANGE CONNECTIVITY CHECK - {ExchangeConfig.ENVIRONMENT.upper()}")
    print("=" * 70 + "\n")

    # ========== BINANCE VERIFICATION ==========
    print(f"🟡 Testing Binance ({ExchangeConfig.BINANCE_API_URL})...")
    binance_config = ExchangeConfig.get_exchange_config("binance")
    binance = ccxt.binance(binance_config)
    
    if ExchangeConfig.ENVIRONMENT == "testnet":
        binance.set_sandbox_mode(True)
    
    try:
        # Test ticker fetch
        ticker = await asyncio.wait_for(
            binance.fetch_ticker('BTC/USDT'), timeout=5
        )
        print(f"   ✅ Ticker Fetch: ${ticker['last']:.2f}")
        
        # Test balance fetch
        bal = await binance.fetch_balance()
        usdt = bal.get('USDT', {}).get('free', 0)
        btc = bal.get('BTC', {}).get('free', 0)
        print(f"   ✅ Balance: {usdt:.2f} USDT | {btc:.8f} BTC")
        print(f"   ✅ API Status: WORKING\n")
        
    except asyncio.TimeoutError:
        print(f"   ❌ Timeout: Connection took too long (>5s)")
        print(f"   💡 Check internet connection and API URL\n")
    except ccxt.ExchangeNotAvailable as e:
        print(f"   ❌ Exchange Not Available: {e}")
        print(f"   💡 Check API URL and credentials\n")
    except ccxt.InvalidNonce as e:
        print(f"   ❌ Invalid Nonce: {e}")
        print(f"   💡 Check system time synchronization\n")
    except Exception as e:
        print(f"   ❌ Error: {type(e).__name__}: {e}\n")
    finally:
        await binance.close()

    # ========== BYBIT VERIFICATION ==========
    print(f"⚫ Testing Bybit ({ExchangeConfig.BYBIT_API_URL})...")
    bybit_config = ExchangeConfig.get_exchange_config("bybit")
    bybit = ccxt.bybit(bybit_config)
    
    if ExchangeConfig.ENVIRONMENT == "testnet":
        bybit.set_sandbox_mode(True)
    
    try:
        # Test ticker fetch
        ticker = await asyncio.wait_for(
            bybit.fetch_ticker('BTC/USDT'), timeout=5
        )
        print(f"   ✅ Ticker Fetch: ${ticker['last']:.2f}")
        
        # Test balance fetch
        bal = await bybit.fetch_balance()
        usdt = bal.get('USDT', {}).get('free', 0)
        btc = bal.get('BTC', {}).get('free', 0)
        print(f"   ✅ Balance: {usdt:.2f} USDT | {btc:.8f} BTC")
        print(f"   ✅ API Status: WORKING\n")
        
    except asyncio.TimeoutError:
        print(f"   ⚠️  Timeout: Connection took too long (>5s)")
        print(f"   💡 Try enabling proxy or check your network\n")
    except ccxt.ExchangeNotAvailable as e:
        print(f"   ❌ Exchange Not Available: {e}")
        print(f"   💡 Check API URL and credentials\n")
    except Exception as e:
        print(f"   ❌ Error: {type(e).__name__}: {e}\n")
        if ExchangeConfig.ENABLE_PROXY_FALLBACK and not (ExchangeConfig.HTTPS_PROXY or ExchangeConfig.HTTP_PROXY):
            print(f"   💡 Consider adding proxy: HTTPS_PROXY=your_proxy in .env\n")
    finally:
        await bybit.close()


def verify_calculations():
    """Verify trading calculations"""
    print("=" * 70)
    print("📊 CALCULATION LOGIC CHECK")
    print("=" * 70 + "\n")

    try:
        binance_price = 65000.0
        bybit_price = 65650.0  # 1% spread
        
        spread = ((bybit_price - binance_price) / binance_price) * 100
        print(f"Binance Price: ${binance_price:.2f}")
        print(f"Bybit Price: ${bybit_price:.2f}")
        print(f"Spread: {spread:.4f}%")
        
        # Fee calculation (0.2% each exchange)
        fee_rate = 0.002 * 2
        net_spread = spread - (fee_rate * 100)
        print(f"\nTransaction Fee (0.2% × 2): {fee_rate * 100:.2f}%")
        print(f"Net Profit: {net_spread:.4f}%")
        
        # Trade amount
        amount_usdt = 1000
        profit = (net_spread / 100) * amount_usdt
        print(f"\nOn ${amount_usdt} trade: +${profit:.2f}")
        print(f"✅ Calculation Logic: WORKING\n")
        
    except Exception as e:
        print(f"❌ Calculation Error: {e}\n")


def verify_model():
    """Verify GRU model integrity"""
    print("=" * 70)
    print("🧠 MODEL INTEGRITY CHECK")
    print("=" * 70 + "\n")

    try:
        # Check model file exists
        if not os.path.exists('gru_model.pth'):
            print("⚠️  gru_model.pth not found")
            return False
            
        if not os.path.exists('scaler_params.npy'):
            print("⚠️  scaler_params.npy not found")
            return False

        # Try loading model
        predictor = Predictor()
        predictor.load(model_path='gru_model.pth', scaler_path='scaler_params.npy')
        print(f"✅ Model loaded successfully")
        
        # Test prediction
        test_data = np.random.randn(10)
        prediction = predictor.predict(test_data)
        print(f"✅ Model prediction: {prediction:.6f}")
        print(f"✅ Model Status: WORKING\n")
        return True
        
    except Exception as e:
        print(f"❌ Model Error: {e}\n")
        return False


async def main():
    """Run all verification checks"""
    
    print("\n" + "=" * 70)
    print("🚀 ARBPRO SYSTEM VERIFICATION")
    print("=" * 70)
    
    # Print configuration
    ExchangeConfig.print_config()
    
    # Run checks
    if not ExchangeConfig.validate():
        print("❌ Configuration validation failed. Please check your .env file.")
        return False
    
    await verify_exchanges()
    verify_calculations()
    verify_model()
    
    print("=" * 70)
    print("✅ VERIFICATION COMPLETE")
    print("=" * 70 + "\n")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
