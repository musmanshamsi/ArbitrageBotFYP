from ui.ui_app import TradingUI
from core.server import run_arbitrage_bot

if __name__ == "__main__":
    # We pass the function 'run_arbitrage_bot' as an argument.
    # The UI will start this function in a background thread for you.
    app = TradingUI(run_arbitrage_bot)
    app.run()