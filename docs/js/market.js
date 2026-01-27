/**
 * Market Heat Map - Multi-Sector Analysis
 * JP Stock Analysis
 */

// Sector configuration
const SECTORS = {
    banks: { name: '🏦 Ngân hàng', file: 'banks.json', color: '#3B82F6' },
    realestate: { name: '🏠 Bất động sản', file: 'realestate.json', color: '#10B981' },
    securities: { name: '📈 Chứng khoán', file: 'securities.json', color: '#8B5CF6' },
    energy: { name: '⚡ Điện & Năng lượng', file: 'energy.json', color: '#F59E0B' },
    oilgas: { name: '🛢️ Dầu khí', file: 'oilgas.json', color: '#78716C' },
    steel: { name: '🏗️ Thép', file: 'steel.json', color: '#6B7280' },
    construction: { name: '🏗️ Xây dựng', file: 'construction.json', color: '#F97316' },
    insurance: { name: '🛡️ Bảo hiểm', file: 'insurance.json', color: '#EC4899' },
    retail: { name: '🛒 Bán lẻ', file: 'retail.json', color: '#14B8A6' },
    technology: { name: '💻 Công nghệ', file: 'technology.json', color: '#6366F1' },
    chemicals: { name: '🧪 Hóa chất', file: 'chemicals.json', color: '#A855F7' }
};

let marketData = null;
let sectorDataCache = {};

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    await loadMarketData();
});

// Load market overview data
async function loadMarketData() {
    try {
        const response = await fetch('data/market_heat.json');
        marketData = await response.json();
        
        renderMarketOverview();
        renderSectorCards();
        renderRecommendations();
    } catch (error) {
        console.error('Error loading market data:', error);
        document.getElementById('sector-cards').innerHTML = `
            <div class="col-span-full text-center py-8 text-red-400">
                ❌ Lỗi tải dữ liệu. Vui lòng thử lại.
            </div>
        `;
    }
}

// Render market overview
function renderMarketOverview() {
    const { market_heat, updated_at } = marketData;
    
    // Update stats
    document.getElementById('market-heat').textContent = market_heat.heat_index.toFixed(1);
    document.getElementById('market-heat').className = `text-3xl font-bold ${getHeatColor(market_heat.heat_index)}`;
    document.getElementById('total-sectors').textContent = market_heat.total_sectors;
    document.getElementById('total-stocks').textContent = market_heat.total_stocks;
    document.getElementById('market-signal').textContent = getSignalText(market_heat.heat_index);
    document.getElementById('market-signal').className = `text-xl font-bold ${getHeatColor(market_heat.heat_index)}`;
    
    // Update timestamp
    const date = new Date(updated_at);
    document.getElementById('last-updated').textContent = `Cập nhật: ${date.toLocaleString('vi-VN')}`;
    
    // Move heat marker
    document.getElementById('market-heat-marker').style.left = `${market_heat.heat_index}%`;
}

