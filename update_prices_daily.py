#!/usr/bin/env python3
"""
Script để cập nhật giá mới nhất cho tất cả các mã cổ phiếu trong files daily
"""
import json
import os
import time
from datetime import datetime, timedelta
from vnstock import Vnstock

def main():
    data_dir = './docs/data'
    
    # Daily files
    daily_files = [
        'banks_daily.json',
        'banks_daily_summary.json',
        'realestate_daily.json',
        'realestate_daily_summary.json',
        'securities_daily.json',
        'securities_daily_summary.json',
        'retail_daily.json',
        'retail_daily_summary.json',
        'construction_daily.json',
        'construction_daily_summary.json',
        'energy_daily.json',
        'energy_daily_summary.json',
        'steel_daily.json',
        'steel_daily_summary.json',
        'technology_daily.json',
        'technology_daily_summary.json',
        'oilgas_daily.json',
        'oilgas_daily_summary.json',
        'insurance_daily.json',
        'insurance_daily_summary.json',
        'chemicals_daily.json',
        'chemicals_daily_summary.json',
    ]
    
    print("=== BẮT ĐẦU CẬP NHẬT GIÁ (Daily Files) ===\n")
    
    # Date range for fetching (last 7 days)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    total_updated = 0
    total_failed = 0
    updated_symbols = set()  # Track which symbols we've already fetched
    
    for filename in daily_files:
        file_path = f'{data_dir}/{filename}'
        if not os.path.exists(file_path):
            print(f"⚠️  File không tồn tại: {filename}")
            continue
        
        print(f"\n📂 Xử lý {filename}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'stocks' not in data:
            print(f"   ⚠️  Không tìm thấy key 'stocks'")
            continue
        
        updated_count = 0
        failed_symbols = []
        
        for symbol, stock_data in data['stocks'].items():
            try:
                # Skip if we've already fetched this symbol
                if symbol in updated_symbols:
                    # Just update the timestamp
                    if 'current' in stock_data:
                        stock_data['current']['last_updated'] = datetime.now().isoformat()
                    updated_count += 1
                    continue
                
                # Fetch giá mới nhất từ vnstock
                stock = Vnstock().stock(symbol=symbol, source='VCI')
                quote = stock.quote.history(start=start_date, end=end_date, interval='1D')
                
                if quote is not None and not quote.empty:
                    latest_price = float(quote['close'].iloc[-1]) * 1000  # Giá trả về là nghìn đồng
                    latest_date = quote['time'].iloc[-1]
                    if hasattr(latest_date, 'strftime'):
                        latest_date = latest_date.strftime('%Y-%m-%d')
                    else:
                        latest_date = str(latest_date)[:10]
                    
                    # Get old price for comparison
                    if 'current' in stock_data:
                        old_price = stock_data['current'].get('price', 0)
                    else:
                        old_price = stock_data.get('current_price', 0)
                    
                    # Update price in current object
                    if 'current' in stock_data:
                        stock_data['current']['price'] = latest_price
                        stock_data['current']['last_updated'] = datetime.now().isoformat()
                        stock_data['current']['last_trade_date'] = latest_date
                    else:
                        stock_data['current_price'] = latest_price
                        stock_data['last_updated'] = datetime.now().isoformat()
                    
                    change_pct = ((latest_price - old_price) / old_price * 100) if old_price > 0 else 0
                    
                    if abs(change_pct) > 0.01:
                        print(f"   ✅ {symbol:6} | {old_price:>12,.0f} → {latest_price:>12,.0f} VNĐ ({change_pct:+.2f}%)")
                    else:
                        print(f"   ➖ {symbol:6} | Không đổi: {latest_price:>12,.0f} VNĐ")
                    
                    updated_count += 1
                    total_updated += 1
                    updated_symbols.add(symbol)
                    
                    # Rate limiting
                    time.sleep(0.3)
                else:
                    print(f"   ❌ {symbol:6} | Không lấy được dữ liệu")
                    failed_symbols.append(symbol)
                    total_failed += 1
                    
            except Exception as e:
                print(f"   ❌ {symbol:6} | Lỗi: {str(e)[:50]}")
                failed_symbols.append(symbol)
                total_failed += 1
        
        # Update file metadata
        data['last_updated'] = datetime.now().isoformat()
        
        # Lưu lại file
        if updated_count > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"   💾 Đã lưu {updated_count} mã trong {filename}")
        
        if failed_symbols:
            print(f"   ⚠️  Thất bại: {', '.join(failed_symbols[:5])}{'...' if len(failed_symbols) > 5 else ''}")
    
    print(f"\n\n=== TỔNG KẾT ===")
    print(f"✅ Cập nhật thành công: {len(updated_symbols)} mã riêng biệt")
    print(f"❌ Thất bại: {total_failed} lần")
    print(f"📅 Hoàn thành lúc: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()
