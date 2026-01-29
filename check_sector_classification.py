#!/usr/bin/env python3
"""
Kiểm tra phân loại ngành sau khi sửa
Xác minh 5 thay đổi đã được áp dụng đúng
"""

import sys
sys.path.insert(0, '/workspaces/jpstock_webapp/src')
from config_sectors import SECTORS

def check_classifications():
    print("=" * 70)
    print("KIỂM TRA PHÂN LOẠI NGÀNH SAU KHI SỬA")
    print("=" * 70)
    
    issues = []
    success = []
    
    # 1. AAA không còn trong Real Estate
    realestate_symbols = SECTORS['realestate']['symbols']
    if 'AAA' not in realestate_symbols:
        success.append("✅ AAA đã xóa khỏi Bất động sản")
    else:
        issues.append("❌ AAA vẫn còn trong Bất động sản")
    
    # 2. VGC có trong Steel
    steel_symbols = SECTORS['steel']['symbols']
    if 'VGC' in steel_symbols:
        success.append("✅ VGC đã thêm vào Thép & Vật liệu")
    else:
        issues.append("❌ VGC không có trong Thép & Vật liệu")
    
    # 3. CSV có trong Construction
    construction_symbols = SECTORS['construction']['symbols']
    if 'CSV' in construction_symbols:
        success.append("✅ CSV đã thêm vào Xây dựng")
    else:
        issues.append("❌ CSV không có trong Xây dựng")
    
    # 4. VGC không còn trong Retail
    retail_symbols = SECTORS['retail']['symbols']
    if 'VGC' not in retail_symbols:
        success.append("✅ VGC đã xóa khỏi Bán lẻ")
    else:
        issues.append("❌ VGC vẫn còn trong Bán lẻ")
    
    # 5. Chemicals: AAA có, CSV và DHC không có
    chemicals_symbols = SECTORS['chemicals']['symbols']
    if 'AAA' in chemicals_symbols:
        success.append("✅ AAA đã thêm vào Hóa chất")
    else:
        issues.append("❌ AAA không có trong Hóa chất")
    
    if 'CSV' not in chemicals_symbols:
        success.append("✅ CSV đã xóa khỏi Hóa chất")
    else:
        issues.append("❌ CSV vẫn còn trong Hóa chất")
    
    if 'DHC' not in chemicals_symbols:
        success.append("✅ DHC duplicate đã xóa khỏi Hóa chất")
    else:
        issues.append("❌ DHC vẫn còn trong Hóa chất (duplicate)")
    
    # DHC vẫn phải có trong Real Estate (đúng)
    if 'DHC' in realestate_symbols:
        success.append("✅ DHC vẫn còn trong Bất động sản (đúng)")
    else:
        issues.append("❌ DHC không có trong Bất động sản (sai)")
    
    print("\nKẾT QUẢ THÀNH CÔNG:")
    for msg in success:
        print(f"  {msg}")
    
    if issues:
        print("\nVẤN ĐỀ CẦN SỬA:")
        for msg in issues:
            print(f"  {msg}")
    else:
        print("\n🎉 TẤT CẢ 8 KIỂM TRA ĐỀU PASS!")
    
    print("\n" + "=" * 70)
    print("THỐNG KÊ SỐ LƯỢNG MÃ THEO NGÀNH:")
    print("=" * 70)
    
    total_stocks = 0
    for sector_key, sector_data in SECTORS.items():
        count = len(sector_data['symbols'])
        total_stocks += count
        print(f"  {sector_data['name']}: {count} mã")
    
    print(f"\n  TỔNG CỘNG: {total_stocks} mã")
    print("=" * 70)
    
    return len(issues) == 0

if __name__ == '__main__':
    success = check_classifications()
    sys.exit(0 if success else 1)
