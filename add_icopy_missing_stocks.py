#!/usr/bin/env python3
"""
Script để thêm 69 mã còn thiếu từ iCopy vào hệ thống
"""
import json
import sys
from pathlib import Path
from datetime import datetime

# Import script fetch data hiện có
sys.path.insert(0, str(Path(__file__).parent / 'src'))
from fetch_all_sectors_daily import fetch_single_stock_daily

# Danh sách mã thiếu và ngành tương ứng
MISSING_STOCKS = {
    'banks_daily.json': ['SSB', 'VIB', 'SHI'],  # SSB là ngân hàng
    'realestate_daily.json': ['AAA', 'DHA', 'DPR', 'DRC', 'DTD', 'HAG', 'HAH', 'IMP', 'NTL', 'PHR', 'PLC', 'VHC'],
    'securities_daily.json': ['AGR', 'BVS', 'CSM', 'EVF', 'IPA', 'SIP', 'VCS', 'VDS', 'VFS', 'VIX'],
    'retail_daily.json': ['ASM', 'BMP', 'DBC', 'DBD', 'GMD', 'KDC', 'NAF', 'PAC', 'PAN', 'PET', 'SBT', 'VOS'],
    'construction_daily.json': ['ANV', 'CTI', 'CTR', 'DCL', 'HHS', 'HTN', 'PTB', 'TNG', 'TRC'],
    'energy_daily.json': ['GEE', 'GEG', 'GEX', 'VSC'],
    'steel_daily.json': ['NTP'],
    'technology_daily.json': ['AGG', 'BWE', 'DSE', 'IDI', 'TCH', 'TCM', 'VTP'],
    'oilgas_daily.json': ['PVL'],
    'insurance_daily.json': ['VPI'],
    'chemicals_daily.json': ['GIL', 'KSB', 'MSH', 'TCX', 'TDP', 'TIG', 'TLG', 'TNH'],
}

def add_stock_to_file(filename, symbol):
    """Thêm một mã vào file"""
    file_path = Path('./docs/data') / filename
    
    print(f"\n{'='*60}")
    print(f"📊 Processing {symbol} -> {filename}")
    print(f"{'='*60}")
    
    try:
        # Load existing file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if already exists
        if symbol in data.get('stocks', {}):
            print(f"   ⏭️  {symbol} đã tồn tại, bỏ qua")
            return True
        
        # Fetch data using existing function
        print(f"   🔄 Fetching complete data for {symbol}...")
        result = fetch_single_stock_daily(symbol, symbol, years=3)
        
        # Handle tuple return (stock_data, count)
        if isinstance(result, tuple):
            stock_data, _ = result
        else:
            stock_data = result
        
        if not stock_data or 'error' in stock_data:
            print(f"   ❌ Không lấy được dữ liệu: {stock_data.get('error', 'Unknown error') if isinstance(stock_data, dict) else 'Unknown error'}")
            return False
        
        # Add to data
        if 'stocks' not in data:
            data['stocks'] = {}
        data['stocks'][symbol] = stock_data
        data['total_stocks'] = len(data['stocks'])
        data['last_updated'] = datetime.now().isoformat()
        
        # Save
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        current_pb = stock_data.get('current', {}).get('pb')
        valuation = stock_data.get('valuation', {})
        daily_data = stock_data.get('daily_data', [])
        
        print(f"   ✅ {symbol} đã được thêm thành công!")
        if current_pb:
            print(f"      - P/B hiện tại: {current_pb:.3f}")
        else:
            print(f"      - P/B hiện tại: N/A")
        print(f"      - Percentile: P{valuation.get('percentile', 0):.0f}")
        print(f"      - Zone: {valuation.get('zone', 'N/A')}")
        print(f"      - Daily samples: {len(daily_data)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Lỗi: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*70)
    print("🚀 BẮT ĐẦU THÊM 69 MÃ iCOPY VÀO HỆ THỐNG")
    print("="*70)
    
    total = sum(len(symbols) for symbols in MISSING_STOCKS.values())
    print(f"\nTổng số mã cần thêm: {total}")
    
    success_count = 0
    failed_count = 0
    failed_symbols = []
    
    for filename, symbols in MISSING_STOCKS.items():
        sector = filename.replace('_daily.json', '')
        print(f"\n\n{'='*70}")
        print(f"📂 SECTOR: {sector.upper()} - {len(symbols)} mã")
        print(f"{'='*70}")
        
        for symbol in symbols:
            if add_stock_to_file(filename, symbol):
                success_count += 1
            else:
                failed_count += 1
                failed_symbols.append(f"{symbol} ({sector})")
            
            # Rate limiting
            import time
            time.sleep(1)
    
    # Update summary files
    print(f"\n\n{'='*70}")
    print("📊 CẬP NHẬT SUMMARY FILES")
    print(f"{'='*70}")
    
    for filename in MISSING_STOCKS.keys():
        summary_file = filename.replace('_daily.json', '_daily_summary.json')
        print(f"\nUpdating {summary_file}...")
        # TODO: Generate summary data
    
    # Final summary
    print(f"\n\n{'='*70}")
    print("📈 TỔNG KẾT")
    print(f"{'='*70}")
    print(f"✅ Thành công: {success_count}/{total} mã")
    print(f"❌ Thất bại: {failed_count}/{total} mã")
    
    if failed_symbols:
        print(f"\n❌ Các mã thất bại:")
        for sym in failed_symbols:
            print(f"   - {sym}")
    
    print(f"\n📅 Hoàn thành: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()
