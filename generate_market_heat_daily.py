#!/usr/bin/env python3
"""
Generate Market Heat JSON from Daily Data
Tạo market_heat.json với lịch sử daily thay vì quarterly
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import statistics

DATA_DIR = Path('./docs/data')

SECTORS = {
    'banks': '🏦 Ngân hàng',
    'realestate': '🏠 Bất động sản', 
    'securities': '📈 Chứng khoán',
    'energy': '⚡ Điện & Năng lượng',
    'oilgas': '🛢️ Dầu khí',
    'steel': '🏗️ Thép',
    'construction': '🏗️ Xây dựng',
    'insurance': '🛡️ Bảo hiểm',
    'retail': '🛒 Bán lẻ',
    'technology': '💻 Công nghệ',
    'chemicals': '🧪 Hóa chất'
}


def calculate_heat_index(avg_pb: float, max_pb: float, min_pb: float) -> float:
    """Tính heat index từ P/B"""
    if max_pb == min_pb:
        return 50.0
    
    # Normalize P/B to 0-100 scale
    heat = ((avg_pb - min_pb) / (max_pb - min_pb)) * 100
    return round(max(0, min(100, heat)), 1)


def get_heat_status(heat_index: float) -> str:
    """Xác định trạng thái nhiệt độ"""
    if heat_index >= 85:
        return "🔥 QUÁ NÓNG"
    elif heat_index >= 70:
        return "🌡️ NÓNG"
    elif heat_index >= 55:
        return "☀️ ẤM"
    elif heat_index >= 45:
        return "😐 TRUNG LƯỠNG"
    elif heat_index >= 35:
        return "🌤️ MÁT"
    elif heat_index >= 20:
        return "❄️ LẠNH"
    else:
        return "🥶 CỰC LẠNH"


def get_signal(heat_index: float) -> str:
    """Xác định tín hiệu giao dịch"""
    if heat_index >= 80:
        return "🚨 BÁN"
    elif heat_index >= 65:
        return "⚠️ THẬN TRỌNG"
    elif heat_index >= 45:
        return "⏸️ QUAN SÁT"
    elif heat_index >= 30:
        return "✅ XEM XÉT"
    else:
        return "💰 MUA"


def load_sector_data(sector_id: str) -> Dict:
    """Load sector data từ file daily_summary"""
    summary_file = DATA_DIR / f"{sector_id}_daily_summary.json"
    
    if not summary_file.exists():
        return None
    
    with open(summary_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_daily_history(sector_id: str) -> List[Dict]:
    """Trích xuất lịch sử P/B daily từ sector data - Tính với stocks có sẵn tại mỗi thời điểm"""
    daily_file = DATA_DIR / f"{sector_id}_daily.json"
    
    if not daily_file.exists():
        return []
    
    with open(daily_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stocks = data.get('stocks', {})
    if not isinstance(stocks, dict):
        return []
    
    # Build một dict: date -> list of P/B values từ các stocks có data
    date_pb_map = {}
    
    for stock_data in stocks.values():
        if not isinstance(stock_data, dict):
            continue
        
        daily_data = stock_data.get('daily_data', [])
        for day in daily_data:
            if not isinstance(day, dict):
                continue
            
            date = day.get('date')
            pb = day.get('pb')
            
            if date and pb and pb > 0:
                if date not in date_pb_map:
                    date_pb_map[date] = []
                date_pb_map[date].append(pb)
    
    # Lấy mẫu: mỗi tháng lấy 1 điểm (ngày cuối tháng có data)
    monthly_dates = {}
    for date in sorted(date_pb_map.keys()):
        month_key = date[:7]  # YYYY-MM
        # Luôn lấy ngày cuối trong tháng
        monthly_dates[month_key] = date
    
    # Lấy 60 tháng gần nhất
    sampled_months = sorted(monthly_dates.keys())[-60:]
    
    daily_history = []
    for month_key in sampled_months:
        date = monthly_dates[month_key]
        pb_values = date_pb_map[date]
        
        # Chỉ tính nếu có ít nhất 30% total stocks (để đảm bảo đại diện)
        # Hoặc ít nhất 5 stocks
        min_stocks_required = max(5, len(stocks) * 0.3) if len(stocks) > 0 else 5
        
        if len(pb_values) >= min_stocks_required:
            avg_pb = statistics.mean(pb_values)
            daily_history.append({
                'date': date,
                'avg_pb': round(avg_pb, 2),
                'stocks_count': len(pb_values)
            })
    
    return daily_history


def generate_market_heat():
    """Generate market_heat.json từ daily data"""
    
    print("🔄 Đang tạo market_heat.json từ dữ liệu daily...")
    
    sector_heats = []
    all_histories = []
    
    # Load data từng sector
    for sector_id, sector_name in SECTORS.items():
        summary = load_sector_data(sector_id)
        
        if not summary:
            print(f"  ⚠️  {sector_name}: Không có dữ liệu")
            continue
        
        # Extract daily history để tính stats
        history = extract_daily_history(sector_id)
        
        if not history or len(history) < 2:
            print(f"  ⚠️  {sector_name}: Không đủ lịch sử P/B (có {len(history)})")
            continue
        
        # Tính stats từ history
        all_pb = [h['avg_pb'] for h in history]
        max_pb = max(all_pb)
        min_pb = min(all_pb)
        
        # P/B hiện tại (cuối cùng trong history)
        current_pb = history[-1]['avg_pb']
        
        # Tính heat index
        heat_index = calculate_heat_index(current_pb, max_pb, min_pb)
        
        # Tính heat_index cho từng điểm trong history
        history_with_heat = []
        for h in history:
            h_heat = calculate_heat_index(h['avg_pb'], max_pb, min_pb)
            history_with_heat.append({
                'period': h['date'],
                'avg_pb': h['avg_pb'],
                'heat_index': h_heat,
                'stocks_count': h.get('stocks_count', 0)
            })
        
        sector_heats.append({
            'sector_id': sector_id,
            'sector_name': sector_name,
            'heat_index': heat_index,
            'status': get_heat_status(heat_index),
            'signal': get_signal(heat_index),
            'stocks_count': summary.get('total_stocks', 0),
            'avg_pb': current_pb,
            'history': history_with_heat  # Thêm history vào từng sector
        })
        
        all_histories.append({
            'sector_id': sector_id,
            'history': history_with_heat
        })
        
        print(f"  ✓ {sector_name}: Heat={heat_index:.1f} (P/B: {current_pb:.2f}, Min: {min_pb:.2f}, Max: {max_pb:.2f}, History: {len(history_with_heat)} points)")
    
    # Calculate market heat (weighted average)
    total_stocks = sum(s['stocks_count'] for s in sector_heats)
    
    if total_stocks > 0:
        weighted_heat = sum(s['heat_index'] * s['stocks_count'] for s in sector_heats) / total_stocks
    else:
        weighted_heat = 50.0
    
    market_heat_index = round(weighted_heat, 1)
    
    # Generate combined history (average of all sectors) - Tính với sectors có sẵn tại mỗi thời điểm
    combined_history = []
    
    if all_histories:
        # Build một dict: date -> list of P/B values từ các sectors có data
        date_sector_map = {}
        
        for sector_hist in all_histories:
            for entry in sector_hist['history']:
                date = entry['period']
                pb = entry['avg_pb']
                
                if date not in date_sector_map:
                    date_sector_map[date] = []
                date_sector_map[date].append(pb)
        
        # Sort dates
        sorted_dates = sorted(date_sector_map.keys())
        
        # Tính stats cho toàn bộ history để có min/max
        all_pb_all_time = []
        for pb_list in date_sector_map.values():
            all_pb_all_time.extend(pb_list)
        
        if all_pb_all_time:
            max_pb = max(all_pb_all_time)
            min_pb = min(all_pb_all_time)
            
            # Tính cho từng ngày với sectors có sẵn
            for date in sorted_dates:
                pb_values = date_sector_map[date]
                
                # Chỉ tính nếu có ít nhất 3 sectors (đại diện tốt hơn)
                if len(pb_values) >= 3:
                    avg_pb = statistics.mean(pb_values)
                    heat_index = calculate_heat_index(avg_pb, max_pb, min_pb)
                    
                    combined_history.append({
                        'period': date,
                        'avg_pb': round(avg_pb, 2),
                        'heat_index': heat_index,
                        'sectors_count': len(pb_values)
                    })
    
    # Analysis
    if combined_history:
        all_heat = [h['heat_index'] for h in combined_history]
        recent_heat = all_heat[-12:]  # 12 tháng gần nhất
        
        analysis = {
            'max_heat': round(max(all_heat), 1),
            'min_heat': round(min(all_heat), 1),
            'avg_heat': round(statistics.mean(all_heat), 1),
            'current_vs_avg': round(market_heat_index - statistics.mean(all_heat), 1),
            'recent_trend': 'tăng' if len(recent_heat) >= 2 and recent_heat[-1] > recent_heat[0] else 'giảm',
            'volatility': round(statistics.stdev(recent_heat) if len(recent_heat) >= 2 else 0, 1)
        }
    else:
        analysis = {
            'max_heat': market_heat_index,
            'min_heat': market_heat_index,
            'avg_heat': market_heat_index,
            'current_vs_avg': 0,
            'recent_trend': 'ổn định',
            'volatility': 0
        }
    
    # Build final JSON
    market_heat_data = {
        'updated_at': datetime.now().isoformat(),
        'sectors': sorted(sector_heats, key=lambda x: x['heat_index'], reverse=True),
        'market_heat': {
            'heat_index': market_heat_index,
            'status': get_heat_status(market_heat_index),
            'signal': get_signal(market_heat_index),
            'total_sectors': len(sector_heats),
            'total_stocks': total_stocks
        },
        'history': combined_history[-60:],  # Keep last 60 months
        'analysis': analysis
    }
    
    # Save
    output_file = DATA_DIR / 'market_heat.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(market_heat_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Đã tạo {output_file}")
    print(f"   Market Heat: {market_heat_index:.1f} - {get_heat_status(market_heat_index)}")
    print(f"   History: {len(combined_history)} điểm dữ liệu")
    print(f"   Sectors: {len(sector_heats)}")
    print(f"   Stocks: {total_stocks}")


if __name__ == '__main__':
    generate_market_heat()
