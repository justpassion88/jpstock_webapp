"""
Banking Sector Heat Index
Đo lường độ nóng/lạnh của ngành ngân hàng dựa trên P/B
"""

import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple


def calculate_sector_heat(bank_data: Dict, current_period: str = None) -> Dict:
    """
    Tính chỉ số nhiệt độ ngành ngân hàng
    
    Returns:
        heat_index: 0-100 (0=cực lạnh/panic, 50=bình thường, 100=cực nóng/bubble)
        status: "ICE_COLD", "COLD", "COOL", "NEUTRAL", "WARM", "HOT", "OVERHEATED"
    """
    
    # Collect current P/B percentiles
    pb_percentiles = []
    pb_values = []
    
    for symbol, data in bank_data.items():
        valuation = data.get("valuation", {})
        percentile = valuation.get("percentile")
        current_pb = data.get("current_pb")
        
        if percentile is not None:
            pb_percentiles.append(percentile)
        if current_pb is not None:
            pb_values.append(current_pb)
    
    if not pb_percentiles:
        return {"heat_index": 50, "status": "NEUTRAL"}
    
    # Calculate metrics
    avg_percentile = np.mean(pb_percentiles)
    median_percentile = np.median(pb_percentiles)
    
    # Count extremes
    very_cheap = sum(1 for p in pb_percentiles if p < 20)  # P/B < P20
    cheap = sum(1 for p in pb_percentiles if p < 35)
    expensive = sum(1 for p in pb_percentiles if p > 65)
    very_expensive = sum(1 for p in pb_percentiles if p > 80)  # P/B > P80
    
    total_banks = len(pb_percentiles)
    
    # Heat Index calculation
    # Base: average percentile (0-100)
    heat_index = avg_percentile
    
    # Adjust for extreme concentration
    if very_expensive / total_banks > 0.5:  # >50% very expensive
        heat_index = min(100, heat_index + 15)
    elif expensive / total_banks > 0.6:  # >60% expensive
        heat_index = min(100, heat_index + 10)
    
    if very_cheap / total_banks > 0.5:  # >50% very cheap
        heat_index = max(0, heat_index - 15)
    elif cheap / total_banks > 0.6:  # >60% cheap
        heat_index = max(0, heat_index - 10)
    
    # Determine status
    if heat_index >= 85:
        status = "🔥 OVERHEATED"
        signal = "SELL_ALL"
        description = "Thị trường cực nóng! Nguy cơ bong bóng. Nên chốt lời và giữ tiền mặt."
        color = "#EF4444"  # Red
    elif heat_index >= 70:
        status = "🌡️ HOT"
        signal = "REDUCE"
        description = "Thị trường nóng. Cân nhắc chốt lời một phần, không mua thêm."
        color = "#F97316"  # Orange
    elif heat_index >= 55:
        status = "☀️ WARM"
        signal = "HOLD"
        description = "Thị trường hơi nóng. Giữ vị thế, thận trọng khi mua thêm."
        color = "#EAB308"  # Yellow
    elif heat_index >= 45:
        status = "😐 NEUTRAL"
        signal = "NORMAL"
        description = "Thị trường bình thường. Giao dịch theo chiến lược."
        color = "#22C55E"  # Green
    elif heat_index >= 35:
        status = "🌤️ COOL"
        signal = "ACCUMULATE"
        description = "Thị trường mát. Cơ hội tích lũy dần."
        color = "#14B8A6"  # Teal
    elif heat_index >= 20:
        status = "❄️ COLD"
        signal = "BUY"
        description = "Thị trường lạnh! Nhiều cổ phiếu rẻ. Mua mạnh!"
        color = "#3B82F6"  # Blue
    else:
        status = "🥶 ICE COLD"
        signal = "BUY_HEAVY"
        description = "Thị trường cực lạnh/panic! Cơ hội vàng để mua. All-in!"
        color = "#8B5CF6"  # Purple
    
    return {
        "heat_index": round(heat_index, 1),
        "status": status,
        "signal": signal,
        "description": description,
        "color": color,
        "metrics": {
            "avg_pb_percentile": round(avg_percentile, 1),
            "median_pb_percentile": round(median_percentile, 1),
            "avg_pb": round(np.mean(pb_values), 2) if pb_values else None,
            "very_cheap_count": very_cheap,
            "cheap_count": cheap,
            "expensive_count": expensive,
            "very_expensive_count": very_expensive,
            "total_banks": total_banks,
            "cheap_percent": round(cheap / total_banks * 100, 1),
            "expensive_percent": round(expensive / total_banks * 100, 1)
        }
    }


