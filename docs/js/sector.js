/**
 * JP Stock Webapp - Sector Detail
 * Hiển thị chi tiết tất cả các ngành (bao gồm ngân hàng)
 * Updated: 2026-01-29 - Sử dụng Daily P/B Data + Đồng bộ UI với bank
 */

let sectorData = null;
let sectorHeat = null;
let currentSector = null;
let allStocks = [];

// Sector configuration - Updated to use daily data files (bao gồm banks)
const SECTORS = {
    banks: { name: '🏦 Ngân hàng', file: 'banks_daily_summary.json', icon: '🏦' },
    realestate: { name: '🏠 Bất động sản', file: 'realestate_daily_summary.json', icon: '🏠' },
    securities: { name: '📈 Chứng khoán', file: 'securities_daily_summary.json', icon: '📈' },
    energy: { name: '⚡ Điện & Năng lượng', file: 'energy_daily_summary.json', icon: '⚡' },
    oilgas: { name: '🛢️ Dầu khí', file: 'oilgas_daily_summary.json', icon: '🛢️' },
    steel: { name: '🏗️ Thép & Vật liệu', file: 'steel_daily_summary.json', icon: '🏗️' },
    construction: { name: '🏗️ Xây dựng', file: 'construction_daily_summary.json', icon: '🏗️' },
    insurance: { name: '🛡️ Bảo hiểm', file: 'insurance_daily_summary.json', icon: '🛡️' },
    retail: { name: '🛒 Bán lẻ & Tiêu dùng', file: 'retail_daily_summary.json', icon: '🛒' },
    technology: { name: '💻 Công nghệ', file: 'technology_daily_summary.json', icon: '💻' },
    chemicals: { name: '🧪 Hóa chất & Công nghiệp', file: 'chemicals_daily_summary.json', icon: '🧪' }
};

// Get sector from URL
function getSector() {
    const params = new URLSearchParams(window.location.search);
    return params.get('sector') || 'banks';
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
        // Load sector data and market heat (for consistent heat index)
        const [sectorRes, marketHeatRes] = await Promise.all([
            fetch(`data/${config.file}`),
            fetch('data/market_heat.json').catch(() => null)
        ]);
        
        sectorData = await sectorRes.json();
        
        // Get sector heat from market_heat.json for consistency
        if (marketHeatRes) {
            const marketHeat = await marketHeatRes.json();
            const sectorHeatData = (marketHeat.sectors || []).find(s => s.sector_id === currentSector);
            if (sectorHeatData) {
                sectorHeat = sectorHeatData;
            }
        }
        
        // Update page title and header
        document.title = `${config.name} | JP Stock Analysis V2`;
        document.getElementById('sectorTitle').innerHTML = `${config.icon} JP Stock Analysis V2 - ${config.name}`;
        document.getElementById('sectorDesc').textContent = 'Phân tích P/B định lượng với Historical Backtest';
        
        // Get stocks array
        const stocks = sectorData.stocks || {};
        allStocks = Object.values(stocks);
        
        // Display in order: heat index -> summary -> stock list
        displayHeatIndex();
        displaySummary();
        displayStockList(allStocks);
    } catch (error) {
        console.error('Error loading sector data:', error);
        document.getElementById('stock-list').innerHTML = `<div class="col-span-full text-center text-red-500">❌ Lỗi tải dữ liệu: ${error.message}</div>`;
    }
}

