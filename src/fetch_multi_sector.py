"""
Multi-Sector Data Fetcher
Fetch P/B data for 115+ stocks across 10 sectors
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional
import numpy as np
from vnstock import Vnstock
import warnings
warnings.filterwarnings('ignore')

from config_sectors import SECTORS, get_all_symbols, get_sector_info, DATA_SOURCE

# Rate limiting
API_DELAY = 0.3  # seconds between API calls
MAX_RETRIES = 3


def fetch_stock_data(symbol: str, source: str = DATA_SOURCE) -> Optional[Dict]:
    """Fetch comprehensive data for a single stock"""
    
    for attempt in range(MAX_RETRIES):
        try:
            stock = Vnstock().stock(symbol=symbol, source=source)
            
            # Get financial ratios (P/B history)
            ratios = stock.finance.ratio(period='quarter', lang='en')
            
            if ratios is None or len(ratios) == 0:
                return None
            
            # Flatten multi-index columns
            ratios.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in ratios.columns]
            
            # Find column names
            year_col = 'Meta_yearReport'
            quarter_col = 'Meta_lengthReport'
            pb_cols = [c for c in ratios.columns if 'P/B' in c]
            
            if not pb_cols:
                return None
            pb_col = pb_cols[0]
            
            # Extract P/B history
            pb_history = []
            
            for _, row in ratios.iterrows():
                year = row.get(year_col)
                quarter = row.get(quarter_col)
                pb = row.get(pb_col)
                
                if year and quarter and pb and not np.isnan(pb) and pb > 0:
                    period = f"{int(year)}-Q{int(quarter)}"
                    pb_history.append({
                        "period": period,
                        "pb": round(float(pb), 2),
                        "year": int(year),
                        "quarter": int(quarter)
                    })
            
            if not pb_history:
                return None
            
            # Sort by newest first
            pb_history.sort(key=lambda x: (x['year'], x['quarter']), reverse=True)
            
            # Get price data
            try:
                price_data = stock.quote.history(start='2010-01-01', end=datetime.now().strftime('%Y-%m-%d'))
                if price_data is not None and len(price_data) > 0:
                    # Map prices to quarters
                    price_data['year'] = price_data['time'].dt.year
                    price_data['quarter'] = price_data['time'].dt.quarter
                    
                    quarterly_prices = price_data.groupby(['year', 'quarter']).agg({
                        'close': 'last'
                    }).reset_index()
                    
                    price_map = {}
                    for _, row in quarterly_prices.iterrows():
                        period = f"{int(row['year'])}-Q{int(row['quarter'])}"
                        price_map[period] = float(row['close'])
                    
                    # Add prices to pb_history
                    for entry in pb_history:
                        period = entry['period']
                        if period in price_map:
                            entry['price'] = round(price_map[period] / 1000, 2)  # Convert to thousands
            except:
                pass
            
            # Calculate statistics
            pb_values = [h['pb'] for h in pb_history]
            
            pb_stats = {
                "min": round(min(pb_values), 2),
                "max": round(max(pb_values), 2),
                "mean": round(np.mean(pb_values), 2),
                "median": round(np.median(pb_values), 2),
                "std": round(np.std(pb_values), 2),
                "p10": round(np.percentile(pb_values, 10), 2),
                "p25": round(np.percentile(pb_values, 25), 2),
                "p50": round(np.percentile(pb_values, 50), 2),
                "p75": round(np.percentile(pb_values, 75), 2),
                "p90": round(np.percentile(pb_values, 90), 2),
                "count": len(pb_values)
            }
            
            # Current P/B and valuation (pb_history[0] is the newest after sorting)
            current_pb = pb_history[0]['pb'] if pb_history else None
            if current_pb:
                if pb_stats['max'] > pb_stats['min']:
                    percentile = (current_pb - pb_stats['min']) / (pb_stats['max'] - pb_stats['min']) * 100
                else:
                    percentile = 50
                percentile = max(0, min(100, percentile))
                
                if percentile < 20:
                    zone = "VERY_CHEAP"
                elif percentile < 35:
                    zone = "CHEAP"
                elif percentile < 65:
                    zone = "FAIR"
                elif percentile < 80:
                    zone = "EXPENSIVE"
                else:
                    zone = "VERY_EXPENSIVE"
            else:
                percentile = None
                zone = None
            
            # Calculate zone statistics (win rate, expected return)
            zone_stats = calculate_zone_statistics(pb_history, pb_stats)
            
            return {
                "symbol": symbol,
                "current_pb": current_pb,
                "current_period": pb_history[0]['period'] if pb_history else None,
                "pb_statistics": pb_stats,
                "pb_history": pb_history,  # Already sorted newest first
                "valuation": {
                    "percentile": round(percentile, 1) if percentile else None,
                    "zone": zone
                },
                "zone_statistics": zone_stats,
                "data_quality": {
                    "quarters": len(pb_history),
                    "years": len(set(h['year'] for h in pb_history)),
                    "has_prices": any('price' in h for h in pb_history)
                }
            }
            
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(1)
                continue
            print(f"    ❌ {symbol}: {str(e)[:50]}")
            return None
    
    return None


def calculate_zone_statistics(pb_history: List[Dict], pb_stats: Dict) -> Dict:
    """Calculate historical returns by P/B zone"""
    
    zones = {
        "very_cheap": {"min_pct": 0, "max_pct": 20, "entries": []},
        "cheap": {"min_pct": 20, "max_pct": 35, "entries": []},
        "fair": {"min_pct": 35, "max_pct": 65, "entries": []},
        "expensive": {"min_pct": 65, "max_pct": 80, "entries": []},
        "very_expensive": {"min_pct": 80, "max_pct": 100, "entries": []},
    }
    
    # Build price map
    price_map = {}
    for h in pb_history:
        if 'price' in h:
            price_map[h['period']] = h['price']
    
    periods = sorted(set(h['period'] for h in pb_history))
    
    for h in pb_history:
        pb = h['pb']
        period = h['period']
        
        # Calculate percentile
        if pb_stats['max'] > pb_stats['min']:
            pct = (pb - pb_stats['min']) / (pb_stats['max'] - pb_stats['min']) * 100
        else:
            pct = 50
        
        # Find zone
        for zone_name, zone_data in zones.items():
            if zone_data['min_pct'] <= pct < zone_data['max_pct']:
                # Calculate forward returns
                if period in price_map:
                    current_price = price_map[period]
                    try:
                        idx = periods.index(period)
                        # 1 year forward (4 quarters)
                        if idx + 4 < len(periods) and periods[idx + 4] in price_map:
                            future_price = price_map[periods[idx + 4]]
                            ret_1y = (future_price / current_price - 1) * 100
                            zone_data['entries'].append({
                                'period': period,
                                'pb': pb,
                                'return_1y': ret_1y
                            })
                    except:
                        pass
                break
    
    # Calculate stats for each zone
    result = {}
    for zone_name, zone_data in zones.items():
        entries = zone_data['entries']
        if entries:
            returns = [e['return_1y'] for e in entries]
            wins = [r for r in returns if r > 0]
            result[zone_name] = {
                "sample_count": len(entries),
                "win_rate_1y": round(len(wins) / len(entries) * 100, 1),
                "return_1y_avg": round(np.mean(returns), 1),
                "return_1y_median": round(np.median(returns), 1),
                "return_1y_best": round(max(returns), 1),
                "return_1y_worst": round(min(returns), 1),
            }
        else:
            result[zone_name] = {
                "sample_count": 0,
                "win_rate_1y": None,
                "return_1y_avg": None
            }
    
    return result


def fetch_sector_data(sector_id: str) -> Dict:
    """Fetch all data for a sector"""
    
    sector_info = get_sector_info(sector_id)
    if not sector_info:
        return {}
    
    symbols = sector_info['symbols']
    print(f"\n{'='*60}")
    print(f"📊 Fetching {sector_info['name']} ({len(symbols)} stocks)")
    print(f"{'='*60}")
    
    stocks_data = {}
    success = 0
    failed = 0
    
    for i, symbol in enumerate(symbols, 1):
        print(f"  [{i}/{len(symbols)}] {symbol}...", end=" ")
        
        data = fetch_stock_data(symbol)
        
        if data:
            stocks_data[symbol] = data
            quality = data.get('data_quality', {})
            print(f"✅ {quality.get('quarters', 0)}Q data")
            success += 1
        else:
            print("❌ Failed")
            failed += 1
        
        time.sleep(API_DELAY)
    
    print(f"\n  Summary: {success} success, {failed} failed")
    
    # Calculate sector heat
    heat_data = calculate_sector_heat(stocks_data)
    
    return {
        "sector_id": sector_id,
        "sector_name": sector_info['name'],
        "sector_name_en": sector_info['name_en'],
        "description": sector_info['description'],
        "pb_suitable": sector_info['pb_suitable'],
        "color": sector_info['color'],
        "updated_at": datetime.now().isoformat(),
        "summary": {
            "total_stocks": len(symbols),
            "stocks_with_data": success,
            "failed": failed
        },
        "heat": heat_data,
        "stocks": stocks_data
    }


def calculate_sector_heat(stocks_data: Dict) -> Dict:
    """Calculate sector heat index"""
    
    percentiles = []
    pb_values = []
    
    for symbol, data in stocks_data.items():
        valuation = data.get('valuation', {})
        pct = valuation.get('percentile')
        current_pb = data.get('current_pb')
        
        if pct is not None:
            percentiles.append(pct)
        if current_pb is not None:
            pb_values.append(current_pb)
    
    if not percentiles:
        return {"heat_index": 50, "status": "NEUTRAL"}
    
    avg_pct = np.mean(percentiles)
    
    # Adjust for extremes
    total = len(percentiles)
    very_cheap = sum(1 for p in percentiles if p < 20)
    very_expensive = sum(1 for p in percentiles if p > 80)
    
    heat_index = avg_pct
    if very_expensive / total > 0.5:
        heat_index = min(100, heat_index + 15)
    if very_cheap / total > 0.5:
        heat_index = max(0, heat_index - 15)
    
    # Determine status
    if heat_index >= 85:
        status = "🔥 OVERHEATED"
        signal = "SELL"
    elif heat_index >= 70:
        status = "🌡️ HOT"
        signal = "REDUCE"
    elif heat_index >= 55:
        status = "☀️ WARM"
        signal = "HOLD"
    elif heat_index >= 45:
        status = "😐 NEUTRAL"
        signal = "NORMAL"
    elif heat_index >= 35:
        status = "🌤️ COOL"
        signal = "ACCUMULATE"
    elif heat_index >= 20:
        status = "❄️ COLD"
        signal = "BUY"
    else:
        status = "🥶 ICE COLD"
        signal = "BUY_HEAVY"
    
    return {
        "heat_index": round(heat_index, 1),
        "status": status,
        "signal": signal,
        "avg_pb_percentile": round(avg_pct, 1),
        "avg_pb": round(np.mean(pb_values), 2) if pb_values else None,
        "very_cheap_count": very_cheap,
        "very_expensive_count": very_expensive,
        "total_stocks": total
    }


def fetch_all_sectors(sector_ids: List[str] = None):
    """Fetch data for multiple sectors"""
    
    if sector_ids is None:
        sector_ids = list(SECTORS.keys())
    
    print("\n" + "="*70)
    print("🚀 MULTI-SECTOR DATA FETCHER")
    print(f"   Sectors: {len(sector_ids)}")
    print(f"   Total stocks: {sum(len(SECTORS[s]['symbols']) for s in sector_ids)}")
    print("="*70)
    
    all_results = {}
    sector_heats = []
    
    for sector_id in sector_ids:
        result = fetch_sector_data(sector_id)
        all_results[sector_id] = result
        
        if result.get('heat') and result['heat'].get('signal'):
            sector_heats.append({
                "sector_id": sector_id,
                "sector_name": result['sector_name'],
                "heat_index": result['heat']['heat_index'],
                "status": result['heat']['status'],
                "signal": result['heat']['signal'],
                "stocks_count": result['summary']['stocks_with_data']
            })
        
        # Save individual sector file
        output_file = f"../docs/data/{sector_id}.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"  💾 Saved to {output_file}")
    
    # Save combined heat index
    market_heat = {
        "updated_at": datetime.now().isoformat(),
        "sectors": sorted(sector_heats, key=lambda x: x['heat_index'], reverse=True),
        "market_heat": calculate_market_heat(sector_heats)
    }
    
    heat_file = "../docs/data/market_heat.json"
    with open(heat_file, 'w', encoding='utf-8') as f:
        json.dump(market_heat, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Market heat saved to {heat_file}")
    
    # Print summary
    print("\n" + "="*70)
    print("📊 SECTOR HEAT SUMMARY")
    print("="*70)
    print(f"{'Sector':<30} {'Heat':>8} {'Status':<15} {'Signal':<12}")
    print("-"*70)
    
    for sh in sorted(sector_heats, key=lambda x: x['heat_index'], reverse=True):
        print(f"{sh['sector_name']:<30} {sh['heat_index']:>7.1f} {sh['status']:<15} {sh['signal']:<12}")
    
    return all_results


def calculate_market_heat(sector_heats: List[Dict]) -> Dict:
    """Calculate overall market heat from sector heats"""
    
    if not sector_heats:
        return {"heat_index": 50, "status": "NEUTRAL"}
    
    # Weighted average by number of stocks
    total_stocks = sum(s['stocks_count'] for s in sector_heats)
    if total_stocks == 0:
        return {"heat_index": 50, "status": "NEUTRAL"}
    
    weighted_heat = sum(s['heat_index'] * s['stocks_count'] for s in sector_heats) / total_stocks
    
    if weighted_heat >= 85:
        status = "🔥 OVERHEATED"
    elif weighted_heat >= 70:
        status = "🌡️ HOT"
    elif weighted_heat >= 55:
        status = "☀️ WARM"
    elif weighted_heat >= 45:
        status = "😐 NEUTRAL"
    elif weighted_heat >= 35:
        status = "🌤️ COOL"
    elif weighted_heat >= 20:
        status = "❄️ COLD"
    else:
        status = "🥶 ICE COLD"
    
    return {
        "heat_index": round(weighted_heat, 1),
        "status": status,
        "total_sectors": len(sector_heats),
        "total_stocks": total_stocks
    }


if __name__ == "__main__":
    import sys
    
    # Allow specifying sectors from command line
    if len(sys.argv) > 1:
        sectors_to_fetch = sys.argv[1:]
        print(f"Fetching specific sectors: {sectors_to_fetch}")
    else:
        sectors_to_fetch = None  # Fetch all
    
    results = fetch_all_sectors(sectors_to_fetch)
    
    print("\n✅ Done!")
