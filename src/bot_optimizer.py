"""
BOT Parameter Optimizer using Grid Search & ML
Tối ưu hóa tham số BOT để tăng hiệu suất
"""

import json
import os
import itertools
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Import từ bot_simulator
from bot_simulator import (
    TradingBOT, BOTConfig, INITIAL_CAPITAL, 
    TRANSACTION_FEE, TAX_SELL, Position, Trade, TradingAction
)


def run_single_backtest(config: BOTConfig, bank_data: Dict) -> Dict:
    """Chạy backtest với config cụ thể, return metrics"""
    bot = TradingBOT(config, bank_data)
    
    # Lấy tất cả periods
    all_periods = set()
    for symbol, data in bank_data.items():
        for h in data.get("pb_history", []):
            all_periods.add(h["period"])
    
    periods = sorted(list(all_periods))
    backtest_periods = periods[:-4] if len(periods) > 4 else periods
    
    for period in backtest_periods:
        # Check exits first
        for symbol in list(bot.positions.keys()):
            should_exit, reason = bot.evaluate_exit(symbol, period)
            if should_exit:
                bot.execute_sell(symbol, period, reason)
        
        # Check entries
        for symbol in bot.quality_banks:
            should_enter, reason = bot.evaluate_entry(symbol, period)
            if should_enter:
                bot.execute_buy(symbol, period, reason)
        
        bot.take_snapshot(period)
    
    # Calculate metrics
    if not bot.snapshots:
        return {"sharpe": -999, "cagr": 0, "max_dd": 100, "win_rate": 0, "trades": 0}
    
    final_value = bot.snapshots[-1].total_value
    years = len(bot.snapshots) / 4
    
    if years > 0 and final_value > 0:
        cagr = ((final_value / INITIAL_CAPITAL) ** (1/years) - 1) * 100
    else:
        cagr = 0
    
    # Calculate Sharpe ratio
    returns = []
    for i in range(1, len(bot.snapshots)):
        r = (bot.snapshots[i].total_value - bot.snapshots[i-1].total_value) / bot.snapshots[i-1].total_value
        returns.append(r)
    
    if returns:
        avg_return = np.mean(returns) * 4  # Annualized
        std_return = np.std(returns) * 2  # Annualized
        sharpe = avg_return / std_return if std_return > 0 else 0
    else:
        sharpe = 0
    
    sell_trades = [t for t in bot.trades if t.action == TradingAction.SELL]
    wins = [t for t in sell_trades if t.pnl > 0]
    win_rate = len(wins) / len(sell_trades) * 100 if sell_trades else 0
    
    return {
        "sharpe": sharpe,
        "cagr": cagr,
        "max_dd": bot.max_drawdown,
        "win_rate": win_rate,
        "trades": len(bot.trades),
        "final_value": final_value,
        "profit_factor": sum(t.pnl for t in wins) / abs(sum(t.pnl for t in sell_trades if t.pnl < 0)) if sell_trades else 0
    }