// Display Sector Heat Index - Sử dụng heat từ market_heat.json
function displayHeatIndex() {
    const stocks = Object.values(sectorData.stocks || {});
    const config = SECTORS[currentSector];
    
    // Check data quality across sector stocks
    let dataWarnings = [];
    let staleDataCount = 0;
    let oldBvpsCount = 0;
    
    stocks.forEach(stock => {
        const dq = stock.data_quality || {};
        if (dq.data_age_days > 1) staleDataCount++;
        if (dq.bvps_age_days > 120) oldBvpsCount++;
    });
    
    if (staleDataCount > stocks.length * 0.2) {
        dataWarnings.push(`⚠️ ${staleDataCount}/${stocks.length} mã có dữ liệu giá cũ >1 ngày`);
    }
    if (oldBvpsCount > stocks.length * 0.3) {
        dataWarnings.push(`⚠️ ${oldBvpsCount}/${stocks.length} mã có BVPS cũ >4 tháng`);
    }
    
    const warningHTML = dataWarnings.length > 0 ? `
        <div class="bg-orange-500/10 border border-orange-500/30 rounded-lg p-3 mb-4">
            <div class="flex items-start gap-2">
                <span class="text-orange-400 text-lg">⚠️</span>
                <div class="text-sm">
                    ${dataWarnings.map(w => `<div class="text-orange-300">${w}</div>`).join('')}
                </div>
            </div>
        </div>` : '';
    
    // Use heat from market_heat.json (sectorHeat) if available, otherwise calculate
    let heatIndex, status, signal, metrics;
    
    if (sectorHeat && sectorHeat.heat_index !== undefined) {
        // Use pre-calculated values from market_heat.json
        heatIndex = sectorHeat.heat_index;
        status = sectorHeat.status || getStatusFromHeat(heatIndex);
        signal = sectorHeat.signal || getSignalFromHeat(heatIndex);
        // Calculate metrics from stocks for display
        const calculated = calculateHeatFromStocks(stocks);
        metrics = calculated.metrics || {};
    } else {
        // Fallback: calculate from stocks
        const calculated = calculateHeatFromStocks(stocks);
        heatIndex = calculated.heat_index || 0;
        metrics = calculated.metrics || {};
        status = getStatusFromHeat(heatIndex);
        signal = getSignalFromHeat(heatIndex);
    }
    
    // Heat gauge gradient
    const heatPercent = heatIndex;
    const gaugeGradient = `linear-gradient(to right, 
        #8B5CF6 0%, #3B82F6 20%, #22C55E 40%, #EAB308 60%, #F97316 80%, #EF4444 100%)`;
    
    const description = getDescriptionFromHeat(heatIndex);
    const heatColor = getHeatColorHex(heatIndex);
    
    document.getElementById('heat-index').innerHTML = `
        <div class="bg-gradient-to-r from-gray-800 to-gray-900 rounded-lg p-6 mb-6 border border-gray-700">
            ${warningHTML}
            <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-4">
                <div>
                    <h2 class="text-xl font-bold text-white flex items-center gap-2">
                        🌡️ Chỉ số Nhiệt độ Ngành ${config.name}
                        <span class="text-sm font-normal text-gray-400">(Sector Heat Index)</span>
                    </h2>
                    <p class="text-gray-400 text-sm mt-1">Đo lường độ nóng/lạnh dựa trên P/B toàn ngành - Data: ${sectorData.last_updated?.split('T')[0] || 'N/A'}</p>
                </div>
                <div class="mt-3 md:mt-0 text-right">
                    <div class="text-4xl font-bold" style="color: ${heatColor}">${heatIndex.toFixed(1)}</div>
                    <div class="text-sm text-gray-400">/ 100</div>
                </div>
            </div>
            
            <!-- Heat Gauge -->
            <div class="mb-4">
                <div class="h-4 rounded-full overflow-hidden" style="background: ${gaugeGradient}">
                    <div class="relative h-full">
                        <div class="absolute top-0 h-full w-1 bg-white shadow-lg" 
                             style="left: ${heatPercent}%; transform: translateX(-50%);">
                        </div>
                    </div>
                </div>
                <div class="flex justify-between text-xs text-gray-500 mt-1">
                    <span>🥶 Cực lạnh</span>
                    <span>❄️ Lạnh</span>
                    <span>😐 Bình thường</span>
                    <span>🌡️ Nóng</span>
                    <span>🔥 Quá nóng</span>
                </div>
            </div>
            
            <!-- Status & Signal -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div class="bg-gray-900/50 rounded-lg p-4">
                    <div class="text-gray-400 text-sm mb-1">Trạng thái</div>
                    <div class="text-2xl font-bold" style="color: ${heatColor}">${status}</div>
                    <div class="text-xs text-gray-500 mt-1">${description}</div>
                </div>
                <div class="bg-gray-900/50 rounded-lg p-4">
                    <div class="text-gray-400 text-sm mb-1">Tín hiệu</div>
                    <div class="text-2xl font-bold ${getSignalClass(signal)}">${signal}</div>
                    <div class="text-xs text-gray-500 mt-1">Dựa trên mức nhiệt độ hiện tại</div>
                </div>
                <div class="bg-gray-900/50 rounded-lg p-4">
                    <div class="text-gray-400 text-sm mb-1">Số mã phân tích</div>
                    <div class="text-2xl font-bold text-white">${stocks.length} mã</div>
                    <div class="text-xs text-gray-500 mt-1">Trong ngành ${config.name}</div>
                </div>
            </div>
            
            <!-- Metrics -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                <div class="bg-gray-900/30 rounded p-3 text-center">
                    <div class="text-gray-400 text-xs">Avg P/B Percentile</div>
                    <div class="text-white font-bold">P${Math.round(heatIndex)}</div>
                </div>
                <div class="bg-gray-900/30 rounded p-3 text-center">
                    <div class="text-gray-400 text-xs">Avg P/B</div>
                    <div class="text-white font-bold">${metrics.avg_pb?.toFixed(2) || 'N/A'}x</div>
                </div>
                <div class="bg-gray-900/30 rounded p-3 text-center">
                    <div class="text-gray-400 text-xs">CP rẻ (P&lt;35)</div>
                    <div class="text-green-400 font-bold">${metrics.cheap_count || 0}/${stocks.length}</div>
                </div>
                <div class="bg-gray-900/30 rounded p-3 text-center">
                    <div class="text-gray-400 text-xs">CP đắt (P&gt;65)</div>
                    <div class="text-red-400 font-bold">${metrics.expensive_count || 0}/${stocks.length}</div>
                </div>
            </div>
            
            <!-- Recommendations based on heat -->
            <div class="border-t border-gray-700 pt-4">
                <div class="text-sm font-semibold text-gray-300 mb-2">💡 Khuyến nghị:</div>
                <div class="text-sm text-gray-300">
                    ${getRecommendationFromHeat(heatIndex)}
                </div>
            </div>
        </div>
    `;
}


