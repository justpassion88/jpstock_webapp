"""
Data Fetcher V3 - Daily P/B for Vietnamese Bank Stocks
- Tính P/B theo NGÀY (daily) thay vì quý
- Sử dụng BVPS quarterly kết hợp với giá daily
- Hỗ trợ phân tích chi tiết hơn với dữ liệu granular
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd
import numpy as np
from scipy import stats

from config import BANK_SYMBOLS, BANK_NAMES, DATA_SOURCE, OUTPUT_DIR

# Rate limiting: 180 requests per minute for Bronze tier
REQUEST_DELAY = 0.5  # seconds between requests

# Quarter periods mapping
QUARTER_START = {1: '-01-01', 2: '-04-01', 3: '-07-01', 4: '-10-01'}
QUARTER_END = {1: '-03-31', 2: '-06-30', 3: '-09-30', 4: '-12-31'}


def fetch_daily_prices(symbol: str, years: int = 15) -> Optional[pd.DataFrame]:
    """
    Lấy giá lịch sử hàng ngày của cổ phiếu
    
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
            # Convert giá sang VND (API trả về đơn vị ngàn đồng)
            for col in ['open', 'high', 'low', 'close']:
                df[col] = df[col] * 1000
            
            print(f"  ✓ Fetched {len(df)} daily price records")
            return df
        return None
            
    except Exception as e:
        print(f"  ✗ Error fetching daily prices: {e}")
        return None


def fetch_quarterly_bvps(symbol: str) -> Optional[pd.DataFrame]:
    """
    Lấy BVPS (Book Value Per Share) theo quý
    
    Args:
        symbol: Mã cổ phiếu
    
    Returns:
        DataFrame với columns: year, quarter, bvps, apply_from
    """
    try:
        from vnstock import Vnstock
        
        stock = Vnstock().stock(symbol=symbol, source=DATA_SOURCE)
        
        # Lấy ratio theo quý
        df = stock.finance.ratio(period="quarter", lang="vi")
        
        if df is None or df.empty:
            print(f"  ⚠ No quarterly ratio data")
            return None
        
        # Tìm columns cần thiết
        bvps_col = year_col = quarter_col = None
        for col in df.columns:
            col_str = str(col).lower()
            if 'bvps' in col_str:
                bvps_col = col
            elif col == ('Meta', 'Năm') or 'năm' in col_str:
                year_col = col
            elif col == ('Meta', 'Kỳ') or 'kỳ' in col_str:
                quarter_col = col
        
        if not all([bvps_col, year_col, quarter_col]):
            # Fallback: try standard column names
            try:
                bvps_col = ('Chỉ tiêu định giá', 'BVPS (VND)')
                year_col = ('Meta', 'Năm')
                quarter_col = ('Meta', 'Kỳ')
                _ = df[bvps_col]  # Test if columns exist
            except KeyError:
                print(f"  ⚠ Cannot find BVPS/Year/Quarter columns")
                return None
        
        # Extract data
        result = pd.DataFrame({
            'year': df[year_col].astype(float).astype(int),
            'quarter': df[quarter_col].astype(float).astype(int),
            'bvps': df[bvps_col].astype(float)
        })
        
        # Tạo ngày áp dụng BVPS (ngày đầu quý)
        result['apply_from'] = result.apply(
            lambda row: f"{int(row['year'])}{QUARTER_START[int(row['quarter'])]}", axis=1
        )
        result['apply_from'] = pd.to_datetime(result['apply_from'], format='%Y-%m-%d')
        result = result.sort_values('apply_from').reset_index(drop=True)
        
        # Lọc BVPS hợp lệ (> 0)
        result = result[result['bvps'] > 0]
        
        print(f"  ✓ Fetched {len(result)} quarterly BVPS records")
        return result
            
    except Exception as e:
        print(f"  ✗ Error fetching quarterly BVPS: {e}")
        return None


