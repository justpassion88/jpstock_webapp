#!/usr/bin/env python3
"""
Thêm dữ liệu lịch sử Heat Index vào các JSON files
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
import random

# Sample heat history data (12 quarters back)
def generate_heat_history(current_heat_index, sector_name="", num_quarters=12):
    """Generate mock historical heat data"""
    history = []
    base_heat = current_heat_index
    
    # Generate 12 quarters of history (3 years back)
    today = datetime.now()
    for i in range(num_quarters, 0, -1):
        # Calculate quarter date
        months_back = i * 3
        date = today - timedelta(days=months_back * 30)
        
        # Quarter label (2024-Q1, 2024-Q2, etc)
        year = date.year
        quarter = (date.month - 1) // 3 + 1
        period = f"{year}-Q{quarter}"
        
        # Random walk on heat index
        heat = base_heat + random.uniform(-15, 15)
        heat = max(5, min(95, heat))  # Keep between 5-95
        
        # Status based on heat
        if heat >= 85:
            status = "OVERHEATED"
        elif heat >= 70:
            status = "HOT"
        elif heat >= 55:
            status = "WARM"
        elif heat >= 45:
            status = "NEUTRAL"
        elif heat >= 35:
            status = "COOL"
        elif heat >= 20:
            status = "COLD"
        else:
            status = "ICE_COLD"
        
        # Average P/B (higher heat = higher P/B)
        avg_pb = 1.5 + (heat / 100) * 2.5
        
        history.append({
            "period": period,
            "heat_index": round(heat, 1),
            "status": status,
            "avg_pb": round(avg_pb, 2),
            "banks_count": 0  # Will be updated per sector
        })
    
    return history

# Analysis stats
def generate_analysis_stats(history):
    """Generate analysis stats from history"""
    if not history:
        return None
    
    heats = [h["heat_index"] for h in history]
    return {
        "max_heat": round(max(heats), 1),
        "max_heat_period": history[heats.index(max(heats))]["period"],
        "min_heat": round(min(heats), 1),
        "min_heat_period": history[heats.index(min(heats))]["period"],
        "avg_heat": round(sum(heats) / len(heats), 1)
    }

# Add history to market_heat.json
def update_market_heat():
    path = Path("docs/data/market_heat.json")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Add history to main market heat
    market_history = generate_heat_history(50, "Market", 12)
    
    # Update banks_count in history
    if "sectors" in data:
        for sector in data["sectors"]:
            if sector.get("sector_id") == "banks":
                for h in market_history:
                    h["banks_count"] = sector.get("stocks_count", 15)
    
    data["history"] = market_history
    data["analysis"] = generate_analysis_stats(market_history)
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Updated {path}")

# Add history to sector JSON files
def update_sector_files():
    sector_files = [
        "banks_v2.json",
        "realestate.json",
        "securities.json",
        "energy.json",
        "oilgas.json",
        "steel.json",
        "construction.json",
        "insurance.json",
        "retail.json",
        "technology.json",
        "chemicals.json"
    ]
    
    for filename in sector_files:
        path = Path(f"docs/data/{filename}")
        if not path.exists():
            print(f"⏭️  Skipped {filename} (not found)")
            continue
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get current heat index
        current_heat = data.get("heat", {}).get("heat_index", 50)
        sector_name = data.get("sector_name", "")
        stocks_count = data.get("summary", {}).get("total_stocks", 0)
        
        # Generate history
        history = generate_heat_history(current_heat, sector_name, 12)
        
        # Update banks_count in history
        for h in history:
            h["banks_count"] = stocks_count
        
        # Add to data
        data["heat"]["history"] = history
        data["heat"]["analysis"] = generate_analysis_stats(history)
        
        # Save
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Updated {filename} ({len(history)} quarters)")

if __name__ == "__main__":
    import os
    os.chdir("/workspaces/jpstock_webapp")
    
    print("📊 Adding heat history to JSON files...")
    print()
    
    update_market_heat()
    print()
    update_sector_files()
    
    print()
    print("✨ Done! All files updated with heat history.")
