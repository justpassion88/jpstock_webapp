/**
 * Market Heat Map - Multi-Sector Analysis
 * JP Stock Analysis
 */

// Sector configuration - Updated to use daily_summary files
const SECTORS = {
    banks: { name: '🏦 Ngân hàng', file: 'banks_daily_summary.json', color: '#3B82F6' },
    realestate: { name: '🏠 Bất động sản', file: 'realestate_daily_summary.json', color: '#10B981' },
    securities: { name: '📈 Chứng khoán', file: 'securities_daily_summary.json', color: '#8B5CF6' },
    energy: { name: '⚡ Điện & Năng lượng', file: 'energy_daily_summary.json', color: '#F59E0B' },
    oilgas: { name: '🛢️ Dầu khí', file: 'oilgas_daily_summary.json', color: '#78716C' },
    steel: { name: '🏗️ Thép', file: 'steel_daily_summary.json', color: '#6B7280' },
    construction: { name: '🏗️ Xây dựng', file: 'construction_daily_summary.json', color: '#F97316' },
    insurance: { name: '🛡️ Bảo hiểm', file: 'insurance_daily_summary.json', color: '#EC4899' },
    retail: { name: '🛒 Bán lẻ', file: 'retail_daily_summary.json', color: '#14B8A6' },
    technology: { name: '💻 Công nghệ', file: 'technology_daily_summary.json', color: '#6366F1' },
    chemicals: { name: '🧪 Hóa chất', file: 'chemicals_daily_summary.json', color: '#A855F7' }
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
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        marketData = await response.json();
        
        console.log('Market data loaded:', marketData);
        
        renderMarketOverview();
        renderSectorCards();
        renderRecommendations();
    } catch (error) {
        console.error('Error loading market data:', error);
        document.getElementById('sector-cards').innerHTML = `
            <div class="col-span-full text-center py-8 text-red-400">
                ❌ Lỗi tải dữ liệu. Vui lòng thử lại.
                <div class="text-sm mt-2">Chi tiết: ${error.message}</div>
            </div>
        `;
    }
}

// Render market overview
function renderMarketOverview() {
    try {
        if (!marketData) {
            console.error('Market data is null');
            return;
        }
        
        const { market_heat, updated_at, history, analysis } = marketData;
        
        if (!market_heat) {
            console.error('market_heat is missing from data');
            return;
        }
        
        // Update stats
        const marketHeatEl = document.getElementById('market-heat');
        if (marketHeatEl) {
            marketHeatEl.textContent = market_heat.heat_index.toFixed(1);
            marketHeatEl.className = `text-3xl font-bold ${getHeatColor(market_heat.heat_index)}`;
        }
        
        const totalSectorsEl = document.getElementById('total-sectors');
        if (totalSectorsEl) totalSectorsEl.textContent = market_heat.total_sectors;
        
        const totalStocksEl = document.getElementById('total-stocks');
        if (totalStocksEl) totalStocksEl.textContent = market_heat.total_stocks;
        
        const marketSignalEl = document.getElementById('market-signal');
        if (marketSignalEl) {
            marketSignalEl.textContent = getSignalText(market_heat.heat_index);
            marketSignalEl.className = `text-xl font-bold ${getHeatColor(market_heat.heat_index)}`;
        }
        
        // Update timestamp
        const lastUpdatedEl = document.getElementById('last-updated');
        if (lastUpdatedEl) {
            const date = new Date(updated_at);
            lastUpdatedEl.textContent = `Cập nhật: ${date.toLocaleString('vi-VN')}`;
        }
        
        // Move heat marker
        const markerEl = document.getElementById('market-heat-marker');
        if (markerEl) {
            markerEl.style.left = `${market_heat.heat_index}%`;
        }
        
        // Render heat history chart and analysis (only if elements exist)
        if (history && history.length > 0) {
            if (document.getElementById('market-heat-history-chart')) {
                renderHeatHistoryChart(history, market_heat.heat_index);
            }
            if (document.getElementById('max-heat')) {
                renderHeatAnalysis(analysis, market_heat.heat_index);
            }
            if (document.getElementById('heat-history-table')) {
                renderHeatHistoryTable(history);
            }
        }
    } catch (error) {
        console.error('Error rendering market overview:', error);
    }
}