// Render sector cards
function renderSectorCards() {
    const container = document.getElementById('sector-cards');
    
    // Sort by heat index
    const sortedSectors = [...marketData.sectors].sort((a, b) => a.heat_index - b.heat_index);
    
    container.innerHTML = sortedSectors.map(sector => {
        const heatColor = getHeatColorHex(sector.heat_index);
        const config = SECTORS[sector.sector_id] || {};
        
        return `
            <div class="sector-card bg-gray-800 rounded-xl p-4 cursor-pointer border-l-4 hover:bg-gray-750"
                 style="border-left-color: ${heatColor}"
                 onclick="showSectorDetail('${sector.sector_id}')">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-lg">${sector.sector_name}</span>
                    <span class="text-xs text-gray-400">${sector.stocks_count} mã</span>
                </div>
                <div class="flex items-end justify-between">
                    <div>
                        <div class="text-2xl font-bold ${getHeatColor(sector.heat_index)}">${sector.heat_index.toFixed(1)}</div>
                        <div class="text-xs text-gray-400">${sector.status}</div>
                    </div>
                    <div class="text-right">
                        <div class="text-sm font-semibold ${getSignalColor(sector.signal)}">${sector.signal}</div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Render recommendations
function renderRecommendations() {
    const buySectors = marketData.sectors.filter(s => s.heat_index < 35);
    const accumulateSectors = marketData.sectors.filter(s => s.heat_index >= 35 && s.heat_index < 50);
    const cautionSectors = marketData.sectors.filter(s => s.heat_index >= 65);
    
    document.getElementById('buy-sectors').innerHTML = buySectors.length > 0 
        ? buySectors.map(s => `
            <div class="flex justify-between items-center text-green-200 bg-green-900/30 rounded px-3 py-2">
                <span>${s.sector_name}</span>
                <span class="font-bold">${s.heat_index.toFixed(1)}</span>
            </div>
        `).join('')
        : '<p class="text-green-300/50 text-sm">Không có ngành nào</p>';
    
    document.getElementById('accumulate-sectors').innerHTML = accumulateSectors.length > 0
        ? accumulateSectors.map(s => `
            <div class="flex justify-between items-center text-yellow-200 bg-yellow-900/30 rounded px-3 py-2">
                <span>${s.sector_name}</span>
                <span class="font-bold">${s.heat_index.toFixed(1)}</span>
            </div>
        `).join('')
        : '<p class="text-yellow-300/50 text-sm">Không có ngành nào</p>';
    
    document.getElementById('caution-sectors').innerHTML = cautionSectors.length > 0
        ? cautionSectors.map(s => `
            <div class="flex justify-between items-center text-red-200 bg-red-900/30 rounded px-3 py-2">
                <span>${s.sector_name}</span>
                <span class="font-bold">${s.heat_index.toFixed(1)}</span>
            </div>
        `).join('')
        : '<p class="text-red-300/50 text-sm">Không có ngành nào</p>';
}

// Show sector detail
async function showSectorDetail(sectorId) {
    const config = SECTORS[sectorId];
    if (!config) return;
    
    // Load sector data if not cached
    if (!sectorDataCache[sectorId]) {
        try {
            const response = await fetch(`data/${config.file}`);
            sectorDataCache[sectorId] = await response.json();
        } catch (error) {
            console.error('Error loading sector data:', error);
            return;
        }
    }
    
    const sectorData = sectorDataCache[sectorId];
    const sectorHeat = marketData.sectors.find(s => s.sector_id === sectorId);
    
    // Update title
    document.getElementById('detail-title').textContent = `📊 ${sectorData.sector_name} - Chi tiết`;
    
    // Render stats
    const heat = sectorData.heat || {};
    document.getElementById('sector-stats').innerHTML = `
        <div class="bg-gray-700 rounded-lg p-3 text-center">
            <div class="text-2xl font-bold ${getHeatColor(heat.heat_index || 0)}">${(heat.heat_index || 0).toFixed(1)}</div>
            <div class="text-gray-400 text-xs">Heat Index</div>
        </div>
        <div class="bg-gray-700 rounded-lg p-3 text-center">
            <div class="text-2xl font-bold text-blue-400">${(heat.avg_pb || 0).toFixed(2)}</div>
            <div class="text-gray-400 text-xs">P/B Trung bình</div>
        </div>
        <div class="bg-gray-700 rounded-lg p-3 text-center">
            <div class="text-2xl font-bold text-green-400">${heat.very_cheap_count || 0}</div>
            <div class="text-gray-400 text-xs">Cực rẻ</div>
        </div>
        <div class="bg-gray-700 rounded-lg p-3 text-center">
            <div class="text-2xl font-bold text-red-400">${heat.very_expensive_count || 0}</div>
            <div class="text-gray-400 text-xs">Cực đắt</div>
        </div>
        <div class="bg-gray-700 rounded-lg p-3 text-center">
            <div class="text-2xl font-bold text-purple-400">${sectorData.summary?.stocks_with_data || 0}</div>
            <div class="text-gray-400 text-xs">Số mã</div>
        </div>
    `;
    
    // Render stock table
    const stocks = sectorData.stocks || {};
    const stocksArray = Object.values(stocks).sort((a, b) => {
        // Support both valuation and evaluation fields
        const valA = a.valuation || a.evaluation || {};
        const valB = b.valuation || b.evaluation || {};
        const pctA = valA.current_percentile || valA.percentile || 50;
        const pctB = valB.current_percentile || valB.percentile || 50;
        return pctA - pctB;
    });
    
    document.getElementById('stock-table-body').innerHTML = stocksArray.map(stock => {
        // Support both valuation and evaluation fields
        const val = stock.valuation || stock.evaluation || {};
        const zone = val.zone || val.status || 'FAIR';
        const percentile = val.current_percentile || val.percentile || 50;
        const stats = stock.pb_statistics || {};
        
        return `
            <tr class="stock-row cursor-pointer hover:bg-gray-700 transition-colors" onclick="window.location.href='stock.html?symbol=${stock.symbol}'">
                <td class="px-4 py-3 font-semibold text-white">${stock.symbol}</td>
                <td class="px-4 py-3 text-right font-bold ${getHeatColor(percentile)}">${(stock.current_pb || 0).toFixed(2)}</td>
                <td class="px-4 py-3 text-right text-green-400">${(stats.min || 0).toFixed(2)}</td>
                <td class="px-4 py-3 text-right text-red-400">${(stats.max || 0).toFixed(2)}</td>
                <td class="px-4 py-3 text-center">
                    <span class="px-2 py-1 rounded text-xs font-semibold ${getZoneClass(zone)}">${getZoneText(zone)}</span>
                </td>
                <td class="px-4 py-3 text-right ${getHeatColor(percentile)}">${percentile.toFixed(1)}%</td>
            </tr>
        `;
    }).join('');
    
    // Show detail panel
    document.getElementById('sector-detail').classList.remove('hidden');
    document.getElementById('sector-detail').scrollIntoView({ behavior: 'smooth' });
}

// Close sector detail
function closeSectorDetail() {
    document.getElementById('sector-detail').classList.add('hidden');
}

// Helper functions
function getHeatColor(heat) {
    if (heat < 20) return 'text-blue-400';
    if (heat < 35) return 'text-cyan-400';
    if (heat < 50) return 'text-green-400';
    if (heat < 65) return 'text-yellow-400';
    if (heat < 80) return 'text-orange-400';
    return 'text-red-400';
}

function getHeatColorHex(heat) {
    if (heat < 20) return '#3B82F6';
    if (heat < 35) return '#22D3EE';
    if (heat < 50) return '#22C55E';
    if (heat < 65) return '#EAB308';
    if (heat < 80) return '#F97316';
    return '#EF4444';
}

function getSignalColor(signal) {
    switch (signal) {
        case 'BUY_HEAVY': return 'text-blue-400';
        case 'BUY': return 'text-green-400';
        case 'ACCUMULATE': return 'text-cyan-400';
        case 'NORMAL': return 'text-yellow-400';
        case 'HOLD': return 'text-orange-400';
        case 'SELL': return 'text-red-400';
        default: return 'text-gray-400';
    }
}

function getSignalText(heat) {
    if (heat < 20) return '🛒 MUA MẠNH';
    if (heat < 35) return '🛒 MUA';
    if (heat < 50) return '📈 TÍCH LŨY';
    if (heat < 65) return '😐 GIỮ';
    if (heat < 80) return '⚠️ CẨN THẬN';
    return '🔥 CHỐT LỜI';
}

function getZoneClass(zone) {
    switch (zone) {
        case 'VERY_CHEAP': return 'bg-blue-600 text-white';
        case 'CHEAP': return 'bg-green-600 text-white';
        case 'FAIR': return 'bg-yellow-600 text-white';
        case 'EXPENSIVE': return 'bg-orange-600 text-white';
        case 'VERY_EXPENSIVE': return 'bg-red-600 text-white';
        default: return 'bg-gray-600 text-white';
    }
}

function getZoneText(zone) {
    switch (zone) {
        case 'VERY_CHEAP': return 'Cực rẻ';
        case 'CHEAP': return 'Rẻ';
        case 'FAIR': return 'Hợp lý';
        case 'EXPENSIVE': return 'Đắt';
        case 'VERY_EXPENSIVE': return 'Cực đắt';
        default: return 'N/A';
    }
}
