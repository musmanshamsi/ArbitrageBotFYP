import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseCore:
    def __init__(self, db_path="arbpro.db"):
        """Initializes SQLite with enterprise PRAGMA optimizations."""
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Creates tables with WAL mode for high-concurrency async reads/writes."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Performance optimizations
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.execute("PRAGMA synchronous=NORMAL;")
                
                # 1. Existing Trades Table (Keeps your current data safe)
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS trades (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        symbol TEXT,
                        profit_usdt REAL,
                        spread REAL
                    )
                ''')

                # 2. NEW: LLM Decision Audit Trail
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

                # 3. NEW: Market Analysis Cache (To prevent API spam)
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
            logger.info("Database Schema verified and updated to v7.0.")
        except Exception as e:
            logger.error(f"Database Initialization Error: {e}")

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
