"""
Data Fetcher V2 for Vietnamese Bank Stocks
- Sử dụng P/B theo QUÝ (quarterly) thay vì năm
- Kết hợp giá cổ phiếu với P/B
- Tính toán lợi nhuận thực tế theo vùng P/B
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd
import numpy as np
from scipy import stats

from config import BANK_SYMBOLS, BANK_NAMES, DATA_SOURCE, OUTPUT_DIR

# Rate limiting: 180 requests per minute for Bronze tier
REQUEST_DELAY = 0.5  # seconds between requests

# Quarter end dates mapping
QUARTER_END = {
    1: '-03-31',
    2: '-06-30', 
    3: '-09-30',
    4: '-12-31'
}


def fetch_stock_price(symbol: str, years: int = 15) -> Optional[pd.DataFrame]:
    """Lấy giá lịch sử của cổ phiếu"""
    try:
        from vnstock import Vnstock
        
        stock = Vnstock().stock(symbol=symbol, source=DATA_SOURCE)
        
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=years * 365)).strftime("%Y-%m-%d")
        
        df = stock.quote.history(start=start_date, end=end_date, interval="1D")
        
        if df is not None and not df.empty:
            print(f"  ✓ Fetched {len(df)} price records")
            return df
        return None
            
    except Exception as e:
        print(f"  ✗ Error fetching price: {e}")
        return None


def fetch_quarterly_ratios(symbol: str) -> Optional[pd.DataFrame]:
    """Lấy chỉ số tài chính theo QUÝ"""
    try:
        from vnstock import Vnstock
        
        stock = Vnstock().stock(symbol=symbol, source=DATA_SOURCE)
        
        # Lấy ratio theo QUÝ
        df = stock.finance.ratio(period="quarter", lang="vi")
        
        if df is not None and not df.empty:
            print(f"  ✓ Fetched {len(df)} quarterly ratios")
            return df
        return None
            
    except Exception as e:
        print(f"  ✗ Error fetching ratios: {e}")
        return None


def extract_quarterly_pb(ratios_df: pd.DataFrame, price_df: pd.DataFrame) -> List[Dict]:
    """
    Trích xuất P/B theo quý và kết hợp với giá cổ phiếu
    
    Returns:
        List of dicts với year, quarter, pb, price, date
    """
    try:
        # Tìm columns
        pb_col = year_col = quarter_col = None
        for col in ratios_df.columns:
            col_str = str(col).lower()
            if 'p/b' in col_str:
                pb_col = col
            if 'năm' in col_str:
                year_col = col
            if 'kỳ' in col_str:
                quarter_col = col
        
        if not all([pb_col, year_col, quarter_col]):
            print("  ⚠ Cannot find required columns")
            return []
        
        # Convert price dates
        price_df = price_df.copy()
        price_df['time_str'] = price_df['time'].astype(str)
        
        quarterly_data = []
        
        for _, row in ratios_df.iterrows():
            try:
                year = int(row[year_col])
                quarter = int(row[quarter_col])
                pb = float(row[pb_col])
                
                if pb <= 0:
                    continue
                
                # Tìm ngày cuối quý
                q_end = f"{year}{QUARTER_END[quarter]}"
                
                # Tìm giá gần nhất với ngày cuối quý
                mask = price_df['time_str'] <= q_end
                if mask.any():
                    close_price = float(price_df[mask]['close'].iloc[-1])
                    actual_date = price_df[mask]['time_str'].iloc[-1]
                    
                    quarterly_data.append({
                        "year": year,
                        "quarter": quarter,
                        "period": f"{year}-Q{quarter}",
                        "date": actual_date,
                        "price": close_price,
                        "pb": pb
                    })
            except (ValueError, TypeError, KeyError):
                continue
        
        # Sort by date
        quarterly_data.sort(key=lambda x: (x["year"], x["quarter"]))
        
        if quarterly_data:
            print(f"  ✓ Extracted {len(quarterly_data)} quarters of P/B + Price data")
        
        return quarterly_data
        
    except Exception as e:
        print(f"  ✗ Error extracting quarterly data: {e}")
        return []


def calculate_historical_returns(quarterly_data: List[Dict]) -> Dict:
    """
    Tính toán lợi nhuận thực tế theo vùng P/B từ dữ liệu lịch sử
    
    Returns:
        Dict với thống kê lợi nhuận theo từng vùng P/B
    """
    if len(quarterly_data) < 8:
        return {}
    
    df = pd.DataFrame(quarterly_data)
    
    # Tính percentile của P/B
    df['pb_percentile'] = df['pb'].apply(
        lambda x: stats.percentileofscore(df['pb'].values, x)
    )
    
    # Tính returns (1 năm = 4 quý, 2 năm = 8 quý)
    df['return_1y'] = df['price'].shift(-4) / df['price'] - 1
    df['return_2y'] = df['price'].shift(-8) / df['price'] - 1
    
    # Phân loại vùng
    def classify_zone(percentile):
        if percentile < 10:
            return 'extremely_cheap'
        elif percentile < 25:
            return 'cheap'
        elif percentile < 75:
            return 'fair'
        elif percentile < 90:
            return 'expensive'
        else:
            return 'extremely_expensive'
    
    df['zone'] = df['pb_percentile'].apply(classify_zone)
    
    # Thống kê theo vùng
    zone_stats = {}
    for zone in ['extremely_cheap', 'cheap', 'fair', 'expensive', 'extremely_expensive']:
        zone_df = df[df['zone'] == zone]
        if len(zone_df) > 0:
            returns_1y = zone_df['return_1y'].dropna()
            returns_2y = zone_df['return_2y'].dropna()
            
            zone_stats[zone] = {
                "count": len(zone_df),
                "pb_min": float(zone_df['pb'].min()),
                "pb_max": float(zone_df['pb'].max()),
                "pb_avg": float(zone_df['pb'].mean()),
                "return_1y_avg": float(returns_1y.mean() * 100) if len(returns_1y) > 0 else None,
                "return_1y_median": float(returns_1y.median() * 100) if len(returns_1y) > 0 else None,
                "return_1y_min": float(returns_1y.min() * 100) if len(returns_1y) > 0 else None,
                "return_1y_max": float(returns_1y.max() * 100) if len(returns_1y) > 0 else None,
                "win_rate_1y": float((returns_1y > 0).mean() * 100) if len(returns_1y) > 0 else None,
                "return_2y_avg": float(returns_2y.mean() * 100) if len(returns_2y) > 0 else None,
                "win_rate_2y": float((returns_2y > 0).mean() * 100) if len(returns_2y) > 0 else None,
            }
    
    return zone_stats


def fetch_single_bank(symbol: str) -> Dict:
    """Fetch và xử lý data cho một ngân hàng"""
    from vnstock import Vnstock
    
    print(f"\nFetching {symbol} ({BANK_NAMES.get(symbol, '')})...")
    
    bank_data = {
        "symbol": symbol,
        "name": BANK_NAMES.get(symbol, symbol),
        "current_price": None,
        "current_pb": None,
        "quarterly_data": [],
        "historical_returns": {},
    }
    
    try:
        stock = Vnstock().stock(symbol=symbol, source=DATA_SOURCE)
        
        # Fetch price
        time.sleep(REQUEST_DELAY)
        price_df = fetch_stock_price(symbol)
        
        if price_df is not None:
            bank_data["current_price"] = float(price_df['close'].iloc[-1])
        
        # Fetch quarterly ratios
        time.sleep(REQUEST_DELAY)
        ratios_df = fetch_quarterly_ratios(symbol)
        
        if ratios_df is not None and price_df is not None:
            # Extract quarterly P/B + Price
            quarterly_data = extract_quarterly_pb(ratios_df, price_df)
            bank_data["quarterly_data"] = quarterly_data
            
            # Get current P/B
            if quarterly_data:
                bank_data["current_pb"] = quarterly_data[-1]["pb"]
            
            # Calculate historical returns by zone
            historical_returns = calculate_historical_returns(quarterly_data)
            bank_data["historical_returns"] = historical_returns
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    return bank_data


def fetch_all_banks() -> Dict:
    """Fetch data cho tất cả ngân hàng"""
    all_data = {
        "last_updated": datetime.now().isoformat(),
        "data_type": "quarterly",
        "total_banks": len(BANK_SYMBOLS),
        "banks": {}
    }
    
    for idx, symbol in enumerate(BANK_SYMBOLS, 1):
        print(f"\n[{idx}/{len(BANK_SYMBOLS)}]", end="")
        bank_data = fetch_single_bank(symbol)
        all_data["banks"][symbol] = bank_data
    
    return all_data


def save_data(data: Dict, filename: str = "raw_bank_data_v2.json"):
    """Lưu data vào JSON"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n✓ Saved to {filepath}")


if __name__ == "__main__":
    print("=" * 60)
    print("JP Stock Webapp - Bank Data Fetcher V2 (Quarterly P/B)")
    print("=" * 60)
    
    data = fetch_all_banks()
    save_data(data)
    
    print("\n" + "=" * 60)
    print("Data fetching completed!")
    print("=" * 60)
