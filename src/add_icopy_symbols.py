"""
Script to add iCopy symbols to sectors configuration
"""

# Phân loại 76 mã mới theo ngành
ICOPY_SYMBOLS = {
    "banks": [
        "NAB",  # Nam A Bank (iCopy)
        "BAF",  # Bac A Bank Finance (iCopy)
        "VAB",  # Vietnam Asia Bank (iCopy) - đã có
        "VIB",  # VIB (iCopy) - đã có
        "SSB",  # Southeast Asia Bank (iCopy) - đã có
    ],
    
    "realestate": [
        "DXS",  # Dat Xanh Services (iCopy)
        "DPG",  # Dat Phuong Group (iCopy)
        "DHA",  # Hoa An (iCopy)
        "NHA",  # Nha Ha Noi (iCopy)
        "CRE",  # Cen Land (iCopy)
        "IJC",  # IJC (iCopy)
        "KHG",  # Khang Hoa (iCopy)
        "TDH",  # Thu Duc House (iCopy) - tương tự TDC
        "SZC",  # Sonadezi Chau Duc (iCopy)
        "ITC",  # InvestConsult (iCopy)
    ],
    
    "securities": [
        "BVS",  # Bao Viet Securities (iCopy)
        "VDS",  # VDSC (iCopy)
        "VCS",  # VietCap Securities (iCopy)
        "IPA",  # IPA (iCopy)
        "VFS",  # VFS (iCopy)
        "SHS",  # SHS (iCopy) - đã có
    ],
    
    "energy": [
        "GEE",  # GEE (iCopy)
        "VSC",  # Southern Seed (iCopy)
        "TBC",  # Thac Ba (iCopy) - đã có
        "PLC",  # Pha Lai Thermopower (iCopy)
        "SIP",  # SP Power (iCopy)
    ],
    
    "oilgas": [
        "PVS",  # PV Service (iCopy) - đã có
        "PVT",  # PV Trans (iCopy) - đã có
        "PVD",  # PV Drilling (iCopy) - đã có
    ],
    
    "steel": [
        "HSG",  # Hoa Sen (iCopy) - đã có
        "HPG",  # Hoa Phat (iCopy) - đã có
        "NKG",  # Nam Kim (iCopy) - đã có
        "VIS",  # VIS (iCopy) - đã có
    ],
    
    "construction": [
        "CTI",  # CTCP Đầu tư & Công nghiệp Cotec (iCopy)
        "HUT",  # Hutec (iCopy) - đã có
        "CTD",  # Coteccons (iCopy) - đã có
        "CII",  # CII (iCopy) - đã có
        "HTN",  # HTXD (iCopy)
        "TRC",  # Cao su Thuan Chau (iCopy)
        "DRC",  # Cao su Danang (iCopy)
        "CSM",  # CSM (iCopy)
        "PTB",  # Phuthobus (iCopy)
    ],
    
    "insurance": [
        "BVH",  # Bao Viet (iCopy) - đã có
        "PVI",  # PVI (iCopy) - đã có
        "BMI",  # Bao Minh (iCopy) - đã có
        "MIG",  # MIG (iCopy) - đã có
    ],
    
    "retail": [
        "MWG",  # Mobile World (iCopy) - đã có
        "FRT",  # FRT (iCopy) - đã có
        "PNJ",  # PNJ (iCopy) - đã có
        "VNM",  # Vinamilk (iCopy) - đã có
        "SAB",  # Sabeco (iCopy) - đã có
        "MSN",  # Masan (iCopy) - đã có
        "KDC",  # Kinh Do (iCopy)
        "SAF",  # Safoco (iCopy)
        "ANV",  # Nam Viet (iCopy)
        "ASM",  # Sao Mai (iCopy)
        "GMD",  # Gemadept (iCopy)
        "HAG",  # HAG (iCopy)
        "SBT",  # SBT (iCopy)
        "VHC",  # Vinhomes (iCopy)
    ],
    
    "technology": [
        "FPT",  # FPT (iCopy) - đã có
        "CMG",  # CMG (iCopy) - đã có
        "VGI",  # VGI (iCopy) - đã có
        "SAM",  # Saigon Cables (iCopy)
        "VNT",  # Vina Transport (iCopy)
        "TNG",  # TNG (iCopy)
        "DTD",  # DTD (iCopy)
        "VIP",  # VIP (iCopy)
        "VIX",  # VIX (iCopy)
        "EVF",  # EVF (iCopy)
    ],
    
    "chemicals": [
        "DCM",  # DCM (iCopy) - đã có
        "DGC",  # DGC (iCopy) - đã có
        "DPM",  # DPM (iCopy) - đã có
        "BFC",  # BFC (iCopy) - đã có
        "CSV",  # CSV (iCopy) - đã có
        "DHC",  # DHC (iCopy) - đã có
        "AAA",  # An Phat Plastic (iCopy)
        "GIL",  # GIL (iCopy)
        "BMP",  # BMP (iCopy)
        "DCL",  # DCL (iCopy)
        "PAC",  # PAC (iCopy)
        "PHR",  # PHR (iCopy)
        "DBC",  # DBC (iCopy)
        "DBD",  # DBD (iCopy)
    ],
    
    # Ngành mới: Vận tải & Logistics
    "transport": [
        "GMD",  # Gemadept (iCopy)
        "VJC",  # Vietjet (iCopy)
        "HAH",  # Hai Au Aviation (iCopy)
        "PAN",  # PAN (iCopy)
        "VOS",  # VOS (iCopy)
        "VTP",  # VTP (iCopy)
        "VPI",  # VPI (iCopy)
        "TCX",  # TCX (iCopy)
    ],
    
    # Ngành mới: Nông nghiệp & Thủy sản
    "agriculture": [
        "HAG",  # HAG (iCopy)
        "AGG",  # AGG (iCopy)
        "HNG",  # HNG (iCopy)
        "NSC",  # NSC (iCopy)
        "VIF",  # VIF (iCopy)
    ],
    
    # Các ngành khác
    "others": [
        "REE",  # REE (iCopy) - đã có
        "GAS",  # GAS (iCopy) - đã có
        "POW",  # POW (iCopy) - đã có
        "GEX",  # GEX (iCopy)
        "GEE",  # GEE (iCopy)
        "IDI",  # IDI (iCopy)
        "IMP",  # IMP (iCopy)
        "KSB",  # KSB (iCopy)
        "MSH",  # MSH (iCopy)
        "NAF",  # NAF (iCopy)
        "NTL",  # NTL (iCopy)
        "NTP",  # NTP (iCopy)
        "PET",  # PET (iCopy)
        "CTR",  # CTR (iCopy)
        "DSE",  # DSE (iCopy)
        "SCS",  # SCS (iCopy)
        "SHI",  # SHI (iCopy)
        "TCH",  # TCH (iCopy)
        "TCM",  # TCM (iCopy)
        "TDP",  # TDP (iCopy)
        "TIG",  # TIG (iCopy)
        "TLG",  # TLG (iCopy)
        "TNH",  # TNH (iCopy)
        "VPL",  # VPL (iCopy)
        "YEG",  # YEG (iCopy)
    ],
}


