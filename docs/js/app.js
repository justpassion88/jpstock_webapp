/**
 * JP Stock Webapp - Main Application JavaScript
 * Phân tích P/B định lượng cho ngành ngân hàng
 */

// Global state
let bankData = null;
let sortColumn = 'expected_return';
let sortDirection = 'desc';

// Format numbers
function formatNumber(num, decimals = 2) {
    if (num === null || num === undefined) return 'N/A';
    return Number(num).toFixed(decimals);
}

function formatPercent(num) {
    if (num === null || num === undefined) return 'N/A';
    const sign = num >= 0 ? '+' : '';
    return `${sign}${formatNumber(num, 1)}%`;
}

function formatPrice(num) {
    if (num === null || num === undefined) return 'N/A';
    return new Intl.NumberFormat('vi-VN').format(Math.round(num));
}

// Get color class for valuation
function getValuationClass(zone) {
    const classes = {
        'EXTREMELY_CHEAP': 'valuation-extremely-cheap',
        'CHEAP': 'valuation-cheap',
        'FAIR': 'valuation-fair',
        'EXPENSIVE': 'valuation-expensive',
        'EXTREMELY_EXPENSIVE': 'valuation-extremely-expensive',
        'UNKNOWN': 'valuation-unknown'
    };
    return classes[zone] || 'valuation-unknown';
}

// Get signal badge
function getSignalBadge(signal, label) {
    const badges = {
        'STRONG_BUY': `<span class="badge badge-strong-buy">${label}</span>`,
        'BUY': `<span class="badge badge-buy">${label}</span>`,
        'HOLD': `<span class="badge badge-hold">${label}</span>`,
        'SELL': `<span class="badge badge-sell">${label}</span>`,
        'STRONG_SELL': `<span class="badge badge-strong-sell">${label}</span>`,
        'N/A': `<span class="badge badge-unknown">${label}</span>`
    };
    return badges[signal] || `<span class="badge badge-unknown">${label}</span>`;
}

// Get risk level badge
function getRiskBadge(riskLevel) {
    const badges = {
        'VERY_LOW': '<span class="badge badge-risk-very-low">Rất thấp</span>',
        'LOW': '<span class="badge badge-risk-low">Thấp</span>',
        'MEDIUM': '<span class="badge badge-risk-medium">Trung bình</span>',
        'HIGH': '<span class="badge badge-risk-high">Cao</span>',
        'VERY_HIGH': '<span class="badge badge-risk-very-high">Rất cao</span>',
        'UNKNOWN': '<span class="badge badge-unknown">N/A</span>'
    };
    return badges[riskLevel] || badges['UNKNOWN'];
}

// Load data from JSON file
async function loadData() {
    try {
        const response = await fetch('data/banks.json');
        if (!response.ok) throw new Error('Failed to load data');
        bankData = await response.json();
        
        // Update last updated time
        document.getElementById('lastUpdated').textContent = 
            new Date(bankData.generated_at || bankData.last_updated).toLocaleString('vi-VN');
        
        // Update summary cards
        updateSummaryCards();
        
        // Render table
        renderTable();
        
    } catch (error) {
        console.error('Error loading data:', error);
        document.getElementById('bankTable').innerHTML = `
            <tr>
                <td colspan="8" class="text-center py-8 text-red-500">
                    Không thể tải dữ liệu. Vui lòng thử lại sau.
                </td>
            </tr>
        `;
    }
}

// Update summary cards
function updateSummaryCards() {
    if (!bankData || !bankData.summary) return;
    
    const summary = bankData.summary;
    
    document.getElementById('countStrongBuy').textContent = 
        summary.extremely_cheap.length + summary.cheap.length;
    document.getElementById('countHold').textContent = summary.fair.length;
    document.getElementById('countSell').textContent = 
        summary.expensive.length + summary.extremely_expensive.length;
    document.getElementById('totalBanks').textContent = bankData.total_banks;
}

// Sort data
function sortData(data, column, direction) {
    return [...data].sort((a, b) => {
        let aVal, bVal;
        
        switch (column) {
            case 'symbol':
                aVal = a.symbol;
                bVal = b.symbol;
                break;
            case 'current_pb':
                aVal = a.current_pb || 0;
                bVal = b.current_pb || 0;
                break;
            case 'percentile':
                aVal = a.valuation?.percentile || 50;
                bVal = b.valuation?.percentile || 50;
                break;
            case 'expected_return':
                aVal = a.expected_return?.expected_return || -999;
                bVal = b.expected_return?.expected_return || -999;
                break;
            case 'risk_score':
                aVal = a.risk?.risk_score || 50;
                bVal = b.risk?.risk_score || 50;
                break;
            default:
                aVal = a.symbol;
                bVal = b.symbol;
        }
        
        if (direction === 'asc') {
            return aVal > bVal ? 1 : -1;
        } else {
            return aVal < bVal ? 1 : -1;
        }
    });
}