def fetch_realtime_data(symbol: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """
    Lấy dữ liệu realtime: giá, P/B, BVPS
    
    Returns:
        Tuple (current_price, current_pb, current_bvps)
    """
    try:
        from vnstock import Vnstock
        
        stock = Vnstock().stock(symbol=symbol, source=DATA_SOURCE)
        
        # Lấy từ ratio_summary (có P/B và BVPS realtime)
        ratio_sum = stock.company.ratio_summary()
        
        if ratio_sum is not None and not ratio_sum.empty:
            current_pb = float(ratio_sum['pb'].iloc[0]) if 'pb' in ratio_sum.columns else None
            current_bvps = float(ratio_sum['bvps'].iloc[0]) if 'bvps' in ratio_sum.columns else None
            
            # Lấy giá từ trading_stats
            trading = stock.company.trading_stats()
            current_price = float(trading['close_price'].iloc[0]) if trading is not None else None
            
            print(f"  ✓ Realtime: Price={current_price:,.0f}, P/B={current_pb:.2f}, BVPS={current_bvps:,.0f}")
            return current_price, current_pb, current_bvps
        
        return None, None, None
            
    except Exception as e:
        print(f"  ⚠ Error fetching realtime data: {e}")
        return None, None, None


def calculate_daily_pb(price_df: pd.DataFrame, bvps_df: pd.DataFrame) -> pd.DataFrame:
    """
    Tính P/B cho từng ngày dựa trên giá daily và BVPS quarterly
    
    Logic: Với mỗi ngày giao dịch, sử dụng BVPS của quý gần nhất đã công bố
    
    Args:
        price_df: DataFrame giá daily
        bvps_df: DataFrame BVPS theo quý
    
    Returns:
        DataFrame với columns: date, price, bvps, pb
    """
    if price_df is None or bvps_df is None:
        return pd.DataFrame()
    
    try:
        # Prepare price data
        prices = price_df.copy()
        prices['date'] = pd.to_datetime(prices['time'])
        prices = prices.sort_values('date')
        
        # Function to get BVPS for a specific date
        def get_bvps_for_date(date, bvps_df):
            """Lấy BVPS của quý gần nhất đã công bố tại thời điểm date"""
            available = bvps_df[bvps_df['apply_from'] <= date]
            if len(available) > 0:
                return available.iloc[-1]['bvps']
            return None
        
        # Calculate P/B for each day
        prices['bvps'] = prices['date'].apply(lambda d: get_bvps_for_date(d, bvps_df))
        prices['pb'] = prices['close'] / prices['bvps']
        
        # Filter valid data
        result = prices[['date', 'close', 'bvps', 'pb']].dropna()
        result.columns = ['date', 'price', 'bvps', 'pb']
        
        print(f"  ✓ Calculated {len(result)} days of P/B data")
        return result
        
    except Exception as e:
        print(f"  ✗ Error calculating daily P/B: {e}")
        return pd.DataFrame()


def calculate_pb_statistics(daily_pb_df: pd.DataFrame) -> Dict:
    """
    Tính toán thống kê P/B từ dữ liệu daily
    
    Returns:
        Dict với percentiles, zones, historical returns
    """
    if daily_pb_df.empty:
        return {}
    
    try:
        pb_values = daily_pb_df['pb'].values
        
        # Basic statistics
        stats_dict = {
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
        
        return stats_dict
        
    except Exception as e:
        print(f"  ⚠ Error calculating statistics: {e}")
        return {}


def calculate_historical_returns(daily_pb_df: pd.DataFrame, holding_days: List[int] = [30, 90, 180, 365]) -> Dict:
    """
    Tính lợi nhuận lịch sử theo từng vùng P/B
    
    Args:
        daily_pb_df: DataFrame với date, price, pb
        holding_days: Danh sách số ngày nắm giữ để tính return
    
    Returns:
        Dict với thống kê return theo vùng P/B
    """
    if daily_pb_df.empty or len(daily_pb_df) < 365:
        return {}
    
    try:
        df = daily_pb_df.copy()
        df = df.sort_values('date').reset_index(drop=True)
        
        # Tính percentile của P/B
        df['pb_percentile'] = df['pb'].apply(
            lambda x: stats.percentileofscore(df['pb'].values, x)
        )
        
        # Tính returns cho các holding periods
        for days in holding_days:
            df[f'return_{days}d'] = df['price'].shift(-days) / df['price'] - 1
        
        # Phân loại vùng P/B
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
        
    except Exception as e:
        print(f"  ⚠ Error calculating historical returns: {e}")
        return {}


def get_current_valuation(current_pb: float, pb_stats: Dict) -> Dict:
    """
    Xác định vùng định giá hiện tại dựa trên P/B
    
    Returns:
        Dict với zone, percentile, signal
    """
    if not pb_stats or 'percentiles' not in pb_stats:
        return {}
    
    try:
        p = pb_stats['percentiles']
        
        # Tính percentile của current P/B
        if current_pb <= p['p10']:
            zone = 'extremely_cheap'
            signal = 'STRONG_BUY'
            percentile = 10
        elif current_pb <= p['p25']:
            zone = 'cheap'
            signal = 'BUY'
            percentile = 25
        elif current_pb <= p['p75']:
            zone = 'fair'
            signal = 'HOLD'
            percentile = 50
        elif current_pb <= p['p90']:
            zone = 'expensive'
            signal = 'SELL'
            percentile = 90
        else:
            zone = 'extremely_expensive'
            signal = 'STRONG_SELL'
            percentile = 95
        
        # Estimate more precise percentile
        all_percentiles = [5, 10, 25, 50, 75, 90, 95]
        all_values = [p['p5'], p['p10'], p['p25'], p['p50'], p['p75'], p['p90'], p['p95']]
        
        for i, (pct, val) in enumerate(zip(all_percentiles, all_values)):
            if current_pb <= val:
                if i == 0:
                    percentile = pct
                else:
                    # Linear interpolation
                    prev_pct, prev_val = all_percentiles[i-1], all_values[i-1]
                    percentile = prev_pct + (pct - prev_pct) * (current_pb - prev_val) / (val - prev_val)
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
        
    except Exception as e:
        print(f"  ⚠ Error determining valuation: {e}")
        return {}


def fetch_single_bank_daily(symbol: str, years: int = 15) -> Dict:
    """
    Fetch và xử lý data daily cho một ngân hàng
    
    Args:
        symbol: Mã cổ phiếu
        years: Số năm dữ liệu lịch sử
    
    Returns:
        Dict với tất cả thông tin cần thiết
    """
    print(f"\nFetching {symbol} ({BANK_NAMES.get(symbol, '')})...")
    
    bank_data = {
        "symbol": symbol,
        "name": BANK_NAMES.get(symbol, symbol),
        "data_type": "daily",
        "years_of_data": years,
        "current": {
            "price": None,
            "pb": None,
            "bvps": None,
        },
        "valuation": {},
        "statistics": {},
        "historical_returns": {},
        "daily_data": [],  # List of {date, price, pb}
    }
    
    try:
        # 1. Fetch realtime data
        time.sleep(REQUEST_DELAY)
        current_price, current_pb, current_bvps = fetch_realtime_data(symbol)
        bank_data["current"]["price"] = current_price
        bank_data["current"]["pb"] = current_pb
        bank_data["current"]["bvps"] = current_bvps
        
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
                bank_data["statistics"] = calculate_pb_statistics(daily_pb_df)
                
                # 6. Calculate historical returns by zone
                bank_data["historical_returns"] = calculate_historical_returns(daily_pb_df)
                
                # 7. Get current valuation
                if current_pb:
                    bank_data["valuation"] = get_current_valuation(current_pb, bank_data["statistics"])
                
                # 8. Store daily data (last 3 years for smaller file size)
                recent_data = daily_pb_df[daily_pb_df['date'] >= (datetime.now() - timedelta(days=3*365))]
                bank_data["daily_data"] = [
                    {
                        "date": row['date'].strftime('%Y-%m-%d'),
                        "price": round(row['price'], 0),
                        "pb": round(row['pb'], 3),
                    }
                    for _, row in recent_data.iterrows()
                ]
                
                print(f"  ✓ Complete: {len(bank_data['daily_data'])} daily records")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    return bank_data


def fetch_all_banks_daily(years: int = 15) -> Dict:
    """
    Fetch daily data cho tất cả ngân hàng
    
    Args:
        years: Số năm dữ liệu lịch sử
    
    Returns:
        Dict với tất cả data
    """
    all_data = {
        "last_updated": datetime.now().isoformat(),
        "data_type": "daily",
        "data_source": DATA_SOURCE,
        "years_of_history": years,
        "total_banks": len(BANK_SYMBOLS),
        "banks": {}
    }
    
    for idx, symbol in enumerate(BANK_SYMBOLS, 1):
        print(f"\n[{idx}/{len(BANK_SYMBOLS)}]", end="")
        bank_data = fetch_single_bank_daily(symbol, years)
        all_data["banks"][symbol] = bank_data
        
        # Progress save every 5 banks
        if idx % 5 == 0:
            save_data(all_data, "banks_daily_progress.json")
    
    return all_data


def save_data(data: Dict, filename: str = "banks_daily.json"):
    """Lưu data vào JSON"""
    # Get absolute path relative to this script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n✓ Saved to {filepath}")
    return filepath


def create_summary_data(full_data: Dict) -> Dict:
    """
    Tạo file summary nhỏ gọn cho frontend (không có daily_data)
    """
    summary = {
        "last_updated": full_data["last_updated"],
        "data_type": "daily_summary",
        "data_source": full_data.get("data_source", DATA_SOURCE),
        "total_banks": full_data["total_banks"],
        "banks": {}
    }
    
    for symbol, bank in full_data["banks"].items():
        summary["banks"][symbol] = {
            "symbol": bank["symbol"],
            "name": bank["name"],
            "current": bank["current"],
            "valuation": bank["valuation"],
            "statistics": bank["statistics"],
            "historical_returns": bank["historical_returns"],
        }
    
    return summary


if __name__ == "__main__":
    print("=" * 60)
    print("JP Stock Webapp - Bank Data Fetcher (Daily P/B)")
    print(f"Data Source: {DATA_SOURCE}")
    print("=" * 60)
    
    # Fetch all data
    data = fetch_all_banks_daily(years=15)
    
    # Save full data
    save_data(data, "banks_daily.json")
    
    # Save summary for frontend
    summary = create_summary_data(data)
    save_data(summary, "banks_daily_summary.json")
    
    print("\n" + "=" * 60)
    print("Data fetching completed!")
    print(f"- Full data: banks_daily.json")
    print(f"- Summary: banks_daily_summary.json")
    print("=" * 60)