# Các mã cần thêm thực sự (loại bỏ đã có)
NEW_SYMBOLS_ONLY = {
    "banks": ["NAB", "BAF"],
    
    "realestate": ["DXS", "DPG", "DHA", "NHA", "CRE", "IJC", "KHG", "SZC"],
    
    "securities": ["BVS", "VDS", "VCS", "IPA", "VFS"],
    
    "energy": ["GEE", "VSC", "PLC", "SIP"],
    
    "steel": [],  # Tất cả đã có
    
    "construction": ["CTI", "HTN", "TRC", "DRC", "CSM", "PTB"],
    
    "insurance": [],  # Tất cả đã có
    
    "retail": ["KDC", "ANV", "ASM", "GMD", "HAG", "SBT", "VHC"],
    
    "technology": ["TNG", "DTD", "VIP", "VIX", "EVF"],
    
    "chemicals": ["AAA", "GIL", "BMP", "DCL", "PAC", "PHR", "DBC", "DBD"],
    
    "transport": ["VJC", "HAH", "PAN", "VOS", "VTP", "VPI", "TCX"],
    
    "agriculture": ["AGG"],
    
    "others": ["GEX", "IDI", "IMP", "KSB", "MSH", "NAF", "NTL", "NTP", "PET", "CTR", "DSE", "SCS", "SHI", "TCH", "TCM", "TDP", "TIG", "TLG", "TNH", "VPL", "YEG"],
}


if __name__ == "__main__":
    total = sum(len(symbols) for symbols in NEW_SYMBOLS_ONLY.values())
    print(f"Tổng số mã mới cần thêm: {total}")
    
    for sector, symbols in NEW_SYMBOLS_ONLY.items():
        if symbols:
            print(f"\n{sector}: {len(symbols)} mã")
            print(f"  {', '.join(symbols)}")
