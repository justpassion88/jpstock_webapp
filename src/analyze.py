"""
P/B Analysis Engine
Phân tích định lượng P/B dựa trên dữ liệu lịch sử
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

from config import (
    BANK_SYMBOLS, 
    BANK_NAMES,
    OUTPUT_DIR, 
    OUTPUT_FILE,
    PERCENTILE_THRESHOLDS,
    VALUATION_ZONES
)


def load_raw_data(filename: str = "raw_bank_data.json") -> Optional[Dict]:
    """Load raw data từ file JSON"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    if not os.path.exists(filepath):
        print(f"✗ File not found: {filepath}")
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_pb_statistics(pb_history: List[Dict]) -> Dict:
    """
    Tính toán thống kê P/B từ lịch sử
    
    Args:
        pb_history: List of {year, pb} dicts
    
    Returns:
        Dict với các thống kê: mean, std, min, max, percentiles
    """
    if not pb_history or len(pb_history) < 3:
        return None
    
    pb_values = [item["pb"] for item in pb_history if item.get("pb") is not None]
    
    if len(pb_values) < 3:
        return None
    
    pb_array = np.array(pb_values)
    
    return {
        "count": len(pb_values),
        "years_of_data": len(pb_history),
        "mean": float(np.mean(pb_array)),
        "median": float(np.median(pb_array)),
        "std": float(np.std(pb_array)),
        "min": float(np.min(pb_array)),
        "max": float(np.max(pb_array)),
        "percentile_10": float(np.percentile(pb_array, 10)),
        "percentile_25": float(np.percentile(pb_array, 25)),
        "percentile_50": float(np.percentile(pb_array, 50)),
        "percentile_75": float(np.percentile(pb_array, 75)),
        "percentile_90": float(np.percentile(pb_array, 90)),
    }


def determine_valuation_zone(current_pb: float, pb_history: List[Dict]) -> Dict:
    """
    Xác định vùng định giá dựa trên percentile của P/B hiện tại
    
    Args:
        current_pb: P/B hiện tại
        pb_history: Lịch sử P/B
    
    Returns:
        Dict với zone, percentile, label, signal, color
    """
    if not pb_history or current_pb is None:
        return {
            "zone": "UNKNOWN",
            "percentile": None,
            "label": "Không có dữ liệu",
            "signal": "N/A",
            "color": "#9ca3af"
        }
    
    pb_values = [item["pb"] for item in pb_history if item.get("pb") is not None]
    
    if len(pb_values) < 3:
        return {
            "zone": "UNKNOWN",
            "percentile": None,
            "label": "Thiếu dữ liệu",
            "signal": "N/A",
            "color": "#9ca3af"
        }
    
    # Tính percentile của P/B hiện tại so với lịch sử
    percentile = float(stats.percentileofscore(pb_values, current_pb))
    
    # Xác định zone
    if percentile < PERCENTILE_THRESHOLDS["extremely_cheap"]:
        zone = "EXTREMELY_CHEAP"
    elif percentile < PERCENTILE_THRESHOLDS["cheap"]:
        zone = "CHEAP"
    elif percentile < PERCENTILE_THRESHOLDS["fair_high"]:
        zone = "FAIR"
    elif percentile < PERCENTILE_THRESHOLDS["expensive"]:
        zone = "EXPENSIVE"
    else:
        zone = "EXTREMELY_EXPENSIVE"
    
    zone_info = VALUATION_ZONES[zone]
    
    return {
        "zone": zone,
        "percentile": round(percentile, 1),
        "label": zone_info["label"],
        "signal": zone_info["signal"],
        "color": zone_info["color"]
    }


def calculate_expected_return(current_pb: float, pb_stats: Dict) -> Dict:
    """
    Tính expected return dựa trên mean reversion
    
    Args:
        current_pb: P/B hiện tại
        pb_stats: Thống kê P/B
    
    Returns:
        Dict với expected_return, return_to_mean, return_to_median
    """
    if not pb_stats or current_pb is None or current_pb <= 0:
        return {
            "return_to_mean": None,
            "return_to_median": None,
            "expected_return": None,
            "confidence": "N/A"
        }
    
    mean_pb = pb_stats["mean"]
    median_pb = pb_stats["median"]
    
    # Return nếu P/B về mean
    return_to_mean = ((mean_pb / current_pb) - 1) * 100
    
    # Return nếu P/B về median
    return_to_median = ((median_pb / current_pb) - 1) * 100
    
    # Confidence dựa trên percentile
    percentile = stats.percentileofscore(
        [pb_stats["percentile_10"], pb_stats["percentile_25"], 
         pb_stats["percentile_50"], pb_stats["percentile_75"], 
         pb_stats["percentile_90"]], 
        current_pb
    )
    
    # Probability factor dựa trên vị trí so với mean
    if current_pb < pb_stats["percentile_25"]:
        probability = 0.7
        confidence = "Cao"
    elif current_pb < pb_stats["percentile_50"]:
        probability = 0.5
        confidence = "Trung bình"
    elif current_pb < pb_stats["percentile_75"]:
        probability = 0.3
        confidence = "Thấp"
    else:
        probability = 0.2
        confidence = "Rất thấp"
    
    expected_return = return_to_median * probability
    
    return {
        "return_to_mean": round(return_to_mean, 2),
        "return_to_median": round(return_to_median, 2),
        "expected_return": round(expected_return, 2),
        "probability": probability,
        "confidence": confidence
    }


