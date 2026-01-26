"""
BOT Recommendation Generator
Tạo khuyến nghị mua/bán dựa trên các BOT strategies
Dùng cho danh mục thực
"""

import json
import os
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass
from bot_optimizer import create_optimized_bots

@dataclass
class Recommendation:
    symbol: str
    action: str  # "BUY", "SELL", "HOLD"
    strength: str  # "STRONG", "MODERATE", "WEAK"
    bots_agree: List[str]
    reasons: List[str]
    target_allocation: float  # % of portfolio
    current_pb: float
    pb_percentile: float
    expected_return: float
    win_rate: float


def generate_recommendations():
    """Tạo khuyến nghị dựa trên consensus của các BOT"""
    
    # Load data
    data_file = "../docs/data/banks_v2.json"
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    bank_data = data.get("banks", {})
    
    recommendations = {
        "generated_at": datetime.now().isoformat(),
        "buy_signals": [],
        "sell_signals": [],
        "hold_signals": [],
        "bot_allocations": {},
        "market_summary": {}
    }
    
    # Get optimized BOT configs
    BOT_CONFIGS = create_optimized_bots()
    
    # Evaluate each symbol with current data directly
    for bot_id, config in BOT_CONFIGS.items():
        buy_signals = []
        
        for symbol, bank in bank_data.items():
            # Check data quality
            pb_stats = bank.get("pb_statistics", {})
            hist_returns = bank.get("historical_returns", {})
            
            if pb_stats.get("count", 0) < 20:  # At least 5 years
                continue
            
            current_pb = bank.get("current_pb")
            if not current_pb:
                continue
            
            # Get valuation info directly from analyzed data
            valuation = bank.get("valuation", {})
            pb_percentile = valuation.get("percentile", 50)
            
            # Check entry conditions
            if pb_percentile > config.pb_percentile_max:
                continue
            
            # Get zone stats
            zone = valuation.get("zone", "fair")
            zone_stats = hist_returns.get(zone, {})
            
            win_rate = zone_stats.get("win_rate_1y", 0) or 0
            expected_return = zone_stats.get("return_1y_avg", 0) or 0
            
            if win_rate < config.min_win_rate:
                continue
            
            if expected_return < config.min_expected_return:
                continue
            
            # This symbol passes all criteria
            buy_signals.append({
                "symbol": symbol,
                "reason": f"P/B P{pb_percentile:.0f}, WR {win_rate:.0f}%, ER {expected_return:.1f}%",
                "bot": config.name
            })
        
        recommendations["bot_allocations"][bot_id] = {
            "name": config.name,
            "buy_signals": buy_signals,
            "config": {
                "pb_max": config.pb_percentile_max,
                "min_wr": config.min_win_rate,
                "max_pos": config.max_positions
            }
        }
    
    # Aggregate signals
    symbol_signals = {}
    
    for bot_id, bot_data in recommendations["bot_allocations"].items():
        for signal in bot_data["buy_signals"]:
            symbol = signal["symbol"]
            if symbol not in symbol_signals:
                symbol_signals[symbol] = {
                    "bots": [],
                    "reasons": []
                }
            symbol_signals[symbol]["bots"].append(bot_data["name"])
            symbol_signals[symbol]["reasons"].append(signal["reason"])
    
    # Create final recommendations
    for symbol, signals in symbol_signals.items():
        bank = bank_data.get(symbol, {})
        valuation = bank.get("valuation", {})
        expected = bank.get("expected_return", {})
        
        num_bots = len(signals["bots"])
        
        if num_bots >= 4:
            strength = "STRONG"
        elif num_bots >= 2:
            strength = "MODERATE"
        else:
            strength = "WEAK"
        
        rec = {
            "symbol": symbol,
            "name": bank.get("name", symbol),
            "action": "BUY",
            "strength": strength,
            "bots_agree": num_bots,
            "bot_names": signals["bots"],
            "reasons": list(set(signals["reasons"])),
            "current_pb": bank.get("current_pb"),
            "current_price": bank.get("current_price"),
            "pb_percentile": valuation.get("percentile"),
            "zone": valuation.get("zone_vi"),
            "expected_return_1y": expected.get("expected_1y"),
            "win_rate_1y": expected.get("win_rate_1y"),
        }
        
        recommendations["buy_signals"].append(rec)
    
    # Sort by number of agreeing bots
    recommendations["buy_signals"].sort(key=lambda x: x["bots_agree"], reverse=True)
    
    # Market summary
    total_banks = len(bank_data)
    cheap_banks = sum(1 for b in bank_data.values() 
                      if b.get("valuation", {}).get("percentile", 100) < 25)
    expensive_banks = sum(1 for b in bank_data.values() 
                         if b.get("valuation", {}).get("percentile", 0) > 75)
    
    recommendations["market_summary"] = {
        "total_banks": total_banks,
        "cheap_banks": cheap_banks,
        "fair_banks": total_banks - cheap_banks - expensive_banks,
        "expensive_banks": expensive_banks,
        "buy_opportunities": len(recommendations["buy_signals"]),
        "strong_buys": len([r for r in recommendations["buy_signals"] if r["strength"] == "STRONG"])
    }
    
    # Save
    output_file = "../docs/data/recommendations.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(recommendations, f, ensure_ascii=False, indent=2)
    
    print("="*60)
    print("BOT RECOMMENDATIONS")
    print("="*60)
    print(f"Generated: {recommendations['generated_at']}")
    print(f"\nMarket Summary:")
    print(f"  - Cheap banks (P<25): {cheap_banks}")
    print(f"  - Fair banks: {total_banks - cheap_banks - expensive_banks}")
    print(f"  - Expensive banks (P>75): {expensive_banks}")
    print(f"\nBuy Signals: {len(recommendations['buy_signals'])}")
    
    print("\n" + "="*60)
    print("TOP RECOMMENDATIONS")
    print("="*60)
    
    for rec in recommendations["buy_signals"][:10]:
        print(f"\n{rec['strength']} BUY: {rec['symbol']} ({rec['name']})")
        print(f"  P/B: {rec['current_pb']:.2f} (P{rec['pb_percentile']:.0f}) - {rec['zone']}")
        print(f"  Expected 1Y: {rec['expected_return_1y']:.1f}% | Win Rate: {rec['win_rate_1y']:.0f}%")
        print(f"  Agreed by {rec['bots_agree']}/5 BOTs: {', '.join(rec['bot_names'][:3])}")
    
    print(f"\n✓ Saved to {output_file}")
    
    return recommendations


if __name__ == "__main__":
    generate_recommendations()
