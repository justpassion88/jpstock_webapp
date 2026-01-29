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
    """Trích xuất lịch sử P/B daily từ sector data"""
    daily_file = DATA_DIR / f"{sector_id}_daily.json"
    
    if not daily_file.exists():
        return []
    
    with open(daily_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Tập hợp tất cả các ngày có dữ liệu
    all_dates = set()
    stocks = data.get('stocks', {})
    
    if isinstance(stocks, dict):
        for stock_data in stocks.values():
            if isinstance(stock_data, dict):
                daily_data = stock_data.get('daily_data', [])
                for day in daily_data:
                    if isinstance(day, dict) and 'date' in day:
                        all_dates.add(day['date'])
    
    # Sort dates
    sorted_dates = sorted(all_dates)
    
    # Tính P/B trung bình cho mỗi ngày
    daily_history = []
    
    # Lấy mẫu: mỗi tháng lấy 1 điểm (ngày cuối tháng)
    monthly_dates = {}
    for date in sorted_dates:
        month_key = date[:7]  # YYYY-MM
        monthly_dates[month_key] = date
    
    sampled_dates = list(monthly_dates.values())[-60:]  # Lấy 60 tháng gần nhất
    
    for date in sampled_dates:
        pb_values = []
        
        for stock_data in stocks.values():
            if isinstance(stock_data, dict):
                daily_data = stock_data.get('daily_data', [])
                # Tìm P/B cho ngày này
                for day in daily_data:
                    if isinstance(day, dict) and day.get('date') == date and day.get('pb') and day['pb'] > 0:
                        pb_values.append(day['pb'])
                        break
        
        if pb_values:
            avg_pb = statistics.mean(pb_values)
            daily_history.append({
                'date': date,
                'avg_pb': round(avg_pb, 2)
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
        
        if not history:
            print(f"  ⚠️  {sector_name}: Không có lịch sử P/B")
            continue
        
        # Tính stats từ history
        all_pb = [h['avg_pb'] for h in history]
        avg_pb = statistics.mean(all_pb)
        max_pb = max(all_pb)
        min_pb = min(all_pb)
        
        # P/B hiện tại (cuối cùng trong history)
        current_pb = history[-1]['avg_pb'] if history else avg_pb
        
        # Tính heat index
        heat_index = calculate_heat_index(current_pb, max_pb, min_pb)
        
        sector_heats.append({
            'sector_id': sector_id,
            'sector_name': sector_name,
            'heat_index': heat_index,
            'status': get_heat_status(heat_index),
            'signal': get_signal(heat_index),
            'stocks_count': summary.get('total_stocks', 0),
            'avg_pb': current_pb
        })
        
        all_histories.append({
            'sector_id': sector_id,
            'history': history
        })
        
        print(f"  ✓ {sector_name}: Heat={heat_index:.1f} (P/B: {current_pb:.2f}, Min: {min_pb:.2f}, Max: {max_pb:.2f})")
    
    # Calculate market heat (weighted average)
    total_stocks = sum(s['stocks_count'] for s in sector_heats)
    
    if total_stocks > 0:
        weighted_heat = sum(s['heat_index'] * s['stocks_count'] for s in sector_heats) / total_stocks
    else:
        weighted_heat = 50.0
    
    market_heat_index = round(weighted_heat, 1)
    
    # Generate combined history (average of all sectors)
    combined_history = []
    
    if all_histories:
        # Tìm tất cả các ngày chung
        all_dates = set()
        for sector_hist in all_histories:
            for entry in sector_hist['history']:
                all_dates.add(entry['date'])
        
        sorted_dates = sorted(all_dates)
        
        for date in sorted_dates:
            pb_values = []
            
            for sector_hist in all_histories:
                for entry in sector_hist['history']:
                    if entry['date'] == date:
                        pb_values.append(entry['avg_pb'])
                        break
            
            if pb_values:
                avg_pb = statistics.mean(pb_values)
                
                # Calculate heat từ P/B
                all_pb = []
                for sector_hist in all_histories:
                    for entry in sector_hist['history']:
                        all_pb.append(entry['avg_pb'])
                
                if all_pb:
                    max_pb = max(all_pb)
                    min_pb = min(all_pb)
                    heat_index = calculate_heat_index(avg_pb, max_pb, min_pb)
                else:
                    heat_index = 50.0
                
                combined_history.append({
                    'period': date,
                    'avg_pb': round(avg_pb, 2),
                    'heat_index': heat_index
                })
    
    # Analysis
    if combined_history:
        recent_heat = [h['heat_index'] for h in combined_history[-12:]]  # 12 tháng gần nhất
        
        analysis = {
            'max_heat': round(max(h['heat_index'] for h in combined_history), 1),
            'min_heat': round(min(h['heat_index'] for h in combined_history), 1),
            'avg_heat': round(statistics.mean([h['heat_index'] for h in combined_history]), 1),
            'current_vs_avg': round(market_heat_index - statistics.mean([h['heat_index'] for h in combined_history]), 1),
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