def calculate_risk_score(current_pb: float, pb_stats: Dict) -> Dict:
    """
    Tính risk score dựa trên P/B
    
    Args:
        current_pb: P/B hiện tại
        pb_stats: Thống kê P/B
    
    Returns:
        Dict với risk_score, risk_level, description
    """
    if not pb_stats or current_pb is None:
        return {
            "risk_score": None,
            "risk_level": "UNKNOWN",
            "description": "Không có dữ liệu"
        }
    
    mean_pb = pb_stats["mean"]
    std_pb = pb_stats["std"]
    
    if std_pb == 0:
        return {
            "risk_score": 0,
            "risk_level": "LOW",
            "description": "Độ biến động thấp"
        }
    
    # Z-score của P/B hiện tại
    z_score = (current_pb - mean_pb) / std_pb
    
    # Risk score: cao hơn mean = risk cao hơn
    # Normalize về thang 0-100
    risk_score = min(100, max(0, 50 + z_score * 25))
    
    # Risk level
    if risk_score < 25:
        risk_level = "VERY_LOW"
        description = "Rủi ro rất thấp - P/B dưới trung bình đáng kể"
    elif risk_score < 40:
        risk_level = "LOW"
        description = "Rủi ro thấp - P/B dưới trung bình"
    elif risk_score < 60:
        risk_level = "MEDIUM"
        description = "Rủi ro trung bình - P/B gần mức trung bình"
    elif risk_score < 75:
        risk_level = "HIGH"
        description = "Rủi ro cao - P/B trên trung bình"
    else:
        risk_level = "VERY_HIGH"
        description = "Rủi ro rất cao - P/B cao hơn trung bình đáng kể"
    
    return {
        "risk_score": round(risk_score, 1),
        "z_score": round(z_score, 2),
        "risk_level": risk_level,
        "description": description
    }


def calculate_mean_reversion_metrics(pb_history: List[Dict]) -> Dict:
    """
    Tính toán các metrics về mean reversion
    
    Args:
        pb_history: Lịch sử P/B
    
    Returns:
        Dict với half_life, reversion_speed, etc.
    """
    if not pb_history or len(pb_history) < 5:
        return {
            "half_life_years": None,
            "reversion_speed": None,
            "ar1_coefficient": None
        }
    
    # Sort by year
    sorted_history = sorted(pb_history, key=lambda x: x["year"])
    pb_values = [item["pb"] for item in sorted_history if item.get("pb") is not None]
    
    if len(pb_values) < 5:
        return {
            "half_life_years": None,
            "reversion_speed": None,
            "ar1_coefficient": None
        }
    
    try:
        # AR(1) regression: pb_t = alpha + beta * pb_{t-1}
        pb_lag = np.array(pb_values[:-1])
        pb_current = np.array(pb_values[1:])
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(pb_lag, pb_current)
        
        # Half-life calculation
        if 0 < slope < 1:
            half_life = -np.log(2) / np.log(slope)
        else:
            half_life = None
        
        reversion_speed = 1 - slope if slope < 1 else 0
        
        return {
            "half_life_years": round(half_life, 2) if half_life else None,
            "reversion_speed": round(reversion_speed, 3),
            "ar1_coefficient": round(slope, 3),
            "r_squared": round(r_value ** 2, 3)
        }
    except Exception as e:
        print(f"    Error calculating mean reversion: {e}")
        return {
            "half_life_years": None,
            "reversion_speed": None,
            "ar1_coefficient": None
        }


