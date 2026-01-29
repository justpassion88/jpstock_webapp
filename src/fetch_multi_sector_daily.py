"""
Data Fetcher Daily - Multi Sector
Fetch P/B daily cho tất cả các sector trong dự án
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

from config import DATA_SOURCE, OUTPUT_DIR
from config_sectors import SECTORS

# Rate limiting
REQUEST_DELAY = 0.5

# Quarter periods mapping
QUARTER_START = {1: '-01-01', 2: '-04-01', 3: '-07-01', 4: '-10-01'}


def fetch_daily_prices(symbol: str, years: int = 15) -> Optional[pd.DataFrame]:
    """Lấy giá lịch sử hàng ngày"""
    try:
        from vnstock import Vnstock
        stock = Vnstock().stock(symbol=symbol, source=DATA_SOURCE)
        
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=years * 365)).strftime("%Y-%m-%d")
        
        df = stock.quote.history(start=start_date, end=end_date, interval="1D")
        
        if df is not None and not df.empty:
            # Convert giá sang VND
            for col in ['open', 'high', 'low', 'close']:
                df[col] = df[col] * 1000
            return df
        return None
    except Exception as e:
        print(f"    ✗ Price error: {e}")
        return None


def fetch_quarterly_bvps(symbol: str) -> Optional[pd.DataFrame]:
    """Lấy BVPS theo quý"""
    try:
        from vnstock import Vnstock
        stock = Vnstock().stock(symbol=symbol, source=DATA_SOURCE)
        
        df = stock.finance.ratio(period="quarter", lang="vi")
        
        if df is None or df.empty:
            return None
        
        # Find columns
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
            try:
                bvps_col = ('Chỉ tiêu định giá', 'BVPS (VND)')
                year_col = ('Meta', 'Năm')
                quarter_col = ('Meta', 'Kỳ')
                _ = df[bvps_col]
            except KeyError:
                return None
        
        result = pd.DataFrame({
            'year': df[year_col].astype(float).astype(int),
            'quarter': df[quarter_col].astype(float).astype(int),
            'bvps': df[bvps_col].astype(float)
        })
        
        result['apply_from'] = result.apply(
            lambda row: f"{int(row['year'])}{QUARTER_START[int(row['quarter'])]}", axis=1
        )
        result['apply_from'] = pd.to_datetime(result['apply_from'], format='%Y-%m-%d')
        result = result.sort_values('apply_from').reset_index(drop=True)
        result = result[result['bvps'] > 0]
        
        return result
    except Exception as e:
        print(f"    ✗ BVPS error: {e}")
        return None


def fetch_realtime_data(symbol: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Lấy dữ liệu realtime"""
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
    """Tính thống kê P/B"""
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