def calculate_historical_heat(bank_data: Dict) -> List[Dict]:
    """Tính heat index cho tất cả các period lịch sử"""
    
    # Collect all periods
    all_periods = set()
    for symbol, data in bank_data.items():
        for h in data.get("pb_history", []):
            all_periods.add(h["period"])
    
    periods = sorted(list(all_periods))
    
    # Calculate heat for each period
    heat_history = []
    
    for period in periods:
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
            
            # Calculate percentile for this period
            pb_mean = pb_stats.get("mean", period_pb)
            pb_std = pb_stats.get("std", 1)
            
            if pb_std > 0:
                # Simple percentile estimation
                z_score = (period_pb - pb_mean) / pb_std
                percentile = 50 + z_score * 15  # Rough conversion
                percentile = max(0, min(100, percentile))
            else:
                percentile = 50
            
            pb_percentiles.append(percentile)
            pb_values.append(period_pb)
        
        if not pb_percentiles:
            continue
        
        avg_percentile = np.mean(pb_percentiles)
        
        # Determine status
        if avg_percentile >= 85:
            status = "OVERHEATED"
        elif avg_percentile >= 70:
            status = "HOT"
        elif avg_percentile >= 55:
            status = "WARM"
        elif avg_percentile >= 45:
            status = "NEUTRAL"
        elif avg_percentile >= 35:
            status = "COOL"
        elif avg_percentile >= 20:
            status = "COLD"
        else:
            status = "ICE_COLD"
        
        heat_history.append({
            "period": period,
            "heat_index": round(avg_percentile, 1),
            "status": status,
            "avg_pb": round(np.mean(pb_values), 2) if pb_values else None,
            "banks_count": len(pb_percentiles)
        })
    
    return heat_history


def get_heat_zones(heat_history: List[Dict]) -> Dict:
    """Phân tích các vùng nhiệt lịch sử"""
    
    if not heat_history:
        return {}
    
    heat_values = [h["heat_index"] for h in heat_history]
    
    # Find extremes
    max_heat = max(heat_values)
    min_heat = min(heat_values)
    max_period = heat_history[heat_values.index(max_heat)]["period"]
    min_period = heat_history[heat_values.index(min_heat)]["period"]
    
    # Count periods in each zone
    zones = {
        "overheated": sum(1 for h in heat_values if h >= 85),
        "hot": sum(1 for h in heat_values if 70 <= h < 85),
        "warm": sum(1 for h in heat_values if 55 <= h < 70),
        "neutral": sum(1 for h in heat_values if 45 <= h < 55),
        "cool": sum(1 for h in heat_values if 35 <= h < 45),
        "cold": sum(1 for h in heat_values if 20 <= h < 35),
        "ice_cold": sum(1 for h in heat_values if h < 20),
    }
    
    return {
        "current_heat": heat_values[-1] if heat_values else 50,
        "max_heat": max_heat,
        "max_heat_period": max_period,
        "min_heat": min_heat,
        "min_heat_period": min_period,
        "avg_heat": round(np.mean(heat_values), 1),
        "zone_distribution": zones,
        "total_periods": len(heat_history)
    }


def generate_heat_report(bank_data: Dict) -> Dict:
    """Tạo báo cáo nhiệt độ ngành đầy đủ"""
    
    current_heat = calculate_sector_heat(bank_data)
    heat_history = calculate_historical_heat(bank_data)
    heat_zones = get_heat_zones(heat_history)
    
    # Recent trend (last 4 quarters)
    if len(heat_history) >= 4:
        recent = heat_history[-4:]
        trend_values = [h["heat_index"] for h in recent]
        
        if trend_values[-1] > trend_values[0] + 5:
            trend = "HEATING_UP"
            trend_emoji = "📈"
        elif trend_values[-1] < trend_values[0] - 5:
            trend = "COOLING_DOWN"
            trend_emoji = "📉"
        else:
            trend = "STABLE"
            trend_emoji = "➡️"
    else:
        trend = "UNKNOWN"
        trend_emoji = "❓"
    
    return {
        "generated_at": datetime.now().isoformat(),
        "current": current_heat,
        "trend": {
            "direction": trend,
            "emoji": trend_emoji,
            "description": {
                "HEATING_UP": "Thị trường đang nóng lên",
                "COOLING_DOWN": "Thị trường đang nguội đi", 
                "STABLE": "Thị trường ổn định",
                "UNKNOWN": "Chưa đủ dữ liệu"
            }.get(trend, "")
        },
        "history": heat_history,
        "analysis": heat_zones,
        "recommendations": generate_heat_recommendations(current_heat, trend)
    }