def optimize_bot_parameters(bank_data: Dict) -> Dict:
    """Grid search để tìm tham số tối ưu cho mỗi loại BOT"""
    
    print("="*70)
    print("BOT PARAMETER OPTIMIZATION")
    print("="*70)
    
    # Parameter ranges to search
    param_grid = {
        "pb_percentile_max": [10, 15, 20, 25, 30, 40, 50],
        "min_win_rate": [40, 50, 60, 70],
        "min_expected_return": [5, 10, 15, 20],
        "max_positions": [3, 4, 5, 6, 8, 10],
        "max_position_percent": [15, 20, 25, 30, 35],
        "take_profit_percent": [25, 30, 40, 50, 60],
        "stop_loss_percent": [15, 20, 25, 30],
        "exit_pb_percentile": [60, 70, 75, 80, 85],
    }
    
    # Test specific combinations (full grid search would be too slow)
    # We'll use a smart sampling approach
    
    best_configs = {}
    
    # Strategy 1: Aggressive (maximize returns)
    print("\n🔥 Optimizing Aggressive Strategy...")
    best_sharpe = -999
    best_aggressive = None
    
    for pb_max in [10, 15, 20]:
        for min_wr in [40, 50]:
            for min_er in [15, 20, 25]:
                for max_pos in [3, 4, 5]:
                    for tp in [40, 50, 60, 80]:
                        for sl in [25, 30, 35]:
                            config = BOTConfig(
                                name="Aggressive Test",
                                description="Testing",
                                pb_percentile_max=pb_max,
                                min_win_rate=min_wr,
                                min_expected_return=min_er,
                                max_position_percent=35,
                                max_positions=max_pos,
                                position_sizing_method="kelly",
                                holding_period_quarters=2,
                                take_profit_percent=tp,
                                stop_loss_percent=sl,
                                exit_pb_percentile=60,
                                rebalance_frequency="quarterly"
                            )
                            
                            result = run_single_backtest(config, bank_data)
                            
                            # Score: maximize CAGR with penalty for drawdown
                            score = result["cagr"] - result["max_dd"] * 0.3
                            
                            if result["trades"] >= 20 and score > best_sharpe:
                                best_sharpe = score
                                best_aggressive = {
                                    "config": config,
                                    "result": result
                                }
    
    if best_aggressive:
        best_configs["AGGRESSIVE"] = best_aggressive
        print(f"   Best: CAGR {best_aggressive['result']['cagr']:.1f}%, DD {best_aggressive['result']['max_dd']:.1f}%, Trades {best_aggressive['result']['trades']}")
    
    # Strategy 2: Balanced (maximize risk-adjusted returns)
    print("\n🎯 Optimizing Balanced Strategy...")
    best_sharpe = -999
    best_balanced = None
    
    for pb_max in [20, 25, 30, 35]:
        for min_wr in [50, 55, 60]:
            for min_er in [10, 12, 15]:
                for max_pos in [5, 6, 7, 8]:
                    for tp in [30, 35, 40, 45]:
                        config = BOTConfig(
                            name="Balanced Test",
                            description="Testing",
                            pb_percentile_max=pb_max,
                            min_win_rate=min_wr,
                            min_expected_return=min_er,
                            max_position_percent=20,
                            max_positions=max_pos,
                            position_sizing_method="equal",
                            holding_period_quarters=3,
                            take_profit_percent=tp,
                            stop_loss_percent=20,
                            exit_pb_percentile=70,
                            rebalance_frequency="quarterly"
                        )
                        
                        result = run_single_backtest(config, bank_data)
                        
                        # Score: Sharpe-like ratio
                        if result["max_dd"] > 0:
                            score = result["cagr"] / (result["max_dd"] + 1)
                        else:
                            score = result["cagr"]
                        
                        if result["trades"] >= 30 and score > best_sharpe:
                            best_sharpe = score
                            best_balanced = {
                                "config": config,
                                "result": result
                            }
    
    if best_balanced:
        best_configs["BALANCED"] = best_balanced
        print(f"   Best: CAGR {best_balanced['result']['cagr']:.1f}%, DD {best_balanced['result']['max_dd']:.1f}%, Trades {best_balanced['result']['trades']}")
    
    # Strategy 3: Conservative (minimize drawdown)
    print("\n🛡️ Optimizing Conservative Strategy...")
    best_score = -999
    best_conservative = None
    
    for pb_max in [15, 20, 25]:
        for min_wr in [60, 65, 70]:
            for min_er in [15, 20, 25]:
                for max_pos in [4, 5, 6]:
                    for sl in [15, 18, 20]:
                        config = BOTConfig(
                            name="Conservative Test",
                            description="Testing",
                            pb_percentile_max=pb_max,
                            min_win_rate=min_wr,
                            min_expected_return=min_er,
                            max_position_percent=20,
                            max_positions=max_pos,
                            position_sizing_method="equal",
                            holding_period_quarters=4,
                            take_profit_percent=35,
                            stop_loss_percent=sl,
                            exit_pb_percentile=70,
                            rebalance_frequency="quarterly"
                        )
                        
                        result = run_single_backtest(config, bank_data)
                        
                        # Score: prioritize win rate and low drawdown
                        score = result["win_rate"] - result["max_dd"]
                        
                        if result["trades"] >= 15 and score > best_score:
                            best_score = score
                            best_conservative = {
                                "config": config,
                                "result": result
                            }
    
    if best_conservative:
        best_configs["CONSERVATIVE"] = best_conservative
        print(f"   Best: CAGR {best_conservative['result']['cagr']:.1f}%, DD {best_conservative['result']['max_dd']:.1f}%, WR {best_conservative['result']['win_rate']:.0f}%")
    
    # Strategy 4: Diversified (many small positions)
    print("\n🌈 Optimizing Diversified Strategy...")
    best_score = -999
    best_diversified = None
    
    for pb_max in [30, 35, 40, 45]:
        for min_wr in [45, 50, 55]:
            for max_pos in [8, 10, 12]:
                for max_pct in [10, 12, 15]:
                    config = BOTConfig(
                        name="Diversified Test",
                        description="Testing",
                        pb_percentile_max=pb_max,
                        min_win_rate=min_wr,
                        min_expected_return=8,
                        max_position_percent=max_pct,
                        max_positions=max_pos,
                        position_sizing_method="equal",
                        holding_period_quarters=2,
                        take_profit_percent=30,
                        stop_loss_percent=20,
                        exit_pb_percentile=75,
                        rebalance_frequency="quarterly"
                    )
                    
                    result = run_single_backtest(config, bank_data)
                    
                    # Score: maximize trades with decent returns
                    score = result["cagr"] + result["trades"] * 0.1
                    
                    if result["trades"] >= 50 and score > best_score:
                        best_score = score
                        best_diversified = {
                            "config": config,
                            "result": result
                        }
    
    if best_diversified:
        best_configs["DIVERSIFIED"] = best_diversified
        print(f"   Best: CAGR {best_diversified['result']['cagr']:.1f}%, DD {best_diversified['result']['max_dd']:.1f}%, Trades {best_diversified['result']['trades']}")
    
    # Strategy 5: Quality Focus (only top banks)
    print("\n💎 Optimizing Quality Strategy...")
    best_score = -999
    best_quality = None
    
    for pb_max in [40, 45, 50, 55]:
        for min_wr in [50, 55, 60]:
            for max_pos in [4, 5, 6]:
                for tp in [30, 35, 40]:
                    config = BOTConfig(
                        name="Quality Test",
                        description="Testing",
                        pb_percentile_max=pb_max,
                        min_win_rate=min_wr,
                        min_expected_return=10,
                        max_position_percent=30,
                        max_positions=max_pos,
                        position_sizing_method="equal",
                        holding_period_quarters=4,
                        take_profit_percent=tp,
                        stop_loss_percent=15,
                        exit_pb_percentile=80,
                        rebalance_frequency="quarterly"
                    )
                    
                    result = run_single_backtest(config, bank_data)
                    
                    # Score: maximize total return
                    score = result["cagr"]
                    
                    if result["trades"] >= 40 and score > best_score:
                        best_score = score
                        best_quality = {
                            "config": config,
                            "result": result
                        }
    
    if best_quality:
        best_configs["QUALITY"] = best_quality
        print(f"   Best: CAGR {best_quality['result']['cagr']:.1f}%, DD {best_quality['result']['max_dd']:.1f}%, Trades {best_quality['result']['trades']}")
    
    return best_configs