// Calculate heat index from stocks data
function calculateHeatFromStocks(stocks) {
    if (!stocks || stocks.length === 0) {
        return { heat_index: 50, metrics: {} };
    }
    
    let totalPercentile = 0;
    let totalPB = 0;
    let validCount = 0;
    let cheapCount = 0;
    let expensiveCount = 0;
    
    stocks.forEach(stock => {
        const percentile = stock.valuation?.percentile;
        const pb = stock.current?.pb_vnstock || stock.current?.pb_calculated || stock.current?.pb;
        
        if (percentile !== undefined && percentile !== null) {
            totalPercentile += percentile;
            validCount++;
            
            if (percentile < 35) cheapCount++;
            if (percentile > 65) expensiveCount++;
        }
        
        if (pb !== undefined && pb !== null) {
            totalPB += pb;
        }
    });
    
    const avgPercentile = validCount > 0 ? totalPercentile / validCount : 50;
    const avgPB = validCount > 0 ? totalPB / validCount : 0;
    
    return {
        heat_index: avgPercentile,
        metrics: {
            avg_pb_percentile: avgPercentile,
            avg_pb: avgPB,
            cheap_count: cheapCount,
            expensive_count: expensiveCount,
            total_stocks: stocks.length
        }
    };
}

// Get recommendation based on heat index
function getRecommendationFromHeat(heat) {
    if (heat < 20) return '🔥 <span class="text-blue-400 font-bold">MUA MẠNH</span> - Ngành đang cực rẻ, đây là cơ hội hiếm có để tích lũy dài hạn';
    if (heat < 35) return '🛒 <span class="text-green-400 font-bold">MUA</span> - Ngành đang rẻ, nên tích lũy từ từ các mã tốt';
    if (heat < 50) return '📈 <span class="text-cyan-400 font-bold">TÍCH LŨY</span> - Ngành hơi rẻ, có thể mua thêm dần';
    if (heat < 65) return '⏸️ <span class="text-yellow-400 font-bold">GIỮ</span> - Ngành trung tính, giữ nguyên danh mục';
    if (heat < 80) return '⚠️ <span class="text-orange-400 font-bold">CẨN THẬN</span> - Ngành hơi đắt, hạn chế mua thêm';
    return '🚨 <span class="text-red-400 font-bold">CHỐT LỜI</span> - Ngành quá nóng, nên giảm tỷ trọng';
}

