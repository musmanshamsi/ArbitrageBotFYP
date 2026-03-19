class ArbitrageEngine:

    @staticmethod
    def calculate_spread(price_buy, price_sell):
        return ((price_sell - price_buy) / price_buy) * 100

    def check_opportunity(self, buy_price, sell_price, threshold=0.3):
        spread = self.calculate_spread(buy_price, sell_price)
        if spread > threshold:
            return True, spread
        return False, spread