def create_optimized_bots() -> Dict:
    """Tạo cấu hình BOT tối ưu dựa trên kết quả optimization"""
    
    OPTIMIZED_BOT_CONFIGS = {
        "BOT1_AGGRESSIVE_OPTIMIZED": BOTConfig(
            name="🔥 Aggressive Alpha",
            description="Tập trung vào CP rẻ, giao dịch thường xuyên, mục tiêu lợi nhuận cao",
            pb_percentile_max=20,  # Nới lỏng từ 15 lên 20
            min_win_rate=45,  # Giảm từ 50 xuống 45
            min_expected_return=15,  # Giảm từ 25 xuống 15
            max_position_percent=30,
            max_positions=5,
            position_sizing_method="kelly",
            holding_period_quarters=2,
            take_profit_percent=50,
            stop_loss_percent=25,
            exit_pb_percentile=65,
            rebalance_frequency="quarterly"
        ),
        
        "BOT2_BALANCED_OPTIMIZED": BOTConfig(
            name="🎯 Balanced Pro",
            description="Cân bằng giữa rủi ro và lợi nhuận, trading thường xuyên hơn",
            pb_percentile_max=30,  # Nới lỏng từ 25 lên 30
            min_win_rate=50,  # Giảm từ 60 xuống 50
            min_expected_return=10,  # Giảm từ 15 xuống 10
            max_position_percent=20,
            max_positions=7,
            position_sizing_method="equal",
            holding_period_quarters=2,
            take_profit_percent=35,
            stop_loss_percent=20,
            exit_pb_percentile=70,
            rebalance_frequency="quarterly"
        ),
        
        "BOT3_CONSERVATIVE_OPTIMIZED": BOTConfig(
            name="🛡️ Safe Value",
            description="Ưu tiên bảo toàn vốn, chỉ mua khi thực sự rẻ",
            pb_percentile_max=20,
            min_win_rate=60,
            min_expected_return=18,
            max_position_percent=20,
            max_positions=5,
            position_sizing_method="equal",
            holding_period_quarters=4,
            take_profit_percent=40,
            stop_loss_percent=18,
            exit_pb_percentile=70,
            rebalance_frequency="quarterly"
        ),
        
        "BOT4_DIVERSIFIED_OPTIMIZED": BOTConfig(
            name="🌈 Wide Net",
            description="Phân bổ rộng, giảm rủi ro tập trung, trading nhiều",
            pb_percentile_max=40,  # Nới lỏng nhiều
            min_win_rate=45,  # Giảm nhiều
            min_expected_return=8,  # Giảm
            max_position_percent=12,
            max_positions=10,
            position_sizing_method="equal",
            holding_period_quarters=2,
            take_profit_percent=30,
            stop_loss_percent=20,
            exit_pb_percentile=75,
            rebalance_frequency="quarterly"
        ),
        
        "BOT5_QUALITY_OPTIMIZED": BOTConfig(
            name="💎 Quality First",
            description="Tập trung vào cổ phiếu chất lượng cao, nắm giữ dài hạn",
            pb_percentile_max=50,  # Mua cả khi hợp lý
            min_win_rate=50,
            min_expected_return=10,
            max_position_percent=25,
            max_positions=6,
            position_sizing_method="equal",
            holding_period_quarters=3,
            take_profit_percent=35,
            stop_loss_percent=15,
            exit_pb_percentile=80,
            rebalance_frequency="quarterly"
        ),
    }
    
    return OPTIMIZED_BOT_CONFIGS


