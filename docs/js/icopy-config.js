/**
 * iCopy Symbols Configuration
 * List of 164 symbols that are part of iCopy portfolio
 * Last updated: 2026-01-29
 */

const ICOPY_SYMBOLS = new Set([
    // === A (6) ===
    "AAA",
    "ACB",
    "AGG",
    "AGR",
    "ANV",
    "ASM",

    // === B (11) ===
    "BAF",
    "BCM",
    "BFC",
    "BID",
    "BMI",
    "BMP",
    "BSI",
    "BSR",
    "BVH",
    "BVS",
    "BWE",

    // === C (11) ===
    "CEO",
    "CII",
    "CMG",
    "CRE",
    "CSM",
    "CSV",
    "CTD",
    "CTG",
    "CTI",
    "CTR",
    "CTS",

    // === D (17) ===
    "DBC",
    "DBD",
    "DCL",
    "DCM",
    "DGC",
    "DGW",
    "DHA",
    "DHC",
    "DIG",
    "DPG",
    "DPM",
    "DPR",
    "DRC",
    "DSE",
    "DTD",
    "DXG",
    "DXS",

    // === E (3) ===
    "EIB",
    "ELC",
    "EVF",

    // === F (4) ===
    "FCN",
    "FPT",
    "FRT",
    "FTS",

    // === G (7) ===
    "GAS",
    "GEE",
    "GEG",
    "GEX",
    "GIL",
    "GMD",
    "GVR",

    // === H (13) ===
    "HAG",
    "HAH",
    "HAX",
    "HCM",
    "HDB",
    "HDC",
    "HDG",
    "HHS",
    "HHV",
    "HPG",
    "HSG",
    "HTN",
    "HUT",

    // === I (5) ===
    "IDC",
    "IDI",
    "IJC",
    "IMP",
    "IPA",

    // === K (5) ===
    "KBC",
    "KDC",
    "KDH",
    "KHG",
    "KSB",

    // === L (3) ===
    "LAS",
    "LCG",
    "LPB",

    // === M (7) ===
    "MBB",
    "MBS",
    "MIG",
    "MSB",
    "MSH",
    "MSN",
    "MWG",

    // === N (7) ===
    "NAB",
    "NAF",
    "NHA",
    "NKG",
    "NLG",
    "NTL",
    "NTP",

    // === O (1) ===
    "OCB",

    // === P (14) ===
    "PAC",
    "PAN",
    "PDR",
    "PET",
    "PHR",
    "PLC",
    "PLX",
    "PNJ",
    "POW",
    "PTB",
    "PVD",
    "PVI",
    "PVS",
    "PVT",

    // === R (1) ===
    "REE",

    // === S (12) ===
    "SAB",
    "SBT",
    "SCR",
    "SCS",
    "SHB",
    "SHI",
    "SHS",
    "SIP",
    "SSB",
    "SSI",
    "STB",
    "SZC",

    // === T (12) ===
    "TCB",
    "TCH",
    "TCM",
    "TCX",
    "TDP",
    "TIG",
    "TLG",
    "TNG",
    "TNH",
    "TPB",
    "TRC",
    "TVS",

    // === V (24) ===
    "VCB",
    "VCG",
    "VCI",
    "VCS",
    "VDS",
    "VFS",
    "VGC",
    "VGS",
    "VHC",
    "VHM",
    "VIB",
    "VIC",
    "VIP",
    "VIX",
    "VJC",
    "VND",
    "VNM",
    "VOS",
    "VPB",
    "VPI",
    "VPL",
    "VRE",
    "VSC",
    "VTP",

    // === Y (1) ===
    "YEG"
]);

// Check if a symbol is in iCopy
function isICopySymbol(symbol) {
    return ICOPY_SYMBOLS.has(symbol?.toUpperCase());
}

// Get iCopy badge HTML
function getICopyBadge(size = 'sm') {
    const sizes = {
        'sm': 'text-xs px-1.5 py-0.5',
        'md': 'text-sm px-2 py-1',
        'lg': 'text-base px-3 py-1.5'
    };
    return `<span class="bg-gradient-to-r from-blue-600 to-purple-600 text-white ${sizes[size] || sizes.sm} rounded-full font-semibold">iCopy</span>`;
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ICOPY_SYMBOLS, isICopySymbol, getICopyBadge };
}
