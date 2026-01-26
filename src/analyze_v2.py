"""
Analyze Module V2 - Phân tích P/B kết hợp với lợi nhuận lịch sử
Tính toán dựa trên dữ liệu thực tế, không dựa trên giả định
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
import numpy as np
from scipy import stats

from config import BANK_SYMBOLS, BANK_NAMES, PERCENTILE_THRESHOLDS, OUTPUT_DIR


def calculate_pb_statistics_v2(quarterly_data: List[Dict]) -> Dict:
    """Tính toán thống kê P/B từ dữ liệu quý"""
    if not quarterly_data:
        return {}
    
    pb_values = [q["pb"] for q in quarterly_data if q.get("pb")]
    
    if not pb_values:
        return {}
    
    stats_result = {
        "count": len(pb_values),
        "years_of_data": len(pb_values) / 4,
        "min": float(np.min(pb_values)),
        "max": float(np.max(pb_values)),
        "mean": float(np.mean(pb_values)),
        "median": float(np.median(pb_values)),
        "std": float(np.std(pb_values)),
        "percentile_10": float(np.percentile(pb_values, 10)),
        "percentile_25": float(np.percentile(pb_values, 25)),
        "percentile_50": float(np.percentile(pb_values, 50)),
        "percentile_75": float(np.percentile(pb_values, 75)),
        "percentile_90": float(np.percentile(pb_values, 90)),
    }
    
    return stats_result


def determine_valuation_zone_v2(current_pb: float, quarterly_data: List[Dict]) -> Dict:
    """
    Xác định vùng định giá dựa trên percentile thực tế
    
    Returns:
        Dict với zone, percentile, score, description
    """
    if not current_pb or not quarterly_data:
        return {"zone": "unknown", "percentile": None}
    
    pb_values = [q["pb"] for q in quarterly_data if q.get("pb")]
    
    # Tính percentile của giá trị hiện tại
    percentile = stats.percentileofscore(pb_values, current_pb)
    
    # Map to zone
    if percentile < PERCENTILE_THRESHOLDS["extremely_cheap"]:
        zone = "extremely_cheap"
        zone_vi = "CỰC RẺ"
        color = "#10B981"  # green
        score = 10
    elif percentile < PERCENTILE_THRESHOLDS["cheap"]:
        zone = "cheap"
        zone_vi = "RẺ"
        color = "#34D399"  # light green
        score = 8
    elif percentile < PERCENTILE_THRESHOLDS["fair_high"]:
        zone = "fair"
        zone_vi = "HỢP LÝ"
        color = "#FBBF24"  # yellow
        score = 5
    elif percentile < PERCENTILE_THRESHOLDS["expensive"]:
        zone = "expensive"
        zone_vi = "ĐẮT"
        color = "#F97316"  # orange
        score = 3
    else:
        zone = "extremely_expensive"
        zone_vi = "CỰC ĐẮT"
        color = "#EF4444"  # red
        score = 1
    
    return {
        "zone": zone,
        "zone_vi": zone_vi,
        "percentile": round(percentile, 1),
        "score": score,
        "color": color,
        "description": f"P/B hiện tại ở percentile {percentile:.1f}% so với lịch sử"
    }


def calculate_expected_return_v2(
    current_pb: float, 
    historical_returns: Dict, 
    valuation: Dict
) -> Dict:
    """
    Tính kỳ vọng lợi nhuận dựa trên BACKTEST lịch sử thực tế
    Không còn dựa trên công thức lý thuyết!
    """
    zone = valuation.get("zone", "unknown")
    
    if zone not in historical_returns:
        return {
            "expected_1y": None,
            "expected_2y": None,
            "win_rate_1y": None,
            "method": "insufficient_data"
        }
    
    zone_data = historical_returns[zone]
    
    return {
        "expected_1y": zone_data.get("return_1y_avg"),
        "expected_1y_median": zone_data.get("return_1y_median"),
        "expected_1y_min": zone_data.get("return_1y_min"),
        "expected_1y_max": zone_data.get("return_1y_max"),
        "expected_2y": zone_data.get("return_2y_avg"),
        "win_rate_1y": zone_data.get("win_rate_1y"),
        "win_rate_2y": zone_data.get("win_rate_2y"),
        "sample_count": zone_data.get("count", 0),
        "method": "historical_backtest"
    }


def calculate_risk_v2(valuation: Dict, historical_returns: Dict) -> Dict:
    """Tính rủi ro dựa trên vùng định giá và win rate lịch sử"""
    zone = valuation.get("zone", "unknown")
    
    # Base risk by zone
    zone_risk = {
        "extremely_cheap": 1,
        "cheap": 2,
        "fair": 4,
        "expensive": 7,
        "extremely_expensive": 9,
        "unknown": 5
    }
    
    base_risk = zone_risk.get(zone, 5)
    
    # Adjust by win rate
    win_rate = historical_returns.get(zone, {}).get("win_rate_1y")
    if win_rate:
        if win_rate >= 80:
            risk_adjustment = -1
        elif win_rate >= 60:
            risk_adjustment = 0
        elif win_rate >= 40:
            risk_adjustment = 1
        else:
            risk_adjustment = 2
        
        adjusted_risk = max(1, min(10, base_risk + risk_adjustment))
    else:
        adjusted_risk = base_risk
    
    # Risk descriptions
    if adjusted_risk <= 3:
        level = "LOW"
        level_vi = "THẤP"
        description = "Rủi ro thấp, lịch sử cho thấy tỷ lệ thắng cao"
    elif adjusted_risk <= 6:
        level = "MEDIUM"
        level_vi = "TRUNG BÌNH"
        description = "Rủi ro trung bình, cần theo dõi"
    else:
        level = "HIGH"
        level_vi = "CAO"
        description = "Rủi ro cao, cần cẩn trọng"
    
    return {
        "score": adjusted_risk,
        "level": level,
        "level_vi": level_vi,
        "description": description
    }


def analyze_single_bank(bank_data: Dict) -> Dict:
    """Phân tích hoàn chỉnh cho một ngân hàng"""
    result = {
        "symbol": bank_data["symbol"],
        "name": bank_data["name"],
        "current_price": bank_data.get("current_price"),
        "current_pb": bank_data.get("current_pb"),
        "last_updated": datetime.now().isoformat(),
    }
    
    quarterly_data = bank_data.get("quarterly_data", [])
    historical_returns = bank_data.get("historical_returns", {})
    
    if not quarterly_data:
        result["status"] = "no_data"
        return result
    
    # P/B Statistics
    result["pb_statistics"] = calculate_pb_statistics_v2(quarterly_data)
    
    # Valuation zone
    current_pb = bank_data.get("current_pb")
    if current_pb:
        result["valuation"] = determine_valuation_zone_v2(current_pb, quarterly_data)
    else:
        result["valuation"] = {"zone": "unknown"}
    
    # Expected returns based on historical backtest
    result["expected_return"] = calculate_expected_return_v2(
        current_pb, historical_returns, result["valuation"]
    )
    
    # Risk assessment
    result["risk"] = calculate_risk_v2(result["valuation"], historical_returns)
    
    # Historical returns by zone
    result["historical_returns"] = historical_returns
    
    # Recent quarterly data (last 3 years = 12 quarters)
    result["quarterly_data"] = quarterly_data[-12:] if len(quarterly_data) >= 12 else quarterly_data
    
    # All P/B history for chart
    result["pb_history"] = [
        {"period": q["period"], "pb": q["pb"], "price": q.get("price")}
        for q in quarterly_data
    ]
    
    # Status
    result["status"] = "ok"
    
    return result


def analyze_all_banks(raw_data: Dict) -> Dict:
    """Phân tích tất cả ngân hàng"""
    analyzed = {
        "last_updated": datetime.now().isoformat(),
        "data_type": "quarterly_backtest",
        "total_banks": 0,
        "banks": {}
    }
    
    banks_data = raw_data.get("banks", {})
    
    for symbol, bank_data in banks_data.items():
        print(f"Analyzing {symbol}...")
        analysis = analyze_single_bank(bank_data)
        analyzed["banks"][symbol] = analysis
        
        # Print summary
        if analysis.get("valuation"):
            val = analysis["valuation"]
            exp_ret = analysis.get("expected_return", {})
            print(f"  → {val.get('zone_vi', 'N/A')} (P{val.get('percentile', '?'):.0f})")
            if exp_ret.get("expected_1y"):
                print(f"  → Kỳ vọng 1Y: {exp_ret['expected_1y']:.1f}% | Win rate: {exp_ret.get('win_rate_1y', 0):.0f}%")
    
    analyzed["total_banks"] = len(analyzed["banks"])
    
    return analyzed


def save_analysis(data: Dict, filename: str = "banks_v2.json"):
    """Lưu kết quả phân tích"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Analysis saved to {filepath}")


def main():
    print("=" * 60)
    print("JP Stock Webapp - Bank Analysis V2 (Historical Backtest)")
    print("=" * 60)
    
    # Load raw data
    raw_file = os.path.join(OUTPUT_DIR, "raw_bank_data_v2.json")
    
    if not os.path.exists(raw_file):
        print(f"✗ Raw data file not found: {raw_file}")
        print("Please run fetch_data_v2.py first")
        return
    
    with open(raw_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    print(f"\nLoaded {len(raw_data.get('banks', {}))} banks from {raw_file}")
    
    # Analyze
    analysis = analyze_all_banks(raw_data)
    
    # Save
    save_analysis(analysis)
    
    print("\n" + "=" * 60)
    print("Analysis completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
