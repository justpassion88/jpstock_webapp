/**
 * Notes & Star Symbols Configuration
 * Ghi chú và đánh dấu cổ phiếu yêu thích
 * 
 * HƯỚNG DẪN SỬ DỤNG:
 * 
 * 1. THÊM MÃ STAR (yêu thích):
 *    - Thêm symbol vào STAR_SYMBOLS bên dưới
 *    - Ví dụ: "VCB", "TCB", "FPT"
 * 
 * 2. THÊM GHI CHÚ:
 *    - Thêm vào STOCK_NOTES với format:
 *      "SYMBOL": "Nội dung ghi chú của bạn"
 * 
 * 3. THÊM GHI CHÚ NGÀNH:
 *    - Thêm vào SECTOR_NOTES với format:
 *      "sector_key": "Nội dung ghi chú"
 *    - sector_key: banks, realestate, securities, steel, etc.
 * 
 * Last updated: 2026-01-28
 */

// ============================================
// ⭐ STAR SYMBOLS - Mã cổ phiếu yêu thích
// ============================================
const STAR_SYMBOLS = new Set([
    // Thêm mã yêu thích của bạn vào đây
    // Ví dụ:
    "MBB",   // MBB - Ngân hàng Quân Đội
    "PNJ",   // PNJ - Vàng bạc đá quý
    "VNM",   // Vinamilk - Hàng tiêu dùng
]);

// ============================================
// 📝 STOCK NOTES - Ghi chú theo mã cổ phiếu
// ============================================
const STOCK_NOTES = {
    // Ví dụ cách thêm ghi chú:
    "MBB": "P/B thấp, tiềm năng tăng trưởng cao. Mua khi P/B < 1.2",
    "PNJ": "P/E = 14 - 16 xem xét thăm dò, P/E = 12 - 13 Hấp dẫn, P/E < 12 Mua mạnh.",
    "VNM": "P/E = 11 - 13 vùng mua tốt, P/E = 13 - 14 xem xét thăm dò, P/E > 14-16 giảm tỷ trọng.P/E ≥18 bán.",
};

// ============================================
// 🏭 SECTOR NOTES - Ghi chú theo ngành
// ============================================
const SECTOR_NOTES = {
    // Ví dụ:
    // "banks": "Ngành ngân hàng đang trong chu kỳ hồi phục. Ưu tiên nhóm big4.",
    // "steel": "Ngành thép phụ thuộc giá thép thế giới. Theo dõi giá HRC.",
    // "realestate": "BĐS vẫn chờ chính sách. Chọn lọc mã có quỹ đất sạch.",
};

// ============================================
// 📊 MARKET NOTES - Ghi chú thị trường chung
// ============================================
const MARKET_NOTES = {
    // Ghi chú chung về thị trường
    general: "",
    // Ví dụ:
    // general: "Thị trường đang sideway 1200-1300. Chờ breakout để tăng tỷ trọng.",
};


// ============================================
// HELPER FUNCTIONS - Không cần sửa phần này
// ============================================

/**
 * Check if a symbol is starred
 */
function isStarSymbol(symbol) {
    if (!symbol) return false;
    return STAR_SYMBOLS.has(symbol.toUpperCase());
}

/**
 * Get Star badge HTML
 */
function getStarBadge(size = 'sm') {
    const sizes = {
        'xs': 'text-[10px] px-1 py-0.5',
        'sm': 'text-[11px] px-1.5 py-0.5',
        'md': 'text-xs px-2 py-1',
        'lg': 'text-sm px-2.5 py-1'
    };
    
    return `<span class="inline-flex items-center ${sizes[size]} font-semibold bg-gradient-to-r from-yellow-500 to-orange-500 text-white rounded-full shadow-sm ml-1" title="⭐ Star - Mã yêu thích">⭐ Star</span>`;
}

/**
 * Get Star icon (smaller version for tables)
 */
function getStarIcon() {
    return `<span class="inline-flex items-center justify-center w-4 h-4 text-[10px] bg-gradient-to-r from-yellow-500 to-orange-500 text-white rounded-full ml-1 shadow-sm" title="⭐ Star - Mã yêu thích">★</span>`;
}

/**
 * Get total Star symbols count
 */
function getStarCount() {
    return STAR_SYMBOLS.size;
}

/**
 * Get note for a stock
 */
function getStockNote(symbol) {
    if (!symbol) return null;
    return STOCK_NOTES[symbol.toUpperCase()] || null;
}

/**
 * Get note for a sector
 */
function getSectorNote(sectorKey) {
    if (!sectorKey) return null;
    return SECTOR_NOTES[sectorKey.toLowerCase()] || null;
}

/**
 * Get market general note
 */
function getMarketNote() {
    return MARKET_NOTES.general || null;
}

/**
 * Get note badge HTML for display
 */
function getNoteBadgeHTML(note) {
    if (!note) return '';
    return `
        <div class="bg-gray-800/80 border border-yellow-500/30 rounded-lg p-3 mt-2">
            <div class="flex items-start gap-2">
                <span class="text-yellow-400">📝</span>
                <p class="text-gray-300 text-sm">${note}</p>
            </div>
        </div>
    `;
}

/**
 * Get inline note icon (for tables - shows tooltip on hover)
 */
function getNoteIcon(note) {
    if (!note) return '';
    // Escape quotes for HTML attribute
    const escapedNote = note.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    return `<span class="inline-flex items-center justify-center w-4 h-4 text-[10px] bg-yellow-500/20 text-yellow-400 rounded ml-1 cursor-help" title="${escapedNote}">📝</span>`;
}

// Log loaded config
console.log(`📝 Notes Config loaded: ${STAR_SYMBOLS.size} Star symbols, ${Object.keys(STOCK_NOTES).length} stock notes`);