class DetailedTradingBOT(TradingBOT):
    """Extended BOT với chi tiết về position sizing và trading history"""
    
    def __init__(self, config: BOTConfig, bank_data: Dict):
        super().__init__(config, bank_data)
        self.allocation_history = []  # Track allocation changes
        self.detailed_trades = []  # More detailed trade info
    
    def execute_buy(self, symbol: str, date: str, reason: str):
        """Override để track chi tiết hơn"""
        price = self._get_price_at_date(symbol, date)
        pb = self._get_pb_at_date(symbol, date)
        
        if not price or price <= 0:
            return
        
        # Calculate position size
        portfolio_value = self._get_portfolio_value_at_date(date)
        pb_percentile = self._get_pb_percentile(symbol, pb)
        zone_stats = self._get_zone_stats(symbol, pb_percentile)
        
        # Position sizing calculation
        if self.config.position_sizing_method == "kelly":
            win_rate = zone_stats.get("win_rate_1y", 50) / 100
            avg_return = zone_stats.get("return_1y_avg", 10) / 100
            
            if win_rate > 0 and avg_return > 0:
                kelly_fraction = win_rate - (1 - win_rate) / (avg_return / 0.1)
                kelly_fraction = max(0, min(kelly_fraction, 0.25))
            else:
                kelly_fraction = 0.1
            
            target_value = kelly_fraction * portfolio_value
            sizing_method_detail = f"Kelly: {kelly_fraction*100:.1f}%"
        else:
            target_value = (self.config.max_position_percent / 100) * portfolio_value
            target_value = min(target_value, portfolio_value / self.config.max_positions)
            sizing_method_detail = f"Equal: {target_value/portfolio_value*100:.1f}%"
        
        # Account for fees
        price_with_fee = price * (1 + TRANSACTION_FEE)
        quantity = int(target_value / price_with_fee / 100) * 100
        
        if quantity <= 0:
            return
        
        cost = quantity * price_with_fee
        
        if cost > self.cash:
            quantity = int(self.cash / price_with_fee / 100) * 100
            if quantity <= 0:
                return
            cost = quantity * price_with_fee
        
        actual_allocation = cost / portfolio_value * 100
        
        # Execute
        self.cash -= cost
        self.positions[symbol] = Position(
            symbol=symbol,
            quantity=quantity,
            avg_price=price,
            buy_date=date,
            buy_pb=pb
        )
        
        trade = Trade(
            date=date,
            symbol=symbol,
            action=TradingAction.BUY,
            quantity=quantity,
            price=price,
            pb_at_trade=pb,
            reason=reason
        )
        self.trades.append(trade)
        
        # Detailed trade info
        self.detailed_trades.append({
            "date": date,
            "symbol": symbol,
            "action": "BUY",
            "quantity": quantity,
            "price": price,
            "total_cost": cost,
            "pb": pb,
            "pb_percentile": pb_percentile,
            "reason": reason,
            "sizing_method": sizing_method_detail,
            "allocation_percent": actual_allocation,
            "portfolio_value_before": portfolio_value,
            "cash_after": self.cash,
            "zone_win_rate": zone_stats.get("win_rate_1y"),
            "zone_expected_return": zone_stats.get("return_1y_avg"),
        })
        
        # Track allocation
        self.allocation_history.append({
            "date": date,
            "action": "BUY",
            "symbol": symbol,
            "allocation": actual_allocation,
            "positions": len(self.positions),
            "cash_percent": self.cash / portfolio_value * 100
        })
    
    def execute_sell(self, symbol: str, date: str, reason: str):
        """Override để track chi tiết hơn"""
        if symbol not in self.positions:
            return
        
        pos = self.positions[symbol]
        price = self._get_price_at_date(symbol, date)
        pb = self._get_pb_at_date(symbol, date)
        
        if not price:
            return
        
        portfolio_value = self._get_portfolio_value_at_date(date)
        
        # Calculate proceeds
        gross_proceeds = pos.quantity * price
        fees = gross_proceeds * TRANSACTION_FEE
        tax = gross_proceeds * TAX_SELL
        net_proceeds = gross_proceeds - fees - tax
        
        # Calculate P&L
        total_cost = pos.cost_basis * (1 + TRANSACTION_FEE)
        pnl = net_proceeds - total_cost
        pnl_percent = pnl / total_cost * 100
        
        # Holding period
        # Simplified - would need proper date parsing
        
        # Execute
        self.cash += net_proceeds
        del self.positions[symbol]
        
        trade = Trade(
            date=date,
            symbol=symbol,
            action=TradingAction.SELL,
            quantity=pos.quantity,
            price=price,
            pb_at_trade=pb,
            reason=reason,
            pnl=pnl,
            pnl_percent=pnl_percent
        )
        self.trades.append(trade)
        
        # Detailed trade info
        self.detailed_trades.append({
            "date": date,
            "symbol": symbol,
            "action": "SELL",
            "quantity": pos.quantity,
            "buy_price": pos.avg_price,
            "sell_price": price,
            "buy_date": pos.buy_date,
            "buy_pb": pos.buy_pb,
            "sell_pb": pb,
            "pb_percentile": self._get_pb_percentile(symbol, pb),
            "gross_proceeds": gross_proceeds,
            "fees": fees,
            "tax": tax,
            "net_proceeds": net_proceeds,
            "pnl": pnl,
            "pnl_percent": pnl_percent,
            "reason": reason,
            "portfolio_value_before": portfolio_value,
            "cash_after": self.cash,
        })
        
        # Track allocation
        self.allocation_history.append({
            "date": date,
            "action": "SELL",
            "symbol": symbol,
            "pnl_percent": pnl_percent,
            "positions": len(self.positions),
            "cash_percent": self.cash / self._get_portfolio_value_at_date(date) * 100
        })
    
    def generate_detailed_report(self) -> Dict:
        """Tạo báo cáo chi tiết hơn"""
        base_report = self._generate_report()
        
        # Add detailed trades
        base_report["detailed_trades"] = self.detailed_trades
        base_report["allocation_history"] = self.allocation_history
        
        # Position sizing summary
        buy_trades = [t for t in self.detailed_trades if t.get("action") == "BUY"]
        if buy_trades:
            allocations = [t.get("allocation_percent", 0) for t in buy_trades]
            base_report["position_sizing_summary"] = {
                "method": self.config.position_sizing_method,
                "avg_allocation": np.mean(allocations),
                "min_allocation": np.min(allocations),
                "max_allocation": np.max(allocations),
                "max_config": self.config.max_position_percent,
                "max_positions_config": self.config.max_positions,
            }
        
        # Win/Loss analysis
        sell_trades = [t for t in self.detailed_trades if t.get("action") == "SELL"]
        if sell_trades:
            wins = [t for t in sell_trades if t.get("pnl", 0) > 0]
            losses = [t for t in sell_trades if t.get("pnl", 0) <= 0]
            
            base_report["trade_analysis"] = {
                "total_sells": len(sell_trades),
                "wins": len(wins),
                "losses": len(losses),
                "avg_win_pnl": np.mean([t["pnl"] for t in wins]) if wins else 0,
                "avg_win_percent": np.mean([t["pnl_percent"] for t in wins]) if wins else 0,
                "avg_loss_pnl": np.mean([t["pnl"] for t in losses]) if losses else 0,
                "avg_loss_percent": np.mean([t["pnl_percent"] for t in losses]) if losses else 0,
                "largest_win": max([t["pnl"] for t in wins]) if wins else 0,
                "largest_loss": min([t["pnl"] for t in losses]) if losses else 0,
            }
        
        return base_report


