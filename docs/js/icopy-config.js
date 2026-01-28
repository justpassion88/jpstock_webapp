/**
 * iCopy Symbols Configuration
 * List of symbols that are part of iCopy portfolio
 */

const ICOPY_SYMBOLS = new Set([
    // Banks (15)
    "ACB", "BID", "CTG", "EIB", "HDB", "LPB", "MBB", "MSB", "OCB", "SHB", "SSB", "STB", "TCB", "TPB", "VCB", "VIB", "VPB",
    
    // Real Estate (16)
    "BCM", "CEO", "CII", "DIG", "DXG", "HDC", "IDC", "KBC", "KDH", "NLG", "PDR", "SCR", "VHM", "VIC", "VRE",
    
    // Securities (10)
    "AGR", "BSI", "CTS", "FTS", "HCM", "MBS", "SHS", "SSI", "TVS", "VCI", "VND",
    
    // Energy (5)
    "GAS", "GEG", "PLX", "POW", "REE",
    
    // Steel (4)
    "HPG", "HSG", "NKG", "VGS",
    
    // Construction (5)
    "CII", "CTD", "HUT", "HBC", "LCG",
    
    // Insurance (5)
    "ABI", "BIC", "BMI", "BVH", "MIG", "PVI",
    
    // Retail (7)
    "DGW", "FRT", "MSN", "MWG", "PNJ", "SAB", "VNM",
    
    // Technology (5)
    "CMG", "ELC", "FPT", "FOX", "ICT",
    
    // Chemicals (8)
    "BFC", "CSV", "DCM", "DGC", "DHC", "DPM", "GVR", "LAS",
    
    // Oil & Gas (5)
    "BSR", "CNG", "OIL", "PVD", "PVS", "PVT", "PVC",
]);

/**
 * Check if a symbol is in iCopy portfolio
 */
function isICopySymbol(symbol) {
    return ICOPY_SYMBOLS.has(symbol.toUpperCase());
}

/**
 * Get iCopy badge HTML
 */
function getICopyBadge(size = 'sm') {
    const sizes = {
        'xs': 'text-[8px] px-1 py-0.5',
        'sm': 'text-[9px] px-1.5 py-0.5',
        'md': 'text-xs px-2 py-1',
        'lg': 'text-sm px-2.5 py-1'
    };
    
    return `<span class="inline-flex items-center ${sizes[size]} font-semibold bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-full shadow-sm ml-1" title="iCopy Portfolio">iCopy</span>`;
}

/**
 * Get iCopy icon (smaller version)
 */
function getICopyIcon() {
    return `<span class="inline-flex items-center justify-center w-4 h-4 text-[8px] font-bold bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-full ml-1 shadow-sm" title="iCopy Portfolio">i</span>`;
}
