import tkinter as tk
from ui.theme import THEMES

class TradingUI:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Arbitrage Bot")
        self.set_theme("binance")
        self.build_ui()

    def set_theme(self, theme_name):
        self.theme = THEMES[theme_name]
        self.root.configure(bg=self.theme["bg"])

    def build_ui(self):
        frame = tk.Frame(self.root, bg=self.theme["panel"])
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        title = tk.Label(
            frame,
            text="AI Arbitrage Dashboard",
            bg=self.theme["panel"],
            fg=self.theme["fg"],
            font=("Arial", 18)
        )
        title.pack(pady=10)

        self.output = tk.Text(frame, height=15, bg="#111", fg="white")
        self.output.pack(fill="both", expand=True)

        theme_btn = tk.Button(
            frame,
            text="Switch Theme",
            command=self.switch_theme
        )
        theme_btn.pack(pady=10)

    def switch_theme(self):
        new_theme = "bybit" if self.theme == THEMES["binance"] else "binance"
        self.set_theme(new_theme)
        self.root.destroy()
        self.__init__()

    def run(self):
        self.root.mainloop()