def calculate_historical_returns(daily_pb_df: pd.DataFrame, holding_days: List[int] = [30, 90, 180, 365]) -> Dict:
    """Tính lợi nhuận lịch sử theo vùng P/B"""
    if daily_pb_df.empty or len(daily_pb_df) < 365:
        return {}
    
    try:
        df = daily_pb_df.copy()
        df = df.sort_values('date').reset_index(drop=True)
        
        df['pb_percentile'] = df['pb'].apply(
            lambda x: stats.percentileofscore(df['pb'].values, x)
        )
        
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
                    # Filter out infinite values
                    returns = returns[~np.isinf(returns)]
                    if len(returns) > 0:
                        def safe_float(val, default=0):
                            """Convert to float, replacing inf/nan with default"""
                            if np.isnan(val) or np.isinf(val):
                                return default
                            return float(val)
                        
                        zone_data["returns"][f"{days}d"] = {
                            "avg": safe_float(returns.mean() * 100),
                            "median": safe_float(returns.median() * 100),
                            "min": safe_float(returns.min() * 100, -100),
                            "max": safe_float(returns.max() * 100, 100),
                            "win_rate": safe_float((returns > 0).mean() * 100),
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
            zone, signal, percentile = 'extremely_cheap', 'STRONG_BUY', 10
        elif current_pb <= p['p25']:
            zone, signal, percentile = 'cheap', 'BUY', 25
        elif current_pb <= p['p75']:
            zone, signal, percentile = 'fair', 'HOLD', 50
        elif current_pb <= p['p90']:
            zone, signal, percentile = 'expensive', 'SELL', 90
        else:
            zone, signal, percentile = 'extremely_expensive', 'STRONG_SELL', 95
        
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


def fetch_single_stock(symbol: str, years: int = 15) -> Dict:
    """Fetch data cho một cổ phiếu"""
    stock_data = {
        "symbol": symbol,
        "data_type": "daily",
        "current": {"price": None, "pb": None, "bvps": None},
        "valuation": {},
        "statistics": {},
        "historical_returns": {},
        "daily_data": [],
    }
    
    try:
        # Realtime
        time.sleep(REQUEST_DELAY)
        current_price, current_pb, current_bvps = fetch_realtime_data(symbol)
        stock_data["current"]["price"] = current_price
        stock_data["current"]["pb"] = current_pb
        stock_data["current"]["bvps"] = current_bvps
        
        # Daily prices
        time.sleep(REQUEST_DELAY)
        price_df = fetch_daily_prices(symbol, years)
        
        # Quarterly BVPS
        time.sleep(REQUEST_DELAY)
        bvps_df = fetch_quarterly_bvps(symbol)
        
        if price_df is not None and bvps_df is not None:
            # Calculate daily P/B
            daily_pb_df = calculate_daily_pb(price_df, bvps_df)
            
            if not daily_pb_df.empty:
                stock_data["statistics"] = calculate_pb_statistics(daily_pb_df)
                stock_data["historical_returns"] = calculate_historical_returns(daily_pb_df)
                
                if current_pb:
                    stock_data["valuation"] = get_current_valuation(current_pb, stock_data["statistics"])
                
                # Last 3 years of daily data
                recent_data = daily_pb_df[daily_pb_df['date'] >= (datetime.now() - timedelta(days=3*365))]
                stock_data["daily_data"] = [
                    {
                        "date": row['date'].strftime('%Y-%m-%d'),
                        "price": round(row['price'], 0),
                        "pb": round(row['pb'], 3),
                    }
                    for _, row in recent_data.iterrows()
                ]
                
                return stock_data
    except Exception as e:
        print(f"    ✗ Error: {e}")
    
    return stock_data


def fetch_sector(sector_key: str, sector_config: Dict, years: int = 15) -> Dict:
    """Fetch data cho một sector"""
    print(f"\n{'='*60}")
    print(f"📊 {sector_config['name']} ({sector_config['name_en']})")
    print(f"   {len(sector_config['symbols'])} stocks")
    print(f"{'='*60}")
    
    sector_data = {
        "last_updated": datetime.now().isoformat(),
        "sector": sector_key,
        "sector_name": sector_config['name'],
        "sector_name_en": sector_config['name_en'],
        "data_type": "daily",
        "data_source": DATA_SOURCE,
        "years_of_history": years,
        "total_stocks": len(sector_config['symbols']),
        "stocks": {}
    }
    
    for idx, symbol in enumerate(sector_config['symbols'], 1):
        print(f"  [{idx}/{len(sector_config['symbols'])}] {symbol}...", end=" ")
        try:
            stock_data = fetch_single_stock(symbol, years)
            sector_data["stocks"][symbol] = stock_data
            
            if stock_data["current"]["pb"]:
                print(f"✓ P/B={stock_data['current']['pb']:.2f}, {len(stock_data['daily_data'])} days")
            else:
                print("⚠ No P/B data")
        except Exception as e:
            print(f"✗ {e}")
            sector_data["stocks"][symbol] = {"symbol": symbol, "error": str(e)}
    
    return sector_data


def save_sector_data(sector_data: Dict, sector_key: str):
    """Lưu data cho một sector"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)
    
    # Full data
    filename = f"{sector_key}_daily.json"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(sector_data, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"  ✓ Saved to {filepath}")
    return filepath


def create_sector_summary(sector_data: Dict) -> Dict:
    """Tạo summary cho sector"""
    summary = {
        "last_updated": sector_data["last_updated"],
        "sector": sector_data["sector"],
        "sector_name": sector_data["sector_name"],
        "data_type": "daily_summary",
        "total_stocks": sector_data["total_stocks"],
        "stocks": {}
    }
    
    for symbol, stock in sector_data["stocks"].items():
        if "error" not in stock:
            summary["stocks"][symbol] = {
                "symbol": stock["symbol"],
                "current": stock.get("current", {}),
                "valuation": stock.get("valuation", {}),
                "statistics": stock.get("statistics", {}),
                "historical_returns": stock.get("historical_returns", {}),
            }
    
    return summary


def fetch_all_sectors(years: int = 15, sectors_to_fetch: List[str] = None):
    """Fetch tất cả sectors"""
    print("=" * 70)
    print("JP Stock Webapp - Multi-Sector Daily P/B Fetcher")
    print(f"Data Source: {DATA_SOURCE}")
    print(f"Years of history: {years}")
    print("=" * 70)
    
    sectors_list = sectors_to_fetch or list(SECTORS.keys())
    total_stocks = sum(len(SECTORS[s]['symbols']) for s in sectors_list)
    
    print(f"\nTotal: {len(sectors_list)} sectors, {total_stocks} stocks")
    
    all_summaries = {}
    
    for sector_key in sectors_list:
        sector_config = SECTORS[sector_key]
        
        # Fetch sector
        sector_data = fetch_sector(sector_key, sector_config, years)
        
        # Save full data
        save_sector_data(sector_data, sector_key)
        
        # Create and save summary
        summary = create_sector_summary(sector_data)
        all_summaries[sector_key] = summary
    
    # Save combined summary
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, OUTPUT_DIR)
    
    combined_summary = {
        "last_updated": datetime.now().isoformat(),
        "data_type": "all_sectors_summary",
        "data_source": DATA_SOURCE,
        "total_sectors": len(sectors_list),
        "total_stocks": total_stocks,
        "sectors": all_summaries
    }
    
    filepath = os.path.join(output_dir, "all_sectors_daily_summary.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(combined_summary, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n✓ Combined summary saved to {filepath}")
    
    return combined_summary


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch daily P/B data for all sectors')
    parser.add_argument('--years', type=int, default=15, help='Years of historical data')
    parser.add_argument('--sector', type=str, help='Fetch only specific sector')
    parser.add_argument('--list', action='store_true', help='List available sectors')
    
    args = parser.parse_args()
    
    if args.list:
        print("Available sectors:")
        for key, config in SECTORS.items():
            print(f"  {key}: {config['name']} ({len(config['symbols'])} stocks)")
        sys.exit(0)
    
    if args.sector:
        if args.sector in SECTORS:
            fetch_all_sectors(years=args.years, sectors_to_fetch=[args.sector])
        else:
            print(f"Unknown sector: {args.sector}")
            print("Use --list to see available sectors")
    else:
        fetch_all_sectors(years=args.years)
