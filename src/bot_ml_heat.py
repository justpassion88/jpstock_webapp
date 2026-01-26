"""
ML-Based Trading BOT with Heat Index Integration
Sử dụng Machine Learning để phân bổ vốn dựa trên P/B và Nhiệt độ ngành
"""

import json
import os
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# Constants
INITIAL_CAPITAL = 1_000_000_000  # 1 tỷ VND
TRANSACTION_FEE = 0.0015  # 0.15% mua
TAX_SELL = 0.001  # 0.1% thuế bán


class TradingAction(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class Position:
    symbol: str
    quantity: int
    avg_price: float
    buy_date: str
    buy_pb: float
    buy_heat: float  # Heat index when bought
    
    @property
    def cost_basis(self):
        return self.quantity * self.avg_price


@dataclass
class Trade:
    date: str
    symbol: str
    action: TradingAction
    quantity: int
    price: float
    pb_at_trade: float
    heat_at_trade: float  # Heat index at trade
    reason: str
    pnl: float = 0
    pnl_percent: float = 0


@dataclass
class HeatAwareBOTConfig:
    """Configuration for Heat-Aware ML BOT"""
    name: str
    description: str
    
    # P/B Parameters
    pb_percentile_max: float = 40  # Max P/B percentile to buy
    exit_pb_percentile: float = 80  # Sell when P/B exceeds
    
    # Heat-based allocation multipliers
    heat_allocation_map: Dict = None  # Heat range -> allocation multiplier
    
    # Position sizing
    base_position_percent: float = 20  # Base allocation per position
    max_position_percent: float = 30  # Max allocation per position
    min_position_percent: float = 5   # Min allocation per position
    max_positions: int = 8
    
    # Risk management
    stop_loss_percent: float = 999  # 999 = no stoploss
    take_profit_percent: float = 80
    
    # Holding
    min_holding_quarters: int = 2
    
    def __post_init__(self):
        if self.heat_allocation_map is None:
            # Default heat allocation map
            # Heat Level -> (allocation_multiplier, cash_reserve_percent)
            self.heat_allocation_map = {
                "ICE_COLD": (1.5, 0),      # Heat < 20: Mua mạnh, không giữ cash
                "COLD": (1.3, 5),           # Heat 20-35: Mua nhiều
                "COOL": (1.1, 10),          # Heat 35-45: Mua bình thường+
                "NEUTRAL": (1.0, 15),       # Heat 45-55: Bình thường
                "WARM": (0.7, 25),          # Heat 55-70: Giảm vị thế
                "HOT": (0.4, 40),           # Heat 70-85: Giảm mạnh
                "OVERHEATED": (0.0, 60),    # Heat > 85: Không mua, chờ bán
            }


def get_heat_level(heat_index: float) -> str:
    """Convert heat index to level string"""
    if heat_index >= 85:
        return "OVERHEATED"
    elif heat_index >= 70:
        return "HOT"
    elif heat_index >= 55:
        return "WARM"
    elif heat_index >= 45:
        return "NEUTRAL"
    elif heat_index >= 35:
        return "COOL"
    elif heat_index >= 20:
        return "COLD"
    else:
        return "ICE_COLD"


def calculate_period_heat(bank_data: Dict, period: str) -> Dict:
    """Calculate heat index for a specific period"""
    pb_percentiles = []
    pb_values = []
    
    for symbol, data in bank_data.items():
        pb_hist = data.get("pb_history", [])
        pb_stats = data.get("pb_statistics", {})
        
        # Find P/B for this period
        period_pb = None
        for h in pb_hist:
            if h["period"] == period:
                period_pb = h.get("pb")
                break
        
        if period_pb is None:
            continue
        
        # Calculate percentile
        p25 = pb_stats.get("p25", period_pb)
        p50 = pb_stats.get("p50", period_pb)
        p75 = pb_stats.get("p75", period_pb)
        pb_min = pb_stats.get("min", period_pb)
        pb_max = pb_stats.get("max", period_pb)
        
        if pb_max > pb_min:
            percentile = (period_pb - pb_min) / (pb_max - pb_min) * 100
        else:
            percentile = 50
        
        percentile = max(0, min(100, percentile))
        pb_percentiles.append(percentile)
        pb_values.append(period_pb)
    
    if not pb_percentiles:
        return {"heat_index": 50, "level": "NEUTRAL"}
    
    avg_percentile = np.mean(pb_percentiles)
    
    # Adjust for extremes
    total = len(pb_percentiles)
    very_cheap = sum(1 for p in pb_percentiles if p < 20)
    very_expensive = sum(1 for p in pb_percentiles if p > 80)
    
    heat_index = avg_percentile
    if very_expensive / total > 0.5:
        heat_index = min(100, heat_index + 15)
    if very_cheap / total > 0.5:
        heat_index = max(0, heat_index - 15)
    
    return {
        "heat_index": round(heat_index, 1),
        "level": get_heat_level(heat_index),
        "avg_pb_percentile": round(avg_percentile, 1),
        "avg_pb": round(np.mean(pb_values), 2) if pb_values else 0
    }


class MLFeatureExtractor:
    """Extract ML features from market data"""
    
    def __init__(self, bank_data: Dict):
        self.bank_data = bank_data
        self.heat_history = self._build_heat_history()
    
    def _build_heat_history(self) -> Dict[str, Dict]:
        """Build heat history for all periods"""
        all_periods = set()
        for symbol, data in self.bank_data.items():
            for h in data.get("pb_history", []):
                all_periods.add(h["period"])
        
        heat_history = {}
        for period in sorted(all_periods):
            heat_history[period] = calculate_period_heat(self.bank_data, period)
        
        return heat_history
    
    def get_features(self, symbol: str, period: str) -> Dict:
        """Extract features for ML decision making"""
        data = self.bank_data.get(symbol, {})
        pb_hist = data.get("pb_history", [])
        pb_stats = data.get("pb_statistics", {})
        zone_stats = data.get("zone_statistics", {})
        
        # Current P/B
        current_pb = None
        current_price = None
        for h in pb_hist:
            if h["period"] == period:
                current_pb = h.get("pb")
                current_price = h.get("price", 0) * 1000  # Convert to VND
                break
        
        if current_pb is None:
            return None
        
        # P/B Percentile
        pb_min = pb_stats.get("min", current_pb)
        pb_max = pb_stats.get("max", current_pb)
        if pb_max > pb_min:
            pb_percentile = (current_pb - pb_min) / (pb_max - pb_min) * 100
        else:
            pb_percentile = 50
        
        # Heat at period
        heat_data = self.heat_history.get(period, {"heat_index": 50, "level": "NEUTRAL"})
        
        # Zone statistics for expected return
        zone = self._get_zone(pb_percentile)
        zone_data = zone_stats.get(zone, {})
        
        # Heat trend (compare with previous quarters)
        heat_trend = self._calculate_heat_trend(period)
        
        return {
            "symbol": symbol,
            "period": period,
            "price": current_price,
            "pb": current_pb,
            "pb_percentile": pb_percentile,
            "heat_index": heat_data["heat_index"],
            "heat_level": heat_data["level"],
            "heat_trend": heat_trend,
            "zone": zone,
            "zone_win_rate": zone_data.get("win_rate_1y", 50),
            "zone_expected_return": zone_data.get("return_1y_avg", 10),
            "zone_sample_count": zone_data.get("sample_count", 0),
        }
    
    def _get_zone(self, percentile: float) -> str:
        """Convert percentile to zone"""
        if percentile < 20:
            return "very_cheap"
        elif percentile < 40:
            return "cheap"
        elif percentile < 60:
            return "fair"
        elif percentile < 80:
            return "expensive"
        else:
            return "very_expensive"
    
    def _calculate_heat_trend(self, current_period: str) -> str:
        """Calculate heat trend based on last 4 quarters"""
        periods = sorted(self.heat_history.keys())
        try:
            idx = periods.index(current_period)
        except ValueError:
            return "STABLE"
        
        if idx < 2:
            return "STABLE"
        
        # Get last 4 heats
        recent_heats = [self.heat_history[periods[max(0, idx-i)]]["heat_index"] 
                       for i in range(min(4, idx+1))]
        
        if len(recent_heats) < 2:
            return "STABLE"
        
        # Calculate trend
        current = recent_heats[0]
        avg_past = np.mean(recent_heats[1:])
        
        diff = current - avg_past
        if diff > 10:
            return "HEATING_UP"
        elif diff < -10:
            return "COOLING_DOWN"
        else:
            return "STABLE"


class HeatAwareMLBot:
    """ML-based Trading BOT with Heat Index Integration"""
    
    def __init__(self, config: HeatAwareBOTConfig, bank_data: Dict):
        self.config = config
        self.bank_data = bank_data
        self.feature_extractor = MLFeatureExtractor(bank_data)
        
        # Portfolio state
        self.cash = INITIAL_CAPITAL
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.snapshots: List[Dict] = []
        
        # Performance tracking
        self.peak_value = INITIAL_CAPITAL
        self.max_drawdown = 0
        
        # Quality banks (Big 4 + mid-caps with good data)
        self.quality_banks = self._identify_quality_banks()
    
    def _identify_quality_banks(self) -> List[str]:
        """Identify quality banks based on data quality and market cap"""
        quality = []
        for symbol, data in self.bank_data.items():
            pb_hist = data.get("pb_history", [])
            if len(pb_hist) >= 20:  # At least 20 quarters of data
                quality.append(symbol)
        
        # Prioritize Big 4
        big4 = ["VCB", "CTG", "BID", "TCB"]
        other = [s for s in quality if s not in big4]
        
        return big4 + sorted(other)[:10]  # Big4 + top 10 others
    
    def _get_price_at_date(self, symbol: str, period: str) -> Optional[float]:
        """Get price at specific period"""
        data = self.bank_data.get(symbol, {})
        for h in data.get("pb_history", []):
            if h["period"] == period:
                return h.get("price", 0) * 1000  # Convert to VND
        return None
    
    def _get_pb_at_date(self, symbol: str, period: str) -> Optional[float]:
        """Get P/B at specific period"""
        data = self.bank_data.get(symbol, {})
        for h in data.get("pb_history", []):
            if h["period"] == period:
                return h.get("pb")
        return None
    
    def _get_portfolio_value(self, period: str) -> float:
        """Calculate total portfolio value"""
        total = self.cash
        for symbol, pos in self.positions.items():
            price = self._get_price_at_date(symbol, period)
            if price:
                total += pos.quantity * price
        return total
    
    def calculate_ml_score(self, features: Dict) -> Tuple[float, str]:
        """
        ML-based scoring function
        Returns (score 0-100, explanation)
        
        High score = Strong BUY signal
        Low score = Strong SELL signal
        """
        score = 50  # Start neutral
        explanations = []
        
        # 1. P/B Percentile Factor (weight: 30%)
        pb_pct = features["pb_percentile"]
        if pb_pct < 20:
            pb_score = 30
            explanations.append(f"P/B cực rẻ (P{pb_pct:.0f})")
        elif pb_pct < 35:
            pb_score = 25
            explanations.append(f"P/B rẻ (P{pb_pct:.0f})")
        elif pb_pct < 50:
            pb_score = 15
            explanations.append(f"P/B hợp lý (P{pb_pct:.0f})")
        elif pb_pct < 70:
            pb_score = 0
            explanations.append(f"P/B trung bình cao (P{pb_pct:.0f})")
        else:
            pb_score = -20
            explanations.append(f"P/B đắt (P{pb_pct:.0f})")
        
        score += pb_score
        
        # 2. Heat Index Factor (weight: 30%)
        heat = features["heat_index"]
        heat_level = features["heat_level"]
        
        if heat < 20:
            heat_score = 35
            explanations.append(f"Ngành ICE COLD (Heat={heat:.0f})")
        elif heat < 35:
            heat_score = 25
            explanations.append(f"Ngành COLD (Heat={heat:.0f})")
        elif heat < 45:
            heat_score = 15
            explanations.append(f"Ngành COOL (Heat={heat:.0f})")
        elif heat < 55:
            heat_score = 5
            explanations.append(f"Ngành NEUTRAL (Heat={heat:.0f})")
        elif heat < 70:
            heat_score = -10
            explanations.append(f"Ngành WARM (Heat={heat:.0f})")
        elif heat < 85:
            heat_score = -25
            explanations.append(f"Ngành HOT (Heat={heat:.0f})")
        else:
            heat_score = -40
            explanations.append(f"Ngành OVERHEATED (Heat={heat:.0f})")
        
        score += heat_score
        
        # 3. Historical Win Rate Factor (weight: 20%)
        win_rate = features.get("zone_win_rate", 50)
        if win_rate >= 70:
            wr_score = 15
            explanations.append(f"Win rate cao ({win_rate:.0f}%)")
        elif win_rate >= 60:
            wr_score = 10
        elif win_rate >= 50:
            wr_score = 5
        else:
            wr_score = -5
            explanations.append(f"Win rate thấp ({win_rate:.0f}%)")
        
        score += wr_score
        
        # 4. Heat Trend Factor (weight: 10%)
        trend = features.get("heat_trend", "STABLE")
        if trend == "COOLING_DOWN":
            trend_score = 10
            explanations.append("Ngành đang nguội dần")
        elif trend == "HEATING_UP":
            trend_score = -10
            explanations.append("Ngành đang nóng lên")
        else:
            trend_score = 0
        
        score += trend_score
        
        # 5. Contrarian Bonus: Strong signal when both P/B cheap AND heat cold
        if pb_pct < 25 and heat < 35:
            score += 15
            explanations.append("🎯 Contrarian: CP rẻ + Ngành lạnh")
        
        # Normalize to 0-100
        score = max(0, min(100, score))
        
        return score, " | ".join(explanations[:3])
    
    def calculate_position_size(self, features: Dict, ml_score: float) -> float:
        """
        Calculate position size based on:
        1. Heat-based allocation multiplier
        2. ML score confidence
        3. Number of existing positions
        """
        heat_level = features["heat_level"]
        multiplier, cash_reserve = self.config.heat_allocation_map.get(
            heat_level, (1.0, 15)
        )
        
        portfolio_value = self._get_portfolio_value(features["period"])
        
        # Required cash reserve
        min_cash = portfolio_value * (cash_reserve / 100)
        available_cash = max(0, self.cash - min_cash)
        
        # Base position size
        base_size = self.config.base_position_percent / 100 * portfolio_value
        
        # Adjust by heat multiplier
        heat_adjusted = base_size * multiplier
        
        # Adjust by ML score (higher score = larger position)
        score_multiplier = 0.5 + (ml_score / 100)  # 0.5 to 1.5
        score_adjusted = heat_adjusted * score_multiplier
        
        # Apply min/max limits
        min_size = self.config.min_position_percent / 100 * portfolio_value
        max_size = self.config.max_position_percent / 100 * portfolio_value
        
        position_size = max(min_size, min(max_size, score_adjusted))
        
        # Don't exceed available cash
        position_size = min(position_size, available_cash)
        
        return position_size
    
    def evaluate_entry(self, symbol: str, period: str) -> Tuple[bool, str, float]:
        """
        Evaluate if should enter position
        Returns: (should_buy, reason, position_size)
        """
        if symbol in self.positions:
            return False, "Already have position", 0
        
        if len(self.positions) >= self.config.max_positions:
            return False, "Max positions reached", 0
        
        features = self.feature_extractor.get_features(symbol, period)
        if not features:
            return False, "No data", 0
        
        # ML Score
        ml_score, explanation = self.calculate_ml_score(features)
        
        # Check entry conditions
        pb_pct = features["pb_percentile"]
        heat = features["heat_index"]
        
        # Don't buy when overheated
        if heat >= 85:
            return False, f"Ngành OVERHEATED ({heat:.0f}), không mua", 0
        
        # Don't buy expensive stocks in hot market
        if heat >= 70 and pb_pct > 40:
            return False, f"Ngành HOT + P/B không rẻ", 0
        
        # Entry threshold based on heat
        if heat < 35:
            entry_threshold = 55  # More lenient when cold
        elif heat < 55:
            entry_threshold = 60
        else:
            entry_threshold = 70  # Stricter when warm/hot
        
        if ml_score < entry_threshold:
            return False, f"ML Score {ml_score:.0f} < {entry_threshold}", 0
        
        # P/B must be below max
        if pb_pct > self.config.pb_percentile_max:
            return False, f"P/B P{pb_pct:.0f} > max P{self.config.pb_percentile_max}", 0
        
        # Calculate position size
        position_size = self.calculate_position_size(features, ml_score)
        
        if position_size < 10_000_000:  # Min 10M VND
            return False, "Position size too small", 0
        
        return True, f"ML={ml_score:.0f} | {explanation}", position_size
    
    def evaluate_exit(self, symbol: str, period: str) -> Tuple[bool, str]:
        """Evaluate if should exit position"""
        if symbol not in self.positions:
            return False, ""
        
        pos = self.positions[symbol]
        features = self.feature_extractor.get_features(symbol, period)
        
        if not features:
            return False, ""
        
        price = features["price"]
        pb_pct = features["pb_percentile"]
        heat = features["heat_index"]
        
        # Calculate current P&L
        pnl_pct = (price / pos.avg_price - 1) * 100
        
        # 1. Take Profit
        if pnl_pct >= self.config.take_profit_percent:
            return True, f"Take Profit +{pnl_pct:.1f}%"
        
        # 2. Stop Loss (if enabled)
        if pnl_pct <= -self.config.stop_loss_percent:
            return True, f"Stop Loss {pnl_pct:.1f}%"
        
        # 3. P/B too high
        if pb_pct >= self.config.exit_pb_percentile:
            return True, f"P/B đắt P{pb_pct:.0f} >= P{self.config.exit_pb_percentile}"
        
        # 4. Overheated market - partial exit consideration
        if heat >= 85 and pnl_pct > 0:
            return True, f"Ngành OVERHEATED ({heat:.0f}), chốt lời +{pnl_pct:.1f}%"
        
        # 5. Hot market + expensive P/B
        if heat >= 70 and pb_pct >= 60:
            return True, f"HOT market ({heat:.0f}) + P/B đắt (P{pb_pct:.0f})"
        
        return False, ""
    
    def execute_buy(self, symbol: str, period: str, reason: str, position_size: float):
        """Execute buy order"""
        features = self.feature_extractor.get_features(symbol, period)
        if not features:
            return
        
        price = features["price"]
        pb = features["pb"]
        heat = features["heat_index"]
        
        if not price or price <= 0:
            return
        
        # Calculate quantity
        price_with_fee = price * (1 + TRANSACTION_FEE)
        quantity = int(position_size / price_with_fee / 100) * 100  # Round to 100 shares
        
        if quantity <= 0:
            return
        
        cost = quantity * price_with_fee
        
        if cost > self.cash:
            quantity = int(self.cash / price_with_fee / 100) * 100
            if quantity <= 0:
                return
            cost = quantity * price_with_fee
        
        # Execute
        self.cash -= cost
        self.positions[symbol] = Position(
            symbol=symbol,
            quantity=quantity,
            avg_price=price,
            buy_date=period,
            buy_pb=pb,
            buy_heat=heat
        )
        
        self.trades.append(Trade(
            date=period,
            symbol=symbol,
            action=TradingAction.BUY,
            quantity=quantity,
            price=price,
            pb_at_trade=pb,
            heat_at_trade=heat,
            reason=reason
        ))
    
    def execute_sell(self, symbol: str, period: str, reason: str):
        """Execute sell order"""
        if symbol not in self.positions:
            return
        
        pos = self.positions[symbol]
        features = self.feature_extractor.get_features(symbol, period)
        
        if not features:
            return
        
        price = features["price"]
        pb = features["pb"]
        heat = features["heat_index"]
        
        if not price:
            return
        
        # Calculate proceeds
        gross = pos.quantity * price
        fees = gross * TRANSACTION_FEE
        tax = gross * TAX_SELL
        net = gross - fees - tax
        
        # P&L
        cost = pos.cost_basis * (1 + TRANSACTION_FEE)
        pnl = net - cost
        pnl_pct = (pnl / cost) * 100
        
        # Execute
        self.cash += net
        del self.positions[symbol]
        
        self.trades.append(Trade(
            date=period,
            symbol=symbol,
            action=TradingAction.SELL,
            quantity=pos.quantity,
            price=price,
            pb_at_trade=pb,
            heat_at_trade=heat,
            reason=reason,
            pnl=pnl,
            pnl_percent=pnl_pct
        ))
    
    def take_snapshot(self, period: str):
        """Record portfolio snapshot"""
        heat_data = self.feature_extractor.heat_history.get(period, {})
        
        total_value = self._get_portfolio_value(period)
        
        # Track drawdown
        if total_value > self.peak_value:
            self.peak_value = total_value
        
        current_dd = (self.peak_value - total_value) / self.peak_value * 100
        if current_dd > self.max_drawdown:
            self.max_drawdown = current_dd
        
        self.snapshots.append({
            "period": period,
            "total_value": total_value,
            "cash": self.cash,
            "positions_value": total_value - self.cash,
            "positions_count": len(self.positions),
            "heat_index": heat_data.get("heat_index", 50),
            "heat_level": heat_data.get("level", "NEUTRAL"),
            "return_pct": (total_value / INITIAL_CAPITAL - 1) * 100,
            "drawdown": current_dd
        })
    
    def generate_report(self) -> Dict:
        """Generate comprehensive trading report"""
        if not self.snapshots:
            return {}
        
        # Final metrics
        final_snapshot = self.snapshots[-1]
        final_value = final_snapshot["total_value"]
        years = len(self.snapshots) / 4
        
        # CAGR
        if years > 0:
            cagr = ((final_value / INITIAL_CAPITAL) ** (1/years) - 1) * 100
        else:
            cagr = 0
        
        # Sharpe Ratio
        returns = []
        for i in range(1, len(self.snapshots)):
            r = (self.snapshots[i]["total_value"] - self.snapshots[i-1]["total_value"]) / self.snapshots[i-1]["total_value"]
            returns.append(r)
        
        if returns:
            avg_return = np.mean(returns) * 4  # Annualized
            std_return = np.std(returns) * 2  # Annualized
            sharpe = avg_return / std_return if std_return > 0 else 0
        else:
            sharpe = 0
        
        # Trade analysis
        sell_trades = [t for t in self.trades if t.action == TradingAction.SELL]
        buy_trades = [t for t in self.trades if t.action == TradingAction.BUY]
        wins = [t for t in sell_trades if t.pnl > 0]
        losses = [t for t in sell_trades if t.pnl <= 0]
        
        win_rate = len(wins) / len(sell_trades) * 100 if sell_trades else 0
        
        # Profit factor (handle division by zero)
        total_wins = sum(t.pnl for t in wins) if wins else 0
        total_losses = abs(sum(t.pnl for t in losses)) if losses else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else (999 if total_wins > 0 else 0)
        
        # Equity curve
        equity_curve = [
            {
                "date": s["period"],
                "value": s["total_value"],
                "return": s["return_pct"],
                "heat": s["heat_index"]
            }
            for s in self.snapshots
        ]
        
        # Current positions
        current_positions = []
        for symbol, pos in self.positions.items():
            features = self.feature_extractor.get_features(symbol, self.snapshots[-1]["period"])
            if features:
                current_pnl = (features["price"] / pos.avg_price - 1) * 100
                current_positions.append({
                    "symbol": symbol,
                    "quantity": pos.quantity,
                    "avg_price": pos.avg_price,
                    "buy_pb": pos.buy_pb,
                    "buy_date": pos.buy_date,
                    "buy_heat": pos.buy_heat,
                    "current_price": features["price"],
                    "current_pb": features["pb"],
                    "current_pnl_pct": current_pnl
                })
        
        # Detailed trades
        detailed_trades = [
            {
                "date": t.date,
                "symbol": t.symbol,
                "action": t.action.value,
                "quantity": t.quantity,
                "price": t.price,
                "pb": t.pb_at_trade,
                "heat": t.heat_at_trade,
                "reason": t.reason,
                "pnl": t.pnl,
                "pnl_percent": t.pnl_percent
            }
            for t in self.trades
        ]
        
        return {
            "bot_name": self.config.name,
            "bot_description": self.config.description,
            "performance": {
                "initial_capital": INITIAL_CAPITAL,
                "final_value": final_value,
                "total_return_percent": (final_value / INITIAL_CAPITAL - 1) * 100,
                "cagr_percent": cagr,
                "max_drawdown_percent": self.max_drawdown,
                "sharpe_ratio": sharpe,
                "years": years
            },
            "trades": {
                "total_trades": len(self.trades),
                "buy_trades": len(buy_trades),
                "sell_trades": len(sell_trades),
                "win_rate_percent": win_rate,
                "profit_factor": min(profit_factor, 999),  # Cap at 999 to avoid Infinity
                "avg_win_percent": np.mean([t.pnl_percent for t in wins]) if wins else 0,
                "avg_loss_percent": np.mean([t.pnl_percent for t in losses]) if losses else 0
            },
            "position_sizing_summary": {
                "method": "ML + Heat-Aware",
                "heat_allocation_map": {k: {"multiplier": v[0], "cash_reserve": v[1]} 
                                       for k, v in self.config.heat_allocation_map.items()}
            },
            "config": {
                "pb_percentile_max": self.config.pb_percentile_max,
                "exit_pb_percentile": self.config.exit_pb_percentile,
                "take_profit": self.config.take_profit_percent,
                "stop_loss": self.config.stop_loss_percent,
                "max_positions": self.config.max_positions
            },
            "equity_curve": equity_curve,
            "current_positions": current_positions,
            "detailed_trades": detailed_trades
        }


# =============================================================================
# Pre-defined BOT Configurations
# =============================================================================

def create_ml_heat_bots() -> Dict[str, HeatAwareBOTConfig]:
    """Create ML Heat-Aware BOT configurations"""
    
    return {
        "BOT1_ML_CONTRARIAN": HeatAwareBOTConfig(
            name="🧠 ML Contrarian",
            description="Machine Learning + Contrarian: Mua mạnh khi ngành lạnh, bán khi nóng",
            pb_percentile_max=45,
            exit_pb_percentile=80,
            base_position_percent=18,
            max_position_percent=28,
            min_position_percent=8,
            max_positions=7,
            stop_loss_percent=999,  # No stoploss
            take_profit_percent=70,
            min_holding_quarters=3,
            heat_allocation_map={
                "ICE_COLD": (1.8, 0),      # All in when panic
                "COLD": (1.5, 5),
                "COOL": (1.2, 10),
                "NEUTRAL": (1.0, 15),
                "WARM": (0.6, 30),
                "HOT": (0.3, 50),
                "OVERHEATED": (0.0, 70),   # No new buys
            }
        ),
        
        "BOT2_ML_AGGRESSIVE": HeatAwareBOTConfig(
            name="🔥 ML Aggressive",
            description="ML Aggressive: Chấp nhận rủi ro cao, tập trung vào CP cực rẻ",
            pb_percentile_max=30,
            exit_pb_percentile=70,
            base_position_percent=22,
            max_position_percent=35,
            min_position_percent=10,
            max_positions=5,
            stop_loss_percent=35,
            take_profit_percent=80,
            min_holding_quarters=2,
            heat_allocation_map={
                "ICE_COLD": (2.0, 0),
                "COLD": (1.6, 5),
                "COOL": (1.3, 10),
                "NEUTRAL": (1.0, 15),
                "WARM": (0.5, 35),
                "HOT": (0.2, 55),
                "OVERHEATED": (0.0, 80),
            }
        ),
        
        "BOT3_ML_BALANCED": HeatAwareBOTConfig(
            name="⚖️ ML Balanced",
            description="ML Balanced: Cân bằng giữa lợi nhuận và rủi ro",
            pb_percentile_max=40,
            exit_pb_percentile=75,
            base_position_percent=16,
            max_position_percent=25,
            min_position_percent=8,
            max_positions=8,
            stop_loss_percent=25,
            take_profit_percent=50,
            min_holding_quarters=3,
            heat_allocation_map={
                "ICE_COLD": (1.5, 5),
                "COLD": (1.3, 10),
                "COOL": (1.15, 15),
                "NEUTRAL": (1.0, 20),
                "WARM": (0.7, 30),
                "HOT": (0.4, 45),
                "OVERHEATED": (0.1, 60),
            }
        ),
        
        "BOT4_ML_DEFENSIVE": HeatAwareBOTConfig(
            name="🛡️ ML Defensive",
            description="ML Defensive: Ưu tiên bảo vệ vốn, giữ cash nhiều khi nóng",
            pb_percentile_max=35,
            exit_pb_percentile=70,
            base_position_percent=15,
            max_position_percent=22,
            min_position_percent=8,
            max_positions=6,
            stop_loss_percent=20,
            take_profit_percent=40,
            min_holding_quarters=4,
            heat_allocation_map={
                "ICE_COLD": (1.4, 10),
                "COLD": (1.2, 15),
                "COOL": (1.1, 20),
                "NEUTRAL": (0.9, 25),
                "WARM": (0.6, 40),
                "HOT": (0.3, 55),
                "OVERHEATED": (0.0, 75),
            }
        ),
        
        "BOT5_ML_QUALITY": HeatAwareBOTConfig(
            name="💎 ML Quality",
            description="ML Quality: Focus vào Big4, hold dài hạn, chờ đợi cơ hội tốt",
            pb_percentile_max=50,
            exit_pb_percentile=85,
            base_position_percent=20,
            max_position_percent=30,
            min_position_percent=10,
            max_positions=5,
            stop_loss_percent=999,  # No stoploss
            take_profit_percent=60,
            min_holding_quarters=5,
            heat_allocation_map={
                "ICE_COLD": (1.6, 0),
                "COLD": (1.4, 5),
                "COOL": (1.2, 10),
                "NEUTRAL": (1.0, 15),
                "WARM": (0.8, 25),
                "HOT": (0.5, 40),
                "OVERHEATED": (0.2, 55),
            }
        ),
    }


def calculate_buy_hold_benchmark(bank_data: Dict) -> Dict:
    """Calculate Buy & Hold benchmark for comparison"""
    
    # Get all periods
    all_periods = set()
    for symbol, data in bank_data.items():
        for h in data.get("pb_history", []):
            all_periods.add(h["period"])
    periods = sorted(list(all_periods))
    
    if len(periods) < 8:
        return {"performance": {"total_return_percent": 0, "cagr_percent": 0}}
    
    start_period = periods[0]
    end_period = periods[-5]  # Skip last 4 quarters like BOTs
    
    # Top banks for Buy & Hold
    top_symbols = ["VCB", "MBB", "ACB", "TCB", "CTG"]
    benchmark_returns = []
    
    for symbol in top_symbols:
        if symbol not in bank_data:
            continue
        
        pb_hist = bank_data[symbol].get("pb_history", [])
        price_map = {p["period"]: p.get("price", 0) * 1000 for p in pb_hist}
        
        start_price = price_map.get(start_period)
        end_price = price_map.get(end_period)
        
        if start_price and end_price and start_price > 0:
            ret = (end_price / start_price - 1) * 100
            benchmark_returns.append({
                "symbol": symbol,
                "start_price": start_price,
                "end_price": end_price,
                "return": ret
            })
    
    if not benchmark_returns:
        return {"performance": {"total_return_percent": 0, "cagr_percent": 0}}
    
    # Equal weight
    avg_return = np.mean([r["return"] for r in benchmark_returns])
    years = (len(periods) - 4) / 4
    cagr = ((1 + avg_return/100) ** (1/years) - 1) * 100 if years > 0 else 0
    
    # Build equity curve
    portfolio_per_stock = INITIAL_CAPITAL / len(benchmark_returns)
    equity_curve = []
    max_value = INITIAL_CAPITAL
    max_dd = 0
    
    # Build heat history for curve
    feature_extractor = MLFeatureExtractor(bank_data)
    
    for period in periods[:-4]:
        total_value = 0
        for br in benchmark_returns:
            symbol = br["symbol"]
            pb_hist = bank_data[symbol].get("pb_history", [])
            price_map = {p["period"]: p.get("price", 0) * 1000 for p in pb_hist}
            
            start_price = br["start_price"]
            current_price = price_map.get(period, start_price)
            
            if start_price > 0:
                shares = portfolio_per_stock / (start_price * (1 + TRANSACTION_FEE))
                total_value += shares * current_price
        
        # Drawdown
        if total_value > max_value:
            max_value = total_value
        dd = (max_value - total_value) / max_value * 100
        if dd > max_dd:
            max_dd = dd
        
        heat_data = feature_extractor.heat_history.get(period, {})
        
        equity_curve.append({
            "date": period,
            "value": total_value,
            "return": (total_value / INITIAL_CAPITAL - 1) * 100,
            "heat": heat_data.get("heat_index", 50)
        })
    
    final_value = equity_curve[-1]["value"] if equity_curve else INITIAL_CAPITAL
    actual_return = (final_value / INITIAL_CAPITAL - 1) * 100
    actual_cagr = ((final_value / INITIAL_CAPITAL) ** (1/years) - 1) * 100 if years > 0 else 0
    
    return {
        "bot_name": "📈 Buy & Hold Benchmark",
        "bot_description": f"Mua & giữ {', '.join([r['symbol'] for r in benchmark_returns])} từ đầu kỳ",
        "performance": {
            "initial_capital": INITIAL_CAPITAL,
            "final_value": final_value,
            "total_return_percent": actual_return,
            "cagr_percent": actual_cagr,
            "max_drawdown_percent": max_dd,
            "sharpe_ratio": 0,  # Simplified
            "years": years
        },
        "trades": {
            "total_trades": len(benchmark_returns),
            "buy_trades": len(benchmark_returns),
            "sell_trades": 0,
            "win_rate_percent": 100 if actual_return > 0 else 0,
            "profit_factor": 999 if actual_return > 0 else 0,
            "avg_win_percent": actual_return / len(benchmark_returns) if benchmark_returns else 0,
            "avg_loss_percent": 0
        },
        "position_sizing_summary": {
            "method": "Equal Weight Buy & Hold",
            "heat_allocation_map": {}
        },
        "config": {
            "pb_percentile_max": "N/A",
            "exit_pb_percentile": "N/A",
            "take_profit": "N/A",
            "stop_loss": "N/A",
            "max_positions": len(benchmark_returns)
        },
        "equity_curve": equity_curve,
        "current_positions": [
            {
                "symbol": r["symbol"],
                "quantity": int(portfolio_per_stock / r["start_price"]),
                "avg_price": r["start_price"],
                "buy_pb": 0,
                "buy_date": start_period,
                "buy_heat": 0,
                "current_price": r["end_price"],
                "current_pb": 0,
                "current_pnl_pct": r["return"]
            } for r in benchmark_returns
        ],
        "detailed_trades": []
    }


def run_ml_heat_bots():
    """Run all ML Heat-Aware BOTs"""
    
    # Load data
    data_file = os.path.join(os.path.dirname(__file__), "../docs/data/banks_v2.json")
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    bank_data = data.get("banks", {})
    
    print("\n" + "="*80)
    print("🧠 RUNNING ML HEAT-AWARE TRADING BOTS")
    print("="*80)
    
    results = {}
    
    # Buy & Hold Benchmark
    print("\n📊 Calculating Buy & Hold Benchmark...")
    benchmark = calculate_buy_hold_benchmark(bank_data)
    results["BENCHMARK_BUY_HOLD"] = benchmark
    print(f"   Return: {benchmark['performance']['total_return_percent']:+.1f}%")
    print(f"   CAGR: {benchmark['performance']['cagr_percent']:+.1f}%")
    print(f"   Max DD: -{benchmark['performance']['max_drawdown_percent']:.1f}%")
    
    # ML BOTs
    bot_configs = create_ml_heat_bots()
    
    # Get all periods
    all_periods = set()
    for symbol, bdata in bank_data.items():
        for h in bdata.get("pb_history", []):
            all_periods.add(h["period"])
    periods = sorted(list(all_periods))
    backtest_periods = periods[:-4] if len(periods) > 4 else periods
    
    for bot_id, config in bot_configs.items():
        print(f"\n🤖 Running {config.name}...")
        
        bot = HeatAwareMLBot(config, bank_data)
        
        for period in backtest_periods:
            # Check exits first
            for symbol in list(bot.positions.keys()):
                should_exit, reason = bot.evaluate_exit(symbol, period)
                if should_exit:
                    bot.execute_sell(symbol, period, reason)
            
            # Check entries
            for symbol in bot.quality_banks:
                should_enter, reason, size = bot.evaluate_entry(symbol, period)
                if should_enter:
                    bot.execute_buy(symbol, period, reason, size)
            
            bot.take_snapshot(period)
        
        report = bot.generate_report()
        results[bot_id] = report
        
        perf = report.get("performance", {})
        trades = report.get("trades", {})
        
        print(f"   Return: {perf.get('total_return_percent', 0):+.1f}%")
        print(f"   CAGR: {perf.get('cagr_percent', 0):+.1f}%")
        print(f"   Max DD: -{perf.get('max_drawdown_percent', 0):.1f}%")
        print(f"   Trades: {trades.get('total_trades', 0)}")
        print(f"   Win Rate: {trades.get('win_rate_percent', 0):.0f}%")
    
    # Save results
    output_file = os.path.join(os.path.dirname(__file__), "../docs/data/bot_results.json")
    
    # Custom JSON encoder to handle special values
    def json_safe(obj):
        if isinstance(obj, float):
            if np.isnan(obj) or np.isinf(obj):
                return 0
        return obj
    
    # Clean results
    def clean_for_json(obj):
        if isinstance(obj, dict):
            return {k: clean_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_for_json(item) for item in obj]
        elif isinstance(obj, float):
            if np.isnan(obj) or np.isinf(obj):
                return 0
            return obj
        else:
            return obj
    
    clean_results = clean_for_json(results)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(clean_results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n✓ Results saved to {output_file}")
    
    # Print comparison table
    print("\n" + "="*100)
    print("📊 ML HEAT-AWARE BOT COMPARISON")
    print("="*100)
    print(f"{'BOT':<25} {'Return':>10} {'CAGR':>8} {'MaxDD':>8} {'Trades':>8} {'WinRate':>10} {'Sharpe':>8}")
    print("-"*100)
    
    for bot_id, report in sorted(results.items(),
                                  key=lambda x: x[1].get("performance", {}).get("cagr_percent", 0),
                                  reverse=True):
        perf = report.get("performance", {})
        trades = report.get("trades", {})
        name = report.get("bot_name", bot_id)[:24]
        
        print(f"{name:<25} {perf.get('total_return_percent', 0):>+9.1f}% "
              f"{perf.get('cagr_percent', 0):>+7.1f}% "
              f"{-perf.get('max_drawdown_percent', 0):>7.1f}% "
              f"{trades.get('total_trades', 0):>7} "
              f"{trades.get('win_rate_percent', 0):>9.0f}% "
              f"{perf.get('sharpe_ratio', 0):>7.2f}")
    
    return results


if __name__ == "__main__":
    results = run_ml_heat_bots()
