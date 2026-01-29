#!/usr/bin/env python3
"""
Validation Script: Verify Data Consistency
Kiểm tra tính nhất quán giữa config và data files
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.END} {msg}")

def print_error(msg):
    print(f"{Colors.RED}✗{Colors.END} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.END} {msg}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.END} {msg}")


def load_config_stocks():
    """Load stocks from config_sectors.py"""
    print("\n📝 Loading config_sectors.py...")
    
    # Import the config
    sys.path.insert(0, 'src')
    from config_sectors import SECTORS, TOTAL_SYMBOLS
    
    config_stocks = {}
    for sector_id, sector_data in SECTORS.items():
        config_stocks[sector_id] = set(sector_data['symbols'])
    
    return config_stocks, TOTAL_SYMBOLS


def load_data_stocks():
    """Load stocks from data files"""
    print("📊 Loading data files...")
    
    data_dir = Path('docs/data')
    data_stocks = {}
    
    for sector_file in sorted(data_dir.glob('*_daily.json')):
        sector_id = sector_file.stem.replace('_daily', '')
        
        with open(sector_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        stocks = set(data.get('stocks', {}).keys())
        data_stocks[sector_id] = stocks
        
    return data_stocks


def load_icopy_stocks():
    """Load iCopy portfolio from icopy-config.js"""
    print("🎯 Loading iCopy portfolio...")
    
    icopy_file = Path('docs/js/icopy-config.js')
    if not icopy_file.exists():
        print_warning("icopy-config.js not found")
        return set()
    
    # Parse JavaScript array
    with open(icopy_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract symbols from ICOPY_SYMBOLS array
    import re
    match = re.search(r'const ICOPY_SYMBOLS = \[(.*?)\];', content, re.DOTALL)
    if match:
        symbols_str = match.group(1)
        symbols = re.findall(r"['\"]([A-Z]+)['\"]", symbols_str)
        return set(symbols)
    
    return set()


def validate():
    """Run all validation checks"""
    
    print("="*70)
    print("🔍 JP STOCK WEBAPP - DATA VALIDATION")
    print("="*70)
    
    # Load data
    config_stocks, config_total = load_config_stocks()
    data_stocks = load_data_stocks()
    icopy_stocks = load_icopy_stocks()
    
    # Calculate totals
    config_count = sum(len(stocks) for stocks in config_stocks.values())
    data_count = sum(len(stocks) for stocks in data_stocks.values())
    
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    print(f"Config (config_sectors.py): {config_count} stocks")
    print(f"Data files (*_daily.json):  {data_count} stocks")
    print(f"iCopy portfolio:             {len(icopy_stocks)} stocks")
    print()
    
    # Check 1: Total count
    print("="*70)
    print("✓ CHECK 1: Total Stock Count")
    print("="*70)
    
    if config_count == data_count:
        print_success(f"Total count matches: {config_count} stocks")
    else:
        print_error(f"Mismatch! Config: {config_count}, Data: {data_count}")
        print_info(f"Difference: {abs(config_count - data_count)} stocks")
    
    # Check 2: Per-sector count
    print("\n" + "="*70)
    print("✓ CHECK 2: Per-Sector Stock Count")
    print("="*70)
    
    all_sectors = set(config_stocks.keys()) | set(data_stocks.keys())
    mismatches = []
    
    for sector in sorted(all_sectors):
        config_set = config_stocks.get(sector, set())
        data_set = data_stocks.get(sector, set())
        
        if len(config_set) == len(data_set):
            print_success(f"{sector:15s}: {len(config_set):3d} stocks (config) = {len(data_set):3d} (data)")
        else:
            print_error(f"{sector:15s}: {len(config_set):3d} stocks (config) ≠ {len(data_set):3d} (data)")
            mismatches.append(sector)
    
    # Check 3: Stock-level comparison
    print("\n" + "="*70)
    print("✓ CHECK 3: Stock-Level Comparison")
    print("="*70)
    
    has_issues = False
    
    for sector in sorted(all_sectors):
        config_set = config_stocks.get(sector, set())
        data_set = data_stocks.get(sector, set())
        
        missing_in_data = config_set - data_set
        missing_in_config = data_set - config_set
        
        if missing_in_data:
            has_issues = True
            print_error(f"\n{sector}: Missing in DATA files:")
            for stock in sorted(missing_in_data):
                print(f"  - {stock}")
        
        if missing_in_config:
            has_issues = True
            print_error(f"\n{sector}: Missing in CONFIG:")
            for stock in sorted(missing_in_config):
                print(f"  - {stock}")
    
    if not has_issues:
        print_success("All stocks present in both config and data files")
    
    # Check 4: Duplicate stocks
    print("\n" + "="*70)
    print("✓ CHECK 4: Duplicate Stocks Across Sectors")
    print("="*70)
    
    # Check config duplicates
    all_config_stocks = []
    for stocks in config_stocks.values():
        all_config_stocks.extend(stocks)
    
    config_duplicates = [stock for stock, count in Counter(all_config_stocks).items() if count > 1]
    
    if config_duplicates:
        print_error(f"Found {len(config_duplicates)} duplicates in CONFIG:")
        for stock in sorted(config_duplicates):
            sectors_with_stock = [s for s, stocks in config_stocks.items() if stock in stocks]
            print(f"  - {stock}: {', '.join(sectors_with_stock)}")
    else:
        print_success("No duplicates in config")
    
    # Check data duplicates
    all_data_stocks = []
    for stocks in data_stocks.values():
        all_data_stocks.extend(stocks)
    
    data_duplicates = [stock for stock, count in Counter(all_data_stocks).items() if count > 1]
    
    if data_duplicates:
        print_error(f"Found {len(data_duplicates)} duplicates in DATA:")
        for stock in sorted(data_duplicates):
            sectors_with_stock = [s for s, stocks in data_stocks.items() if stock in stocks]
            print(f"  - {stock}: {', '.join(sectors_with_stock)}")
    else:
        print_success("No duplicates in data files")
    
    # Check 5: iCopy coverage
    if icopy_stocks:
        print("\n" + "="*70)
        print("✓ CHECK 5: iCopy Portfolio Coverage")
        print("="*70)
        
        all_system_stocks = set(all_data_stocks)
        missing_icopy = icopy_stocks - all_system_stocks
        
        if missing_icopy:
            print_error(f"{len(missing_icopy)} iCopy stocks missing from system:")
            for stock in sorted(missing_icopy):
                print(f"  - {stock}")
        else:
            print_success(f"All {len(icopy_stocks)} iCopy stocks present in system")
        
        coverage = len(icopy_stocks & all_system_stocks) / len(icopy_stocks) * 100
        print_info(f"iCopy coverage: {coverage:.1f}%")
    
    # Check 6: Data quality
    print("\n" + "="*70)
    print("✓ CHECK 6: Data Quality")
    print("="*70)
    
    data_dir = Path('docs/data')
    low_data_stocks = []
    
    for sector_file in sorted(data_dir.glob('*_daily.json')):
        with open(sector_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for symbol, stock_data in data.get('stocks', {}).items():
            daily_data = stock_data.get('daily_data', [])
            if len(daily_data) < 100:
                low_data_stocks.append((symbol, len(daily_data)))
    
    if low_data_stocks:
        print_warning(f"Found {len(low_data_stocks)} stocks with < 100 days data:")
        for symbol, count in sorted(low_data_stocks, key=lambda x: x[1]):
            print(f"  - {symbol}: {count} days")
    else:
        print_success("All stocks have sufficient data (≥100 days)")
    
    # Final summary
    print("\n" + "="*70)
    print("📋 VALIDATION SUMMARY")
    print("="*70)
    
    issues_found = (
        config_count != data_count or
        len(mismatches) > 0 or
        has_issues or
        len(config_duplicates) > 0 or
        len(data_duplicates) > 0 or
        (icopy_stocks and len(missing_icopy) > 0) or
        len(low_data_stocks) > 0
    )
    
    if issues_found:
        print_error("❌ VALIDATION FAILED - Issues found")
        print_info("Please fix the issues above before proceeding")
        return False
    else:
        print_success("✅ ALL CHECKS PASSED")
        print_info(f"System is consistent with {config_count} stocks across {len(all_sectors)} sectors")
        return True


if __name__ == '__main__':
    success = validate()
    sys.exit(0 if success else 1)