// Helper functions for heat calculation
function countCheapStocks() {
    return allStocks.filter(s => (s.valuation?.percentile || 50) < 35).length;
}

function countExpensiveStocks() {
    return allStocks.filter(s => (s.valuation?.percentile || 50) > 65).length;
}

function calculateAvgPB() {
    const validStocks = allStocks.filter(s => s.current?.pb_vnstock || s.current?.pb_calculated || s.current?.pb);
    if (validStocks.length === 0) return 0;
    return validStocks.reduce((sum, s) => sum + (s.current.pb_vnstock || s.current.pb_calculated || s.current.pb), 0) / validStocks.length;
}

// Get signal from heat index
function getSignalFromHeat(heat) {
    if (heat < 20) return 'BUY_HEAVY';
    if (heat < 35) return 'BUY';
    if (heat < 50) return 'ACCUMULATE';
    if (heat < 65) return 'HOLD';
    if (heat < 80) return 'REDUCE';
    return 'SELL';
}

// Get status from heat index
function getStatusFromHeat(heat) {
    if (heat < 20) return '🥶 ICE COLD';
    if (heat < 35) return '❄️ COLD';
    if (heat < 50) return '🌤️ COOL';
    if (heat < 65) return '😐 NEUTRAL';
    if (heat < 80) return '☀️ WARM';
    return '🔥 HOT';
}

// Get description from heat
function getDescriptionFromHeat(heat) {
    if (heat < 20) return 'Ngành cực lạnh, cơ hội mua mạnh';
    if (heat < 35) return 'Ngành lạnh, nên tích lũy';
    if (heat < 50) return 'Hơi rẻ, có thể mua từ từ';
    if (heat < 65) return 'Trung tính, giữ nguyên';
    if (heat < 80) return 'Hơi đắt, cẩn thận';
    return 'Quá nóng, cân nhắc chốt lời';
}

// Get heat color hex
function getHeatColorHex(heat) {
    if (heat >= 85) return '#EF4444';
    if (heat >= 70) return '#F97316';
    if (heat >= 55) return '#EAB308';
    if (heat >= 45) return '#22C55E';
    if (heat >= 35) return '#14B8A6';
    if (heat >= 20) return '#3B82F6';
    return '#8B5CF6';
}

// Get status emoji
function getStatusEmoji(status) {
    const emojis = {
        'OVERHEATED': '🔥',
        'HOT': '🌡️',
        'WARM': '☀️',
        'NEUTRAL': '😐',
        'COOL': '🌤️',
        'COLD': '❄️',
        'ICE_COLD': '🥶'
    };
    return emojis[status] || '❓';
}

// Get signal CSS class (alias for getSignalColor)
function getSignalClass(signal) {
    const classes = {
        'SELL_ALL': 'text-red-500',
        'SELL': 'text-red-500',
        'REDUCE': 'text-orange-400',
        'HOLD': 'text-yellow-400',
        'NORMAL': 'text-green-400',
        'ACCUMULATE': 'text-cyan-400',
        'BUY': 'text-blue-500',
        'BUY_HEAVY': 'text-purple-500'
    };
    return classes[signal] || 'text-gray-400';
}

