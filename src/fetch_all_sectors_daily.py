"""
Fetch Daily P/B Data for ALL Sectors
Script để lấy dữ liệu P/B daily cho tất cả các sectors trong dự án
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd
import numpy as np
from scipy import stats

# Ensure stdout is unbuffered
sys.stdout.reconfigure(line_buffering=True)

# Import sector configs
from config_sectors import SECTORS

# Data source
DATA_SOURCE = "VCI"
OUTPUT_DIR = "../docs/data"
REQUEST_DELAY = 0.35  # seconds between requests (Bronze tier: 180 req/min)
MAX_RETRIES = 3
RATE_LIMIT_WAIT = 35  # seconds to wait when rate limited

# Quarter periods mapping
# BVPS should apply AFTER financial reports are published (typically 30-45 days after quarter end)
QUARTER_START = {1: '-01-01', 2: '-04-01', 3: '-07-01', 4: '-10-01'}
QUARTER_END = {1: '-03-31', 2: '-06-30', 3: '-09-30', 4: '-12-31'}
REPORT_PUBLISH_DELAY_DAYS = 45  # Days after quarter end when reports are typically published


def get_output_dir():
    """Get absolute output directory path"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, OUTPUT_DIR)


def handle_rate_limit(func):
    """Decorator to handle rate limit with retry"""
    def wrapper(*args, **kwargs):
        for attempt in range(MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_str = str(e).lower()
                if 'rate limit' in error_str or 'ratelimit' in error_str or '429' in error_str:
                    if attempt < MAX_RETRIES - 1:
                        print(f"\n    ⏳ Rate limit hit, waiting {RATE_LIMIT_WAIT}s...", end="", flush=True)
                        time.sleep(RATE_LIMIT_WAIT)
                        print(" retrying...", flush=True)
                    else:
                        raise
                else:
                    raise
        return None
    return wrapper


def fetch_daily_prices(symbol: str, years: int = 15) -> Optional[pd.DataFrame]:
    """Lấy giá lịch sử hàng ngày của cổ phiếu"""
    for attempt in range(MAX_RETRIES):
        try:
            from vnstock import Vnstock
            
            stock = Vnstock().stock(symbol=symbol, source=DATA_SOURCE)
            
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=years * 365)).strftime("%Y-%m-%d")
            
            df = stock.quote.history(start=start_date, end=end_date, interval="1D")
            
            if df is not None and not df.empty:
                # Convert giá sang VND (API trả về đơn vị ngàn đồng)
                for col in ['open', 'high', 'low', 'close']:
                    df[col] = df[col] * 1000
                return df
            return None
                
        except Exception as e:
            error_str = str(e).lower()
            if 'rate limit' in error_str or 'ratelimit' in error_str:
                if attempt < MAX_RETRIES - 1:
                    print(f"\n    ⏳ Rate limit, waiting {RATE_LIMIT_WAIT}s...", end="", flush=True)
                    time.sleep(RATE_LIMIT_WAIT)
                    continue
            print(f"    ✗ Error fetching prices: {e}")
            return None
    return None