def generate_heat_recommendations(current_heat: Dict, trend: str) -> List[Dict]:
    """Tạo khuyến nghị dựa trên nhiệt độ ngành"""
    
    heat_index = current_heat.get("heat_index", 50)
    recommendations = []
    
    if heat_index >= 80:
        recommendations.append({
            "priority": "HIGH",
            "action": "DEFENSIVE",
            "message": "🚨 Ngành ngân hàng quá nóng! Nên chốt lời 50-70% vị thế.",
            "position_adjust": -50
        })
    elif heat_index >= 65:
        recommendations.append({
            "priority": "MEDIUM",
            "action": "CAUTIOUS",
            "message": "⚠️ Ngành đang nóng. Không nên mua thêm, cân nhắc chốt lời.",
            "position_adjust": -20
        })
    elif heat_index <= 25:
        recommendations.append({
            "priority": "HIGH",
            "action": "AGGRESSIVE_BUY",
            "message": "🎯 Cơ hội vàng! Ngành cực rẻ. Tăng tỷ trọng mạnh.",
            "position_adjust": +50
        })
    elif heat_index <= 40:
        recommendations.append({
            "priority": "MEDIUM",
            "action": "ACCUMULATE",
            "message": "✅ Ngành đang rẻ. Tích lũy dần các cổ phiếu chất lượng.",
            "position_adjust": +25
        })
    else:
        recommendations.append({
            "priority": "LOW",
            "action": "NORMAL",
            "message": "📊 Ngành ở mức bình thường. Giao dịch theo chiến lược.",
            "position_adjust": 0
        })
    
    # Add trend-based recommendation
    if trend == "HEATING_UP" and heat_index > 60:
        recommendations.append({
            "priority": "MEDIUM",
            "action": "TRAIL_STOP",
            "message": "📈 Thị trường đang nóng lên - Đặt trailing stop để bảo vệ lợi nhuận.",
            "position_adjust": 0
        })
    elif trend == "COOLING_DOWN" and heat_index < 40:
        recommendations.append({
            "priority": "MEDIUM",
            "action": "DCA",
            "message": "📉 Thị trường đang nguội - Cơ hội DCA (mua trung bình giá).",
            "position_adjust": +10
        })
    
    return recommendations


if __name__ == "__main__":
    # Load data and generate report
    with open("../docs/data/banks_v2.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    bank_data = data.get("banks", {})
    report = generate_heat_report(bank_data)
    
    # Save report
    with open("../docs/data/sector_heat.json", 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # Print summary
    print("="*60)
    print("BANKING SECTOR HEAT INDEX")
    print("="*60)
    
    current = report["current"]
    print(f"\n🌡️ Current Heat Index: {current['heat_index']}/100")
    print(f"   Status: {current['status']}")
    print(f"   Signal: {current['signal']}")
    print(f"   {current['description']}")
    
    print(f"\n📊 Trend: {report['trend']['emoji']} {report['trend']['direction']}")
    print(f"   {report['trend']['description']}")
    
    metrics = current["metrics"]
    print(f"\n📈 Metrics:")
    print(f"   Avg P/B Percentile: P{metrics['avg_pb_percentile']}")
    print(f"   Avg P/B: {metrics['avg_pb']}")
    print(f"   Cheap banks (P<35): {metrics['cheap_count']}/{metrics['total_banks']} ({metrics['cheap_percent']}%)")
    print(f"   Expensive banks (P>65): {metrics['expensive_count']}/{metrics['total_banks']} ({metrics['expensive_percent']}%)")
    
    print(f"\n📜 Historical Analysis:")
    analysis = report["analysis"]
    print(f"   Max Heat: {analysis['max_heat']} ({analysis['max_heat_period']})")
    print(f"   Min Heat: {analysis['min_heat']} ({analysis['min_heat_period']})")
    print(f"   Avg Heat: {analysis['avg_heat']}")
    
    print(f"\n💡 Recommendations:")
    for rec in report["recommendations"]:
        print(f"   [{rec['priority']}] {rec['message']}")
    
    print(f"\n✓ Report saved to ../docs/data/sector_heat.json")
