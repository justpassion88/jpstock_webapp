# JP Stock Webapp - Phân Tích P/B Định Lượng Ngân Hàng

[![Update Bank Data](https://github.com/justpassion88/jpstock_webapp/actions/workflows/update-data.yml/badge.svg)](https://github.com/justpassion88/jpstock_webapp/actions/workflows/update-data.yml)

## 🎯 Giới Thiệu

Ứng dụng web phân tích định lượng P/B (Price-to-Book) cho ngành ngân hàng Việt Nam. Sử dụng dữ liệu lịch sử 10+ năm để đánh giá vùng định giá rẻ/đắt của từng cổ phiếu so với chính nó.

**🌐 Live Demo:** [https://justpassion88.github.io/jpstock_webapp/](https://justpassion88.github.io/jpstock_webapp/)

## ✨ Tính Năng

- 📊 **Phân tích P/B định lượng** - Dựa trên dữ liệu lịch sử 13 năm (2012-2024)
- 🎯 **AI định lượng vùng giá** - Xác định rẻ/đắt dựa trên percentile thực tế
- 💰 **Expected Return** - Ước tính lợi nhuận kỳ vọng dựa trên mean reversion
- ⚠️ **Risk Score** - Đánh giá rủi ro dựa trên Z-score
- 📈 **Biểu đồ tương tác** - Visualize P/B lịch sử với Plotly.js
- 🔄 **Cập nhật tự động** - GitHub Actions chạy daily batch job

## 🏦 Ngân Hàng Được Phân Tích

27 mã ngân hàng niêm yết: VCB, BID, CTG, TCB, MBB, VPB, ACB, HDB, STB, TPB, SHB, LPB, MSB, OCB, EIB, SSB, ABB, VIB, NAB, PGB, BVB, VAB, KLB, BAB, SGB, NVB

## 📊 Phương Pháp Định Giá

### Vùng Định Giá (Percentile-based)

| Percentile | Vùng | Tín Hiệu |
|------------|------|----------|
| < 10% | Cực rẻ | 🟢 STRONG BUY |
| 10-25% | Rẻ | 🟢 BUY |
| 25-75% | Hợp lý | ⚪ HOLD |
| 75-90% | Đắt | 🟠 SELL |
| > 90% | Cực đắt | 🔴 STRONG SELL |

### Công Thức

```
Expected Return = (P/B_median - P/B_current) / P/B_current × Probability

Risk Score = 50 + Z_score × 25 (normalized 0-100)

Z_score = (P/B_current - P/B_mean) / P/B_std
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Data Source | [vnstock](https://github.com/thinh-vu/vnstock) |
| Analysis | Python + pandas + scipy |
| Frontend | HTML + Tailwind CSS + Plotly.js |
| Automation | GitHub Actions (daily cron) |
| Hosting | GitHub Pages |

## 📁 Cấu Trúc Dự Án

```
jpstock_webapp/
├── .github/workflows/
│   └── update-data.yml    # Daily batch job
├── src/
│   ├── config.py          # Cấu hình (danh sách mã, thresholds)
│   ├── fetch_data.py      # Lấy dữ liệu từ vnstock
│   ├── analyze.py         # P/B analysis engine
│   └── requirements.txt   # Python dependencies
├── docs/                   # GitHub Pages
│   ├── index.html         # Dashboard chính
│   ├── stock.html         # Trang chi tiết
│   ├── data/
│   │   └── banks.json     # Dữ liệu đã phân tích
│   ├── js/
│   │   ├── app.js         # Main app logic
│   │   └── stock.js       # Stock detail logic
│   └── css/
│       └── style.css      # Custom styles
└── README.md
```

## 🚀 Chạy Local

### 1. Clone repo

```bash
git clone https://github.com/justpassion88/jpstock_webapp.git
cd jpstock_webapp
```

### 2. Cài đặt dependencies

```bash
cd src
pip install -r requirements.txt
```

### 3. Fetch data & analyze

```bash
python fetch_data.py
python analyze.py
```

### 4. Chạy web local

```bash
cd ../docs
python -m http.server 8000
# Mở http://localhost:8000
```

## 🔄 GitHub Actions

Workflow tự động chạy lúc 6:00 AM UTC (1:00 PM Vietnam) mỗi ngày:
1. Fetch dữ liệu mới từ vnstock
2. Chạy phân tích P/B
3. Commit kết quả vào `docs/data/banks.json`
4. GitHub Pages tự động update

**Trigger thủ công:** Actions → Update Bank Data Daily → Run workflow

## 📝 Plan Phát Triển

### Phase 1 (Hiện tại) ✅
- [x] MVP cho ngành ngân hàng (27 mã)
- [x] Phân tích P/B percentile-based
- [x] GitHub Pages deployment
- [x] Daily auto-update

### Phase 2 (Tương lai)
- [ ] Thêm các ngành khác (BĐS, Chứng khoán, etc.)
- [ ] Kết hợp chỉ số ROE để tránh value trap
- [ ] Phân tích P/B toàn ngành (sector average)
- [ ] AI Bot chatbot hỏi đáp

### Phase 3 (Tương lai xa)
- [ ] Backtesting chiến lược P/B mean-reversion
- [ ] Portfolio optimization
- [ ] Alert system (Telegram/Email)

## ⚠️ Disclaimer

Đây là công cụ phân tích tham khảo dựa trên phương pháp định lượng. **KHÔNG phải khuyến nghị đầu tư**. Mọi quyết định đầu tư là trách nhiệm của người dùng.

## 📄 License

MIT License - Sử dụng tự do cho mục đích cá nhân và thương mại.

---

Made with ❤️ by [@justpassion88](https://github.com/justpassion88)