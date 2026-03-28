import os
import ccxt.async_support as ccxt
from dotenv import load_dotenv

class TradeExecutor:
    def __init__(self, binance_api, binance_secret, bybit_api="", bybit_secret="", testnet=True):
        # Initialize Binance
        self.binance = ccxt.binance({
            'apiKey': binance_api,
            'secret': binance_secret,
            'enableRateLimit': True,
            'proxies': {},  # Force no proxy for Binance to avoid local stalls
            'options': {
                'adjustForTimeDifference': True,
                'recvWindow': 10000
            }
        })
        
        # Initialize Bybit
        bybit_opts = {
            'apiKey': bybit_api,
            'secret': bybit_secret,
            'enableRateLimit': True,
        }
        
        # Conditionally add proxy configuration for Bybit if defined in env to bypass ISP block
        bybit_proxy = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
        if bybit_proxy:
            bybit_opts['proxies'] = {
                'http': bybit_proxy,
                'https': bybit_proxy,
            }

        self.bybit = ccxt.bybit(bybit_opts)
        
        # Turn on Testnet mode for BOTH
        if testnet:
            self.binance.set_sandbox_mode(True)
            self.bybit.set_sandbox_mode(True)

    async def close(self):
        await self.binance.close()
        await self.bybit.close()

    async def check_balances(self):
        print("🔄 Connecting to Testnets...")
        
        # Check Binance
        try:
            bin_balance = await self.binance.fetch_balance()
            print("\n🟡 --- BINANCE TESTNET BALANCE ---")
            print(f"USDT: {bin_balance.get('USDT', {}).get('free', 0)}")
            print(f"BTC: {bin_balance.get('BTC', {}).get('free', 0)}")
        except Exception as e:
            print(f"❌ Binance Connection Error: {str(e)}")

        # Check Bybit
        try:
            byb_balance = await self.bybit.fetch_balance()
            print("\n⚫ --- BYBIT TESTNET BALANCE ---")
            print(f"USDT: {byb_balance.get('USDT', {}).get('free', 0)}")
            print(f"BTC: {byb_balance.get('BTC', {}).get('free', 0)}")
            print("----------------------------------\n")
        except Exception as e:
            print(f"❌ Bybit Connection Error: {str(e)}")

    async def execute_test_trade(self, symbol='BTC/USDT', amount=0.01):
        """Places a Market Buy Order on Binance"""
        print(f"🚀 Initiating Market Buy: {amount} {symbol} on Binance...")
        try:
            order = await self.binance.create_market_buy_order(symbol, amount)
            print("✅ SUCCESS! Trade Executed.")
            print(f"📋 Order ID: {order['id']}")
            print(f"💵 Average Price: {order.get('average', order.get('price', 'N/A'))}")
            print(f"💰 Total Cost: {order.get('cost', 'N/A')} USDT\n")
            return order
        except Exception as e:
            print(f"❌ Trade Failed: {str(e)}")

    async def execute_arbitrage(self, symbol='BTC/USDT', amount=0.01):
        print("\n⚡ --- INITIATING ARBITRAGE EXECUTION --- ⚡")
        
        # 1. Real Trade on Binance (e.g., Buying Low)
        print("🟢 Leg 1: Executing Real BUY on Binance...")
        binance_order = await self.execute_test_trade(symbol, amount)
        
        if not binance_order:
            print("❌ Binance trade failed. Aborting arbitrage.")
            return
            
        # 2. Real Trade on Bybit (e.g., Selling High) - Now utilizing the proxy
        print("🔴 Leg 2: Attempting SELL on Bybit...")
        try:
            # Replaced fetch_balance with the real sell execution
            bybit_order = await self.bybit.create_market_sell_order(symbol, amount)
            print("✅ SUCCESS! Sold Phase 2 on Bybit.")
            print(f"📋 Order ID: {bybit_order['id']}")
            print(f"💵 Average Price: {bybit_order.get('average', bybit_order.get('price', 'N/A'))}")
        except Exception as e:
            print(f"❌ Bybit Network/Execution Failed: {str(e)}")
            print("⚠️ NOTE: Arb is broken since Leg 1 executed but Leg 2 failed.")
            return
            
        print("\n🎉 ARBITRAGE CYCLE COMPLETE! 🎉\n")