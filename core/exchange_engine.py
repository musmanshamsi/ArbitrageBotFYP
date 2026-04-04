"""
PROFESSIONAL EXCHANGE ENGINE
AI Arbitrage Bot v7.0

Provides unified interface for all supported exchanges
Automatically applies correct configuration from config.py
"""

import ccxt
from config import ExchangeConfig
import asyncio


class ExchangeEngine:
    """Synchronous exchange interface"""

    def __init__(self, exchange_name: str = "binance"):
        """
        Initialize exchange engine with professional configuration
        
        Args:
            exchange_name: 'binance', 'bybit', 'kraken', or 'coinbase'
        
        Raises:
            ValueError: If exchange not supported
        """
        self.name = exchange_name.lower()
        self.config = ExchangeConfig.get_exchange_config(self.name)

        # Create exchange instance
        exchange_class = getattr(ccxt, self.name, None)
        if not exchange_class:
            raise ValueError(f"❌ Unsupported exchange: {self.name}")

        self.exchange = exchange_class(self.config)

        # Set sandbox mode if testnet
        if ExchangeConfig.is_testnet():
            self.exchange.set_sandbox_mode(True)

        print(f"✅ {self.name.upper()} Exchange Initialized")
        print(f"   URL: {ExchangeConfig.BINANCE_API_URL if self.name == 'binance' else ExchangeConfig.BYBIT_API_URL}")

    def load_markets(self):
        """Load available trading pairs from exchange"""
        try:
            markets = self.exchange.load_markets()
            print(f"📊 Loaded {len(markets)} markets from {self.name.upper()}")
            return markets
        except Exception as e:
            print(f"❌ Failed to load markets from {self.name}: {e}")
            raise

    def fetch_ticker(self, symbol: str):
        """
        Fetch current ticker with comprehensive error handling
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
        
        Returns:
            Ticker data dictionary
        
        Raises:
            Exception: If API call fails after retries
        """
        attempts = 0
        last_error = None

        while attempts < ExchangeConfig.API_RETRY_ATTEMPTS:
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                return ticker
            except (ConnectionError, TimeoutError) as e:
                last_error = e
                attempts += 1
                if attempts < ExchangeConfig.API_RETRY_ATTEMPTS:
                    wait_time = ExchangeConfig.API_RETRY_DELAY * (2 ** (attempts - 1))
                    print(
                        f"⚠️  {self.name.upper()} ticker timeout. Retrying in {wait_time}s..."
                    )
                    asyncio.run(asyncio.sleep(wait_time))
            except Exception as e:
                print(f"❌ {self.name.upper()} fetch_ticker error: {type(e).__name__}: {e}")
                raise

        raise Exception(
            f"❌ Failed to fetch {symbol} from {self.name} after {attempts} attempts: {last_error}"
        )

    def fetch_order_book(self, symbol: str, limit: int = None):
        """
        Fetch order book with error handling
        
        Args:
            symbol: Trading pair
            limit: Maximum number of bids/asks
        
        Returns:
            Order book data
        """
        try:
            return self.exchange.fetch_order_book(symbol, limit)
        except Exception as e:
            print(f"❌ {self.name.upper()} fetch_order_book error: {e}")
            raise

    def fetch_balance(self):
        """
        Fetch account balance with error handling
        
        Returns:
            Balance data dictionary
        """
        try:
            return self.exchange.fetch_balance()
        except Exception as e:
            print(f"❌ {self.name.upper()} fetch_balance error: {e}")
            raise

    def create_order(
        self,
        symbol: str,
        order_type: str,
        side: str,
        amount: float,
        price: float = None,
    ):
        """
        Create order with comprehensive error handling
        
        Args:
            symbol: Trading pair
            order_type: 'market' or 'limit'
            side: 'buy' or 'sell'
            amount: Amount to trade
            price: Price (required for limit orders)
        
        Returns:
            Order data
        """
        try:
            order = self.exchange.create_order(symbol, order_type, side, amount, price)
            print(f"✅ {self.name.upper()} Order Created")
            print(f"   ID: {order['id']}")
            print(f"   Amount: {order['amount']} {symbol.split('/')[0]}")
            return order
        except Exception as e:
            print(f"❌ {self.name.upper()} create_order error: {e}")
            raise

    def close(self):
        """Properly close exchange connection"""
        try:
            self.exchange.close()
            print(f"✅ {self.name.upper()} connection closed")
        except Exception as e:
            print(f"⚠️  Error closing {self.name} connection: {e}")