// Get signal color class
function getSignalColor(signal) {
    const colors = {
        'SELL_ALL': 'text-red-500',
        'SELL': 'text-red-500',
        'REDUCE': 'text-orange-400',
        'HOLD': 'text-yellow-400',
        'NORMAL': 'text-green-400',
        'ACCUMULATE': 'text-blue-400',
        'BUY': 'text-blue-500',
        'BUY_HEAVY': 'text-purple-500'
    };
    return colors[signal] || 'text-gray-400';
}

// Draw heat history chart - Only show if we have daily data (not quarterly)
function drawHeatHistoryChart() {
    const history = sectorHeat?.history || sectorData?.heat?.history || [];
    
    // Skip if no data or if data is quarterly (contains Q1-Q4 in period)
    if (history.length === 0) return;
    
    // Check if this is quarterly data (old format) - skip if so
    const firstPeriod = history[0]?.period || '';
    if (firstPeriod.includes('-Q') || firstPeriod.match(/\d{4}-Q\d/)) {
        console.log('Skipping heat history chart - data is quarterly format');
        return;
    }
    
    const periods = history.map(h => h.period);
    const heatValues = history.map(h => h.heat_index);
    
    // Color based on heat level
    const colors = heatValues.map(h => getHeatColorHex(h));
    
    // Heat line
    const trace1 = {
        x: periods,
        y: heatValues,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Heat Index',
        line: { color: '#F97316', width: 2 },
        marker: { color: colors, size: 6 },
        fill: 'tozeroy',
        fillcolor: 'rgba(249, 115, 22, 0.1)'
    };
    
    // Zone lines
    const overheatedLine = {
        x: [periods[0], periods[periods.length-1]],
        y: [85, 85],
        type: 'scatter',
        mode: 'lines',
        name: 'Overheated (85)',
        line: { color: '#EF4444', width: 1, dash: 'dash' }
    };
    
    const hotLine = {
        x: [periods[0], periods[periods.length-1]],
        y: [70, 70],
        type: 'scatter',
        mode: 'lines',
        name: 'Hot (70)',
        line: { color: '#F97316', width: 1, dash: 'dot' }
    };
    
    const coldLine = {
        x: [periods[0], periods[periods.length-1]],
        y: [35, 35],
        type: 'scatter',
        mode: 'lines',
        name: 'Cold (35)',
        line: { color: '#3B82F6', width: 1, dash: 'dot' }
    };
    
    const iceColdLine = {
        x: [periods[0], periods[periods.length-1]],
        y: [20, 20],
        type: 'scatter',
        mode: 'lines',
        name: 'Ice Cold (20)',
        line: { color: '#8B5CF6', width: 1, dash: 'dash' }
    };
    
    const layout = {
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: '#9ca3af', size: 10 },
        margin: { t: 10, b: 50, l: 40, r: 10 },
        xaxis: {
            gridcolor: '#374151',
            tickangle: -45,
            tickfont: { size: 9 }
        },
        yaxis: {
            title: 'Heat Index',
            gridcolor: '#374151',
            range: [0, 100],
            tickfont: { size: 9 }
        },
        legend: {
            x: 0,
            y: 1.15,
            orientation: 'h',
            font: { size: 9 }
        },
        shapes: [
            // Overheated zone (red)
            {
                type: 'rect',
                xref: 'paper', yref: 'y',
                x0: 0, x1: 1, y0: 85, y1: 100,
                fillcolor: 'rgba(239, 68, 68, 0.1)',
                line: { width: 0 }
            },
            // Cold zone (blue)
            {
                type: 'rect',
                xref: 'paper', yref: 'y',
                x0: 0, x1: 1, y0: 0, y1: 35,
                fillcolor: 'rgba(59, 130, 246, 0.1)',
                line: { width: 0 }
            }
        ],
        annotations: heatValues.length > 0 ? [
            {
                x: periods[periods.length-1],
                y: heatValues[heatValues.length-1],
                text: `${heatValues[heatValues.length-1].toFixed(0)}`,
                showarrow: true,
                arrowhead: 2,
                arrowsize: 1,
                arrowcolor: '#F97316',
                font: { color: '#F97316', size: 12, weight: 'bold' },
                ax: 30,
                ay: -20
            }
        ] : []
    };
    
    Plotly.newPlot('heat-history-chart', [trace1, overheatedLine, hotLine, coldLine, iceColdLine], layout, { 
        responsive: true,
        displayModeBar: false
    });
}

