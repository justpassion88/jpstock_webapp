#!/usr/bin/env python3
"""
Tính toán Heat Index lịch sử thực sự từ dữ liệu P/B lịch sử
"""

import json
from pathlib import Path
from collections import defaultdict
import numpy as np

def get_heat_status(heat):
    """Get status text based on heat index"""
    if heat >= 85:
        return "OVERHEATED"
    elif heat >= 70:
        return "HOT"
    elif heat >= 55:
        return "WARM"
    elif heat >= 45:
        return "NEUTRAL"
    elif heat >= 35:
        return "COOL"
    elif heat >= 20:
        return "COLD"
    else:
        return "ICE_COLD"

def calculate_percentile(value, all_values):
    """Calculate percentile of value in all_values"""
    if not all_values or value is None:
        return 50
    sorted_vals = sorted(all_values)
    count_below = sum(1 for v in sorted_vals if v < value)
    return (count_below / len(sorted_vals)) * 100

def load_sector_data(filename):
    """Load sector JSON data"""
    path = Path(f"docs/data/{filename}")
    if not path.exists():
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_pb_history_by_period(data, stocks_key='stocks'):
    """Extract P/B history grouped by period from sector data"""
    period_pb = defaultdict(list)
    
    stocks = data.get(stocks_key, data.get('banks', {}))
    
    for symbol, stock_data in stocks.items():
        pb_history = stock_data.get('pb_history', [])
        for entry in pb_history:
            period = entry.get('period')
            pb = entry.get('pb')
            if period and pb and pb > 0:
                period_pb[period].append(pb)
    
    return period_pb

def calculate_heat_history_from_pb(period_pb_data, all_pb_values):
    """Calculate heat index for each period based on P/B percentile"""
    history = []
    
    # Sort periods chronologically
    sorted_periods = sorted(period_pb_data.keys())
    
    for period in sorted_periods:
        pb_values = period_pb_data[period]
        if not pb_values:
            continue
        
        avg_pb = np.mean(pb_values)
        
        # Calculate heat as average percentile of P/B values
        percentiles = [calculate_percentile(pb, all_pb_values) for pb in pb_values]
        heat_index = np.mean(percentiles)
        
        status = get_heat_status(heat_index)
        
        history.append({
            "period": period,
            "heat_index": round(heat_index, 1),
            "status": status,
            "avg_pb": round(avg_pb, 2),
            "stocks_count": len(pb_values)
        })
    
    return history

def generate_analysis_stats(history):
    """Generate analysis stats from history"""
    if not history:
        return None
    
    heats = [h["heat_index"] for h in history]
    max_idx = heats.index(max(heats))
    min_idx = heats.index(min(heats))
    
    return {
        "max_heat": round(max(heats), 1),
        "max_heat_period": history[max_idx]["period"],
        "min_heat": round(min(heats), 1),
        "min_heat_period": history[min_idx]["period"],
        "avg_heat": round(np.mean(heats), 1)
    }

def process_all_sectors():
    """Process all sector files and calculate real heat history"""
    
    sector_configs = [
        ("banks_v2.json", "banks"),
        ("realestate.json", "stocks"),
        ("securities.json", "stocks"),
        ("energy.json", "stocks"),
        ("oilgas.json", "stocks"),
        ("steel.json", "stocks"),
        ("construction.json", "stocks"),
        ("insurance.json", "stocks"),
        ("retail.json", "stocks"),
        ("technology.json", "stocks"),
        ("chemicals.json", "stocks"),
    ]
    
    all_sector_histories = {}
    
    for filename, stocks_key in sector_configs:
        print(f"\n📊 Processing {filename}...")
        data = load_sector_data(filename)
        if not data:
            print(f"  ⏭️ Skipped (not found)")
            continue
        
        # Extract P/B history
        period_pb = extract_pb_history_by_period(data, stocks_key)
        
        if not period_pb:
            print(f"  ⚠️ No P/B history found")
            continue
        
        # Get all P/B values for percentile calculation
        all_pb = []
        for pbs in period_pb.values():
            all_pb.extend(pbs)
        
        # Calculate heat history
        history = calculate_heat_history_from_pb(period_pb, all_pb)
        analysis = generate_analysis_stats(history)
        
        print(f"  ✅ Found {len(history)} periods ({history[0]['period']} to {history[-1]['period']})")
        print(f"  📈 Max heat: {analysis['max_heat']} ({analysis['max_heat_period']})")
        print(f"  📉 Min heat: {analysis['min_heat']} ({analysis['min_heat_period']})")
        
        sector_id = filename.replace('.json', '').replace('_v2', '')
        all_sector_histories[sector_id] = {
            "history": history,
            "analysis": analysis
        }
        
        # Update sector file with history
        if 'heat' not in data:
            data['heat'] = {}
        data['heat']['history'] = history
        data['heat']['analysis'] = analysis
        
        path = Path(f"docs/data/{filename}")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  💾 Saved to {filename}")
    
    return all_sector_histories

def update_market_heat(all_sector_histories):
    """Update market_heat.json with aggregated history from all sectors"""
    print("\n📊 Updating market_heat.json...")
    
    path = Path("docs/data/market_heat.json")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Aggregate all periods across all sectors
    period_heats = defaultdict(list)
    period_pbs = defaultdict(list)
    period_counts = defaultdict(int)
    
    for sector_id, sector_data in all_sector_histories.items():
        for entry in sector_data['history']:
            period = entry['period']
            period_heats[period].append(entry['heat_index'])
            period_pbs[period].append(entry['avg_pb'])
            period_counts[period] += entry['stocks_count']
    
    # Calculate market-wide heat for each period
    market_history = []
    for period in sorted(period_heats.keys()):
        avg_heat = np.mean(period_heats[period])
        avg_pb = np.mean(period_pbs[period])
        status = get_heat_status(avg_heat)
        
        market_history.append({
            "period": period,
            "heat_index": round(avg_heat, 1),
            "status": status,
            "avg_pb": round(avg_pb, 2),
            "stocks_count": period_counts[period]
        })
    
    analysis = generate_analysis_stats(market_history)
    
    data['history'] = market_history
    data['analysis'] = analysis
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✅ Found {len(market_history)} periods ({market_history[0]['period']} to {market_history[-1]['period']})")
    print(f"  📈 Max heat: {analysis['max_heat']} ({analysis['max_heat_period']})")
    print(f"  📉 Min heat: {analysis['min_heat']} ({analysis['min_heat_period']})")
    print(f"  💾 Saved to market_heat.json")

if __name__ == "__main__":
    import os
    os.chdir("/workspaces/jpstock_webapp")
    
    print("=" * 60)
    print("🔥 CALCULATING REAL HEAT INDEX HISTORY FROM P/B DATA")
    print("=" * 60)
    
    all_histories = process_all_sectors()
    update_market_heat(all_histories)
    
    print("\n" + "=" * 60)
    print("✨ Done! All files updated with real historical heat data.")
    print("=" * 60)