// Handle sort click
function handleSort(column) {
    if (sortColumn === column) {
        sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        sortColumn = column;
        sortDirection = 'desc';
    }
    renderTable();
    updateSortIndicators();
}

// Update sort indicators
function updateSortIndicators() {
    document.querySelectorAll('.sort-indicator').forEach(el => {
        el.textContent = '';
    });
    
    const indicator = document.querySelector(`[data-sort="${sortColumn}"] .sort-indicator`);
    if (indicator) {
        indicator.textContent = sortDirection === 'asc' ? ' ↑' : ' ↓';
    }
}

// Render table
function renderTable() {
    if (!bankData || !bankData.banks) return;
    
    const sortedBanks = sortData(bankData.banks, sortColumn, sortDirection);
    const tbody = document.getElementById('bankTable');
    
    tbody.innerHTML = sortedBanks.map(bank => {
        const valuation = bank.valuation || {};
        const expectedReturn = bank.expected_return || {};
        const risk = bank.risk || {};
        const pbStats = bank.pb_statistics || {};
        
        return `
            <tr class="hover:bg-gray-50 cursor-pointer" onclick="viewDetail('${bank.symbol}')">
                <td class="px-4 py-3 font-semibold">
                    <div class="flex items-center">
                        <span class="text-blue-600">${bank.symbol}</span>
                    </div>
                    <div class="text-xs text-gray-500">${bank.name}</div>
                </td>
                <td class="px-4 py-3 text-right">
                    ${formatPrice(bank.current_price)}
                </td>
                <td class="px-4 py-3 text-right font-medium">
                    ${formatNumber(bank.current_pb)}
                </td>
                <td class="px-4 py-3 text-right text-gray-500 text-sm">
                    ${formatNumber(pbStats.mean)} ± ${formatNumber(pbStats.std)}
                </td>
                <td class="px-4 py-3 text-center">
                    ${getSignalBadge(valuation.signal, valuation.label)}
                    <div class="text-xs text-gray-500 mt-1">P${formatNumber(valuation.percentile, 0)}%</div>
                </td>
                <td class="px-4 py-3 text-right ${expectedReturn.expected_return >= 0 ? 'text-green-600' : 'text-red-600'}">
                    ${formatPercent(expectedReturn.expected_return)}
                    <div class="text-xs text-gray-500">${expectedReturn.confidence || ''}</div>
                </td>
                <td class="px-4 py-3 text-center">
                    ${getRiskBadge(risk.risk_level)}
                </td>
                <td class="px-4 py-3 text-center">
                    <button onclick="event.stopPropagation(); viewDetail('${bank.symbol}')" 
                            class="text-blue-600 hover:text-blue-800 text-sm font-medium">
                        Chi tiết →
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

// View detail page
function viewDetail(symbol) {
    window.location.href = `stock.html?symbol=${symbol}`;
}

// Filter by zone
function filterByZone(zone) {
    if (!bankData || !bankData.banks) return;
    
    const filteredBanks = zone === 'all' 
        ? bankData.banks 
        : bankData.banks.filter(b => {
            if (zone === 'buy') {
                return b.valuation?.zone === 'EXTREMELY_CHEAP' || b.valuation?.zone === 'CHEAP';
            } else if (zone === 'sell') {
                return b.valuation?.zone === 'EXPENSIVE' || b.valuation?.zone === 'EXTREMELY_EXPENSIVE';
            } else if (zone === 'hold') {
                return b.valuation?.zone === 'FAIR';
            }
            return true;
        });
    
    // Temporarily replace banks array and render
    const originalBanks = bankData.banks;
    bankData.banks = filteredBanks;
    renderTable();
    bankData.banks = originalBanks;
    
    // Update active filter button
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-filter="${zone}"]`)?.classList.add('active');
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadData();
    
    // Add sort click handlers
    document.querySelectorAll('[data-sort]').forEach(el => {
        el.addEventListener('click', () => handleSort(el.dataset.sort));
    });
});
