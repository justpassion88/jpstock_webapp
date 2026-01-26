"""
Data Fetcher for Vietnamese Bank Stocks
Sử dụng vnstock để lấy dữ liệu P/B và giá cổ phiếu
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd

from config import BANK_SYMBOLS, BANK_NAMES, DATA_SOURCE, OUTPUT_DIR

# Rate limiting: 180 requests per minute for Bronze tier
# Có thể giảm delay xuống còn 0.5s
REQUEST_DELAY = 0.5  # seconds between requests (safe for 180 req/min)


def fetch_stock_price(symbol: str, years: int = 10) -> Optional[pd.DataFrame]:
    """
    Lấy giá lịch sử của cổ phiếu
    
    Args:
        symbol: Mã cổ phiếu
        years: Số năm lịch sử cần lấy
    
    Returns:
        DataFrame với columns: time, open, high, low, close, volume
    """
    try:
        from vnstock import Vnstock
        
        stock = Vnstock().stock(symbol=symbol, source=DATA_SOURCE)
        
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=years * 365)).strftime("%Y-%m-%d")
        
        df = stock.quote.history(start=start_date, end=end_date, interval="1D")
        
        if df is not None and not df.empty:
            print(f"  ✓ Fetched {len(df)} price records for {symbol}")
            return df
        else:
            print(f"  ✗ No price data for {symbol}")
            return None
            
    except Exception as e:
        print(f"  ✗ Error fetching price for {symbol}: {e}")
        return None


def fetch_financial_ratios(symbol: str) -> Optional[pd.DataFrame]:
    """
    Lấy chỉ số tài chính (P/B, P/E, ROE, etc.) từ vnstock
    
    Args:
        symbol: Mã cổ phiếu
    
    Returns:
        DataFrame với các chỉ số tài chính theo năm
    """
    try:
        from vnstock import Vnstock
        
        stock = Vnstock().stock(symbol=symbol, source=DATA_SOURCE)
        
        # Lấy ratio theo năm
        df = stock.finance.ratio(period="year", lang="vi")
        
        if df is not None and not df.empty:
            print(f"  ✓ Fetched financial ratios for {symbol}: {len(df)} periods")
            return df
        else:
            print(f"  ✗ No financial ratios for {symbol}")
            return None
            
    except Exception as e:
        print(f"  ✗ Error fetching ratios for {symbol}: {e}")
        return None


def fetch_company_overview(symbol: str) -> Optional[Dict]:
    """
    Lấy thông tin tổng quan công ty
    
    Args:
        symbol: Mã cổ phiếu
    
    Returns:
        Dict với thông tin công ty
    """
    try:
        from vnstock import Vnstock
        
        stock = Vnstock().stock(symbol=symbol, source=DATA_SOURCE)
        overview = stock.company.overview()
        
        if overview is not None and not overview.empty:
            # Convert to dict
            result = overview.iloc[0].to_dict() if len(overview) > 0 else {}
            print(f"  ✓ Fetched overview for {symbol}")
            return result
        else:
            return {"symbol": symbol, "name": BANK_NAMES.get(symbol, symbol)}
            
    except Exception as e:
        print(f"  ✗ Error fetching overview for {symbol}: {e}")
        return {"symbol": symbol, "name": BANK_NAMES.get(symbol, symbol)}


def fetch_all_bank_data() -> Dict:
    """
    Lấy tất cả dữ liệu cho các ngân hàng
    
    Returns:
        Dict chứa dữ liệu tất cả ngân hàng
    """
    all_data = {
        "last_updated": datetime.now().isoformat(),
        "banks": {}
    }
    
    total = len(BANK_SYMBOLS)
    
    for idx, symbol in enumerate(BANK_SYMBOLS, 1):
        print(f"\n[{idx}/{total}] Fetching data for {symbol} ({BANK_NAMES.get(symbol, '')})...")
        
        bank_data = {
            "symbol": symbol,
            "name": BANK_NAMES.get(symbol, symbol),
            "overview": None,
            "price_history": None,
            "financial_ratios": None,
            "pb_history": None,
        }
        
        # Fetch overview
        time.sleep(REQUEST_DELAY)
        overview = fetch_company_overview(symbol)
        if overview:
            bank_data["overview"] = overview
        
        # Fetch price history
        time.sleep(REQUEST_DELAY)
        price_df = fetch_stock_price(symbol, years=15)
        if price_df is not None:
            # Convert to list of dicts for JSON - only keep essential columns
            price_cols = ['time', 'open', 'high', 'low', 'close', 'volume']
            available_cols = [c for c in price_cols if c in price_df.columns]
            bank_data["price_history"] = price_df[available_cols].to_dict(orient="records")
            # Get current price
            bank_data["current_price"] = float(price_df["close"].iloc[-1]) if len(price_df) > 0 else None
        
        # Fetch financial ratios
        time.sleep(REQUEST_DELAY)
        ratios_df = fetch_financial_ratios(symbol)
        if ratios_df is not None:
            # Don't save raw ratios (MultiIndex causes JSON issues)
            # Only extract P/B history
            pb_history = extract_pb_history(ratios_df)
            if pb_history:
                bank_data["pb_history"] = pb_history
        
        all_data["banks"][symbol] = bank_data
    
    return all_data


def extract_pb_history(ratios_df: pd.DataFrame) -> Optional[List[Dict]]:
    """
    Trích xuất lịch sử P/B từ DataFrame ratios
    
    Args:
        ratios_df: DataFrame chứa các chỉ số tài chính
    
    Returns:
        List of dicts với year và P/B value
    """
    try:
        pb_history = []
        
        # Xử lý MultiIndex columns từ vnstock
        if isinstance(ratios_df.columns, pd.MultiIndex):
            # Tìm cột P/B trong MultiIndex
            pb_col = None
            year_col = None
            
            for col in ratios_df.columns:
                col_str = str(col).lower()
                if 'p/b' in col_str:
                    pb_col = col
                if 'năm' in col_str or 'year' in col_str:
                    year_col = col
            
            if pb_col is None:
                # Thử tìm bằng cách khác
                for col in ratios_df.columns:
                    if len(col) >= 2 and 'P/B' in str(col[1]):
                        pb_col = col
                    if len(col) >= 2 and ('Năm' in str(col[1]) or 'Year' in str(col[1])):
                        year_col = col
            
            if pb_col is not None and year_col is not None:
                for _, row in ratios_df.iterrows():
                    try:
                        year = int(row[year_col])
                        pb_value = row[pb_col]
                        if pd.notna(pb_value) and pb_value > 0:
                            pb_history.append({"year": year, "pb": float(pb_value)})
                    except (ValueError, TypeError):
                        continue
        else:
            # Xử lý DataFrame thường
            # Tìm cột P/B
            pb_col = None
            year_col = None
            
            for col in ratios_df.columns:
                col_lower = str(col).lower()
                if 'p/b' in col_lower or col_lower == 'pb':
                    pb_col = col
                if 'year' in col_lower or 'năm' in col_lower:
                    year_col = col
            
            if pb_col is not None and year_col is not None:
                for _, row in ratios_df.iterrows():
                    try:
                        year = int(row[year_col])
                        pb_value = row[pb_col]
                        if pd.notna(pb_value) and pb_value > 0:
                            pb_history.append({"year": year, "pb": float(pb_value)})
                    except (ValueError, TypeError):
                        continue
        
        # Sắp xếp theo năm
        pb_history.sort(key=lambda x: x["year"])
        
        if pb_history:
            print(f"    ✓ Extracted {len(pb_history)} years of P/B data")
            return pb_history
        else:
            print(f"    ⚠ No P/B data extracted")
            return None
        
    except Exception as e:
        print(f"    Error extracting P/B history: {e}")
        return None


def save_raw_data(data: Dict, filename: str = "raw_bank_data.json"):
    """
    Lưu dữ liệu thô vào file JSON
    
    Args:
        data: Dict chứa dữ liệu
        filename: Tên file output
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Custom JSON encoder for datetime and numpy types
    class CustomEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (pd.Timestamp, datetime)):
                return obj.isoformat()
            if hasattr(obj, 'item'):  # numpy types
                return obj.item()
            return super().default(obj)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, cls=CustomEncoder)
    
    print(f"\n✓ Saved raw data to {filepath}")


if __name__ == "__main__":
    print("=" * 60)
    print("JP Stock Webapp - Bank Data Fetcher")
    print("=" * 60)
    
    # Fetch all data
    data = fetch_all_bank_data()
    
    # Save raw data
    save_raw_data(data)
    
    print("\n" + "=" * 60)
    print("Data fetching completed!")
    print("=" * 60)
