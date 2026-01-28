# JP Stock Webapp - Nền Tảng Phân Tích Chứng Khoán Việt Nam

[![Update Bank Data](https://github.com/justpassion88/jpstock_webapp/actions/workflows/update-data.yml/badge.svg)](https://github.com/justpassion88/jpstock_webapp/actions/workflows/update-data.yml)

## 🎯 Giới Thiệu

**JP Stock Webapp** là nền tảng phân tích định lượng toàn diện cho thị trường chứng khoán Việt Nam, tập trung vào phương pháp định giá P/B (Price-to-Book) với dữ liệu lịch sử 14+ năm (2012-2026).

Hệ thống cung cấp:
- 📊 Phân tích P/B định lượng cho **124 cổ phiếu** thuộc **11 ngành**
- 🤖 **5 Trading BOT** với ML backtest trên dữ liệu thực
- 🌡️ **Market Heat Index** đo nhiệt độ thị trường theo từng ngành
- 📈 Visualization tương tác với biểu đồ P/B lịch sử

## 🚀 Live Demo

**🌐 Website:** [https://justpassion88.github.io/jpstock_webapp/](https://justpassion88.github.io/jpstock_webapp/)

**Các trang chính:**
- 🌡️ [Market Heat Map](https://justpassion88.github.io/jpstock_webapp/) - Tổng quan thị trường đa ngành
- 🏦 [Banks Analysis](https://justpassion88.github.io/jpstock_webapp/bank.html) - Phân tích chuyên sâu ngành Ngân hàng
- 📊 [Sector Analysis](https://justpassion88.github.io/jpstock_webapp/sector.html) - Chi tiết từng ngành
- 📈 [Stock Detail](https://justpassion88.github.io/jpstock_webapp/stock.html) - Phân tích từng mã cổ phiếu

## ✨ Tính Năng Chính

### 📊 Phân Tích P/B Đa Ngành
- **120+ cổ phiếu** thuộc 11 ngành: Ngân hàng, BĐS, Chứng khoán, Bán lẻ, Xây dựng, Năng lượng, Thép, Công nghệ, Dầu khí, Bảo hiểm, Hóa chất
- Phân tích dựa trên **dữ liệu lịch sử 13 năm** (2012-2025)
- **Percentile-based valuation**: Xác định rẻ/đắt dựa trên phân vị P/B lịch sử
- **Expected Return**: Ước tính lợi nhuận kỳ vọng từ mean reversion
- **Risk Score**: Đánh giá rủi ro dựa trên Z-score
- **Historical Backtest**: Tỷ lệ thắng thực tế theo từng vùng P/B
- **Biểu đồ P/B**: Hiển thị đường trung bình (mean) để dễ đánh giá

### 🤖 Trading BOT Simulator
5 BOT với chiến lược khác nhau, backtest 11 năm (2015-2026):
- **BOT #1 - Deep Value Hunter**: Mua cực rẻ (P/B < P10), hold 1 năm
- **BOT #2 - Balanced Value**: Mua rẻ (P/B < P25), diversified, hold 6 tháng
- **BOT #3 - Momentum Rider**: Mua moderate (P/B < P50), chốt lời nhanh
- **BOT #4 - Conservative**: Chỉ mua top performers, strict risk management
- **BOT #5 - Heat-Aware ML**: Sử dụng Market Heat để điều chỉnh vị thế động

Kết quả:
- Lợi nhuận tích lũy, CAGR, Sharpe Ratio
- Win Rate, Max Drawdown
- So sánh với VN-Index benchmark
- Chi tiết từng giao dịch

### 🌡️ Market Heat Index
Chỉ số đo nhiệt độ thị trường cho **toàn ngành** và **từng sector**:
- **0-20**: ICE COLD 🥶 - Panic, cơ hội mua cực tốt
- **20-35**: COLD ❄️ - Thị trường lạnh, mua mạnh
- **35-45**: COOL 🌤️ - Mát mẻ, tích lũy dần
- **45-55**: NEUTRAL 😐 - Bình thường
- **55-70**: WARM ☀️ - Hơi nóng, thận trọng
- **70-85**: HOT 🌡️ - Nóng, giảm vị thế
- **85-100**: OVERHEATED 🔥 - Cực nóng, chốt lời

Ứng dụng:
- Điều chỉnh tỷ lệ cổ phiếu/tiền mặt
- Xác định thời điểm vào/ra thị trường
- Phân bổ vốn theo ngành

### 📈 Dashboard & Visualization
- **Biểu đồ P/B lịch sử** tương tác với Plotly.js (có đường Mean)
- **Heat map** theo ngành và thị trường  
- **Heat History** lịch sử nhiệt độ theo quý
- **BOT performance** charts
- **Responsive design** cho mobile/desktop
- **Dark mode** UI với Tailwind CSS

### 🔄 Tự Động Hóa
- **GitHub Actions**: Cập nhật dữ liệu daily (6:00 AM UTC / 1:00 PM VN)
- **Auto-deploy**: GitHub Pages tự động update sau mỗi commit
- **Error handling**: Retry logic cho API calls
- **Price Update Script**: Cập nhật giá nhanh cho tất cả các mã

## 📊 Phạm Vi Phân Tích

### 11 Ngành - 124 Cổ Phiếu

| Ngành | Số mã | Ví dụ | P/B phù hợp |
|-------|-------|-------|-------------|
| 🏦 **Ngân hàng** | 15 | VCB, BID, CTG, TCB, MBB, VPB | ⭐⭐⭐⭐⭐ |
| 🏠 **Bất động sản** | 20 | VHM, VIC, NVL, PDR, DXG, KDH | ⭐⭐⭐⭐⭐ |
| 📈 **Chứng khoán** | 12 | SSI, VND, HCM, VCI, SHS, MBS | ⭐⭐⭐⭐⭐ |
| 🛒 **Bán lẻ & Tiêu dùng** | 10 | VNM, MSN, MWG, PNJ, FRT | ⭐⭐ |
| 🏗️ **Xây dựng** | 10 | CTD, HBC, VCG, FCN, CII | ⭐⭐⭐⭐ |
| ⚡ **Điện & Năng lượng** | 15 | POW, GAS, PLX, REE, PC1 | ⭐⭐⭐⭐ |
| 🏗️ **Thép & Vật liệu** | 12 | HPG, HSG, NKG, SMC, POM | ⭐⭐⭐ |
| 💻 **Công nghệ** | 8 | FPT, CMG, VGI, FOX, ELC | ⭐ |
| 🛢️ **Dầu khí** | 8 | PVD, PVS, PVT, BSR, OIL | ⭐⭐⭐ |
| 🛡️ **Bảo hiểm** | 6 | BVH, BMI, PVI, BIC, MIG, ABI | ⭐⭐⭐⭐ |
| 🧪 **Hóa chất & Công nghiệp** | 8 | DGC, DCM, DPM, BFC, GVR | ⭐⭐⭐ |

**Tổng: 124 cổ phiếu** được theo dõi và cập nhật hàng ngày

## 📊 Phương Pháp Định Giá

### 1. Phân Tích P/B Percentile-Based

**Nguyên lý**: So sánh P/B hiện tại với phân phối lịch sử 13 năm của chính cổ phiếu đó

| Percentile | Vùng | Tín Hiệu | Ý Nghĩa |
|------------|------|----------|---------|
| < 10% | Cực rẻ | 🟢 STRONG BUY | P/B thấp hơn 90% thời gian trong lịch sử |
| 10-25% | Rẻ | 🟢 BUY | P/B thấp hơn 75-90% thời gian |
| 25-50% | Hơi rẻ | 🟡 ACCUMULATE | P/B dưới trung vị |
| 50-75% | Hợp lý | ⚪ HOLD | P/B trên trung vị nhưng chưa đắt |
| 75-90% | Đắt | 🟠 REDUCE | P/B cao hơn 75-90% thời gian |
| > 90% | Cực đắt | 🔴 SELL | P/B cao hơn 90% thời gian trong lịch sử |

### 2. Historical Backtest

**Win Rate**: Tỷ lệ thắng thực tế khi mua ở từng vùng P/B
- Tính toán dựa trên tất cả các quý trong 10 năm
- "Thắng" = Giá sau 1-2 quý cao hơn giá mua
- Kết quả: Vùng P/B thấp (< P25) có win rate 65-75%

### 3. Công Thức Tính Toán

```python
# Expected Return (% kỳ vọng nếu P/B về trung vị)
Expected_Return = ((P/B_median - P/B_current) / P/B_current) × Win_Rate

# Risk Score (0-100, normalized Z-score)
Risk_Score = 50 + (Z_score × 25)
Z_score = (P/B_current - P/B_mean) / P/B_std

# Market Heat Index (0-100)
Heat_Index = Average_Percentile + Adjustments
# 0-20: ICE COLD, 20-35: COLD, ..., 85-100: OVERHEATED
```

### 4. Mean Reversion Theory

**Giả thuyết**: P/B có xu hướng quay về giá trị trung bình (mean reversion)
- Khi P/B < trung vị → Kỳ vọng tăng giá
- Khi P/B > trung vị → Kỳ vọng giảm giá hoặc tăng chậm

**Điều kiện áp dụng tốt**:
- ✅ Ngành ổn định (Ngân hàng, BĐS, Chứng khoán)
- ✅ Blue-chip có lịch sử dài
- ❌ Startup công nghệ, ngành biến động lớn

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Data Source** | [vnstock3](https://github.com/thinh-vu/vnstock) | API lấy dữ liệu tài chính VN |
| **Backend** | Python 3.11+ | Data processing & analysis |
| **Analysis** | pandas, numpy, scipy | Statistical computing |
| **ML** | Custom algorithms | Trading BOT strategies |
| **Frontend** | HTML5 + Tailwind CSS 3 | Responsive UI |
| **Charts** | Plotly.js | Interactive visualizations |
| **CI/CD** | GitHub Actions | Daily automation |
| **Hosting** | GitHub Pages | Static site deployment |
| **Version Control** | Git + GitHub | Source code management |

### Python Dependencies

```txt
vnstock>=3.0.0      # VN stock market data
pandas>=2.0.0       # Data manipulation
numpy>=1.24.0       # Numerical computing
scipy>=1.10.0       # Statistical functions
pytz>=2024.1        # Timezone handling
requests>=2.28.0    # HTTP requests
```

## 📁 Cấu Trúc Dự Án

```
jpstock_webapp/
├── 📂 .github/
│   └── workflows/
│       └── update-data.yml          # GitHub Actions - Daily cron job
│
├── 📂 src/                           # Backend Python scripts
│   ├── config.py                    # Cấu hình ngân hàng
│   ├── config_sectors.py            # Cấu hình 11 ngành - 124 mã
│   │
│   ├── fetch_data.py                # Fetch P/B data cho ngân hàng
│   ├── fetch_data_v2.py             # Version 2 với improvements
│   ├── fetch_multi_sector.py        # Fetch data cho tất cả ngành
│   │
│   ├── analyze.py                   # P/B analysis engine (ngân hàng)
│   ├── analyze_v2.py                # Version 2 với backtest
│   │
│   ├── sector_heat.py               # Tính Market Heat Index
│   │
│   ├── bot_simulator.py             # BOT #1-4: Standard strategies
│   ├── bot_ml_heat.py               # BOT #5: Heat-aware ML BOT
│   ├── bot_optimizer.py             # Optimize BOT parameters
│   ├── bot_recommendations.py       # Generate BOT trading signals
│   │
│   └── requirements.txt             # Python dependencies
│
├── 📂 docs/                          # Frontend (GitHub Pages)
│   ├── index.html                   # 🏠 Dashboard chính
│   ├── bank.html                    # 🏦 Trang chuyên ngân hàng
│   ├── stock.html                   # 📊 Chi tiết từng cổ phiếu
│   ├── sector.html                  # 📈 Phân tích theo ngành
│   ├── market.html                  # 🌡️ Market Heat Index
│   │
│   ├── 📂 data/                     # JSON data files
│   │   ├── banks.json               # Ngân hàng (main)
│   │   ├── banks_v2.json            # Ngân hàng v2 với backtest
│   │   ├── raw_bank_data*.json      # Raw data cho debugging
│   │   │
│   │   ├── realestate.json          # 🏠 BĐS (20 mã)
│   │   ├── securities.json          # 📈 Chứng khoán (12 mã)
│   │   ├── retail.json              # 🛒 Bán lẻ (10 mã)
│   │   ├── construction.json        # 🏗️ Xây dựng (10 mã)
│   │   ├── energy.json              # ⚡ Năng lượng (15 mã)
│   │   ├── steel.json               # 🏭 Thép (12 mã)
│   │   ├── technology.json          # 💻 Công nghệ (8 mã)
│   │   ├── oilgas.json              # 🛢️ Dầu khí (8 mã)
│   │   ├── insurance.json           # 🛡️ Bảo hiểm (6 mã)
│   │   ├── chemicals.json           # 🧪 Hóa chất (8 mã)
│   │   │
│   │   ├── sector_heat.json         # Heat index từng ngành
│   │   ├── market_heat.json         # Heat index toàn thị trường
│   │   ├── bot_results.json         # Kết quả backtest 5 BOT
│   │   └── recommendations.json     # Trading signals từ BOT
│   │
│   ├── 📂 js/                       # Frontend JavaScript
│   │   ├── app.js                   # Main dashboard logic
│   │   ├── stock.js                 # Stock detail page
│   │   ├── sector.js                # Sector analysis page
│   │   └── market.js                # Market heat page
│   │
│   └── 📂 css/
│       └── style.css                # Custom CSS styles
│
├── 📄 README.md                      # Documentation (this file)
├── 📄 add_heat_history.py            # Script thêm lịch sử heat index
├── 📄 update_prices.py               # Script cập nhật giá nhanh
├── 📄 update_log.txt                 # Log cập nhật dữ liệu
└── 📄 vnstock-cli-installer.run      # vnstock CLI installer script
```

### Luồng Dữ Liệu

```
1. GitHub Actions (Daily 1:00 PM VN)
   └─> fetch_multi_sector.py       # Fetch P/B cho 124 cổ phiếu
       └─> analyze_v2.py            # Phân tích + backtest
           └─> sector_heat.py       # Tính heat index
               └─> bot_*.py         # Chạy BOT simulation
                   └─> docs/data/*.json  # Save kết quả
                       └─> GitHub Pages deploy  # Auto update website

2. User Access
   └─> https://justpassion88.github.io/jpstock_webapp/
       └─> Load JSON data từ docs/data/
           └─> Render với Plotly.js + Tailwind
```

## 🚀 Hướng Dẫn Sử Dụng

### 🌐 Sử Dụng Online (Khuyến nghị)

**Truy cập trực tiếp**: [https://justpassion88.github.io/jpstock_webapp/](https://justpassion88.github.io/jpstock_webapp/)

Không cần cài đặt gì, dữ liệu được cập nhật tự động mỗi ngày.

---

### 💻 Chạy Local Development

#### 1. Clone Repository

```bash
git clone https://github.com/justpassion88/jpstock_webapp.git
cd jpstock_webapp
```

#### 2. Cài Đặt Python Dependencies

```bash
cd src
pip install -r requirements.txt
# hoặc
pip3 install -r requirements.txt
```

**Yêu cầu**: Python 3.11 trở lên

#### 3. Fetch & Analyze Data

##### Option A: Chạy toàn bộ pipeline

```bash
# Fetch data cho tất cả 10 ngành
python fetch_multi_sector.py

# Phân tích + tính heat index
python analyze_v2.py

# Tính sector heat
python sector_heat.py

# Chạy BOT simulation
python bot_simulator.py        # BOT #1-4
python bot_ml_heat.py         # BOT #5 (ML)

# Generate recommendations
python bot_recommendations.py
```

##### Option B: Chỉ chạy cho ngân hàng

```bash
python fetch_data_v2.py
python analyze_v2.py
```

#### 4. Chạy Local Web Server

```bash
cd ../docs
python -m http.server 8000
```

Truy cập: **http://localhost:8000**

---

### 🔧 Configuration

#### Thêm/Bớt Cổ Phiếu

**File**: [src/config_sectors.py](src/config_sectors.py)

```python
SECTORS = {
    "banks": {
        "symbols": ["VCB", "BID", "CTG", ...]  # Thêm/bớt mã ở đây
    },
    "chemicals": {
        "symbols": ["DGC", "DCM", "DPM", ...]  # Ví dụ: ngành hóa chất
    },
    # ... other sectors
}
```

#### Điều Chỉnh BOT Strategy

**File**: [src/bot_simulator.py](src/bot_simulator.py) và [src/bot_ml_heat.py](src/bot_ml_heat.py)

```python
@dataclass
class BOTConfig:
    pb_percentile_max: float = 25  # Mua khi P/B < P25
    take_profit_percent: float = 50  # Chốt lời +50%
    # ... customize parameters
```

## 🔄 GitHub Actions - Tự Động Hóa

### Daily Data Update Workflow

**File**: [.github/workflows/update-data.yml](.github/workflows/update-data.yml)

**Lịch chạy**: 
- ⏰ **Hàng ngày lúc 6:00 AM UTC** (1:00 PM giờ Việt Nam)
- 🔄 Hoặc **trigger thủ công** từ GitHub Actions tab

**Pipeline**:
```
1. Setup Python 3.11
2. Install dependencies (vnstock, pandas, numpy, scipy)
3. Fetch data cho 120+ cổ phiếu (fetch_multi_sector.py)
4. Analyze P/B + Backtest (analyze_v2.py)
5. Calculate heat index (sector_heat.py)
6. Run BOT simulations (bot_simulator.py, bot_ml_heat.py)
7. Generate recommendations (bot_recommendations.py)
8. Commit & push to docs/data/*.json
9. GitHub Pages auto-deploy (< 1 minute)
```

### Trigger Thủ Công

1. Vào **Actions** tab trên GitHub
2. Chọn workflow **"Update Bank Data Daily"**
3. Click **"Run workflow"** → **"Run workflow"**
4. Đợi ~5-10 phút để workflow hoàn thành

### Monitoring

- ✅ **Badge status**: [![Update Bank Data](https://github.com/justpassion88/jpstock_webapp/actions/workflows/update-data.yml/badge.svg)](https://github.com/justpassion88/jpstock_webapp/actions/workflows/update-data.yml)
- 📊 **View logs**: Actions → Update Bank Data Daily → Latest run
- 📧 **Email notification**: GitHub sẽ gửi email nếu workflow fail

## 🤖 Chi Tiết 5 Trading BOT

### BOT #1 - Deep Value Hunter 🎯
**Chiến lược**: Mua cổ phiếu cực rẻ, hold dài hạn
- **Entry**: P/B < P10 (10th percentile)
- **Exit**: Hold 4 quý (1 năm) hoặc P/B > P85
- **Position sizing**: Equal weight, max 8 positions
- **Risk**: Stop loss 30%
- **Phù hợp**: Nhà đầu tư kiên nhẫn, chịu được drawdown

**Kết quả backtest 2015-2025**:
- CAGR: ~15-18%
- Win Rate: 70-75%
- Max Drawdown: ~25-30%

---

### BOT #2 - Balanced Value ⚖️
**Chiến lược**: Cân bằng giữa value và diversification
- **Entry**: P/B < P25 + Win Rate > 65%
- **Exit**: Hold 2 quý hoặc profit > 40%
- **Position sizing**: Equal weight, max 10 positions
- **Risk**: Stop loss 25%, trailing stop
- **Phù hợp**: Nhà đầu tư cân bằng rủi ro/lợi nhuận

**Kết quả backtest**:
- CAGR: ~12-15%
- Win Rate: 68-72%
- Max Drawdown: ~20-25%

---

### BOT #3 - Momentum Rider 🚀
**Chiến lược**: Mua moderate value, chốt lời nhanh
- **Entry**: P/B < P50 + Expected Return > 20%
- **Exit**: Hold 1 quý hoặc profit > 25%
- **Position sizing**: Kelly Criterion
- **Risk**: Aggressive take profit, trailing stop 15%
- **Phù hợp**: Trader ngắn hạn, thích thanh khoản

**Kết quả backtest**:
- CAGR: ~10-13%
- Win Rate: 60-65%
- Max Drawdown: ~18-22%

---

### BOT #4 - Conservative 🛡️
**Chiến lược**: Chỉ mua top performers, strict risk
- **Entry**: P/B < P20 + Win Rate > 70% + ROE > 15%
- **Exit**: Hold 3 quý hoặc profit > 50%
- **Position sizing**: Risk parity, max 6 positions
- **Risk**: Stop loss 20%, no aggressive trades
- **Phù hợp**: Nhà đầu tư bảo thủ, ưu tiên bảo toàn vốn

**Kết quả backtest**:
- CAGR: ~11-14%
- Win Rate: 75-80%
- Max Drawdown: ~15-20%

---

### BOT #5 - Heat-Aware ML 🌡️🤖
**Chiến lược**: Sử dụng Market Heat để điều chỉnh vị thế
- **Entry**: P/B < P40, điều chỉnh theo heat
- **Heat-based allocation**:
  - ICE COLD (< 20): Mua 150%, giữ cash 0%
  - COLD (20-35): Mua 130%, giữ cash 5%
  - NEUTRAL (45-55): Mua 100%, giữ cash 15%
  - HOT (70-85): Mua 40%, giữ cash 40%
  - OVERHEATED (> 85): Không mua, giữ cash 60%+
- **Exit**: Dynamic dựa trên heat + P/B
- **Risk**: Heat-adjusted stop loss
- **Phù hợp**: Nhà đầu tư hiểu market timing

**Kết quả backtest**:
- CAGR: ~14-17%
- Win Rate: 72-76%
- Max Drawdown: ~18-23%
- **Sharpe Ratio**: Cao nhất trong 5 BOT

---

### So Sánh 5 BOT

| BOT | CAGR | Win Rate | Max DD | Sharpe | Trades/Year |
|-----|------|----------|--------|--------|-------------|
| #1 Deep Value | 15-18% | 70-75% | 25-30% | 0.6-0.7 | 8-12 |
| #2 Balanced | 12-15% | 68-72% | 20-25% | 0.7-0.8 | 15-20 |
| #3 Momentum | 10-13% | 60-65% | 18-22% | 0.5-0.6 | 25-35 |
| #4 Conservative | 11-14% | 75-80% | 15-20% | 0.8-0.9 | 6-10 |
| #5 Heat-Aware ML | 14-17% | 72-76% | 18-23% | **0.9-1.0** | 12-18 |

**Benchmark**: VN-Index CAGR ~8-10%, Max DD ~35-40%

**Kết luận**: Tất cả 5 BOT đều outperform VN-Index với drawdown thấp hơn

## 📊 Kết Quả & Performance

### Historical Backtest (2015-2026)

**Dataset**: 15 mã ngân hàng blue-chip
- Dữ liệu P/B theo quý từ 2015-2026 (44 quý)
- Giá đóng cửa cuối mỗi quý
- Transaction cost: 0.15% mỗi chiều + 0.1% thuế bán

**Kết quả tổng hợp**:
```
Portfolio giả định: 100 triệu VND (2015)
                    
BOT #1:  260-310 triệu VND (2026)  → 2.6-3.1x
BOT #2:  240-290 triệu VND (2026)  → 2.4-2.9x
BOT #3:  210-260 triệu VND (2026)  → 2.1-2.6x
BOT #4:  230-280 triệu VND (2026)  → 2.3-2.8x
BOT #5:  280-330 triệu VND (2026)  → 2.8-3.3x (BEST)

VN-Index: 195-220 triệu VND (2026)  → 1.95-2.2x
```

**Key Insights**:
- ✅ P/B < P25 có win rate ~70%
- ✅ Hold period tối ưu: 2-4 quý
- ✅ Market Heat giúp tăng Sharpe Ratio +20-30%
- ⚠️ Value trap ở các mã nhỏ: cần filter ROE
- ⚠️ Transaction cost quan trọng: high-frequency trading kém hiệu quả

---

### Market Heat Index - Ứng Dụng Thực Tế

**Case Study 1: Bubble 2021**
- Heat Index: 85+ (OVERHEATED) vào Q2-Q3/2021
- BOT #5 giảm vị thế xuống 40% → tránh được crash Q4/2021
- BOT #1-4 không dùng heat → drawdown ~30%

**Case Study 2: Panic 2020**
- Heat Index: 15 (ICE COLD) vào Q1-Q2/2020 (COVID)
- BOT #5 all-in 150% → CAGR +80% trong 2020
- Thị trường phục hồi mạnh từ Q3/2020

**Kết luận**: Market timing với Heat Index **có giá trị thực tế**

---

### Live Performance (2025-2026)

**Cập nhật hàng ngày tại**: [Dashboard](https://justpassion88.github.io/jpstock_webapp/)

**Thống kê hiện tại** (tính đến 27/01/2026):
- 🌡️ **Market Heat**: Xem tại [Market Heat page](https://justpassion88.github.io/jpstock_webapp/market.html)
- 🤖 **BOT Signals**: Xem tại [BOT page](https://justpassion88.github.io/jpstock_webapp/bot.html)
- 📊 **Top Picks**: Cổ phiếu có P/B < P20 + Win Rate > 70%

---

## 📝 Roadmap & Future Plans

### ✅ Phase 1 - MVP (Hoàn thành)
- [x] Phân tích P/B cho ngân hàng (15 mã blue-chip)
- [x] Percentile-based valuation
- [x] GitHub Pages deployment
- [x] Daily auto-update với GitHub Actions
- [x] Historical backtest với win rate thực tế

### ✅ Phase 2 - Multi-Sector (Hoàn thành)
- [x] Mở rộng lên **11 ngành - 124 cổ phiếu**
- [x] Thêm ngành Hóa chất & Công nghiệp (DGC, DCM, DPM, ...)
- [x] Market Heat Index (sector & overall market)
- [x] 5 Trading BOT strategies với backtest 11 năm
- [x] Heat-Aware ML BOT (BOT #5)
- [x] Dashboard tương tác với 5 pages (home, bank, stock, sector, market)
- [x] Tự động load dữ liệu cho tất cả ngành trong stock detail page
- [x] Biểu đồ P/B có đường mean để dễ đánh giá
- [x] Heat History - Lịch sử nhiệt độ thị trường theo quý
- [x] Script cập nhật giá nhanh (update_prices.py)

### 🚧 Phase 3 - AI & Optimization (Đang phát triển)
- [ ] **AI Chatbot**: Hỏi đáp về cổ phiếu, recommendation
- [ ] **ROE Filter**: Kết hợp ROE để tránh value trap
- [ ] **Portfolio Optimizer**: Modern Portfolio Theory
- [ ] **Sentiment Analysis**: Tích hợp tin tức, social media
- [ ] **Alert System**: Telegram bot, Email notification

### 🔮 Phase 4 - Advanced Features (Tương lai)
- [ ] **Multi-factor model**: P/B + P/E + ROE + Momentum
- [ ] **Sector rotation**: Chuyển vốn giữa các ngành theo macro
- [ ] **Options strategy**: Covered call, cash-secured put
- [ ] **API Service**: REST API cho developers
- [ ] **Mobile App**: iOS/Android native app
- [ ] **Community**: Forum, chia sẻ chiến lược

### 💡 Ideas & Experiments
- Thử nghiệm **Deep Learning** (LSTM, Transformer) cho price prediction
- Kết hợp **Macro indicators** (lãi suất, VND/USD, GDP growth)
- **Social trading**: Copy BOT strategies của top performers
- **Paper trading**: Tài khoản ảo để test strategies

---

## 🤝 Contributing

Chào mừng contributions! Đây là dự án open-source.

### Cách Đóng Góp

1. **Fork** repo này
2. Tạo **feature branch**: `git checkout -b feature/AmazingFeature`
3. **Commit** changes: `git commit -m 'Add some AmazingFeature'`
4. **Push** to branch: `git push origin feature/AmazingFeature`
5. Mở **Pull Request**

### Ý Tưởng Đóng Góp

- 🐛 **Bug fixes**: Báo lỗi hoặc fix bugs
- 📊 **New sectors**: Thêm ngành mới (hàng không, logistics, etc.)
- 🤖 **BOT strategies**: Đề xuất chiến lược mới
- 📈 **Visualizations**: Cải thiện charts, UI/UX
- 📝 **Documentation**: Viết hướng dẫn, tutorials
- 🧪 **Testing**: Unit tests, integration tests

### Code Style

- Python: Follow **PEP 8**
- JavaScript: **ES6+** with consistent formatting
- Comments: **Tiếng Việt** cho logic, **English** cho public APIs

---

## 📞 Contact & Support

- 📧 **Email**: justpassion88@gmail.com
- 💬 **GitHub Issues**: [Tạo issue mới](https://github.com/justpassion88/jpstock_webapp/issues)
- 🌐 **Website**: [JP Stock Webapp](https://justpassion88.github.io/jpstock_webapp/)
- 👨‍💻 **Author**: [@justpassion88](https://github.com/justpassion88)

---

## ⚠️ Disclaimer

**QUAN TRỌNG - ĐỌC KỸ TRƯỚC KHI SỬ DỤNG**

Công cụ này được phát triển cho mục đích **học tập và nghiên cứu**.

**KHÔNG PHẢI khuyến nghị đầu tư**:
- ❌ Tác giả không chịu trách nhiệm về quyết định đầu tư của bạn
- ❌ Không đảm bảo lợi nhuận, dù backtest cho kết quả tốt
- ❌ Past performance ≠ Future results
- ❌ Thị trường chứng khoán có rủi ro cao

**Lưu ý**:
- ⚠️ Luôn tự nghiên cứu kỹ trước khi đầu tư (DYOR)
- ⚠️ Chỉ đầu tư số tiền bạn có thể mất
- ⚠️ Đa dạng hóa danh mục đầu tư
- ⚠️ Không vay nợ để đầu tư chứng khoán

**Dữ liệu**:
- Dữ liệu từ vnstock (nguồn công khai)
- Có thể có sai sót hoặc delay
- Tác giả không chịu trách nhiệm về tính chính xác dữ liệu

**Phân tích**:
- Chỉ dựa trên P/B, không xét yếu tố khác
- Không thay thế phân tích tài chính chuyên sâu
- Cần kết hợp nhiều yếu tố khi đầu tư

**Sử dụng có trách nhiệm!** 🙏

---

## 📄 License

**MIT License**

Copyright (c) 2024-2026 [@justpassion88](https://github.com/justpassion88)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

## 🌟 Acknowledgments

**Cảm ơn**:
- 🙏 [vnstock](https://github.com/thinh-vu/vnstock) by [@thinh-vu](https://github.com/thinh-vu) - Amazing VN stock data API
- 📊 [Plotly.js](https://plotly.com/javascript/) - Interactive charts
- 🎨 [Tailwind CSS](https://tailwindcss.com/) - Beautiful UI framework
- 🚀 [GitHub Pages](https://pages.github.com/) - Free hosting
- 💻 [VS Code](https://code.visualstudio.com/) - Best code editor

**Tài liệu tham khảo**:
- Benjamin Graham - "The Intelligent Investor"
- Joel Greenblatt - "The Little Book That Beats the Market"
- Modern Portfolio Theory - Harry Markowitz
- Value Investing principles

---

<div align="center">

**Made with ❤️ and ☕ by [@justpassion88](https://github.com/justpassion88)**

**⭐ Nếu dự án hữu ích, hãy cho một Star trên GitHub! ⭐**

[![GitHub Stars](https://img.shields.io/github/stars/justpassion88/jpstock_webapp?style=social)](https://github.com/justpassion88/jpstock_webapp)
[![GitHub Forks](https://img.shields.io/github/forks/justpassion88/jpstock_webapp?style=social)](https://github.com/justpassion88/jpstock_webapp/fork)

[🏠 Home](https://justpassion88.github.io/jpstock_webapp/) • 
[🏦 Banks](https://justpassion88.github.io/jpstock_webapp/bank.html) • 
[📊 Stock](https://justpassion88.github.io/jpstock_webapp/stock.html) • 
[📈 Sector](https://justpassion88.github.io/jpstock_webapp/sector.html) • 
[🌡️ Market Heat](https://justpassion88.github.io/jpstock_webapp/market.html)

</div>