def fetch_quarterly_bvps(symbol: str) -> Optional[pd.DataFrame]:
    """Lấy BVPS (Book Value Per Share) theo quý từ finance.ratio()"""
    for attempt in range(MAX_RETRIES):
        try:
            from vnstock import Vnstock
            
            stock = Vnstock().stock(symbol=symbol, source=DATA_SOURCE)
            df = stock.finance.ratio(period="quarter", lang="vi")
            
            if df is None or df.empty:
                return None
            
            # Use exact column names (MultiIndex)
            try:
                bvps_col = ('Chỉ tiêu định giá', 'BVPS (VND)')
                year_col = ('Meta', 'Năm')
                quarter_col = ('Meta', 'Kỳ')
                
                # Verify columns exist
                _ = df[bvps_col]
                _ = df[year_col]
                _ = df[quarter_col]
            except KeyError:
                # Fallback: search for columns
                bvps_col = year_col = quarter_col = None
                for col in df.columns:
                    if isinstance(col, tuple):
                        col_str = str(col[1]).upper() if len(col) > 1 else str(col[0]).upper()
                        if 'BVPS' in col_str:
                            bvps_col = col
                        elif col == ('Meta', 'Năm'):
                            year_col = col
                        elif col == ('Meta', 'Kỳ'):
                            quarter_col = col
                
                if not all([bvps_col, year_col, quarter_col]):
                    return None
            
            result = pd.DataFrame({
                'year': pd.to_numeric(df[year_col], errors='coerce').astype('Int64'),
                'quarter': pd.to_numeric(df[quarter_col], errors='coerce').astype('Int64'),
                'bvps': pd.to_numeric(df[bvps_col], errors='coerce')
            })
            
            # Remove rows with NaN
            result = result.dropna(subset=['year', 'quarter', 'bvps'])
            
            if result.empty:
                return None
            
            result['year'] = result['year'].astype(int)
            result['quarter'] = result['quarter'].astype(int)
            
            # CRITICAL FIX: BVPS chỉ nên được áp dụng SAU KHI báo cáo tài chính được công bố
            # Thông thường là 30-45 ngày sau khi kết thúc quý
            result['quarter_end'] = result.apply(
                lambda row: f"{int(row['year'])}{QUARTER_END[int(row['quarter'])]}", axis=1
            )
            result['quarter_end'] = pd.to_datetime(result['quarter_end'], format='%Y-%m-%d')
            result['apply_from'] = result['quarter_end'] + pd.Timedelta(days=REPORT_PUBLISH_DELAY_DAYS)
            result = result.sort_values('apply_from').reset_index(drop=True)
            result = result[result['bvps'] > 0]
            
            return result if not result.empty else None
                
        except Exception as e:
            error_str = str(e).lower()
            if 'rate limit' in error_str or 'ratelimit' in error_str:
                if attempt < MAX_RETRIES - 1:
                    print(f"\n    ⏳ Rate limit, waiting {RATE_LIMIT_WAIT}s...", end="", flush=True)
                    time.sleep(RATE_LIMIT_WAIT)
                    continue
            # Don't print error for simple missing data
            return None
    return None


