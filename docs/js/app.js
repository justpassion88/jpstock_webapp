/**
 * JP Stock Webapp - Dashboard V2
 * Phân tích P/B với Historical Backtest
 */

let banksData = null;

// Fetch and display banks data
async function loadBanks() {
    try {
        const response = await fetch('data/banks_v2.json');
        banksData = await response.json();
        displayBankList(banksData.banks);
        displaySummary(banksData);
    } catch (error) {
        console.error('Error loading banks:', error);
        document.getElementById('bank-list').innerHTML = `
            <div class="col-span-full text-center text-red-500 py-8">
                <p class="text-xl">⚠️ Không thể tải dữ liệu</p>
                <p class="text-sm mt-2">Error: ${error.message}</p>
            </div>
        `;
    }
}

// Display summary statistics
function displaySummary(data) {
    const banks = Object.values(data.banks);
    
    // Count by zone
    const zoneCounts = {
        'extremely_cheap': 0,
        'cheap': 0,
        'fair': 0,
        'expensive': 0,
        'extremely_expensive': 0
    };
    
    let totalReturn = 0, countReturn = 0;
    
    banks.forEach(bank => {
        const zone = bank.valuation?.zone || 'unknown';
        if (zoneCounts.hasOwnProperty(zone)) {
            zoneCounts[zone]++;
        }
        if (bank.expected_return?.expected_1y != null) {
            totalReturn += bank.expected_return.expected_1y;
            countReturn++;
        }
    });
    
    const avgReturn = countReturn > 0 ? (totalReturn / countReturn).toFixed(1) : 'N/A';
    
    document.getElementById('summary').innerHTML = `
        <div class="bg-gray-800 rounded-lg p-6 mb-6">
            <h2 class="text-xl font-bold text-white mb-4">📊 Tổng quan thị trường ngân hàng</h2>
            <div class="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4">
                <div class="text-center p-3 bg-green-900/30 rounded-lg">
                    <div class="text-3xl font-bold text-green-400">${zoneCounts.extremely_cheap}</div>
                    <div class="text-sm text-gray-400">Cực rẻ</div>
                </div>
                <div class="text-center p-3 bg-green-800/30 rounded-lg">
                    <div class="text-3xl font-bold text-green-300">${zoneCounts.cheap}</div>
                    <div class="text-sm text-gray-400">Rẻ</div>
                </div>
                <div class="text-center p-3 bg-yellow-800/30 rounded-lg">
                    <div class="text-3xl font-bold text-yellow-400">${zoneCounts.fair}</div>
                    <div class="text-sm text-gray-400">Hợp lý</div>
                </div>
                <div class="text-center p-3 bg-orange-800/30 rounded-lg">
                    <div class="text-3xl font-bold text-orange-400">${zoneCounts.expensive}</div>
                    <div class="text-sm text-gray-400">Đắt</div>
                </div>
                <div class="text-center p-3 bg-red-900/30 rounded-lg">
                    <div class="text-3xl font-bold text-red-400">${zoneCounts.extremely_expensive}</div>
                    <div class="text-sm text-gray-400">Cực đắt</div>
                </div>
            </div>
            <div class="text-sm text-gray-400 text-center border-t border-gray-700 pt-3">
                <span class="mr-4">📅 Cập nhật: ${new Date(data.last_updated).toLocaleString('vi-VN')}</span>
                <span>📈 Dựa trên backtest lịch sử P/B theo quý</span>
            </div>
        </div>
    `;
}

// Display bank list
function displayBankList(banks) {
    const container = document.getElementById('bank-list');
    
    // Sort by valuation score (best buys first)
    const sortedBanks = Object.values(banks).sort((a, b) => {
        const scoreA = a.valuation?.score || 0;
        const scoreB = b.valuation?.score || 0;
        return scoreB - scoreA;
    });
    
    container.innerHTML = sortedBanks.map(bank => createBankCard(bank)).join('');
}