// Display summary statistics - Đồng bộ với bank.html
function displaySummary() {
    // Count by zone
    const zoneCounts = {
        'extremely_cheap': 0,
        'cheap': 0,
        'fair': 0,
        'expensive': 0,
        'extremely_expensive': 0
    };
    
    let totalReturn = 0, countReturn = 0;
    
    allStocks.forEach(stock => {
        const zone = stock.valuation?.zone || 'fair';
        // Map zone names
        let mappedZone = zone.toLowerCase().replace('very_', 'extremely_').replace('overvalued', 'extremely_expensive');
        if (mappedZone === 'extremely_cheap' || mappedZone === 'cheap' || mappedZone === 'fair' || mappedZone === 'expensive' || mappedZone === 'extremely_expensive') {
            zoneCounts[mappedZone]++;
        } else if (zone.includes('CỰC RẺ') || zone === 'VERY_CHEAP') {
            zoneCounts.extremely_cheap++;
        } else if (zone.includes('RẺ') || zone === 'CHEAP') {
            zoneCounts.cheap++;
        } else if (zone.includes('ĐẮT') && zone.includes('CỰC') || zone === 'VERY_EXPENSIVE') {
            zoneCounts.extremely_expensive++;
        } else if (zone.includes('ĐẮT') || zone === 'EXPENSIVE') {
            zoneCounts.expensive++;
        } else {
            zoneCounts.fair++;
        }
        
        // Calculate expected return from historical_returns
        const hr = stock.historical_returns || {};
        const zoneReturns = hr[zone] || hr.fair || {};
        if (zoneReturns.returns && zoneReturns.returns['365d']) {
            totalReturn += zoneReturns.returns['365d'].avg || 0;
            countReturn++;
        }
    });
    
    const avgReturn = countReturn > 0 ? (totalReturn / countReturn).toFixed(1) : 'N/A';
    
    document.getElementById('summary').innerHTML = `
        <div class="bg-gray-800 rounded-lg p-6 mb-6">
            <h2 class="text-xl font-bold text-white mb-4">📊 Tổng quan ${SECTORS[currentSector]?.name || 'ngành'}</h2>
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
                <span class="mr-4">📅 Cập nhật: ${new Date(sectorData.last_updated).toLocaleString('vi-VN')}</span>
                <span>📈 Dựa trên backtest lịch sử P/B theo ngày</span>
            </div>
        </div>
    `;
}

// Display stock list
function displayStockList(stocks) {
    const container = document.getElementById('stock-list');
    
    // Sort by valuation score (best buys first - lowest percentile)
    const sortedStocks = [...stocks].sort((a, b) => {
        const pctA = a.valuation?.percentile ?? 50;
        const pctB = b.valuation?.percentile ?? 50;
        return pctA - pctB;
    });
    
    container.innerHTML = sortedStocks.map(stock => createStockCard(stock)).join('');
}

// Helper: Map English zone to Vietnamese
function getZoneVietnamese(zone) {
    const zoneMap = {
        'VERY_CHEAP': '🟢 CỰC RẺ',
        'CHEAP': '🟢 RẺ',
        'FAIR': '🟡 HỢP LÝ',
        'EXPENSIVE': '🔴 ĐẮT',
        'VERY_EXPENSIVE': '🔴 CỰC ĐẮT',
        'OVERVALUED': '🔴 QUÁ ĐẮT',
        'extremely_cheap': '🟢 CỰC RẺ',
        'cheap': '🟢 RẺ',
        'fair': '🟡 HỢP LÝ',
        'expensive': '🔴 ĐẮT',
        'extremely_expensive': '🔴 CỰC ĐẮT'
    };
    return zoneMap[zone] || zone || 'N/A';
}