def fetch_realtime_data(symbol: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Lấy dữ liệu realtime: giá, P/B, BVPS"""
    for attempt in range(MAX_RETRIES):
        try:
            from vnstock import Vnstock
            
            stock = Vnstock().stock(symbol=symbol, source=DATA_SOURCE)
            ratio_sum = stock.company.ratio_summary()
            
            if ratio_sum is not None and not ratio_sum.empty:
                current_pb = float(ratio_sum['pb'].iloc[0]) if 'pb' in ratio_sum.columns else None
                current_bvps = float(ratio_sum['bvps'].iloc[0]) if 'bvps' in ratio_sum.columns else None
                
                trading = stock.company.trading_stats()
                current_price = float(trading['close_price'].iloc[0]) if trading is not None else None
                
                return current_price, current_pb, current_bvps
            
            return None, None, None
                
        except Exception as e:
            error_str = str(e).lower()
            if 'rate limit' in error_str or 'ratelimit' in error_str:
                if attempt < MAX_RETRIES - 1:
                    print(f"\n    ⏳ Rate limit, waiting {RATE_LIMIT_WAIT}s...", end="", flush=True)
                    time.sleep(RATE_LIMIT_WAIT)
                    continue
            return None, None, None
    return None, None, None


def calculate_daily_pb(price_df: pd.DataFrame, bvps_df: pd.DataFrame) -> pd.DataFrame:
    """Tính P/B cho từng ngày"""
    if price_df is None or bvps_df is None:
        return pd.DataFrame()
    
    try:
        prices = price_df.copy()
        prices['date'] = pd.to_datetime(prices['time'])
        prices = prices.sort_values('date')
        
        def get_bvps_for_date(date, bvps_df):
            available = bvps_df[bvps_df['apply_from'] <= date]
            if len(available) > 0:
                return available.iloc[-1]['bvps']
            return None
        
        prices['bvps'] = prices['date'].apply(lambda d: get_bvps_for_date(d, bvps_df))
        prices['pb'] = prices['close'] / prices['bvps']
        
        result = prices[['date', 'close', 'bvps', 'pb']].dropna()
        result.columns = ['date', 'price', 'bvps', 'pb']
        
        return result
        
    except Exception as e:
        return pd.DataFrame()


def calculate_pb_statistics(daily_pb_df: pd.DataFrame) -> Dict:
    """Tính toán thống kê P/B"""
    if daily_pb_df.empty:
        return {}
    
    try:
        pb_values = daily_pb_df['pb'].values
        
        return {
            "count": len(pb_values),
            "min": float(np.min(pb_values)),
            "max": float(np.max(pb_values)),
            "mean": float(np.mean(pb_values)),
            "median": float(np.median(pb_values)),
            "std": float(np.std(pb_values)),
            "percentiles": {
                "p5": float(np.percentile(pb_values, 5)),
                "p10": float(np.percentile(pb_values, 10)),
                "p25": float(np.percentile(pb_values, 25)),
                "p50": float(np.percentile(pb_values, 50)),
                "p75": float(np.percentile(pb_values, 75)),
                "p90": float(np.percentile(pb_values, 90)),
                "p95": float(np.percentile(pb_values, 95)),
            }
        }
    except:
        return {}


def calculate_historical_returns(daily_pb_df: pd.DataFrame) -> Dict:
    """Tính lợi nhuận lịch sử theo vùng P/B"""
    if daily_pb_df.empty or len(daily_pb_df) < 365:
        return {}
    
    try:
        df = daily_pb_df.copy()
        df = df.sort_values('date').reset_index(drop=True)
        
        df['pb_percentile'] = df['pb'].apply(
            lambda x: stats.percentileofscore(df['pb'].values, x)
        )
        
        holding_days = [30, 90, 180, 365]
        for days in holding_days:
            df[f'return_{days}d'] = df['price'].shift(-days) / df['price'] - 1
        
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
        
        zone_stats = {}
        for zone in ['extremely_cheap', 'cheap', 'fair', 'expensive', 'extremely_expensive']:
            zone_df = df[df['zone'] == zone]
            if len(zone_df) > 0:
                zone_data = {
                    "count": len(zone_df),
                    "pb_range": {
                        "min": float(zone_df['pb'].min()),
                        "max": float(zone_df['pb'].max()),
                        "avg": float(zone_df['pb'].mean()),
                    },
                    "returns": {}
                }
                
                for days in holding_days:
                    returns = zone_df[f'return_{days}d'].dropna()
                    if len(returns) > 0:
                        zone_data["returns"][f"{days}d"] = {
                            "avg": float(returns.mean() * 100),
                            "median": float(returns.median() * 100),
                            "min": float(returns.min() * 100),
                            "max": float(returns.max() * 100),
                            "win_rate": float((returns > 0).mean() * 100),
                            "sample_size": len(returns),
                        }
                
                zone_stats[zone] = zone_data
        
        return zone_stats
    except:
        return {}


def get_current_valuation(current_pb: float, pb_stats: Dict) -> Dict:
    """Xác định vùng định giá hiện tại"""
    if not pb_stats or 'percentiles' not in pb_stats or current_pb is None:
        return {}
    
    try:
        p = pb_stats['percentiles']
        
        if current_pb <= p['p10']:
            zone, signal = 'extremely_cheap', 'STRONG_BUY'
        elif current_pb <= p['p25']:
            zone, signal = 'cheap', 'BUY'
        elif current_pb <= p['p75']:
            zone, signal = 'fair', 'HOLD'
        elif current_pb <= p['p90']:
            zone, signal = 'expensive', 'SELL'
        else:
            zone, signal = 'extremely_expensive', 'STRONG_SELL'
        
        # Estimate percentile
        all_percentiles = [5, 10, 25, 50, 75, 90, 95]
        all_values = [p['p5'], p['p10'], p['p25'], p['p50'], p['p75'], p['p90'], p['p95']]
        percentile = 50
        
        for i, (pct, val) in enumerate(zip(all_percentiles, all_values)):
            if current_pb <= val:
                if i == 0:
                    percentile = pct
                else:
                    prev_pct, prev_val = all_percentiles[i-1], all_values[i-1]
                    if val != prev_val:
                        percentile = prev_pct + (pct - prev_pct) * (current_pb - prev_val) / (val - prev_val)
                    else:
                        percentile = pct
                break
        
        return {
            "zone": zone,
            "signal": signal,
            "percentile": round(percentile, 1),
            "pb_thresholds": {
                "extremely_cheap": p['p10'],
                "cheap": p['p25'],
                "fair_high": p['p75'],
                "expensive": p['p90'],
            }
        }
    except:
        return {}


def fetch_single_stock_daily(symbol: str, name: str, years: int = 15) -> Dict:
    """Fetch và xử lý data daily cho một cổ phiếu"""
    stock_data = {
        "symbol": symbol,
        "name": name,
        "data_type": "daily",
        "years_of_data": years,
        "current": {
            "price": None,
            "pb_vnstock": None,  # Official P/B from vnstock (preferred for current valuation)
            "pb_calculated": None,  # Manual calculation using latest BVPS (for consistency check)
            "bvps": None,
            "pb_source": "vnstock"  # Which P/B to use: 'vnstock' (more accurate) or 'calculated'
        },
        "valuation": {},
        "statistics": {},
        "historical_returns": {},
        "daily_data": [],
        "data_quality": {  # NEW: Data quality metrics
            "latest_date": None,
            "data_age_days": None,
            "bvps_latest_quarter": None,
            "bvps_age_days": None
        }
    }
    
    try:
        # 1. Fetch realtime data
        time.sleep(REQUEST_DELAY)
        current_price, current_pb_vnstock, current_bvps = fetch_realtime_data(symbol)
        stock_data["current"]["price"] = current_price
        stock_data["current"]["pb_vnstock"] = current_pb_vnstock  # Official vnstock P/B
        stock_data["current"]["bvps"] = current_bvps
        
        # Calculate P/B manually for comparison (if we have price and BVPS)
        if current_price and current_bvps and current_bvps > 0:
            stock_data["current"]["pb_calculated"] = round(current_price / current_bvps, 3)
        
        # Use vnstock P/B as primary source (more accurate, accounts for all adjustments)
        current_pb = current_pb_vnstock if current_pb_vnstock else stock_data["current"]["pb_calculated"]
        
        # 2. Fetch daily prices
        time.sleep(REQUEST_DELAY)
        price_df = fetch_daily_prices(symbol, years)
        
        # 3. Fetch quarterly BVPS
        time.sleep(REQUEST_DELAY)
        bvps_df = fetch_quarterly_bvps(symbol)
        
        if price_df is not None and bvps_df is not None:
            # 4. Calculate daily P/B
            daily_pb_df = calculate_daily_pb(price_df, bvps_df)
            
            if not daily_pb_df.empty:
                # 5. Calculate statistics
                stock_data["statistics"] = calculate_pb_statistics(daily_pb_df)
                
                # 6. Calculate historical returns
                stock_data["historical_returns"] = calculate_historical_returns(daily_pb_df)
                
                # 7. Get current valuation
                if current_pb:
                    stock_data["valuation"] = get_current_valuation(current_pb, stock_data["statistics"])
                
                # 8. Add data quality metrics
                latest_date = daily_pb_df['date'].max()
                stock_data["data_quality"]["latest_date"] = latest_date.strftime('%Y-%m-%d')
                stock_data["data_quality"]["data_age_days"] = (datetime.now() - latest_date).days
                
                if not bvps_df.empty:
                    latest_bvps_date = bvps_df['quarter_end'].max()
                    stock_data["data_quality"]["bvps_latest_quarter"] = latest_bvps_date.strftime('%Y-%m-%d')
                    stock_data["data_quality"]["bvps_age_days"] = (datetime.now() - latest_bvps_date).days
                
                # 9. Store ALL daily data (REMOVED 3-year limit for complete history)
                # IMPORTANT: Lưu toàn bộ lịch sử để có đủ context cho phân tích dài hạn
                stock_data["daily_data"] = [
                    {
                        "date": row['date'].strftime('%Y-%m-%d'),
                        "price": round(row['price'], 0),
                        "pb": round(row['pb'], 3),
                        "bvps": round(row['bvps'], 0)  # Add BVPS to track which quarterly value was used
                    }
                    for _, row in daily_pb_df.iterrows()
                ]
                
                return stock_data, len(stock_data['daily_data'])
        
    except Exception as e:
        print(f"    ✗ Error: {e}")
    
    return stock_data, 0


def fetch_sector_daily(sector_name: str, symbols: Dict[str, str], years: int = 15) -> Dict:
    """Fetch daily data cho một sector"""
    print(f"\n{'='*60}")
    print(f"SECTOR: {sector_name.upper()}")
    print(f"Symbols: {len(symbols)}")
    print('='*60)
    
    sector_data = {
        "last_updated": datetime.now().isoformat(),
        "data_type": "daily",
        "data_source": DATA_SOURCE,
        "sector": sector_name,
        "years_of_history": years,
        "total_stocks": len(symbols),
        "stocks": {}
    }
    
    for idx, (symbol, name) in enumerate(symbols.items(), 1):
        print(f"  [{idx}/{len(symbols)}] {symbol} ({name})...", end=" ", flush=True)
        
        stock_data, daily_count = fetch_single_stock_daily(symbol, name, years)
        sector_data["stocks"][symbol] = stock_data
        
        if daily_count > 0:
            pb = stock_data["current"].get("pb")
            pb_str = f"P/B={pb:.2f}" if pb else "P/B=N/A"
            print(f"✓ {daily_count} days, {pb_str}")
        else:
            print("✗ No data")
    
    return sector_data


def save_sector_data(data: Dict, filename: str):
    """Lưu data sector vào JSON"""
    output_dir = get_output_dir()
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"  ✓ Saved to {filepath}")
    return filepath


def create_sector_summary(full_data: Dict) -> Dict:
    """Tạo summary cho một sector (không có daily_data)"""
    summary = {
        "last_updated": full_data["last_updated"],
        "data_type": "daily_summary",
        "data_source": full_data.get("data_source", DATA_SOURCE),
        "sector": full_data.get("sector", ""),
        "total_stocks": full_data["total_stocks"],
        "stocks": {}
    }
    
    for symbol, stock in full_data["stocks"].items():
        summary["stocks"][symbol] = {
            "symbol": stock["symbol"],
            "name": stock["name"],
            "current": stock["current"],
            "valuation": stock["valuation"],
            "statistics": stock["statistics"],
            "historical_returns": stock["historical_returns"],
        }
    
    return summary


def main():
    print("=" * 70)
    print("JP Stock Webapp - Fetch ALL Sectors Daily P/B Data")
    print(f"Data Source: {DATA_SOURCE}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    years = 15
    total_stocks = sum(len(cfg['symbols']) for cfg in SECTORS.values())
    print(f"\nTotal sectors: {len(SECTORS)}")
    print(f"Total stocks: {total_stocks}")
    
    # Mapping sector_key to output file name
    sector_output_files = {
        "banks": "banks",
        "realestate": "realestate",
        "securities": "securities",
        "energy": "energy",
        "oilgas": "oilgas",
        "steel": "steel",
        "construction": "construction",
        "insurance": "insurance",
        "retail": "retail",
        "technology": "technology",
        "chemicals": "chemicals",
    }
    
    # Process each sector
    for sector_key, sector_config in SECTORS.items():
        sector_name = sector_config['name']
        symbols_list = sector_config['symbols']
        
        # Create symbols dict with names (symbol -> name mapping)
        # For simplicity, use symbol as name if not available
        symbols = {s: s for s in symbols_list}
        
        output_base = sector_output_files.get(sector_key, sector_key)
        
        # Fetch sector data
        sector_data = fetch_sector_daily(sector_name, symbols, years)
        
        # Save full data
        save_sector_data(sector_data, f"{output_base}_daily.json")
        
        # Save summary
        summary = create_sector_summary(sector_data)
        save_sector_data(summary, f"{output_base}_daily_summary.json")
    
    print("\n" + "=" * 70)
    print("ALL SECTORS COMPLETED!")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)


if __name__ == "__main__":
    main()