// Render heat history chart
// Render heat history chart
function renderHeatHistoryChart(history, currentHeat) {
    try {
        const periods = history.map(h => h.period);
        const heatValues = history.map(h => h.heat_index);
        const pbValues = history.map(h => h.avg_pb);
        
        // Add current data point
        const currentPeriod = getCurrentQuarter();
        periods.push(currentPeriod);
        heatValues.push(currentHeat);
    
    // Define heat zones for background
    const shapes = [
        // ICE COLD zone (0-20) - Blue
        {
            type: 'rect', xref: 'paper', yref: 'y',
            x0: 0, x1: 1, y0: 0, y1: 20,
            fillcolor: 'rgba(59, 130, 246, 0.1)', line: { width: 0 }
        },
        // COLD zone (20-35) - Cyan
        {
            type: 'rect', xref: 'paper', yref: 'y',
            x0: 0, x1: 1, y0: 20, y1: 35,
            fillcolor: 'rgba(34, 211, 238, 0.1)', line: { width: 0 }
        },
        // COOL zone (35-50) - Green
        {
            type: 'rect', xref: 'paper', yref: 'y',
            x0: 0, x1: 1, y0: 35, y1: 50,
            fillcolor: 'rgba(34, 197, 94, 0.1)', line: { width: 0 }
        },
        // NEUTRAL zone (50-65) - Yellow
        {
            type: 'rect', xref: 'paper', yref: 'y',
            x0: 0, x1: 1, y0: 50, y1: 65,
            fillcolor: 'rgba(234, 179, 8, 0.1)', line: { width: 0 }
        },
        // WARM zone (65-80) - Orange
        {
            type: 'rect', xref: 'paper', yref: 'y',
            x0: 0, x1: 1, y0: 65, y1: 80,
            fillcolor: 'rgba(249, 115, 22, 0.15)', line: { width: 0 }
        },
        // HOT zone (80-100) - Red
        {
            type: 'rect', xref: 'paper', yref: 'y',
            x0: 0, x1: 1, y0: 80, y1: 100,
            fillcolor: 'rgba(239, 68, 68, 0.15)', line: { width: 0 }
        }
    ];
    
    // Color each point based on heat value
    const markerColors = heatValues.map(h => getHeatColorHex(h));
    
    const trace = {
        x: periods,
        y: heatValues,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Heat Index',
        line: { 
            color: '#8B5CF6', 
            width: 3,
            shape: 'spline'
        },
        marker: { 
            size: 10, 
            color: markerColors,
            line: { color: '#1F2937', width: 2 }
        },
        fill: 'tozeroy',
        fillcolor: 'rgba(139, 92, 246, 0.1)',
        hovertemplate: '<b>%{x}</b><br>Heat: %{y:.1f}<extra></extra>'
    };
    
    // Average line
    const avgHeat = heatValues.reduce((a, b) => a + b, 0) / heatValues.length;
    const avgTrace = {
        x: periods,
        y: Array(periods.length).fill(avgHeat),
        type: 'scatter',
        mode: 'lines',
        name: `TB: ${avgHeat.toFixed(1)}`,
        line: { color: '#F59E0B', width: 2, dash: 'dash' },
        hoverinfo: 'skip'
    };
    
    // Warning lines
    const warningLine = {
        x: periods,
        y: Array(periods.length).fill(65),
        type: 'scatter',
        mode: 'lines',
        name: 'Cẩn thận (65)',
        line: { color: '#F97316', width: 1, dash: 'dot' },
        hoverinfo: 'skip'
    };
    
    const dangerLine = {
        x: periods,
        y: Array(periods.length).fill(80),
        type: 'scatter',
        mode: 'lines',
        name: 'Nguy hiểm (80)',
        line: { color: '#EF4444', width: 1, dash: 'dot' },
        hoverinfo: 'skip'
    };
    
    const layout = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(55, 65, 81, 0.5)',
        font: { color: '#9CA3AF', size: 11 },
        margin: { l: 50, r: 20, t: 30, b: 50 },
        xaxis: {
            gridcolor: 'rgba(75, 85, 99, 0.5)',
            tickangle: -45
        },
        yaxis: {
            title: 'Heat Index',
            gridcolor: 'rgba(75, 85, 99, 0.5)',
            range: [0, 100],
            dtick: 20
        },
        shapes: shapes,
        legend: {
            orientation: 'h',
            y: 1.15,
            x: 0.5,
            xanchor: 'center'
        },
        annotations: [
            {
                x: periods[periods.length - 1],
                y: currentHeat,
                xref: 'x',
                yref: 'y',
                text: `Hiện tại: ${currentHeat.toFixed(1)}`,
                showarrow: true,
                arrowhead: 2,
                arrowcolor: '#8B5CF6',
                ax: -50,
                ay: -30,
                font: { color: '#8B5CF6', size: 12, weight: 'bold' }
            }
        ],
        hovermode: 'x unified'
    };
    
    const config = {
        responsive: true,
        displayModeBar: false
    };
    
    Plotly.newPlot('market-heat-history-chart', [trace, avgTrace, warningLine, dangerLine], layout, config);
    } catch (error) {
        console.error('Error rendering heat history chart:', error);
    }
}

