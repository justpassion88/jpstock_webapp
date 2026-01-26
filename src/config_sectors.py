"""
Multi-Sector Configuration for JP Stock Webapp
P/B Analysis across VN100+ stocks
"""

# =============================================================================
# SECTOR DEFINITIONS (~115 stocks)
# =============================================================================

SECTORS = {
    # =========================================================================
    # 🏦 NGÂN HÀNG - Banks (15 mã)
    # P/B analysis: ⭐⭐⭐⭐⭐ (Tuyệt vời)
    # =========================================================================
    "banks": {
        "name": "🏦 Ngân hàng",
        "name_en": "Banks",
        "description": "Ngân hàng thương mại Việt Nam",
        "pb_suitable": 5,  # 1-5 rating
        "color": "#3B82F6",  # Blue
        "symbols": [
            "VCB",  # Vietcombank
            "BID",  # BIDV
            "CTG",  # VietinBank
            "TCB",  # Techcombank
            "MBB",  # MB Bank
            "VPB",  # VPBank
            "ACB",  # ACB
            "HDB",  # HDBank
            "STB",  # Sacombank
            "TPB",  # TPBank
            "SHB",  # SHB
            "LPB",  # LienVietPostBank
            "MSB",  # MSB
            "OCB",  # OCB
            "EIB",  # Eximbank
        ],
    },
    
    # =========================================================================
    # 🏠 BẤT ĐỘNG SẢN - Real Estate (20 mã)
    # P/B analysis: ⭐⭐⭐⭐⭐ (Tuyệt vời)
    # =========================================================================
    "realestate": {
        "name": "🏠 Bất động sản",
        "name_en": "Real Estate",
        "description": "Công ty bất động sản, phát triển dự án",
        "pb_suitable": 5,
        "color": "#10B981",  # Green
        "symbols": [
            "VHM",  # Vinhomes
            "VIC",  # Vingroup
            "NVL",  # Novaland
            "PDR",  # Phát Đạt
            "DXG",  # Đất Xanh
            "KDH",  # Khang Điền
            "NLG",  # Nam Long
            "DIG",  # DIC Corp
            "CEO",  # C.E.O Group
            "KBC",  # Kinh Bắc
            "BCM",  # Becamex
            "IDC",  # IDICO
            "ITA",  # Itaco
            "HDC",  # HDC
            "LDG",  # LDG Investment
            "NBB",  # NBB
            "TDC",  # Thu Duc Housing
            "VRE",  # Vincom Retail
            "SCR",  # Sài Gòn Thương Tín
            "HPX",  # Hai Phat Land
        ],
    },
    
    # =========================================================================
    # 📈 CHỨNG KHOÁN - Securities (12 mã)
    # P/B analysis: ⭐⭐⭐⭐⭐ (Tuyệt vời)
    # =========================================================================
    "securities": {
        "name": "📈 Chứng khoán",
        "name_en": "Securities",
        "description": "Công ty chứng khoán, môi giới",
        "pb_suitable": 5,
        "color": "#8B5CF6",  # Purple
        "symbols": [
            "SSI",  # SSI Securities
            "VND",  # VNDirect
            "HCM",  # HCMC Securities
            "VCI",  # Vietcap
            "SHS",  # SHS
            "MBS",  # MB Securities
            "FTS",  # FPT Securities
            "BSI",  # BVSC
            "CTS",  # Vietinbank Securities
            "ORS",  # ORS
            "TVS",  # Thien Viet
            "AGR",  # Agribank Securities
        ],
    },
    
    # =========================================================================
    # ⚡ ĐIỆN & NĂNG LƯỢNG - Energy & Utilities (15 mã)
    # P/B analysis: ⭐⭐⭐⭐ (Tốt)
    # =========================================================================
    "energy": {
        "name": "⚡ Điện & Năng lượng",
        "name_en": "Energy & Utilities",
        "description": "Sản xuất và phân phối điện, năng lượng tái tạo",
        "pb_suitable": 4,
        "color": "#F59E0B",  # Yellow
        "symbols": [
            "POW",  # PetroVietnam Power
            "GEG",  # Gia Lai Electricity
            "REE",  # REE Corp
            "NT2",  # NT2
            "PPC",  # Pha Lai Thermal Power
            "HND",  # Hai Phong Power
            "SJD",  # Can Don Hydro
            "VSH",  # Vinh Son Song Hinh
            "TBC",  # Thac Ba Power
            "HDG",  # Ha Do
            "PC1",  # Power Construction 1
            "QTP",  # Quang Ninh Power
            "PGV",  # PV Power
            "GAS",  # PV Gas
            "PLX",  # Petrolimex
        ],
    },
    
    # =========================================================================
    # 🛢️ DẦU KHÍ - Oil & Gas (8 mã)
    # P/B analysis: ⭐⭐⭐ (Khá)
    # =========================================================================
    "oilgas": {
        "name": "🛢️ Dầu khí",
        "name_en": "Oil & Gas",
        "description": "Khai thác, dịch vụ dầu khí",
        "pb_suitable": 3,
        "color": "#78716C",  # Gray
        "symbols": [
            "PVD",  # PV Drilling
            "PVS",  # PV Technical
            "PVT",  # PV Trans
            "BSR",  # Binh Son Refining
            "OIL",  # PV Oil
            "CNG",  # CNG Vietnam
            "PVC",  # PVC
            "PXS",  # PXS
        ],
    },
    
    # =========================================================================
    # 🏗️ THÉP & VẬT LIỆU - Steel & Materials (12 mã)
    # P/B analysis: ⭐⭐⭐ (Khá)
    # =========================================================================
    "steel": {
        "name": "🏗️ Thép & Vật liệu",
        "name_en": "Steel & Materials",
        "description": "Sản xuất thép, kim loại, vật liệu xây dựng",
        "pb_suitable": 3,
        "color": "#6B7280",  # Gray
        "symbols": [
            "HPG",  # Hoa Phat
            "HSG",  # Hoa Sen
            "NKG",  # Nam Kim
            "TLH",  # Thep Lao Hai
            "SMC",  # SMC
            "POM",  # Pomina
            "DTL",  # Dai Thien Loc
            "VIS",  # Vietnam Italy Steel
            "TVN",  # Thep Viet Nhat
            "TIS",  # TIS
            "VGS",  # VG Steel
            "HMC",  # Ho Chi Minh Metal
        ],
    },
    
    # =========================================================================
    # 🏗️ XÂY DỰNG - Construction (10 mã)
    # P/B analysis: ⭐⭐⭐⭐ (Tốt)
    # =========================================================================
    "construction": {
        "name": "🏗️ Xây dựng",
        "name_en": "Construction",
        "description": "Xây dựng hạ tầng, công trình",
        "pb_suitable": 4,
        "color": "#F97316",  # Orange
        "symbols": [
            "CTD",  # Coteccons
            "HBC",  # Hoa Binh Corp
            "VCG",  # Vinaconex
            "FCN",  # FECON
            "LCG",  # LICOGI 16
            "HUT",  # HUDVN
            "C4G",  # CIENCO 4
            "CII",  # Ho Chi Minh Infrastructure
            "HHV",  # Hai Hung JSC
            "TV2",  # Tu Liem Urban
        ],
    },
    
    # =========================================================================
    # 🛡️ BẢO HIỂM - Insurance (5 mã)
    # P/B analysis: ⭐⭐⭐⭐ (Tốt)
    # =========================================================================
    "insurance": {
        "name": "🛡️ Bảo hiểm",
        "name_en": "Insurance",
        "description": "Bảo hiểm phi nhân thọ, tái bảo hiểm",
        "pb_suitable": 4,
        "color": "#EC4899",  # Pink
        "symbols": [
            "BVH",  # Bao Viet Holdings
            "BMI",  # Bao Minh Insurance
            "PVI",  # PVI Holdings
            "BIC",  # BIC Corp
            "MIG",  # Military Insurance
            "ABI",  # Agribank Insurance
        ],
    },
    
    # =========================================================================
    # 🛒 BÁN LẺ & TIÊU DÙNG - Retail & Consumer (10 mã)
    # P/B analysis: ⭐⭐ (P/E phù hợp hơn)
    # =========================================================================
    "retail": {
        "name": "🛒 Bán lẻ & Tiêu dùng",
        "name_en": "Retail & Consumer",
        "description": "Bán lẻ, hàng tiêu dùng",
        "pb_suitable": 2,
        "color": "#14B8A6",  # Teal
        "symbols": [
            "VNM",  # Vinamilk
            "MSN",  # Masan
            "SAB",  # Sabeco
            "PNJ",  # PNJ
            "MWG",  # The Gioi Di Dong
            "DGW",  # Digiworld
            "FRT",  # FPT Retail
            "HAX",  # HAX
            "VGC",  # Viglacera
            "BCG",  # Bamboo Capital
        ],
    },
    
    # =========================================================================
    # 💻 CÔNG NGHỆ - Technology (8 mã)
    # P/B analysis: ⭐ (P/E, PS phù hợp hơn)
    # =========================================================================
    "technology": {
        "name": "💻 Công nghệ",
        "name_en": "Technology",
        "description": "Công nghệ thông tin, phần mềm, viễn thông",
        "pb_suitable": 1,
        "color": "#06B6D4",  # Cyan
        "symbols": [
            "FPT",  # FPT Corp
            "CMG",  # CMC Corp
            "VGI",  # Viettel Global
            "FOX",  # FPT Online
            "ELC",  # ELCOM
            "ITD",  # Intelli Development
            "ICT",  # ICT Corp
            "LHG",  # Long Hau Corp
        ],
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_all_symbols() -> list:
    """Get all symbols across all sectors"""
    symbols = []
    for sector_data in SECTORS.values():
        symbols.extend(sector_data["symbols"])
    return list(set(symbols))  # Remove duplicates


def get_sector_symbols(sector_id: str) -> list:
    """Get symbols for a specific sector"""
    if sector_id in SECTORS:
        return SECTORS[sector_id]["symbols"]
    return []


def get_symbol_sector(symbol: str) -> str:
    """Get sector for a symbol"""
    for sector_id, sector_data in SECTORS.items():
        if symbol in sector_data["symbols"]:
            return sector_id
    return "unknown"


def get_sector_info(sector_id: str) -> dict:
    """Get sector info"""
    return SECTORS.get(sector_id, {})


def get_pb_suitable_sectors(min_rating: int = 3) -> list:
    """Get sectors suitable for P/B analysis"""
    return [
        sector_id
        for sector_id, data in SECTORS.items()
        if data.get("pb_suitable", 0) >= min_rating
    ]


# =============================================================================
# SUMMARY
# =============================================================================

TOTAL_SYMBOLS = len(get_all_symbols())
TOTAL_SECTORS = len(SECTORS)

# Print summary when loaded
if __name__ == "__main__":
    print("=" * 60)
    print("MULTI-SECTOR CONFIGURATION")
    print("=" * 60)
    print(f"\nTotal Sectors: {TOTAL_SECTORS}")
    print(f"Total Symbols: {TOTAL_SYMBOLS}")
    print("\nSector breakdown:")
    for sector_id, data in SECTORS.items():
        pb_stars = "⭐" * data["pb_suitable"]
        print(f"  {data['name']}: {len(data['symbols'])} mã | P/B: {pb_stars}")
    
    print("\n\nP/B Suitable sectors (≥3 stars):")
    for sector_id in get_pb_suitable_sectors(3):
        print(f"  - {SECTORS[sector_id]['name']}")


# =============================================================================
# DATA SOURCE CONFIG
# =============================================================================

DATA_SOURCE = "VCI"  # VCI hoặc TCBS

# Output paths
OUTPUT_DIR = "../docs/data"

# Analysis parameters
PERCENTILE_THRESHOLDS = {
    "very_cheap": 20,    # < 20th percentile
    "cheap": 35,         # 20-35th percentile
    "fair_low": 35,      # 35-65th percentile (fair value)
    "fair_high": 65,
    "expensive": 80,     # 65-80th percentile
    "very_expensive": 80  # > 80th percentile
}

# Valuation zones
VALUATION_ZONES = {
    "VERY_CHEAP": {"label": "Rất rẻ", "signal": "STRONG_BUY", "color": "#15803d"},
    "CHEAP": {"label": "Rẻ", "signal": "BUY", "color": "#22c55e"},
    "FAIR": {"label": "Hợp lý", "signal": "HOLD", "color": "#6b7280"},
    "EXPENSIVE": {"label": "Đắt", "signal": "REDUCE", "color": "#f97316"},
    "VERY_EXPENSIVE": {"label": "Rất đắt", "signal": "SELL", "color": "#dc2626"},
}