// Create individual stock card - Đồng bộ với bank.html
function createStockCard(stock) {
    const valuation = stock.valuation || {};
    const stats = stock.statistics || stock.pb_statistics || {};
    const historicalReturns = stock.historical_returns || {};
    
    // Zone/Status - convert to Vietnamese
    const zone = valuation.zone || 'fair';
    const zoneVi = valuation.zone_vi || getZoneVietnamese(zone);
    
    // Zone color
    const zoneColor = zoneVi.includes('RẺ') ? '#10B981' :
                     zoneVi.includes('ĐẮT') ? '#EF4444' :
                     zoneVi.includes('HỢP') ? '#F59E0B' : '#6B7280';
    
    // P/B values
    const currentPb = (stock.current?.pb_vnstock || stock.current?.pb_calculated || stock.current?.pb || stock.current_pb)?.toFixed(2) || 'N/A';
    const avgPb = stats.mean?.toFixed(2) || 'N/A';
    
    // Percentile
    const percentile = (valuation.percentile || 50).toFixed(0);
    
    // Current price
    let currentPrice = 'N/A';
    if (stock.current?.price) {
        currentPrice = stock.current.price.toLocaleString('vi-VN');
    } else if (stock.current_price) {
        currentPrice = stock.current_price.toLocaleString('vi-VN');
    }
    
    // Expected return from backtest (use zone's historical returns)
    let return1y = 'N/A';
    let winRate = 'N/A';
    let returnClass = 'text-gray-400';
    let winRateClass = 'text-gray-400';
    
    // Try to get returns from historical_returns based on zone
    const zoneKey = zone.toLowerCase().replace('very_', 'extremely_');
    const zoneReturns = historicalReturns[zoneKey] || historicalReturns[zone] || historicalReturns.fair;
    
    if (zoneReturns && zoneReturns.returns && zoneReturns.returns['365d']) {
        const returns365 = zoneReturns.returns['365d'];
        if (returns365.avg != null) {
            return1y = `${returns365.avg > 0 ? '+' : ''}${returns365.avg.toFixed(1)}%`;
            returnClass = returns365.avg >= 20 ? 'text-green-400' : 
                         returns365.avg >= 0 ? 'text-yellow-400' : 'text-red-400';
        }
        if (returns365.win_rate != null) {
            winRate = `${returns365.win_rate.toFixed(0)}%`;
            winRateClass = returns365.win_rate >= 70 ? 'text-green-400' :
                          returns365.win_rate >= 50 ? 'text-yellow-400' : 'text-red-400';
        }
    }
    
    // Risk level (derived from zone)
    let riskLevel = 'Trung bình';
    if (zone.includes('expensive') || zone.includes('EXPENSIVE') || zone.includes('ĐẮT')) {
        riskLevel = 'Cao';
    } else if (zone.includes('cheap') || zone.includes('CHEAP') || zone.includes('RẺ')) {
        riskLevel = 'Thấp';
    }
    
    const icopyBadge = (typeof isICopySymbol === 'function' && isICopySymbol(stock.symbol)) ? getICopyBadge('sm') : '';
    const starBadge = (typeof isStarSymbol === 'function' && isStarSymbol(stock.symbol)) ? getStarBadge('sm') : '';
    
    return `
        <a href="stock.html?symbol=${stock.symbol}" class="stock-card block bg-gray-800 rounded-lg p-4 hover:bg-gray-700 transition-all hover:scale-[1.02]">
            <div class="flex justify-between items-start mb-3">
                <div>
                    <h3 class="text-xl font-bold text-white inline-flex items-center">
                        ${stock.symbol}${starBadge}${icopyBadge}
                    </h3>
                    <p class="text-sm text-gray-400">${stock.name || ''}</p>
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
                <span class="text-gray-500">⚠️ Rủi ro: ${riskLevel}</span>
            </div>
        </a>
    `;
}

