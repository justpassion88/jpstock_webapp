"""
JP Stock Webapp - Trading BOT Simulator
5 BOT với chiến lược khác nhau, backtest trên dữ liệu lịch sử
Sử dụng LÃI KÉP để tính toán

Author: JP Stock Analysis
Version: 1.0
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
import numpy as np
from scipy import stats

# Constants
INITIAL_CAPITAL = 100_000_000  # 100 triệu VND
TRANSACTION_FEE = 0.0015  # 0.15% phí giao dịch mỗi chiều
TAX_SELL = 0.001  # 0.1% thuế bán


class TradingAction(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class Position:
    """Vị thế đang nắm giữ"""
    symbol: str
    quantity: int
    avg_price: float
    buy_date: str
    buy_pb: float
    
    @property
    def cost_basis(self) -> float:
        return self.quantity * self.avg_price


@dataclass
class Trade:
    """Giao dịch đã thực hiện"""
    date: str
    symbol: str
    action: TradingAction
    quantity: int
    price: float
    pb_at_trade: float
    reason: str
    pnl: float = 0  # Profit/Loss for SELL trades
    pnl_percent: float = 0


@dataclass
class PortfolioSnapshot:
    """Trạng thái portfolio tại một thời điểm"""
    date: str
    cash: float
    positions: Dict[str, Position]
    total_value: float
    total_return: float  # % return từ đầu
    drawdown: float  # % từ đỉnh


@dataclass 
class BOTConfig:
    """Cấu hình BOT"""
    name: str
    description: str
    
    # Entry rules
    pb_percentile_max: float  # Chỉ mua khi P/B dưới percentile này
    min_win_rate: float  # Win rate tối thiểu của vùng P/B
    min_expected_return: float  # Expected return tối thiểu (%)
    
    # Position sizing
    max_position_percent: float  # % tối đa cho 1 cổ phiếu
    max_positions: int  # Số vị thế tối đa
    position_sizing_method: str  # "equal", "kelly", "risk_parity"
    
    # Exit rules
    holding_period_quarters: int  # Số quý nắm giữ tối thiểu
    take_profit_percent: float  # Chốt lời khi đạt %
    stop_loss_percent: float  # Cắt lỗ khi mất %
    exit_pb_percentile: float  # Bán khi P/B vượt percentile này
    
    # Rebalancing
    rebalance_frequency: str  # "quarterly", "monthly"


# ============================================
# 5 BOT STRATEGIES
# ============================================

BOT_CONFIGS = {
    "BOT1_CONSERVATIVE": BOTConfig(
        name="🛡️ Conservative Value",
        description="Chỉ mua cổ phiếu CỰC RẺ, ưu tiên an toàn và win rate cao",
        pb_percentile_max=10,  # Chỉ mua khi P/B < P10 (cực rẻ)
        min_win_rate=70,
        min_expected_return=20,
        max_position_percent=20,  # Max 20% cho 1 CP
        max_positions=5,
        position_sizing_method="equal",
        holding_period_quarters=4,  # Giữ ít nhất 1 năm
        take_profit_percent=50,
        stop_loss_percent=20,
        exit_pb_percentile=75,  # Bán khi P/B > P75
        rebalance_frequency="quarterly"
    ),
    
    "BOT2_VALUE_HUNTER": BOTConfig(
        name="🎯 Value Hunter",
        description="Săn cổ phiếu RẺ, cân bằng giữa cơ hội và rủi ro",
        pb_percentile_max=25,  # Mua khi P/B < P25 (rẻ)
        min_win_rate=60,
        min_expected_return=15,
        max_position_percent=25,
        max_positions=6,
        position_sizing_method="equal",
        holding_period_quarters=3,
        take_profit_percent=40,
        stop_loss_percent=25,
        exit_pb_percentile=70,
        rebalance_frequency="quarterly"
    ),
    
    "BOT3_QUALITY_VALUE": BOTConfig(
        name="💎 Quality Value",
        description="Mua CP chất lượng (Big4) khi định giá hợp lý hoặc rẻ",
        pb_percentile_max=50,  # Mua khi P/B < P50 (dưới trung bình)
        min_win_rate=50,
        min_expected_return=10,
        max_position_percent=30,
        max_positions=4,  # Tập trung vào Big4
        position_sizing_method="equal",
        holding_period_quarters=4,
        take_profit_percent=35,
        stop_loss_percent=15,
        exit_pb_percentile=85,
        rebalance_frequency="quarterly"
    ),
    
    "BOT4_DIVERSIFIED": BOTConfig(
        name="🌈 Diversified",
        description="Phân bổ đều nhiều CP, giảm rủi ro tập trung",
        pb_percentile_max=40,
        min_win_rate=55,
        min_expected_return=12,
        max_position_percent=12,  # Max 12% mỗi CP
        max_positions=10,  # Nhiều CP
        position_sizing_method="risk_parity",
        holding_period_quarters=2,
        take_profit_percent=30,
        stop_loss_percent=20,
        exit_pb_percentile=75,
        rebalance_frequency="quarterly"
    ),
    
    "BOT5_AGGRESSIVE": BOTConfig(
        name="🔥 Aggressive Growth",
        description="Tập trung vào CP rẻ nhất, chấp nhận rủi ro cao để tìm lợi nhuận cao",
        pb_percentile_max=15,
        min_win_rate=50,
        min_expected_return=25,
        max_position_percent=35,  # Có thể tập trung cao
        max_positions=3,  # Ít CP, tập trung
        position_sizing_method="kelly",  # Dùng Kelly Criterion
        holding_period_quarters=2,
        take_profit_percent=80,  # Mục tiêu cao
        stop_loss_percent=30,  # Chịu lỗ nhiều hơn
        exit_pb_percentile=60,
        rebalance_frequency="quarterly"
    ),
}


class TradingBOT:
    """Trading BOT với chiến lược cụ thể"""
    
    def __init__(self, config: BOTConfig, bank_data: Dict):
        self.config = config
        self.bank_data = bank_data
        
        # Portfolio state
        self.cash = INITIAL_CAPITAL
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.snapshots: List[PortfolioSnapshot] = []
        
        # Performance tracking
        self.peak_value = INITIAL_CAPITAL
        self.max_drawdown = 0
        
        # Qualified banks (có đủ data và quality)
        self.quality_banks = self._filter_quality_banks()
    
    def _filter_quality_banks(self) -> List[str]:
        """Lọc các ngân hàng có đủ data chất lượng"""
        quality = []
        
        # Big 4 banks (always quality for BOT3)
        big4 = ["VCB", "BID", "CTG", "TCB"]
        
        for symbol, data in self.bank_data.items():
            pb_stats = data.get("pb_statistics", {})
            hist_returns = data.get("historical_returns", {})
            
            # Cần ít nhất 8 năm data (32 quý)
            if pb_stats.get("count", 0) < 32:
                continue
            
            # Cần có historical returns data
            if not hist_returns:
                continue
            
            quality.append(symbol)
        
        return quality
    
    def _get_pb_percentile(self, symbol: str, current_pb: float) -> float:
        """Tính percentile của P/B hiện tại"""
        data = self.bank_data.get(symbol, {})
        pb_history = data.get("pb_history", [])
        
        if not pb_history:
            return 50  # Default
        
        pb_values = [h["pb"] for h in pb_history if h.get("pb")]
        return stats.percentileofscore(pb_values, current_pb)
    
    def _get_zone_stats(self, symbol: str, pb_percentile: float) -> Dict:
        """Lấy thống kê của vùng P/B"""
        data = self.bank_data.get(symbol, {})
        hist_returns = data.get("historical_returns", {})
        
        # Xác định zone
        if pb_percentile < 10:
            zone = "extremely_cheap"
        elif pb_percentile < 25:
            zone = "cheap"
        elif pb_percentile < 75:
            zone = "fair"
        elif pb_percentile < 90:
            zone = "expensive"
        else:
            zone = "extremely_expensive"
        
        return hist_returns.get(zone, {})
    
    def _calculate_position_size(self, symbol: str, zone_stats: Dict) -> float:
        """Tính kích thước vị thế dựa trên phương pháp"""
        portfolio_value = self._get_portfolio_value_at_date(None)
        
        if self.config.position_sizing_method == "equal":
            # Chia đều
            return min(
                self.config.max_position_percent / 100,
                1.0 / self.config.max_positions
            ) * portfolio_value
        
        elif self.config.position_sizing_method == "kelly":
            # Kelly Criterion: f = (p*b - q) / b
            # p = win rate, q = 1-p, b = win/loss ratio
            win_rate = zone_stats.get("win_rate_1y", 50) / 100
            avg_return = zone_stats.get("return_1y_avg", 10) / 100
            
            if win_rate <= 0 or avg_return <= 0:
                return 0
            
            # Simplified Kelly
            kelly_fraction = win_rate - (1 - win_rate) / (avg_return / 0.1)
            kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Cap at 25%
            
            return kelly_fraction * portfolio_value
        
        elif self.config.position_sizing_method == "risk_parity":
            # Risk parity - allocate based on inverse volatility
            # Simplified: equal weight for now
            return (self.config.max_position_percent / 100) * portfolio_value
        
        return 0
    
    def _get_portfolio_value_at_date(self, date: str) -> float:
        """Tính tổng giá trị portfolio"""
        total = self.cash
        
        for symbol, pos in self.positions.items():
            # Lấy giá hiện tại
            current_price = self._get_price_at_date(symbol, date)
            if current_price:
                total += pos.quantity * current_price
        
        return total
    
    def _get_price_at_date(self, symbol: str, date: str) -> Optional[float]:
        """Lấy giá tại thời điểm"""
        data = self.bank_data.get(symbol, {})
        pb_history = data.get("pb_history", [])
        
        if not date:
            # Current price
            return data.get("current_price", 0) * 1000
        
        for h in pb_history:
            if h.get("period") == date:
                return h.get("price", 0) * 1000
        
        return None
    
    def _get_pb_at_date(self, symbol: str, date: str) -> Optional[float]:
        """Lấy P/B tại thời điểm"""
        data = self.bank_data.get(symbol, {})
        pb_history = data.get("pb_history", [])
        
        for h in pb_history:
            if h.get("period") == date:
                return h.get("pb")
        
        return None
    
    def evaluate_entry(self, symbol: str, date: str) -> Tuple[bool, str]:
        """Đánh giá có nên mua không"""
        if symbol not in self.quality_banks:
            return False, "Not a quality bank"
        
        if symbol in self.positions:
            return False, "Already in portfolio"
        
        if len(self.positions) >= self.config.max_positions:
            return False, "Max positions reached"
        
        # Lấy P/B và percentile
        current_pb = self._get_pb_at_date(symbol, date)
        if not current_pb:
            return False, "No P/B data"
        
        pb_percentile = self._get_pb_percentile(symbol, current_pb)
        
        # Check P/B percentile threshold
        if pb_percentile > self.config.pb_percentile_max:
            return False, f"P/B percentile {pb_percentile:.0f} > {self.config.pb_percentile_max}"
        
        # Check zone statistics
        zone_stats = self._get_zone_stats(symbol, pb_percentile)
        
        win_rate = zone_stats.get("win_rate_1y", 0)
        expected_return = zone_stats.get("return_1y_avg", 0)
        
        if win_rate and win_rate < self.config.min_win_rate:
            return False, f"Win rate {win_rate:.0f}% < {self.config.min_win_rate}%"
        
        if expected_return and expected_return < self.config.min_expected_return:
            return False, f"Expected return {expected_return:.1f}% < {self.config.min_expected_return}%"
        
        return True, f"P/B P{pb_percentile:.0f}, WR {win_rate:.0f}%, ER {expected_return:.1f}%"
    
    def evaluate_exit(self, symbol: str, date: str) -> Tuple[bool, str]:
        """Đánh giá có nên bán không"""
        if symbol not in self.positions:
            return False, "No position"
        
        pos = self.positions[symbol]
        current_price = self._get_price_at_date(symbol, date)
        current_pb = self._get_pb_at_date(symbol, date)
        
        if not current_price or not current_pb:
            return False, "No price data"
        
        # Calculate P&L
        pnl_percent = (current_price - pos.avg_price) / pos.avg_price * 100
        
        # Check take profit
        if pnl_percent >= self.config.take_profit_percent:
            return True, f"Take profit: +{pnl_percent:.1f}%"
        
        # Check stop loss
        if pnl_percent <= -self.config.stop_loss_percent:
            return True, f"Stop loss: {pnl_percent:.1f}%"
        
        # Check P/B percentile exit
        pb_percentile = self._get_pb_percentile(symbol, current_pb)
        if pb_percentile >= self.config.exit_pb_percentile:
            return True, f"P/B P{pb_percentile:.0f} >= {self.config.exit_pb_percentile}"
        
        # Check holding period
        # (Simplified - would need proper date parsing in production)
        
        return False, "Hold"
    
    def execute_buy(self, symbol: str, date: str, reason: str):
        """Thực hiện lệnh mua"""
        price = self._get_price_at_date(symbol, date)
        pb = self._get_pb_at_date(symbol, date)
        
        if not price or price <= 0:
            return
        
        # Calculate position size
        pb_percentile = self._get_pb_percentile(symbol, pb)
        zone_stats = self._get_zone_stats(symbol, pb_percentile)
        target_value = self._calculate_position_size(symbol, zone_stats)
        
        # Account for transaction fees
        price_with_fee = price * (1 + TRANSACTION_FEE)
        quantity = int(target_value / price_with_fee / 100) * 100  # Round to lot of 100
        
        if quantity <= 0:
            return
        
        cost = quantity * price_with_fee
        
        if cost > self.cash:
            # Reduce quantity
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
            buy_date=date,
            buy_pb=pb
        )
        
        self.trades.append(Trade(
            date=date,
            symbol=symbol,
            action=TradingAction.BUY,
            quantity=quantity,
            price=price,
            pb_at_trade=pb,
            reason=reason
        ))
    
    def execute_sell(self, symbol: str, date: str, reason: str):
        """Thực hiện lệnh bán"""
        if symbol not in self.positions:
            return
        
        pos = self.positions[symbol]
        price = self._get_price_at_date(symbol, date)
        pb = self._get_pb_at_date(symbol, date)
        
        if not price:
            return
        
        # Calculate proceeds after fees and tax
        gross_proceeds = pos.quantity * price
        fees = gross_proceeds * TRANSACTION_FEE
        tax = gross_proceeds * TAX_SELL
        net_proceeds = gross_proceeds - fees - tax
        
        # Calculate P&L
        pnl = net_proceeds - pos.cost_basis
        pnl_percent = pnl / pos.cost_basis * 100
        
        # Execute
        self.cash += net_proceeds
        del self.positions[symbol]
        
        self.trades.append(Trade(
            date=date,
            symbol=symbol,
            action=TradingAction.SELL,
            quantity=pos.quantity,
            price=price,
            pb_at_trade=pb,
            reason=reason,
            pnl=pnl,
            pnl_percent=pnl_percent
        ))
    
    def take_snapshot(self, date: str):
        """Chụp trạng thái portfolio"""
        total_value = self._get_portfolio_value_at_date(date)
        total_return = (total_value - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100
        
        # Update peak and drawdown
        if total_value > self.peak_value:
            self.peak_value = total_value
        
        drawdown = (self.peak_value - total_value) / self.peak_value * 100
        if drawdown > self.max_drawdown:
            self.max_drawdown = drawdown
        
        self.snapshots.append(PortfolioSnapshot(
            date=date,
            cash=self.cash,
            positions=dict(self.positions),
            total_value=total_value,
            total_return=total_return,
            drawdown=drawdown
        ))
    
    def run_backtest(self) -> Dict:
        """Chạy backtest trên toàn bộ lịch sử"""
        # Lấy tất cả các period từ data
        all_periods = set()
        for symbol, data in self.bank_data.items():
            for h in data.get("pb_history", []):
                all_periods.add(h["period"])
        
        periods = sorted(list(all_periods))
        
        # Bỏ 4 quý gần nhất (cần để tính return)
        backtest_periods = periods[:-4] if len(periods) > 4 else periods
        
        print(f"\n{'='*60}")
        print(f"Running backtest for {self.config.name}")
        print(f"Periods: {backtest_periods[0]} to {backtest_periods[-1]}")
        print(f"{'='*60}")
        
        for period in backtest_periods:
            # Check exits first
            symbols_to_sell = []
            for symbol in list(self.positions.keys()):
                should_exit, reason = self.evaluate_exit(symbol, period)
                if should_exit:
                    symbols_to_sell.append((symbol, reason))
            
            for symbol, reason in symbols_to_sell:
                self.execute_sell(symbol, period, reason)
            
            # Then check entries
            for symbol in self.quality_banks:
                should_enter, reason = self.evaluate_entry(symbol, period)
                if should_enter:
                    self.execute_buy(symbol, period, reason)
            
            # Take snapshot
            self.take_snapshot(period)
        
        # Generate report
        return self._generate_report()
    
    def _generate_report(self) -> Dict:
        """Tạo báo cáo kết quả"""
        if not self.snapshots:
            return {}
        
        final_value = self.snapshots[-1].total_value
        total_return = (final_value - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100
        
        # Calculate CAGR
        years = len(self.snapshots) / 4  # quarters to years
        if years > 0:
            cagr = ((final_value / INITIAL_CAPITAL) ** (1/years) - 1) * 100
        else:
            cagr = 0
        
        # Win/Loss statistics
        sell_trades = [t for t in self.trades if t.action == TradingAction.SELL]
        wins = [t for t in sell_trades if t.pnl > 0]
        losses = [t for t in sell_trades if t.pnl <= 0]
        
        win_rate = len(wins) / len(sell_trades) * 100 if sell_trades else 0
        
        avg_win = np.mean([t.pnl_percent for t in wins]) if wins else 0
        avg_loss = np.mean([t.pnl_percent for t in losses]) if losses else 0
        
        # Profit factor
        total_wins = sum(t.pnl for t in wins)
        total_losses = abs(sum(t.pnl for t in losses))
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        report = {
            "bot_name": self.config.name,
            "bot_description": self.config.description,
            "config": {
                "pb_percentile_max": self.config.pb_percentile_max,
                "min_win_rate": self.config.min_win_rate,
                "min_expected_return": self.config.min_expected_return,
                "max_positions": self.config.max_positions,
                "max_position_percent": self.config.max_position_percent,
                "position_sizing": self.config.position_sizing_method,
                "take_profit": self.config.take_profit_percent,
                "stop_loss": self.config.stop_loss_percent,
            },
            "performance": {
                "initial_capital": INITIAL_CAPITAL,
                "final_value": final_value,
                "total_return_percent": total_return,
                "cagr_percent": cagr,
                "max_drawdown_percent": self.max_drawdown,
            },
            "trades": {
                "total_trades": len(self.trades),
                "buy_trades": len([t for t in self.trades if t.action == TradingAction.BUY]),
                "sell_trades": len(sell_trades),
                "win_rate_percent": win_rate,
                "avg_win_percent": avg_win,
                "avg_loss_percent": avg_loss,
                "profit_factor": profit_factor,
            },
            "current_positions": [
                {
                    "symbol": pos.symbol,
                    "quantity": pos.quantity,
                    "avg_price": pos.avg_price,
                    "buy_date": pos.buy_date,
                    "buy_pb": pos.buy_pb,
                }
                for pos in self.positions.values()
            ],
            "trade_history": [
                {
                    "date": t.date,
                    "symbol": t.symbol,
                    "action": t.action.value,
                    "quantity": t.quantity,
                    "price": t.price,
                    "pb": t.pb_at_trade,
                    "reason": t.reason,
                    "pnl": t.pnl,
                    "pnl_percent": t.pnl_percent,
                }
                for t in self.trades[-20:]  # Last 20 trades
            ],
            "equity_curve": [
                {
                    "date": s.date,
                    "value": s.total_value,
                    "return": s.total_return,
                    "drawdown": s.drawdown,
                }
                for s in self.snapshots
            ]
        }
        
        return report


def run_all_bots():
    """Chạy tất cả 5 BOT và so sánh"""
    # Load bank data
    data_file = "../docs/data/banks_v2.json"
    
    if not os.path.exists(data_file):
        print(f"Error: Data file not found: {data_file}")
        return
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    bank_data = data.get("banks", {})
    
    print("="*60)
    print("JP STOCK WEBAPP - TRADING BOT SIMULATOR")
    print("="*60)
    print(f"Initial Capital: {INITIAL_CAPITAL:,.0f} VND")
    print(f"Transaction Fee: {TRANSACTION_FEE*100:.2f}%")
    print(f"Sell Tax: {TAX_SELL*100:.2f}%")
    print(f"Banks in universe: {len(bank_data)}")
    
    results = {}
    
    for bot_id, config in BOT_CONFIGS.items():
        bot = TradingBOT(config, bank_data)
        report = bot.run_backtest()
        results[bot_id] = report
        
        # Print summary
        perf = report.get("performance", {})
        trades = report.get("trades", {})
        
        print(f"\n📊 {config.name}")
        print(f"   Total Return: {perf.get('total_return_percent', 0):+.1f}%")
        print(f"   CAGR: {perf.get('cagr_percent', 0):+.1f}%")
        print(f"   Max Drawdown: -{perf.get('max_drawdown_percent', 0):.1f}%")
        print(f"   Win Rate: {trades.get('win_rate_percent', 0):.0f}%")
        print(f"   Profit Factor: {trades.get('profit_factor', 0):.2f}")
        print(f"   Final Value: {perf.get('final_value', 0):,.0f} VND")
    
    # Save results
    output_file = "../docs/data/bot_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n✓ Results saved to {output_file}")
    
    # Print comparison table
    print("\n" + "="*80)
    print("COMPARISON TABLE")
    print("="*80)
    print(f"{'BOT':<25} {'Return':>10} {'CAGR':>8} {'MaxDD':>8} {'WinRate':>8} {'PF':>6}")
    print("-"*80)
    
    for bot_id, report in sorted(results.items(), 
                                  key=lambda x: x[1].get("performance", {}).get("total_return_percent", 0),
                                  reverse=True):
        perf = report.get("performance", {})
        trades = report.get("trades", {})
        name = report.get("bot_name", bot_id)[:24]
        
        print(f"{name:<25} {perf.get('total_return_percent', 0):>+9.1f}% "
              f"{perf.get('cagr_percent', 0):>+7.1f}% "
              f"{-perf.get('max_drawdown_percent', 0):>7.1f}% "
              f"{trades.get('win_rate_percent', 0):>7.0f}% "
              f"{trades.get('profit_factor', 0):>5.2f}")
    
    return results


if __name__ == "__main__":
    results = run_all_bots()
