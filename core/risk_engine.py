class RiskEngine:

    def __init__(self, max_loss_percent=2):
        self.max_loss_percent = max_loss_percent

    def check_risk(self, entry_price, current_price):
        loss = ((entry_price - current_price) / entry_price) * 100
        if loss >= self.max_loss_percent:
            return True
        return False