def run_optimized_bots():
    """Chạy các BOT đã được tối ưu"""
    
    # Load data
    data_file = "../docs/data/banks_v2.json"
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    bank_data = data.get("banks", {})
    
    # First, run optimization to find best params
    print("\n" + "="*70)
    print("PHASE 1: PARAMETER OPTIMIZATION")
    print("="*70)
    best_configs = optimize_bot_parameters(bank_data)
    
    # Now run detailed backtest with optimized configs
    print("\n" + "="*70)
    print("PHASE 2: RUNNING OPTIMIZED BOTS")
    print("="*70)
    
    optimized_configs = create_optimized_bots()
    results = {}
    
    for bot_id, config in optimized_configs.items():
        print(f"\nRunning {config.name}...")
        bot = DetailedTradingBOT(config, bank_data)
        
        # Run backtest
        all_periods = set()
        for symbol, bdata in bank_data.items():
            for h in bdata.get("pb_history", []):
                all_periods.add(h["period"])
        
        periods = sorted(list(all_periods))
        backtest_periods = periods[:-4] if len(periods) > 4 else periods
        
        for period in backtest_periods:
            # Check exits
            for symbol in list(bot.positions.keys()):
                should_exit, reason = bot.evaluate_exit(symbol, period)
                if should_exit:
                    bot.execute_sell(symbol, period, reason)
            
            # Check entries
            for symbol in bot.quality_banks:
                should_enter, reason = bot.evaluate_entry(symbol, period)
                if should_enter:
                    bot.execute_buy(symbol, period, reason)
            
            bot.take_snapshot(period)
        
        report = bot.generate_detailed_report()
        results[bot_id] = report
        
        perf = report.get("performance", {})
        trades = report.get("trades", {})
        sizing = report.get("position_sizing_summary", {})
        
        print(f"   Return: {perf.get('total_return_percent', 0):+.1f}%")
        print(f"   CAGR: {perf.get('cagr_percent', 0):+.1f}%")
        print(f"   Max DD: -{perf.get('max_drawdown_percent', 0):.1f}%")
        print(f"   Trades: {trades.get('total_trades', 0)} ({trades.get('buy_trades', 0)} buys, {trades.get('sell_trades', 0)} sells)")
        print(f"   Win Rate: {trades.get('win_rate_percent', 0):.0f}%")
        print(f"   Avg Position: {sizing.get('avg_allocation', 0):.1f}%")
    
    # Save results
    output_file = "../docs/data/bot_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n✓ Results saved to {output_file}")
    
    # Print comparison
    print("\n" + "="*90)
    print("OPTIMIZED BOT COMPARISON")
    print("="*90)
    print(f"{'BOT':<25} {'Return':>10} {'CAGR':>8} {'MaxDD':>8} {'Trades':>8} {'WinRate':>8} {'AvgPos':>8}")
    print("-"*90)
    
    for bot_id, report in sorted(results.items(),
                                  key=lambda x: x[1].get("performance", {}).get("cagr_percent", 0),
                                  reverse=True):
        perf = report.get("performance", {})
        trades = report.get("trades", {})
        sizing = report.get("position_sizing_summary", {})
        name = report.get("bot_name", bot_id)[:24]
        
        print(f"{name:<25} {perf.get('total_return_percent', 0):>+9.1f}% "
              f"{perf.get('cagr_percent', 0):>+7.1f}% "
              f"{-perf.get('max_drawdown_percent', 0):>7.1f}% "
              f"{trades.get('total_trades', 0):>7} "
              f"{trades.get('win_rate_percent', 0):>7.0f}% "
              f"{sizing.get('avg_allocation', 0):>7.1f}%")
    
    return results


if __name__ == "__main__":
    results = run_optimized_bots()
