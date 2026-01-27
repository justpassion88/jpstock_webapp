#!/usr/bin/env python3
"""
Script để cập nhật giá mới nhất cho tất cả các mã cổ phiếu trong dự án
"""
import json
import os
import time
from datetime import datetime
from vnstock import Vnstock

def main():
    data_dir = './docs/data'
    sectors = ['banks_v2', 'retail', 'chemicals', 'construction', 'energy', 
               'insurance', 'oilgas', 'realestate', 'securities', 'steel', 'technology']
    
    print("=== BẮT ĐẦU CẬP NHẬT GIÁ ===\n")
    
    total_updated = 0
    total_failed = 0
    
    for sector in sectors:
        file_path = f'{data_dir}/{sector}.json'
        if not os.path.exists(file_path):
            print(f"⚠️  File không tồn tại: {sector}.json")
            continue
        
        print(f"\n📂 Xử lý {sector}.json...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        stocks_key = 'banks' if sector == 'banks_v2' else 'stocks'
        
        if stocks_key not in data:
            print(f"   ⚠️  Không tìm thấy key '{stocks_key}'")
            continue
        
        updated_count = 0
        failed_symbols = []
        
        for symbol in data[stocks_key].keys():
            try:
                # Fetch giá mới nhất từ vnstock
                stock = Vnstock().stock(symbol=symbol, source='VCI')
                quote = stock.quote.history(start='2026-01-20', end='2026-01-27', interval='1D')
                
                if quote is not None and not quote.empty:
                    latest_price = float(quote['close'].iloc[-1]) * 1000  # Giá trả về là nghìn đồng
                    old_price = data[stocks_key][symbol].get('current_price', 'None')
                    
                    # Cập nhật giá mới
                    data[stocks_key][symbol]['current_price'] = latest_price
                    data[stocks_key][symbol]['last_updated'] = datetime.now().isoformat()
                    
                    if old_price != latest_price and old_price != 'None':
                        print(f"   ✅ {symbol:6} | {old_price:>10,.0f} → {latest_price:>10,.0f} VNĐ")
                    elif old_price == 'None':
                        print(f"   ✅ {symbol:6} | (Mới) → {latest_price:>10,.0f} VNĐ")
                    else:
                        print(f"   ➖ {symbol:6} | Giá không đổi: {latest_price:>10,.0f} VNĐ")
                    
                    updated_count += 1
                    total_updated += 1
                    
                    # Rate limiting
                    time.sleep(0.5)
                else:
                    print(f"   ❌ {symbol:6} | Không lấy được dữ liệu")
                    failed_symbols.append(symbol)
                    total_failed += 1
                    
            except Exception as e:
                print(f"   ❌ {symbol:6} | Lỗi: {str(e)}")
                failed_symbols.append(symbol)
                total_failed += 1
        
        # Lưu lại file
        if updated_count > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"   💾 Đã lưu {updated_count} mã trong {sector}.json")
        
        if failed_symbols:
            print(f"   ⚠️  Thất bại: {', '.join(failed_symbols)}")
    
    print(f"\n\n=== TỔNG KẾT ===")
    print(f"✅ Cập nhật thành công: {total_updated} mã")
    print(f"❌ Thất bại: {total_failed} mã")
    print(f"📅 Hoàn thành lúc: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()
