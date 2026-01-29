#!/usr/bin/env python3
"""
Extract all stocks từ data files để sync với config
"""
import json
from pathlib import Path
from collections import defaultdict

data_dir = Path('./docs/data')
sector_files = sorted(data_dir.glob('*_daily.json'))

sector_stocks = defaultdict(list)

for file in sector_files:
    sector_name = file.stem.replace('_daily', '')
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stocks = data.get('stocks', {})
    symbols = sorted(stocks.keys())
    sector_stocks[sector_name] = symbols

# Print Python format for config_sectors.py
for sector, symbols in sorted(sector_stocks.items()):
    print(f"\n# {sector.upper()}: {len(symbols)} mã")
    print(f'"symbols": [')
    for sym in symbols:
        print(f'    "{sym}",')
    print(f'],')
