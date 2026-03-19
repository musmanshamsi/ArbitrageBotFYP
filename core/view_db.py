import sqlite3

def view_trades():
    try:
        conn = sqlite3.connect('trades.db')
        cursor = conn.cursor()
        
        print("\n--- DATABASE: TRADES LOG ---")
        cursor.execute("SELECT * FROM trades ORDER BY id DESC")
        rows = cursor.fetchall()
        
        if not rows:
            print("No trades found yet. Start the bot and wait for an opportunity!")
        else:
            print(f"{'ID':<5} | {'TIME':<20} | {'ROUTE':<20} | {'PROFIT ($)':<10}")
            print("-" * 65)
            for row in rows:
                print(f"{row[0]:<5} | {row[1]:<20} | {row[2]:<20} | {row[3]:<10}")
        
        conn.close()
    except Exception as e:
        print(f"Error reading DB: {e}")

if __name__ == "__main__":
    view_trades()