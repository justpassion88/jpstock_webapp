"""
Multi-Sector Configuration for JP Stock Webapp
P/B Analysis across VN100+ stocks
"""

# =============================================================================
# SECTOR DEFINITIONS (~115 stocks)
# =============================================================================

SECTORS = {
    # =========================================================================
    # 🏦 NGÂN HÀNG - Banks (20 mã)
    # P/B analysis: ⭐⭐⭐⭐⭐ (Tuyệt vời)
    # =========================================================================
    "banks": {
        "name": "🏦 Ngân hàng",
        "name_en": "Banks",
        "description": "Ngân hàng thương mại Việt Nam",
        "pb_suitable": 5,  # 1-5 rating
        "color": "#3B82F6",  # Blue
        "symbols": [
            "ACB",  # ACB
            "BAF",  # Bac A Bank Finance (iCopy)
            "BID",  # BIDV
            "CTG",  # VietinBank
            "EIB",  # Eximbank
            "HDB",  # HDBank
            "LPB",  # LienVietPostBank
            "MBB",  # MB Bank
            "MSB",  # MSB
            "NAB",  # Nam A Bank (iCopy)
            "OCB",  # OCB
            "SHB",  # SHB
            "SHI",  # SHI (iCopy)
            "SSB",  # SSB (iCopy)
            "STB",  # Sacombank
            "TCB",  # Techcombank
            "TPB",  # TPBank
            "VCB",  # Vietcombank
            "VIB",  # VIB (iCopy)
            "VPB",  # VPBank
        ],
    },
    
    # =========================================================================
    # 🏠 BẤT ĐỘNG SẢN - Real Estate (39 mã)
    # P/B analysis: ⭐⭐⭐⭐⭐ (Tuyệt vời)
    # =========================================================================
    "realestate": {
        "name": "🏠 Bất động sản",
        "name_en": "Real Estate",
        "description": "Công ty bất động sản, phát triển dự án",
        "pb_suitable": 5,
        "color": "#10B981",  # Green
        "symbols": [
            "AAA",  # AAA (iCopy)
            "BCM",  # Becamex
            "CEO",  # C.E.O Group
            "CRE",  # Cen Land (iCopy)
            "DHA",  # Hoa An (iCopy)
            "DHC",  # DHC (iCopy)
            "DIG",  # DIC Corp
            "DPG",  # Dat Phuong Group (iCopy)
            "DPR",  # Phát Đạt (iCopy)
            "DRC",  # DRC (iCopy)
            "DTD",  # DTD (iCopy)
            "DXG",  # Đất Xanh
            "DXS",  # Dat Xanh Services (iCopy)
            "HAG",  # HAG (iCopy)
            "HAH",  # HAH (iCopy)
            "HDC",  # HDC
            "HPX",  # Hai Phat Land
            "IDC",  # IDICO
            "IJC",  # IJC (iCopy)
            "IMP",  # IMP (iCopy)
            "ITA",  # Itaco
            "KBC",  # Kinh Bắc
            "KDH",  # Khang Điền
            "KHG",  # Khang Hoa (iCopy)
            "LDG",  # LDG Investment
            "NBB",  # NBB
            "NHA",  # Nha Ha Noi (iCopy)
            "NLG",  # Nam Long
            "NTL",  # NTL (iCopy)
            "NVL",  # Novaland
            "PDR",  # Phát Đạt
            "PHR",  # PHR (iCopy)
            "PLC",  # PLC (iCopy)
            "SCR",  # Sài Gòn Thương Tín
            "SZC",  # Sonadezi Chau Duc (iCopy)
            "TDC",  # Thu Duc Housing
            "VHC",  # VHC (iCopy)
            "VHM",  # Vinhomes
            "VIC",  # Vingroup
            "VRE",  # Vincom Retail
        ],
    },
    
    # =========================================================================
    # 📈 CHỨNG KHOÁN - Securities (22 mã)
    # P/B analysis: ⭐⭐⭐⭐⭐ (Tuyệt vời)
    # =========================================================================
    "securities": {
        "name": "📈 Chứng khoán",
        "name_en": "Securities",
        "description": "Công ty chứng khoán, môi giới",
        "pb_suitable": 5,
        "color": "#8B5CF6",  # Purple
        "symbols": [
            "AGR",  # Agribank Securities (iCopy)
            "BSI",  # BVSC
            "BVS",  # BVS (iCopy)
            "CSM",  # CSM (iCopy)
            "CTS",  # Vietinbank Securities
            "EVF",  # EVF (iCopy)
            "FTS",  # FPT Securities
            "HCM",  # HCMC Securities
            "IPA",  # IPA (iCopy)
            "MBS",  # MB Securities
            "ORS",  # ORS
            "SCS",  # SCS (iCopy)
            "SHS",  # SHS
            "SIP",  # SIP (iCopy)
            "SSI",  # SSI Securities
            "TVS",  # Thien Viet
            "VCI",  # Vietcap
            "VCS",  # VCS (iCopy)
            "VDS",  # VDS (iCopy)
            "VFS",  # VFS (iCopy)
            "VIX",  # VIX (iCopy)
            "VND",  # VNDirect
        ],
    },
    
    # =========================================================================
    # ⚡ ĐIỆN & NĂNG LƯỢNG - Energy & Utilities (19 mã)
    # P/B analysis: ⭐⭐⭐⭐ (Tốt)
    # =========================================================================
    "energy": {
        "name": "⚡ Điện & Năng lượng",
        "name_en": "Energy & Utilities",
        "description": "Sản xuất và phân phối điện, năng lượng tái tạo",
        "pb_suitable": 4,
        "color": "#F59E0B",  # Yellow
        "symbols": [
            "GAS",  # PV Gas
            "GEE",  # GEE (iCopy)
            "GEG",  # Gia Lai Electricity
            "GEX",  # GEX (iCopy)
            "HDG",  # Ha Do
            "HND",  # Hai Phong Power
            "NT2",  # NT2
            "PC1",  # Power Construction 1
            "PGV",  # PV Power
            "PLX",  # Petrolimex
            "POW",  # PetroVietnam Power
            "PPC",  # Pha Lai Thermal Power
            "QTP",  # Quang Ninh Power
            "REE",  # REE Corp
            "SJD",  # Can Don Hydro
            "TBC",  # Thac Ba Power
            "VSC",  # VSC (iCopy)
            "VSH",  # Vinh Son Song Hinh
            "YEG",  # YEG (iCopy)
        ],
    },
    
    # =========================================================================
    # 🛢️ DẦU KHÍ - Oil & Gas (10 mã)
    # P/B analysis: ⭐⭐⭐ (Khá)
    # =========================================================================
    "oilgas": {
        "name": "🛢️ Dầu khí",
        "name_en": "Oil & Gas",
        "description": "Khai thác, dịch vụ dầu khí",
        "pb_suitable": 3,
        "color": "#78716C",  # Gray
        "symbols": [
            "BSR",  # Binh Son Refining
            "CNG",  # CNG Vietnam
            "OIL",  # PV Oil
            "PVC",  # PVC
            "PVD",  # PV Drilling
            "PVS",  # PV Technical
            "PVT",  # PV Trans
            "PVL",  # PVL (iCopy)
            "PXS",  # PXS
            "VPL",  # VPL (iCopy)
        ],
    },
    
    # =========================================================================
    # 🏗️ THÉP & VẬT LIỆU - Steel & Materials (13 mã)
    # P/B analysis: ⭐⭐⭐ (Khá)
    # =========================================================================
    "steel": {
        "name": "🏗️ Thép & Vật liệu",
        "name_en": "Steel & Materials",
        "description": "Sản xuất thép, kim loại, vật liệu xây dựng",
        "pb_suitable": 3,
        "color": "#6B7280",  # Gray
        "symbols": [
            "DTL",  # Dai Thien Loc
            "HMC",  # Ho Chi Minh Metal
            "HPG",  # Hoa Phat
            "HSG",  # Hoa Sen
            "NKG",  # Nam Kim
            "NTP",  # NTP (iCopy)
            "POM",  # Pomina
            "SMC",  # SMC
            "TIS",  # TIS
            "TLH",  # Thep Lao Hai
            "TVN",  # Thep Viet Nhat
            "VGS",  # VG Steel
            "VIS",  # Vietnam Italy Steel
        ],
    },
    
    # =========================================================================
    # 🏗️ XÂY DỰNG - Construction (19 mã)
    # P/B analysis: ⭐⭐⭐⭐ (Tốt)
    # =========================================================================
    "construction": {
        "name": "🏗️ Xây dựng",
        "name_en": "Construction",
        "description": "Xây dựng hạ tầng, công trình",
        "pb_suitable": 4,
        "color": "#F97316",  # Orange
        "symbols": [
            "ANV",  # ANV (iCopy)
            "C4G",  # CIENCO 4
            "CII",  # Ho Chi Minh Infrastructure
            "CTD",  # Coteccons
            "CTI",  # CTI (iCopy)
            "CTR",  # CTR (iCopy)
            "DCL",  # DCL (iCopy)
            "FCN",  # FECON
            "HBC",  # Hoa Binh Corp
            "HHV",  # Hai Hung JSC
            "HHS",  # HHS (iCopy)
            "HTN",  # HTN (iCopy)
            "HUT",  # HUDVN
            "LCG",  # LICOGI 16
            "PTB",  # PTB (iCopy)
            "TNG",  # TNG (iCopy)
            "TRC",  # TRC (iCopy)
            "TV2",  # Tu Liem Urban
            "VCG",  # Vinaconex
        ],
    },
    
    # =========================================================================
    # 🛡️ BẢO HIỂM - Insurance (7 mã)
    # P/B analysis: ⭐⭐⭐⭐ (Tốt)
    # =========================================================================
    "insurance": {
        "name": "🛡️ Bảo hiểm",
        "name_en": "Insurance",
        "description": "Bảo hiểm phi nhân thọ, tái bảo hiểm",
        "pb_suitable": 4,
        "color": "#EC4899",  # Pink
        "symbols": [
            "ABI",  # Agribank Insurance
            "BIC",  # BIC Corp
            "BMI",  # Bao Minh Insurance
            "BVH",  # Bao Viet Holdings
            "MIG",  # Military Insurance
            "PVI",  # PVI Holdings
            "VPI",  # VPI (iCopy)
        ],
    },
    
    # =========================================================================
    # 🛒 BÁN LẺ & TIÊU DÙNG - Retail & Consumer (23 mã)
    # P/B analysis: ⭐⭐ (P/E phù hợp hơn)
    # =========================================================================
    "retail": {
        "name": "🛒 Bán lẻ & Tiêu dùng",
        "name_en": "Retail & Consumer",
        "description": "Bán lẻ, hàng tiêu dùng",
        "pb_suitable": 2,
        "color": "#14B8A6",  # Teal
        "symbols": [
            "ASM",  # ASM (iCopy)
            "BCG",  # Bamboo Capital
            "BMP",  # BMP (iCopy)
            "DBC",  # DBC (iCopy)
            "DBD",  # DBD (iCopy)
            "DGW",  # Digiworld
            "FRT",  # FPT Retail
            "GMD",  # GMD (iCopy)
            "HAX",  # HAX
            "KDC",  # KDC (iCopy)
            "MSN",  # Masan
            "MWG",  # The Gioi Di Dong
            "NAF",  # NAF (iCopy)
            "PAC",  # PAC (iCopy)
            "PAN",  # PAN (iCopy)
            "PET",  # PET (iCopy)
            "PNJ",  # PNJ
            "SAB",  # Sabeco
            "SBT",  # SBT (iCopy)
            "VGC",  # Viglacera
            "VJC",  # VJC (iCopy)
            "VNM",  # Vinamilk
            "VOS",  # VOS (iCopy)
        ],
    },
    
    # =========================================================================
    # 💻 CÔNG NGHỆ - Technology (16 mã)
    # P/B analysis: ⭐ (P/E, PS phù hợp hơn)
    # =========================================================================
    "technology": {
        "name": "💻 Công nghệ",
        "name_en": "Technology",
        "description": "Công nghệ thông tin, phần mềm, viễn thông",
        "pb_suitable": 1,
        "color": "#06B6D4",  # Cyan
        "symbols": [
            "AGG",  # AGG (iCopy)
            "BWE",  # BWE (iCopy)
            "CMG",  # CMC Corp
            "DSE",  # DSE (iCopy)
            "ELC",  # ELCOM
            "FOX",  # FPT Online
            "FPT",  # FPT Corp
            "ICT",  # ICT Corp
            "IDI",  # IDI (iCopy)
            "ITD",  # Intelli Development
            "LHG",  # Long Hau Corp
            "TCH",  # TCH (iCopy)
            "TCM",  # TCM (iCopy)
            "VGI",  # Viettel Global
            "VIP",  # VIP (iCopy)
            "VTP",  # VTP (iCopy)
        ],
    },
    
    # =========================================================================
    # 🧪 HÓA CHẤT & CÔNG NGHIỆP - Chemicals & Industrial (16 mã)
    # P/B analysis: ⭐⭐⭐ (Khá)
    # =========================================================================
    "chemicals": {
        "name": "🧪 Hóa chất & Công nghiệp",
        "name_en": "Chemicals & Industrial",
        "description": "Sản xuất hóa chất, phân bón, công nghiệp",
        "pb_suitable": 3,
        "color": "#A855F7",  # Purple
        "symbols": [
            "BFC",  # Binh Dien Fertilizer
            "CSV",  # CSV Construction
            "DCM",  # DCM Corp
            "DGC",  # Duc Giang Chemicals
            "DHC",  # Dong Hai Bentre
            "DPM",  # PetroVietnam Fertilizer
            "GIL",  # GIL (iCopy)
            "GVR",  # Group Cao Su VN
            "KSB",  # KSB (iCopy)
            "LAS",  # Lam Thao Fertilizer
            "MSH",  # MSH (iCopy)
            "TCX",  # TCX (iCopy)
            "TDP",  # TDP (iCopy)
            "TIG",  # TIG (iCopy)
            "TLG",  # TLG (iCopy)
            "TNH",  # TNH (iCopy)
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
