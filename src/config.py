"""
Configuration for JP Stock Webapp
Banking sector P/B analysis
"""

# Danh sách mã ngân hàng Việt Nam
BANK_SYMBOLS = [
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
    "SSB",  # SeABank
    "ABB",  # ABBank
    "VIB",  # VIB
    "NAB",  # Nam A Bank
    "PGB",  # PG Bank
    "BVB",  # Viet Capital Bank
    "VAB",  # VietABank
    "KLB",  # Kien Long Bank
    "BAB",  # Bac A Bank
    "SGB",  # Saigonbank
    "NVB",  # NCB
]

# Bank names mapping
BANK_NAMES = {
    "VCB": "Vietcombank",
    "BID": "BIDV",
    "CTG": "VietinBank",
    "TCB": "Techcombank",
    "MBB": "MB Bank",
    "VPB": "VPBank",
    "ACB": "ACB",
    "HDB": "HDBank",
    "STB": "Sacombank",
    "TPB": "TPBank",
    "SHB": "SHB",
    "LPB": "LienVietPostBank",
    "MSB": "MSB",
    "OCB": "OCB",
    "EIB": "Eximbank",
    "SSB": "SeABank",
    "ABB": "ABBank",
    "VIB": "VIB",
    "NAB": "Nam A Bank",
    "PGB": "PG Bank",
    "BVB": "Viet Capital Bank",
    "VAB": "VietABank",
    "KLB": "Kien Long Bank",
    "BAB": "Bac A Bank",
    "SGB": "Saigonbank",
    "NVB": "NCB",
}

# Data source configuration
DATA_SOURCE = "VCI"  # VCI hoặc TCBS hoặc MSN

# Output paths
OUTPUT_DIR = "../docs/data"
OUTPUT_FILE = "banks.json"

# Analysis parameters
PERCENTILE_THRESHOLDS = {
    "extremely_cheap": 10,   # < 10th percentile
    "cheap": 25,             # 10-25th percentile
    "fair_low": 25,          # 25-75th percentile (fair value)
    "fair_high": 75,
    "expensive": 90,         # 75-90th percentile
    "extremely_expensive": 90  # > 90th percentile
}

# Valuation zones labels
VALUATION_ZONES = {
    "EXTREMELY_CHEAP": {"label": "Cực rẻ", "signal": "STRONG_BUY", "color": "#15803d"},
    "CHEAP": {"label": "Rẻ", "signal": "BUY", "color": "#22c55e"},
    "FAIR": {"label": "Hợp lý", "signal": "HOLD", "color": "#6b7280"},
    "EXPENSIVE": {"label": "Đắt", "signal": "SELL", "color": "#f97316"},
    "EXTREMELY_EXPENSIVE": {"label": "Cực đắt", "signal": "STRONG_SELL", "color": "#dc2626"},
}