// Render heat analysis stats
function renderHeatAnalysis(analysis, currentHeat) {
    try {
        if (!analysis) return;
        
        document.getElementById('max-heat').textContent = analysis.max_heat.toFixed(1);
        document.getElementById('max-heat-period').innerHTML = `Nóng nhất<br><span class="text-red-300">${analysis.max_heat_period}</span>`;
        
        document.getElementById('min-heat').textContent = analysis.min_heat.toFixed(1);
        document.getElementById('min-heat-period').innerHTML = `Lạnh nhất<br><span class="text-blue-300">${analysis.min_heat_period}</span>`;
        
        document.getElementById('avg-heat').textContent = analysis.avg_heat.toFixed(1);
        
        const diff = currentHeat - analysis.avg_heat;
        const diffText = diff >= 0 ? `+${diff.toFixed(1)}` : diff.toFixed(1);
        const diffColor = diff >= 0 ? 'text-red-400' : 'text-green-400';
        document.getElementById('current-vs-avg').textContent = diffText;
        document.getElementById('current-vs-avg').className = `text-xl font-bold ${diffColor}`;
    } catch (error) {
        console.error('Error rendering heat analysis:', error);
    }
}

// Render heat history table
function renderHeatHistoryTable(history) {
    const tableBody = document.getElementById('heat-history-table');
    if (!tableBody) return;
    
    // Sort by period descending (newest first)
    const sortedHistory = [...history].sort((a, b) => b.period.localeCompare(a.period));
    
    tableBody.innerHTML = sortedHistory.map(h => {
        const signalText = getSignalTextFromHeat(h.heat_index);
        const statusEmoji = getStatusEmoji(h.status);
        
        return `
            <tr class="hover:bg-gray-600/50">
                <td class="px-4 py-2 font-semibold text-white">${h.period}</td>
                <td class="px-4 py-2 text-right font-bold ${getHeatColor(h.heat_index)}">${h.heat_index.toFixed(1)}</td>
                <td class="px-4 py-2 text-center">${statusEmoji} ${h.status}</td>
                <td class="px-4 py-2 text-right text-blue-400">${h.avg_pb.toFixed(2)}</td>
                <td class="px-4 py-2 text-center ${getSignalColorFromHeat(h.heat_index)}">${signalText}</td>
            </tr>
        `;
    }).join('');
}

// Get current quarter string
function getCurrentQuarter() {
    const now = new Date();
    const quarter = Math.floor(now.getMonth() / 3) + 1;
    return `${now.getFullYear()}-Q${quarter}`;
}

// Get signal text from heat value
function getSignalTextFromHeat(heat) {
    if (heat < 20) return 'MUA MẠNH';
    if (heat < 35) return 'MUA';
    if (heat < 50) return 'TÍCH LŨY';
    if (heat < 65) return 'GIỮ';
    if (heat < 80) return 'CẨN THẬN';
    return 'CHỐT LỜI';
}

