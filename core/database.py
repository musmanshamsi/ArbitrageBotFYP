import sqlite3
import os
from datetime import datetime

# Centralized Database Configuration
DB_NAME = "arbitrage.db"

def init_db():
    """Initializes the trades table in the database."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT,
            route TEXT,
            profit REAL
        )
    ''')
    conn.commit()
    conn.close()

def save_trade(route, profit):
    """Saves a trade record to the database."""
    time_now = datetime.now().strftime("%H:%M:%S")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO trades (time, route, profit) VALUES (?, ?, ?)", 
              (time_now, route, profit))
    conn.commit()
    conn.close()
    return {"time": time_now, "route": route, "profit": f"+${profit:.2f}"}

def get_trade_history():
    """Retrieves all trade history from the database."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT time, route, profit FROM trades ORDER BY id DESC")
    rows = c.fetchall()
    
    history = [{"time": r[0], "route": r[1], "profit": f"+${r[2]:.2f}"} for r in rows]
    
    c.execute("SELECT SUM(profit) FROM trades")
    total = c.fetchone()[0]
    total_profit = total if total is not None else 0.00
    
    conn.close()
    return history, total_profit

# Initialization on import
init_db()
