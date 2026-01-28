"""
Auto-update config_sectors.py with iCopy symbols
"""

# Read current config
with open('config_sectors.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define all updates
updates = {
    '"securities": {': {
        'old_count': '(12 mã)',
        'new_count': '(17 mã)',
        'add_after': '"AGR",  # Agribank Securities',
        'new_symbols': [
            '            "BVS",  # Bao Viet Securities (iCopy)',
            '            "VDS",  # VDSC (iCopy)',
            '            "VCS",  # VietCap Securities (iCopy)',
            '            "IPA",  # IPA (iCopy)',
            '            "VFS",  # VFS (iCopy)',
        ]
    },
    '"energy": {': {
        'old_count': '(15 mã)',
        'new_count': '(19 mã)',
        'add_after': '            "PLX",  # Petrolimex',
        'new_symbols': [
            '            "GEE",  # GEE (iCopy)',
            '            "VSC",  # Southern Seed (iCopy)',
            '            "PLC",  # Pha Lai Thermopower (iCopy)',
            '            "SIP",  # SP Power (iCopy)',
        ]
    },
    '"construction": {': {
        'old_count': '(10 mã)',
        'new_count': '(16 mã)',
        'add_after': '            "TV2",  # Tu Liem Urban',
        'new_symbols': [
            '            "CTI",  # Cotec Investment (iCopy)',
            '            "HTN",  # HTXD (iCopy)',
            '            "TRC",  # Thuan Chau Rubber (iCopy)',
            '            "DRC",  # Danang Rubber (iCopy)',
            '            "CSM",  # CSM (iCopy)',
            '            "PTB",  # Phuthobus (iCopy)',
        ]
    },
    '"retail": {': {
        'old_count': '(10 mã)',
        'new_count': '(17 mã)',
        'add_after': '            "BCG",  # Bamboo Capital',
        'new_symbols': [
            '            "KDC",  # Kinh Do (iCopy)',
            '            "ANV",  # Nam Viet (iCopy)',
            '            "ASM",  # Sao Mai (iCopy)',
            '            "GMD",  # Gemadept (iCopy)',
            '            "HAG",  # HAG (iCopy)',
            '            "SBT",  # SBT (iCopy)',
            '            "VHC",  # Vinhomes Commercial (iCopy)',
        ]
    },
    '"technology": {': {
        'old_count': '(8 mã)',
        'new_count': '(13 mã)',
        'add_after': '            "LHG",  # Long Hau Corp',
        'new_symbols': [
            '            "TNG",  # TNG (iCopy)',
            '            "DTD",  # DTD (iCopy)',
            '            "VIP",  # VIP (iCopy)',
            '            "VIX",  # VIX (iCopy)',
            '            "EVF",  # EVF (iCopy)',
        ]
    },
    '"chemicals": {': {
        'old_count': '(8 mã)',
        'new_count': '(16 mã)',
        'add_after': '            "GVR",  # Group Cao Su VN',
        'new_symbols': [
            '            "AAA",  # An Phat Plastic (iCopy)',
            '            "GIL",  # GIL (iCopy)',
            '            "BMP",  # BMP (iCopy)',
            '            "DCL",  # DCL (iCopy)',
            '            "PAC",  # PAC (iCopy)',
            '            "PHR",  # PHR (iCopy)',
            '            "DBC",  # DBC (iCopy)',
            '            "DBD",  # DBD (iCopy)',
        ]
    },
}

# Apply updates
for sector_marker, update_info in updates.items():
    if sector_marker in content:
        # Update count in comment
        content = content.replace(
            f"{sector_marker.split(':')[0]} {update_info['old_count']}",
            f"{sector_marker.split(':')[0]} {update_info['new_count']}"
        )
        
        # Add new symbols
        add_after = update_info['add_after']
        new_symbols_str = '\n' + '\n'.join(update_info['new_symbols'])
        content = content.replace(add_after, add_after + new_symbols_str)

# Write back
with open('config_sectors.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Updated config_sectors.py with iCopy symbols")