def analyze_single_bank(bank_data: Dict) -> Dict:
    """
    Phân tích đầy đủ cho một ngân hàng
    
    Args:
        bank_data: Raw data của ngân hàng
    
    Returns:
        Dict với kết quả phân tích đầy đủ
    """
    symbol = bank_data.get("symbol", "")
    pb_history = bank_data.get("pb_history", [])
    
    # Current P/B (lấy từ năm gần nhất trong lịch sử)
    current_pb = None
    if pb_history:
        sorted_history = sorted(pb_history, key=lambda x: x.get("year", 0), reverse=True)
        current_pb = sorted_history[0].get("pb") if sorted_history else None
    
    # Statistics
    pb_stats = calculate_pb_statistics(pb_history)
    
    # Valuation zone
    valuation = determine_valuation_zone(current_pb, pb_history)
    
    # Expected return
    expected_return = calculate_expected_return(current_pb, pb_stats)
    
    # Risk score
    risk = calculate_risk_score(current_pb, pb_stats)
    
    # Mean reversion metrics
    mean_reversion = calculate_mean_reversion_metrics(pb_history)
    
    return {
        "symbol": symbol,
        "name": bank_data.get("name", BANK_NAMES.get(symbol, symbol)),
        "current_price": bank_data.get("current_price"),
        "current_pb": current_pb,
        "pb_history": pb_history,
        "pb_statistics": pb_stats,
        "valuation": valuation,
        "expected_return": expected_return,
        "risk": risk,
        "mean_reversion": mean_reversion,
        "data_quality": {
            "has_price_data": bank_data.get("price_history") is not None,
            "has_pb_data": pb_history is not None and len(pb_history) > 0,
            "years_of_pb_data": len(pb_history) if pb_history else 0
        }
    }


def analyze_all_banks(raw_data: Dict) -> Dict:
    """
    Phân tích tất cả ngân hàng
    
    Args:
        raw_data: Raw data từ fetch_data.py
    
    Returns:
        Dict với kết quả phân tích tất cả ngân hàng
    """
    results = {
        "last_updated": datetime.now().isoformat(),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_banks": len(BANK_SYMBOLS),
        "banks": [],
        "summary": {
            "extremely_cheap": [],
            "cheap": [],
            "fair": [],
            "expensive": [],
            "extremely_expensive": [],
            "no_data": []
        }
    }
    
    banks_data = raw_data.get("banks", {})
    
    for symbol in BANK_SYMBOLS:
        bank_data = banks_data.get(symbol, {"symbol": symbol, "name": BANK_NAMES.get(symbol, symbol)})
        
        print(f"Analyzing {symbol}...")
        analysis = analyze_single_bank(bank_data)
        results["banks"].append(analysis)
        
        # Categorize by valuation zone
        zone = analysis["valuation"]["zone"]
        if zone == "EXTREMELY_CHEAP":
            results["summary"]["extremely_cheap"].append(symbol)
        elif zone == "CHEAP":
            results["summary"]["cheap"].append(symbol)
        elif zone == "FAIR":
            results["summary"]["fair"].append(symbol)
        elif zone == "EXPENSIVE":
            results["summary"]["expensive"].append(symbol)
        elif zone == "EXTREMELY_EXPENSIVE":
            results["summary"]["extremely_expensive"].append(symbol)
        else:
            results["summary"]["no_data"].append(symbol)
    
    # Sort banks by expected return (highest first)
    results["banks"].sort(
        key=lambda x: x["expected_return"]["expected_return"] or -999,
        reverse=True
    )
    
    return results


def save_analysis_results(results: Dict, filename: str = None):
    """
    Lưu kết quả phân tích vào file JSON
    
    Args:
        results: Dict kết quả phân tích
        filename: Tên file output
    """
    if filename is None:
        filename = OUTPUT_FILE
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Saved analysis results to {filepath}")


def main():
    """Main function"""
    print("=" * 60)
    print("JP Stock Webapp - P/B Analysis Engine")
    print("=" * 60)
    
    # Load raw data
    print("\nLoading raw data...")
    raw_data = load_raw_data()
    
    if not raw_data:
        print("✗ No raw data found. Please run fetch_data.py first.")
        return
    
    # Analyze all banks
    print("\nAnalyzing banks...")
    results = analyze_all_banks(raw_data)
    
    # Save results
    save_analysis_results(results)
    
    # Print summary
    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Total banks analyzed: {results['total_banks']}")
    print(f"\nValuation Distribution:")
    print(f"  🟢 Cực rẻ (Strong Buy): {len(results['summary']['extremely_cheap'])} - {results['summary']['extremely_cheap']}")
    print(f"  🟢 Rẻ (Buy): {len(results['summary']['cheap'])} - {results['summary']['cheap']}")
    print(f"  ⚪ Hợp lý (Hold): {len(results['summary']['fair'])} - {results['summary']['fair']}")
    print(f"  🟠 Đắt (Sell): {len(results['summary']['expensive'])} - {results['summary']['expensive']}")
    print(f"  🔴 Cực đắt (Strong Sell): {len(results['summary']['extremely_expensive'])} - {results['summary']['extremely_expensive']}")
    print(f"  ⚫ Không có dữ liệu: {len(results['summary']['no_data'])} - {results['summary']['no_data']}")
    
    print("\n" + "=" * 60)
    print("Analysis completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