// Get signal color from heat value
function getSignalColorFromHeat(heat) {
    if (heat < 20) return 'text-blue-400 font-bold';
    if (heat < 35) return 'text-green-400 font-bold';
    if (heat < 50) return 'text-cyan-400';
    if (heat < 65) return 'text-yellow-400';
    if (heat < 80) return 'text-orange-400';
    return 'text-red-400 font-bold';
}

// Get status emoji
function getStatusEmoji(status) {
    const emojiMap = {
        'ICE_COLD': '🥶',
        'COLD': '❄️',
        'COOL': '🌤️',
        'NEUTRAL': '😐',
        'WARM': '☀️',
        'HOT': '🔥',
        'OVERHEATED': '🌋'
    };
    return emojiMap[status] || '📊';
}

// Render sector cards
function renderSectorCards() {
    try {
        const container = document.getElementById('sector-cards');
        
        if (!marketData || !marketData.sectors) {
            console.error('Market data or sectors is missing');
            container.innerHTML = `
                <div class="col-span-full text-center py-8 text-red-400">
                    ❌ Không tìm thấy dữ liệu ngành.
                </div>
            `;
            return;
        }
        
        // Sort by heat index
        const sortedSectors = [...marketData.sectors].sort((a, b) => a.heat_index - b.heat_index);
        
        container.innerHTML = sortedSectors.map(sector => {
            const heatColor = getHeatColorHex(sector.heat_index);
            const config = SECTORS[sector.sector_id] || {};
            
            return `
                <div class="sector-card bg-gray-800 rounded-xl p-4 cursor-pointer border-l-4 hover:bg-gray-750"
                     style="border-left-color: ${heatColor}"
                     onclick="goToSectorDetail('${sector.sector_id}')">
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
    } catch (error) {
        console.error('Error rendering sector cards:', error);
        const container = document.getElementById('sector-cards');
        container.innerHTML = `
            <div class="col-span-full text-center py-8 text-red-400">
                ❌ Lỗi hiển thị dữ liệu ngành: ${error.message}
            </div>
        `;
    }
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

// Go to sector detail page
function goToSectorDetail(sectorId) {
    // All sectors now go to sector.html (including banks)
    window.location.href = `sector.html?sector=${sectorId}`;
}

// Show sector detail (legacy - kept for compatibility)
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
    document.getElementById('detail-title').textContent = `📊 ${sectorHeat?.sector_name || 'Chi tiết'} - Chi tiết`;
    
    // Render stats - use sectorHeat from market_heat.json or fall back to sectorData.heat
    const heat = sectorData.heat || sectorHeat || {};
    document.getElementById('sector-stats').innerHTML = `
        <div class="bg-gray-700 rounded-lg p-3 text-center">
            <div class="text-2xl font-bold ${getHeatColor(sectorHeat?.heat_index || heat.heat_index || 0)}">${(sectorHeat?.heat_index || heat.heat_index || 0).toFixed(1)}</div>
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
            <div class="text-2xl font-bold text-purple-400">${sectorHeat?.stocks_count || sectorData.summary?.stocks_with_data || 0}</div>
            <div class="text-gray-400 text-xs">Số mã</div>
        </div>
    `;
    
    // Render stock table
    // Handle both "stocks" field (for sectors) and "banks" field (for banks_v2.json)
    const stocks = sectorData.stocks || sectorData.banks || {};
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
        const icopyBadge = isICopySymbol(stock.symbol) ? getICopyIcon() : '';
        const starBadge = (typeof isStarSymbol === 'function' && isStarSymbol(stock.symbol)) ? getStarIcon() : '';
        const noteIcon = (typeof getStockNote === 'function' && getStockNote(stock.symbol)) ? getNoteIcon(getStockNote(stock.symbol)) : '';
        
        return `
            <tr class="stock-row cursor-pointer hover:bg-gray-700 transition-colors" onclick="window.location.href='stock.html?symbol=${stock.symbol}'">
                <td class="px-4 py-3 font-semibold text-white">
                    <span class="inline-flex items-center">
                        ${stock.symbol}${starBadge}${icopyBadge}${noteIcon}
                    </span>
                </td>
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
