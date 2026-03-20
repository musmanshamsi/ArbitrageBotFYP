import tkinter as tk
from tkinter import scrolledtext
import threading
import sys
import queue

class TradingUI:
    def __init__(self, bot_function):
        self.root = tk.Tk()
        self.root.title("AI Arbitrage Bot v2.0")
        self.root.geometry("800x600")
        
        # This queue will pass messages from the Bot to the UI
        self.msg_queue = queue.Queue()
        self.bot_function = bot_function
        
        self.theme = {
            "bg": "#121212",
            "panel": "#1e1e1e",
            "fg": "#00ff00",
            "accent": "#f3ba2f" # Binance Gold
        }
        
        self.build_ui()
        
        # Start the bot in a background thread
        self.bot_thread = threading.Thread(target=self.bot_function, daemon=True)
        self.bot_thread.start()
        
        # Start checking the queue for new messages
        self.update_logs()

    def build_ui(self):
        self.root.configure(bg=self.theme["bg"])
        
        # Header
        header = tk.Frame(self.root, bg=self.theme["panel"], height=60)
        header.pack(fill="x", padx=10, pady=5)
        
        tk.Label(header, text="📊 AI ARBITRAGE LIVE MONITOR", 
                 bg=self.theme["panel"], fg=self.theme["accent"], 
                 font=("Arial", 16, "bold")).pack(pady=10)

        # Log Output (The terminal inside the UI)
        self.log_widget = scrolledtext.ScrolledText(
            self.root, bg="#000", fg=self.theme["fg"], 
            font=("Consolas", 10), insertbackground="white"
        )
        self.log_widget.pack(fill="both", expand=True, padx=10, pady=10)

    def write_log(self, message):
        """Helper to safely add text to the UI from another thread"""
        self.msg_queue.put(message)

    def update_logs(self):
        """Check the queue and update the text box"""
        try:
            while True:
                msg = self.msg_queue.get_nowait()
                self.log_widget.insert(tk.END, msg + "\n")
                self.log_widget.see(tk.END) # Auto-scroll to bottom
        except queue.Empty:
            pass
        self.root.after(100, self.update_logs) # Check again in 100ms

    def run(self):
        self.root.mainloop()

# --- HOW TO CONNECT TO YOUR SERVER.PY ---
# In your server.py, you would do:
# ui = TradingUI(run_arbitrage_bot)
# ui.run()