import sqlite3
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RiskEngine:
    def __init__(self, db_path="arbpro.db", max_risk_per_trade=0.02, kelly_fraction=0.2, daily_loss_limit=50.0):
        """Tier 5 Safety Net: Kelly Criterion & Circuit Breakers"""
        self.db_path = db_path
        self.max_risk_per_trade = max_risk_per_trade
        self.kelly_fraction = kelly_fraction  # 0.2 means '20% of the optimal Kelly size'
        self.daily_loss_limit = daily_loss_limit

    def get_daily_pnl(self) -> float:
        """Calculates the cumulative profit/loss for the last 24 hours."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT sum(profit_usdt) as daily_pnl FROM trades WHERE timestamp >= datetime('now', '-1 day')"
                )
                result = cursor.fetchone()
                return result["daily_pnl"] if result and result["daily_pnl"] else 0.0
        except Exception as e:
            logger.error(f"Risk Engine DB Error: {e}")
            return 0.0

    def get_recent_trades(self, limit=100):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT profit_usdt FROM trades ORDER BY id DESC LIMIT ?", (limit,))
                return [row["profit_usdt"] for row in cursor.fetchall()]
        except Exception:
            return []

    def check_circuit_breaker(self) -> dict:
        """
        Veto System: Checks Daily Loss Limit and Consecutive Losses.
        Returns {"halted": bool, "reason": str}
        """
        # 1. Check Hard Daily Drawdown Limit
        daily_pnl = self.get_daily_pnl()
        if daily_pnl <= -abs(self.daily_loss_limit):
            logger.critical(f"CIRCUIT BREAKER: Daily loss limit (${self.daily_loss_limit}) exceeded.")
            return {"halted": True, "reason": "Daily Drawdown Exceeded"}

        # 2. Check Consecutive Loss Streak (Stop after 3 bad trades)
        trades = self.get_recent_trades(limit=3)
        if len(trades) == 3 and all(p < 0 for p in trades):
            logger.warning("CIRCUIT BREAKER: 3 consecutive losses detected.")
            return {"halted": True, "reason": "Consecutive Loss Streak"}

        return {"halted": False, "reason": "System Healthy"}

    def calculate_kelly_position(self, ai_confidence: int) -> float:
        """Calculates fractional Kelly based on historical win rate and current AI confidence."""
        trades = self.get_recent_trades(limit=100)
        
        # Base fallback if not enough history
        base_size = self.max_risk_per_trade * 0.10 
        
        if len(trades) < 10:
            return base_size
            
        wins = [t for t in trades if t > 0]
        losses = [t for t in trades if t <= 0]
        
        if not losses or not wins:
            return base_size
            
        historical_win_rate = len(wins) / len(trades)
        
        # Blend historical win rate with current AI confidence (e.g., 80% confidence = 0.8)
        blended_win_rate = (historical_win_rate * 0.5) + ((ai_confidence / 100.0) * 0.5)
        loss_rate = 1.0 - blended_win_rate
        
        avg_win = sum(wins) / len(wins)
        avg_loss = abs(sum(losses) / len(losses))
        
        if avg_loss == 0: return base_size
            
        # b = odds ratio
        b = avg_win / avg_loss
        
        # Standard Kelly Formula
        kelly_fraction = (b * blended_win_rate - loss_rate) / b
        
        # Apply fractional modifier (0.2) to prevent over-leveraging
        adjusted_kelly = max(0, kelly_fraction * self.kelly_fraction)
        
        # Never exceed absolute max risk (e.g., 2% of portfolio)
        return min(adjusted_kelly, self.max_risk_per_trade)

    def validate_and_size_trade(self, llm_decision: str, llm_confidence: int) -> dict:
        """The final gatekeeper called by api.py before execution."""
        breaker_status = self.check_circuit_breaker()
        if breaker_status["halted"]:
            return {"approved": False, "reason": breaker_status["reason"], "size": 0}
            
        if llm_decision in ["WAIT", "REJECT"]:
            return {"approved": False, "reason": "AI Veto", "size": 0}
            
        optimal_size = self.calculate_kelly_position(ai_confidence=llm_confidence)
        
        if optimal_size <= 0:
            return {"approved": False, "reason": "Kelly sizing <= 0 (EV is negative)", "size": 0}
            
        return {"approved": True, "reason": "Risk checks passed", "size": optimal_size}