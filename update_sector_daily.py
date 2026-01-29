#!/usr/bin/env python3
"""
Update Daily P/B Data - Chạy từng sector hoặc tất cả
Sử dụng: python update_sector_daily.py [sector_name] [--all]

Ví dụ:
  python update_sector_daily.py banks        # Chỉ fetch sector banks
  python update_sector_daily.py --all        # Fetch tất cả sectors
  python update_sector_daily.py --list       # Liệt kê các sectors
"""

import argparse
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config_sectors import SECTORS


def main():
    parser = argparse.ArgumentParser(description='Update Daily P/B Data by Sector')
    parser.add_argument('sector', nargs='?', help='Sector key to update (e.g., banks, realestate)')
    parser.add_argument('--all', action='store_true', help='Update all sectors')
    parser.add_argument('--list', action='store_true', help='List available sectors')
    parser.add_argument('--years', type=int, default=15, help='Years of historical data')
    
    args = parser.parse_args()
    
    if args.list:
        print("\n📊 Available Sectors:")
        print("-" * 50)
        for key, data in SECTORS.items():
            print(f"  {key:15} - {data['name']} ({len(data['symbols'])} stocks)")
        print("-" * 50)
        total = sum(len(d['symbols']) for d in SECTORS.values())
        print(f"  Total: {len(SECTORS)} sectors, {total} stocks")
        return
    
    # Import fetch functions
    from src.fetch_all_sectors_daily import (
        fetch_sector_daily, 
        save_sector_data, 
        create_sector_summary
    )
    
    if args.all:
        sectors_to_update = list(SECTORS.keys())
    elif args.sector:
        if args.sector not in SECTORS:
            print(f"❌ Unknown sector: {args.sector}")
            print(f"   Available: {', '.join(SECTORS.keys())}")
            return
        sectors_to_update = [args.sector]
    else:
        parser.print_help()
        return
    
    print(f"\n🚀 Starting update for {len(sectors_to_update)} sector(s)...")
    print(f"   Years of data: {args.years}")
    
    for sector_key in sectors_to_update:
        sector_config = SECTORS[sector_key]
        sector_name = sector_config['name']
        symbols = {s: s for s in sector_config['symbols']}
        
        # Fetch sector data
        sector_data = fetch_sector_daily(sector_name, symbols, args.years)
        
        # Save files
        save_sector_data(sector_data, f"{sector_key}_daily.json")
        summary = create_sector_summary(sector_data)
        save_sector_data(summary, f"{sector_key}_daily_summary.json")
    
    print("\n✅ Update completed!")


if __name__ == "__main__":
    main()
