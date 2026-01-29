#!/usr/bin/env python3
"""
Update Daily P/B Data
Script tiện dụng để cập nhật dữ liệu P/B daily cho tất cả ngân hàng
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.fetch_data_daily import fetch_all_banks_daily, save_data, create_summary_data


def main():
    print("=" * 60)
    print("JP Stock Webapp - Daily P/B Data Updater")
    print("=" * 60)
    
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(description='Fetch daily P/B data for Vietnamese banks')
    parser.add_argument('--years', type=int, default=15, help='Years of historical data (default: 15)')
    parser.add_argument('--test', action='store_true', help='Test mode - fetch only 3 banks')
    args = parser.parse_args()
    
    if args.test:
        # Test mode: chỉ fetch 3 ngân hàng
        from src.fetch_data_daily import fetch_single_bank_daily
        from datetime import datetime
        
        test_symbols = ['VCB', 'TCB', 'MBB']
        print(f"TEST MODE: Fetching only {test_symbols}")
        
        all_data = {
            'last_updated': datetime.now().isoformat(),
            'data_type': 'daily',
            'data_source': 'VCI',
            'years_of_history': args.years,
            'total_banks': len(test_symbols),
            'banks': {}
        }
        
        for symbol in test_symbols:
            result = fetch_single_bank_daily(symbol, years=args.years)
            all_data['banks'][symbol] = result
    else:
        # Full mode: fetch tất cả ngân hàng
        all_data = fetch_all_banks_daily(years=args.years)
    
    # Save files
    save_data(all_data, "banks_daily.json")
    
    summary = create_summary_data(all_data)
    save_data(summary, "banks_daily_summary.json")
    
    print("\n" + "=" * 60)
    print("Update completed!")
    print("Files created:")
    print("  - banks_daily.json (full data with daily records)")
    print("  - banks_daily_summary.json (summary for frontend)")
    print("=" * 60)


if __name__ == "__main__":
    main()