// Create individual bank card
function createBankCard(bank) {
    const valuation = bank.valuation || {};
    const expectedReturn = bank.expected_return || {};
    const risk = bank.risk || {};
    const stats = bank.pb_statistics || {};
    
    const zoneColor = valuation.color || '#6b7280';
    const zoneVi = valuation.zone_vi || 'N/A';
    const percentile = valuation.percentile != null ? valuation.percentile.toFixed(0) : 'N/A';
    
    const currentPb = bank.current_pb?.toFixed(2) || 'N/A';
    const currentPrice = bank.current_price ? (bank.current_price * 1000).toLocaleString('vi-VN') : 'N/A';
    const avgPb = stats.mean?.toFixed(2) || 'N/A';
    
    const return1y = expectedReturn.expected_1y != null ? 
        `${expectedReturn.expected_1y > 0 ? '+' : ''}${expectedReturn.expected_1y.toFixed(1)}%` : 'N/A';
    const winRate = expectedReturn.win_rate_1y != null ? 
        `${expectedReturn.win_rate_1y.toFixed(0)}%` : 'N/A';
    
    const returnClass = (expectedReturn.expected_1y || 0) >= 20 ? 'text-green-400' : 
                        (expectedReturn.expected_1y || 0) >= 0 ? 'text-yellow-400' : 'text-red-400';
    
    const winRateClass = (expectedReturn.win_rate_1y || 0) >= 70 ? 'text-green-400' :
                         (expectedReturn.win_rate_1y || 0) >= 50 ? 'text-yellow-400' : 'text-red-400';
    
    return `
        <a href="stock.html?symbol=${bank.symbol}" class="bank-card block bg-gray-800 rounded-lg p-4 hover:bg-gray-700 transition-all hover:scale-[1.02]">
            <div class="flex justify-between items-start mb-3">
                <div>
                    <h3 class="text-xl font-bold text-white">${bank.symbol}</h3>
                    <p class="text-sm text-gray-400">${bank.name}</p>
                </div>
                <span class="px-3 py-1 rounded-full text-sm font-bold" 
                      style="background-color: ${zoneColor}25; color: ${zoneColor}; border: 2px solid ${zoneColor}">
                    ${zoneVi}
                </span>
            </div>
            
            <div class="grid grid-cols-2 gap-3 text-sm mb-3">
                <div class="bg-gray-900/50 rounded p-2">
                    <div class="text-gray-500 text-xs">P/B hiện tại</div>
                    <div class="text-white font-bold text-lg">${currentPb}</div>
                    <div class="text-gray-500 text-xs">TB: ${avgPb}</div>
                </div>
                <div class="bg-gray-900/50 rounded p-2">
                    <div class="text-gray-500 text-xs">Percentile</div>
                    <div class="text-white font-bold text-lg">P${percentile}</div>
                    <div class="text-gray-500 text-xs">vs lịch sử</div>
                </div>
                <div class="bg-gray-900/50 rounded p-2">
                    <div class="text-gray-500 text-xs">Kỳ vọng 1Y</div>
                    <div class="${returnClass} font-bold text-lg">${return1y}</div>
                    <div class="text-gray-500 text-xs">từ backtest</div>
                </div>
                <div class="bg-gray-900/50 rounded p-2">
                    <div class="text-gray-500 text-xs">Win Rate 1Y</div>
                    <div class="${winRateClass} font-bold text-lg">${winRate}</div>
                    <div class="text-gray-500 text-xs">tỷ lệ có lãi</div>
                </div>
            </div>
            
            <div class="flex justify-between items-center text-xs pt-2 border-t border-gray-700">
                <span class="text-gray-500">💰 ${currentPrice}đ</span>
                <span class="text-gray-500">⚠️ Rủi ro: ${risk.level_vi || 'N/A'}</span>
            </div>
        </a>
    `;
}

// Filter by zone
function filterByZone(zone, btn) {
    if (!banksData) return;
    
    if (zone === 'all') {
        displayBankList(banksData.banks);
    } else {
        const filtered = {};
        Object.entries(banksData.banks).forEach(([symbol, bank]) => {
            if (bank.valuation?.zone === zone) {
                filtered[symbol] = bank;
            }
        });
        displayBankList(filtered);
    }
    
    // Update active button
    document.querySelectorAll('.filter-btn').forEach(b => {
        b.classList.remove('ring-2', 'ring-blue-500');
    });
    btn.classList.add('ring-2', 'ring-blue-500');
}

// Sort banks
function sortBanks(field) {
    if (!banksData) return;
    
    const banks = Object.values(banksData.banks);
    
    banks.sort((a, b) => {
        let valA, valB;
        
        switch(field) {
            case 'return':
                valA = a.expected_return?.expected_1y ?? -999;
                valB = b.expected_return?.expected_1y ?? -999;
                return valB - valA;
            case 'winrate':
                valA = a.expected_return?.win_rate_1y ?? -999;
                valB = b.expected_return?.win_rate_1y ?? -999;
                return valB - valA;
            case 'cheap':
                valA = a.valuation?.percentile ?? 999;
                valB = b.valuation?.percentile ?? 999;
                return valA - valB;
            case 'risk':
                valA = a.risk?.score ?? 999;
                valB = b.risk?.score ?? 999;
                return valA - valB;
            default:
                return (b.valuation?.score ?? 0) - (a.valuation?.score ?? 0);
        }
    });
    
    const banksObj = {};
    banks.forEach(bank => banksObj[bank.symbol] = bank);
    displayBankList(banksObj);
}

// Initialize
document.addEventListener('DOMContentLoaded', loadBanks);
