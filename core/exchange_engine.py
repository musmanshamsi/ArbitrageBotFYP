import ccxt

class ExchangeEngine:
    def __init__(self, exchange_name="binance"):
        exchange_class = getattr(ccxt, exchange_name)
        self.exchange = exchange_class({
            "enableRateLimit": True
        })

    def load_markets(self):
        return self.exchange.load_markets()

    def fetch_ticker(self, symbol):
        return self.exchange.fetch_ticker(symbol)

    def fetch_order_book(self, symbol):
        return self.exchange.fetch_order_book(symbol)

    def create_order(self, symbol, order_type, side, amount, price=None):
        return self.exchange.create_order(symbol, order_type, side, amount, price)