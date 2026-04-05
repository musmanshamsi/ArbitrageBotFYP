import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def save_trade(route, profit, symbol="BTC/USDT"):
    """Standalone helper to save a trade from any module."""
    try:
        db = DatabaseCore(db_path="arbitrage.db")
        db.save_trade_record(route, profit, symbol)
    except Exception as e:
        logger.error(f"Global save_trade failed: {e}")

class DatabaseCore:
    def __init__(self, db_path="arbitrage.db"):
        """Initializes SQLite with enterprise PRAGMA optimizations."""
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Creates tables and performs migrations if old schema exists."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.execute("PRAGMA synchronous=NORMAL;")
                
                cursor = conn.cursor()
                
                # 1. TRADES TABLE MIGRATION/INIT
                cursor.execute("PRAGMA table_info(trades)")
                cols = [c[1] for c in cursor.fetchall()]
                
                if not cols:
                    conn.execute('''
                        CREATE TABLE trades (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                            symbol TEXT DEFAULT 'BTC/USDT',
                            route TEXT,
                            profit REAL
                        )
                    ''')
                else:
                    # Migrate 'time' -> 'timestamp' if old schema exists
                    if 'time' in cols and 'timestamp' not in cols:
                        conn.execute("ALTER TABLE trades RENAME COLUMN time TO timestamp")
                    # Ensure symbol exists
                    if 'symbol' not in cols:
                        conn.execute("ALTER TABLE trades ADD COLUMN symbol TEXT DEFAULT 'BTC/USDT'")
                    # Ensure route exists
                    if 'route' not in cols:
                        conn.execute("ALTER TABLE trades ADD COLUMN route TEXT")
                    # Rename profit_usdt -> profit if it exists
                    if 'profit_usdt' in cols and 'profit' not in cols:
                        conn.execute("ALTER TABLE trades RENAME COLUMN profit_usdt TO profit")

                # 2. LLM Decisions
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS llm_decisions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        binance_price REAL,
                        bybit_price REAL,
                        spread REAL,
                        decision TEXT,
                        confidence INTEGER,
                        position_size REAL,
                        reasoning TEXT
                    )
                ''')

                # 3. Market Analysis
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS market_analysis (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        market_regime TEXT,
                        volatility_score REAL,
                        sentiment REAL,
                        support_level REAL,
                        resistance_level REAL
                    )
                ''')
            logger.info(f"Database {self.db_path} schema verified.")
        except Exception as e:
            logger.error(f"Migration/Init Error: {e}")

    def save_trade_record(self, route, profit, symbol="BTC/USDT"):
        """Saves a successful arbitrage trade."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO trades (symbol, route, profit)
                    VALUES (?, ?, ?)
                ''', (symbol, route, profit))
        except Exception as e:
            logger.error(f"Failed to save trade: {e}")

    def log_llm_decision(self, binance_price, bybit_price, spread, llm_output):
        """Saves the AI's exact reasoning for every trade."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO llm_decisions 
                    (binance_price, bybit_price, spread, decision, confidence, position_size, reasoning)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    binance_price, bybit_price, spread,
                    llm_output.get("decision", "WAIT"),
                    llm_output.get("confidence", 0),
                    llm_output.get("position_size", 0.0),
                    llm_output.get("reasoning", "No reason provided")
                ))
        except Exception as e:
            logger.error(f"Failed to log LLM decision: {e}")

    def cache_market_analysis(self, analysis_data):
        """Saves market conditions for frontend display and caching."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO market_analysis 
                    (market_regime, volatility_score, sentiment, support_level, resistance_level)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    analysis_data.get("regime", "UNKNOWN"),
                    float(analysis_data.get("volatility", 5.0)),
                    float(analysis_data.get("sentiment", 0.0)),
                    float(analysis_data.get("support", 0.0)),
                    float(analysis_data.get("resistance", 0.0))
                ))
        except Exception as e:
            logger.error(f"Failed to cache market analysis: {e}")
