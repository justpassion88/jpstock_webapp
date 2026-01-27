/**
 * JP Stock Webapp - Sector Detail
 * Hiển thị chi tiết các ngành (không phải ngân hàng)
 */

let sectorData = null;
let currentSector = null;
let allStocks = [];

// Sector configuration
const SECTORS = {
    realestate: { name: '🏠 Bất động sản', file: 'realestate.json' },
    securities: { name: '📈 Chứng khoán', file: 'securities.json' },
    energy: { name: '⚡ Điện & Năng lượng', file: 'energy.json' },
    oilgas: { name: '🛢️ Dầu khí', file: 'oilgas.json' },
    steel: { name: '🏗️ Thép & Vật liệu', file: 'steel.json' },
    construction: { name: '🏗️ Xây dựng', file: 'construction.json' },
    insurance: { name: '🛡️ Bảo hiểm', file: 'insurance.json' },
    retail: { name: '🛒 Bán lẻ & Tiêu dùng', file: 'retail.json' },
    technology: { name: '💻 Công nghệ', file: 'technology.json' },
    chemicals: { name: '🧪 Hóa chất & Công nghiệp', file: 'chemicals.json' }
};

// Get sector from URL
function getSector() {
    const params = new URLSearchParams(window.location.search);
    return params.get('sector') || 'realestate';
}

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    currentSector = getSector();
    await loadSectorData();
});

// Load sector data
async function loadSectorData() {
    const config = SECTORS[currentSector];
    if (!config) {
        document.getElementById('stock-list').innerHTML = '<div class="col-span-full text-center text-red-500">❌ Ngành không tồn tại</div>';
        return;
    }

    try {
        const response = await fetch(`data/${config.file}`);
        sectorData = await response.json();
        
        // Update page title
        document.title = `${config.name} | JP Stock Analysis V2`;
        
        // Display sector header
        displaySectorHeader(config);
        
        // Get stocks array
        const stocks = sectorData.stocks || {};
        allStocks = Object.values(stocks);
        
        // Display summary
        displaySummary();
        
        // Display stock list
        displayStockList(allStocks);
    } catch (error) {
        console.error('Error loading sector data:', error);
        document.getElementById('stock-list').innerHTML = `<div class="col-span-full text-center text-red-500">❌ Lỗi tải dữ liệu: ${error.message}</div>`;
    }
}

// Display sector header
function displaySectorHeader(config) {
    document.getElementById('sector-header').innerHTML = `
        <div class="mb-6">
            <h2 class="text-3xl font-bold text-white mb-2">${config.name}</h2>
            <p class="text-gray-400">${sectorData.description || 'Chi tiết ngành'}</p>
        </div>
    `;
}

// Display summary
function displaySummary() {
    const heat = sectorData.heat || {};
    const summary = sectorData.summary || {};
    
    const cheapCount = allStocks.filter(s => {
        const eval = s.evaluation || {};
        return eval.status === '🟢 RẺ' || eval.status === '🟢 CỰC RẺ';
    }).length;
    
    const expensiveCount = allStocks.filter(s => {
        const eval = s.evaluation || {};
        return eval.status === '🔴 ĐẮT' || eval.status === '🔴 CỰC ĐẮT';
    }).length;
    
    document.getElementById('summary').innerHTML = `
        <div class="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
            <div class="bg-gray-800 rounded-lg p-4 text-center">
                <div class="text-2xl font-bold text-blue-400">${(heat.heat_index || 0).toFixed(1)}</div>
                <div class="text-gray-400 text-sm">Heat Index</div>
            </div>
            <div class="bg-gray-800 rounded-lg p-4 text-center">
                <div class="text-2xl font-bold text-blue-400">${(heat.avg_pb || 0).toFixed(2)}</div>
                <div class="text-gray-400 text-sm">P/B Trung bình</div>
            </div>
            <div class="bg-gray-800 rounded-lg p-4 text-center">
                <div class="text-2xl font-bold text-green-400">${cheapCount}</div>
                <div class="text-gray-400 text-sm">Cực rẻ</div>
            </div>
            <div class="bg-gray-800 rounded-lg p-4 text-center">
                <div class="text-2xl font-bold text-red-400">${expensiveCount}</div>
                <div class="text-gray-400 text-sm">Cực đắt</div>
            </div>
            <div class="bg-gray-800 rounded-lg p-4 text-center">
                <div class="text-2xl font-bold text-purple-400">${summary.stocks_with_data || allStocks.length}</div>
                <div class="text-gray-400 text-sm">Số mã</div>
            </div>
        </div>
    `;
}