// Filter by zone - Đồng bộ với bank.html
function filterByZone(zone, btn) {
    if (!sectorData) return;
    
    let filtered = allStocks;
    if (zone !== 'all') {
        filtered = allStocks.filter(stock => {
            const val = stock.valuation || {};
            const stockZone = (val.zone || '').toLowerCase();
            const stockZoneVi = val.zone_vi || '';
            
            if (zone === 'extremely_cheap') {
                return stockZone.includes('extremely_cheap') || stockZone === 'very_cheap' || stockZoneVi.includes('CỰC RẺ');
            }
            if (zone === 'cheap') {
                return (stockZone === 'cheap' || stockZoneVi.includes('RẺ')) && !stockZone.includes('extremely') && !stockZoneVi.includes('CỰC');
            }
            if (zone === 'fair') {
                return stockZone === 'fair' || stockZoneVi.includes('HỢP LÝ');
            }
            if (zone === 'expensive') {
                return (stockZone === 'expensive' || stockZoneVi.includes('ĐẮT')) && !stockZone.includes('extremely') && !stockZoneVi.includes('CỰC');
            }
            if (zone === 'extremely_expensive') {
                return stockZone.includes('extremely_expensive') || stockZone === 'very_expensive' || stockZone === 'overvalued' || stockZoneVi.includes('CỰC ĐẮT') || stockZoneVi.includes('QUÁ ĐẮT');
            }
            return true;
        });
    }
    
    displayStockList(filtered);
    
    // Update active button
    document.querySelectorAll('.filter-btn').forEach(b => {
        b.classList.remove('ring-2', 'ring-blue-500', 'bg-blue-600');
        b.classList.add('bg-gray-700');
    });
    btn.classList.remove('bg-gray-700');
    btn.classList.add('ring-2', 'ring-blue-500', 'bg-blue-600');
}

// Sort stocks - Đồng bộ với bank.html
function sortStocks(field) {
    if (!sectorData) return;
    
    const sorted = [...allStocks].sort((a, b) => {
        let valA, valB;
        
        switch(field) {
            case 'return':
                valA = getExpectedReturn(a);
                valB = getExpectedReturn(b);
                return valB - valA;
            case 'winrate':
                valA = getWinRate(a);
                valB = getWinRate(b);
                return valB - valA;
            case 'cheap':
            case 'percentile':
                valA = a.valuation?.percentile ?? 999;
                valB = b.valuation?.percentile ?? 999;
                return valA - valB;
            case 'risk':
                valA = getRiskScore(a);
                valB = getRiskScore(b);
                return valA - valB;
            case 'current_pb':
                valA = a.current?.pb_vnstock || a.current?.pb_calculated || a.current?.pb || a.current_pb || 0;
                valB = b.current?.pb_vnstock || b.current?.pb_calculated || b.current?.pb || b.current_pb || 0;
                return valA - valB;
            default:
                return (a.valuation?.percentile ?? 50) - (b.valuation?.percentile ?? 50);
        }
    });
    
    displayStockList(sorted);
}

// Helper: Get expected 1Y return from backtest
function getExpectedReturn(stock) {
    const historicalReturns = stock.historical_returns || {};
    const zone = (stock.valuation?.zone || 'fair').toLowerCase();
    const zoneReturns = historicalReturns[zone] || historicalReturns.fair;
    if (zoneReturns && zoneReturns.returns && zoneReturns.returns['365d']) {
        return zoneReturns.returns['365d'].avg || -999;
    }
    return -999;
}

// Helper: Get win rate
function getWinRate(stock) {
    const historicalReturns = stock.historical_returns || {};
    const zone = (stock.valuation?.zone || 'fair').toLowerCase();
    const zoneReturns = historicalReturns[zone] || historicalReturns.fair;
    if (zoneReturns && zoneReturns.returns && zoneReturns.returns['365d']) {
        return zoneReturns.returns['365d'].win_rate || -999;
    }
    return -999;
}

// Helper: Get risk score (based on zone - higher percentile = higher risk)
function getRiskScore(stock) {
    return stock.valuation?.percentile ?? 50;
}
