import os
import ccxt.async_support as ccxt
import aiohttp
import random
from dotenv import load_dotenv
from config import ExchangeConfig

load_dotenv()


class TradeExecutor:
    def __init__(self, testnet: bool = None):
        """
        Initialize Trade Executor with professional configuration
        
        Args:
            testnet (bool, optional): Override environment for testnet mode.
                                     If None, uses ENVIRONMENT from .env
        """
        # Determine testnet mode
        self._testnet = testnet if testnet is not None else ExchangeConfig.is_testnet()
        self.proxy_pool = []

        # Initialize Binance with professional config
        binance_config = ExchangeConfig.get_exchange_config("binance")
        self.binance = ccxt.binance(binance_config)

        # Initialize Bybit with professional config
        bybit_config = ExchangeConfig.get_exchange_config("bybit")
        self.bybit = ccxt.bybit(bybit_config)

        # Set sandbox mode based on mode
        if self._testnet:
            self.binance.set_sandbox_mode(True)
            self.bybit.set_sandbox_mode(True)
            print("🧪 TESTNET MODE - Using sandboxed APIs")
        else:
            print("🔴 PRODUCTION MODE - REAL MONEY TRADING ENABLED")

        # Print configuration for verification
        print(f"📍 Exchange URLs:")
        print(f"   Binance: {ExchangeConfig.BINANCE_API_URL}")
        print(f"   Bybit: {ExchangeConfig.BYBIT_API_URL}")
        print()

    async def close(self):
        await self.binance.close()
        await self.bybit.close()

    async def _refresh_proxy_pool(self):
        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.get('https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt')
                if resp.status == 200:
                    text = await resp.text()
                    self.proxy_pool = text.strip().split('\n')
        except Exception as e:
            print(f"⚠️ Proxy Scraper failed: {e}")

    async def rotate_bybit_proxy(self):
        if not self.proxy_pool:
             await self._refresh_proxy_pool()
        if self.proxy_pool:
             new_proxy = "http://" + random.choice(self.proxy_pool).strip()
             print(f"🔄 Rotating Bybit to secure proxy tunnel: {new_proxy}")
             self.bybit.proxies = {'http': new_proxy, 'https': new_proxy}
        else:
             self.bybit.proxies = {}

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

        # Check Bybit with Proxy Fallback Logic
        try:
            byb_balance = await self.bybit.fetch_balance()
            print("\n⚫ --- BYBIT TESTNET BALANCE ---")
            print(f"USDT: {byb_balance.get('USDT', {}).get('free', 0)}")
            print(f"BTC: {byb_balance.get('BTC', {}).get('free', 0)}")
            print("----------------------------------\n")
        except Exception as e:
            print(f"⚠️ Initial Bybit Connection Failed ({str(e)}). Switching to Direct ISP Routing...")
            self.bybit.proxies = {}  # Dynamically detach proxy configuration
            try:
                byb_balance = await self.bybit.fetch_balance()
                print("✅ Bybit Direct connection successful.")
                print("\n⚫ --- BYBIT TESTNET BALANCE ---")
                print(f"USDT: {byb_balance.get('USDT', {}).get('free', 0)}")
                print(f"BTC: {byb_balance.get('BTC', {}).get('free', 0)}")
                print("----------------------------------\n")
            except Exception as e2:
                print(f"❌ Bybit Direct Connection Error: {str(e2)}")

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