// Display stock list
function displayStockList(stocks) {
    document.getElementById('stock-list').innerHTML = stocks.map(stock => {
        const eval = stock.evaluation || {};
        const stats = stock.pb_statistics || {};
        const statusColor = getStatusColor(eval.status);
        
        return `
            <a href="stock.html?symbol=${stock.symbol}" class="bg-gray-800 rounded-lg p-4 hover:bg-gray-750 transition-colors border-l-4 ${statusColor}">
                <div class="flex justify-between items-start mb-3">
                    <h3 class="text-lg font-bold text-white">${stock.symbol}</h3>
                    <span class="text-xs px-2 py-1 rounded ${getStatusBg(eval.status)}">${eval.status || 'N/A'}</span>
                </div>
                <div class="grid grid-cols-2 gap-2 text-sm">
                    <div>
                        <span class="text-gray-400">P/B Hiện tại:</span>
                        <div class="text-blue-400 font-semibold">${(stock.current_pb || 0).toFixed(2)}</div>
                    </div>
                    <div>
                        <span class="text-gray-400">P/B Mean:</span>
                        <div class="text-green-400 font-semibold">${(stats.mean || 0).toFixed(2)}</div>
                    </div>
                    <div>
                        <span class="text-gray-400">Min:</span>
                        <div class="text-gray-300">${(stats.min || 0).toFixed(2)}</div>
                    </div>
                    <div>
                        <span class="text-gray-400">Max:</span>
                        <div class="text-gray-300">${(stats.max || 0).toFixed(2)}</div>
                    </div>
                </div>
                <div class="mt-3 pt-3 border-t border-gray-700">
                    <div class="text-xs text-gray-400">Percentile: <span class="text-yellow-400">${(eval.current_percentile || 0).toFixed(1)}%</span></div>
                </div>
            </a>
        `;
    }).join('');
}

// Filter by zone
function filterByZone(zone, element) {
    // Update button style
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('bg-blue-600', 'text-white', 'ring-2', 'ring-blue-500');
        btn.classList.add('bg-gray-700');
    });
    element.classList.remove('bg-gray-700');
    element.classList.add('bg-blue-600', 'text-white', 'ring-2', 'ring-blue-500');
    
    // Filter stocks
    let filtered = allStocks;
    if (zone !== 'all') {
        filtered = allStocks.filter(stock => {
            const eval = stock.evaluation || {};
            const status = eval.status || '';
            
            if (zone === 'extremely_cheap') return status.includes('CỰC RẺ');
            if (zone === 'cheap') return status.includes('RẺ');
            if (zone === 'fair') return status.includes('HỢPÝ');
            if (zone === 'expensive') return status.includes('ĐẮT');
            if (zone === 'extremely_expensive') return status.includes('CỰC ĐẮT');
            return true;
        });
    }
    
    displayStockList(filtered);
}

// Sort stocks
function sortStocks(type) {
    const sorted = [...allStocks].sort((a, b) => {
        if (type === 'percentile') {
            const pctA = (a.evaluation?.current_percentile || 0);
            const pctB = (b.evaluation?.current_percentile || 0);
            return pctA - pctB;
        } else if (type === 'current_pb') {
            return (a.current_pb || 0) - (b.current_pb || 0);
        }
        return 0;
    });
    displayStockList(sorted);
}

// Helper functions
function getStatusColor(status) {
    if (!status) return 'border-gray-600';
    if (status.includes('CỰC RẺ') || status.includes('RẺ')) return 'border-green-500';
    if (status.includes('HỢPÝ')) return 'border-yellow-500';
    if (status.includes('ĐẮT')) return 'border-red-500';
    return 'border-gray-600';
}

function getStatusBg(status) {
    if (!status) return 'bg-gray-700 text-gray-300';
    if (status.includes('CỰC RẺ') || status.includes('RẺ')) return 'bg-green-900 text-green-300';
    if (status.includes('HỢPÝ')) return 'bg-yellow-900 text-yellow-300';
    if (status.includes('ĐẮT')) return 'bg-red-900 text-red-300';
    return 'bg-gray-700 text-gray-300';
}
