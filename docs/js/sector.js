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
        
        // Get stocks array
        const stocks = sectorData.stocks || {};
        allStocks = Object.values(stocks);
        
        // Display in order: heat index -> summary -> stock list
        displayHeatIndex(config);
        displaySummary();
        displayStockList(allStocks);
    } catch (error) {
        console.error('Error loading sector data:', error);
        document.getElementById('stock-list').innerHTML = `<div class="col-span-full text-center text-red-500">❌ Lỗi tải dữ liệu: ${error.message}</div>`;
    }
}

// Display sector heat index
function displayHeatIndex(config) {
    const heat = sectorData.heat || {};
    const heatIndex = heat.heat_index || 0;
    const status = heat.status || '😐 NEUTRAL';
    const signal = heat.signal || 'NORMAL';
    
    const heatColor = heatIndex < 20 ? 'text-blue-400' :
                     heatIndex < 35 ? 'text-cyan-400' :
                     heatIndex < 50 ? 'text-green-400' :
                     heatIndex < 65 ? 'text-yellow-400' :
                     heatIndex < 80 ? 'text-orange-400' : 'text-red-400';
    
    const signalColor = signal === 'BUY' ? 'text-green-400' :
                       signal === 'ACCUMULATE' ? 'text-blue-400' :
                       signal === 'HOLD' ? 'text-yellow-400' : 'text-gray-400';
    
    document.getElementById('heat-index').innerHTML = `
        <div class="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 mb-6 border border-gray-700">
            <h2 class="text-2xl font-bold text-white mb-4">🌡️ Chỉ Số Nhiệt Độ Ngành - ${config.name}</h2>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="text-center p-4 bg-gray-700/50 rounded-lg">
                    <div class="text-3xl font-bold ${heatColor}">${heatIndex.toFixed(1)}</div>
                    <div class="text-gray-400 text-sm mt-1">Heat Index</div>
                </div>
                <div class="text-center p-4 bg-gray-700/50 rounded-lg">
                    <div class="text-2xl font-bold text-white">${status}</div>
                    <div class="text-gray-400 text-sm mt-1">Trạng thái</div>
                </div>
                <div class="text-center p-4 bg-gray-700/50 rounded-lg">
                    <div class="text-2xl font-bold ${signalColor}">${signal}</div>
                    <div class="text-gray-400 text-sm mt-1">Tín hiệu</div>
                </div>
                <div class="text-center p-4 bg-gray-700/50 rounded-lg">
                    <div class="text-2xl font-bold text-purple-400">${allStocks.length}</div>
                    <div class="text-gray-400 text-sm mt-1">Số mã</div>
                </div>
            </div>
            <div class="mt-4 p-4 bg-blue-900/20 border border-blue-500/30 rounded-lg">
                <p class="text-blue-300 text-sm">
                    💡 <strong>Giải thích:</strong> Heat Index thấp (&lt;35) = Ngành đang rẻ, có thể tích lũy. 
                    Heat Index cao (&gt;65) = Ngành đang đắt, cân nhắc chốt lời.
                </p>
            </div>
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
    
    // Display heat history chart
    displayHeatHistory(heat);
}

// Display heat history
function displayHeatHistory(heat) {
    const history = heat.history || [];
    const analysis = heat.analysis || {};
    
    if (history.length === 0) {
        document.getElementById('heat-history').innerHTML = '';
        return;
    }
    
    document.getElementById('heat-history').innerHTML = `
        <div class="bg-gradient-to-br from-gray-800 to-gray-900 rounded-lg p-6 border border-gray-700">
            <div class="flex justify-between items-center mb-4">
                <div class="text-sm font-semibold text-gray-300">📈 Lịch sử Nhiệt độ ngành (${history.length} quý)</div>
                <div class="text-xs text-gray-500">
                    🔥 Max: <span class="text-red-400 font-bold">${analysis.max_heat || 0}</span> (${analysis.max_heat_period || 'N/A'}) | 
                    ❄️ Min: <span class="text-blue-400 font-bold">${analysis.min_heat || 0}</span> (${analysis.min_heat_period || 'N/A'}) |
                    📊 Avg: <span class="text-yellow-400">${analysis.avg_heat || 0}</span>
                </div>
            </div>
            <div id="heat-chart" style="height: 300px;"></div>
            
            <!-- Historical Data Table -->
            <div class="mt-4">
                <details class="group">
                    <summary class="cursor-pointer text-sm text-gray-400 hover:text-white flex items-center gap-2">
                        <span>📋 Xem bảng dữ liệu chi tiết</span>
                        <svg class="w-4 h-4 transform group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                        </svg>
                    </summary>
                    <div class="mt-3 max-h-64 overflow-y-auto">
                        <table class="w-full text-xs">
                            <thead class="sticky top-0 bg-gray-800">
                                <tr class="border-b border-gray-700">
                                    <th class="py-2 px-2 text-left text-gray-400">Kỳ</th>
                                    <th class="py-2 px-2 text-right text-gray-400">Heat Index</th>
                                    <th class="py-2 px-2 text-center text-gray-400">Trạng thái</th>
                                    <th class="py-2 px-2 text-right text-gray-400">Avg P/B</th>
                                    <th class="py-2 px-2 text-right text-gray-400">Mã</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${history.slice().reverse().map(h => `
                                    <tr class="border-b border-gray-700/50 hover:bg-gray-700/30">
                                        <td class="py-1 px-2 text-gray-300">${h.period}</td>
                                        <td class="py-1 px-2 text-right font-bold" style="color: ${getHeatColor(h.heat_index)}">${h.heat_index?.toFixed(1)}</td>
                                        <td class="py-1 px-2 text-center">${getStatusEmoji(h.status)}</td>
                                        <td class="py-1 px-2 text-right text-cyan-400">${h.avg_pb?.toFixed(2)}x</td>
                                        <td class="py-1 px-2 text-right text-gray-500">${h.banks_count}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </details>
            </div>
        </div>
    `;
    
    // Draw chart after DOM is ready
    setTimeout(() => {
        drawHeatChart(history);
    }, 100);
}

// Get heat color
function getHeatColor(heat) {
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

// Draw heat chart
function drawHeatChart(history) {
    if (!history || history.length === 0) return;
    
    const periods = history.map(h => h.period);
    const heatValues = history.map(h => h.heat_index);
    
    // Color based on heat level
    const colors = heatValues.map(h => getHeatColor(h));
    
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
    
    // Reference lines
    const overheatedLine = {
        x: periods,
        y: periods.map(() => 85),
        mode: 'lines',
        name: 'Overheated (85)',
        line: { color: 'rgba(239, 68, 68, 0.5)', width: 1, dash: 'dash' },
        hoverinfo: 'skip',
        showlegend: false
    };
    
    const hotLine = {
        x: periods,
        y: periods.map(() => 70),
        mode: 'lines',
        name: 'Hot (70)',
        line: { color: 'rgba(249, 115, 22, 0.5)', width: 1, dash: 'dash' },
        hoverinfo: 'skip',
        showlegend: false
    };
    
    const coldLine = {
        x: periods,
        y: periods.map(() => 35),
        mode: 'lines',
        name: 'Cold (35)',
        line: { color: 'rgba(59, 130, 246, 0.5)', width: 1, dash: 'dash' },
        hoverinfo: 'skip',
        showlegend: false
    };
    
    const iceColdLine = {
        x: periods,
        y: periods.map(() => 20),
        mode: 'lines',
        name: 'Ice Cold (20)',
        line: { color: 'rgba(139, 92, 246, 0.5)', width: 1, dash: 'dash' },
        hoverinfo: 'skip',
        showlegend: false
    };
    
    const layout = {
        title: '',
        xaxis: { title: '' },
        yaxis: { title: 'Heat Index', range: [0, 100] },
        hovermode: 'x unified',
        plot_bgcolor: 'rgba(17,24,39,0.5)',
        paper_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#9CA3AF', family: 'system-ui' },
        margin: { l: 50, r: 50, t: 20, b: 40 },
        showlegend: true,
        legend: {
            x: 0.02,
            y: 0.98,
            bgcolor: 'rgba(0,0,0,0.5)',
            bordercolor: 'rgba(255,255,255,0.2)',
            borderwidth: 1
        }
    };
    
    Plotly.newPlot('heat-chart', [trace1, overheatedLine, hotLine, coldLine, iceColdLine], layout, { 
        responsive: true,
        displayModeBar: false
    });
}

// Display stock list
function displayStockList(stocks) {
    document.getElementById('stock-list').innerHTML = stocks.map(stock => createStockCard(stock)).join('');
}

// Create individual stock card (giống bank card)
function createStockCard(stock) {
    const eval = stock.evaluation || stock.valuation || {};
    const stats = stock.pb_statistics || {};
    
    // Zone/Status color
    const status = eval.status || eval.zone_vi || 'N/A';
    const zoneColor = eval.status?.includes('RẺ') ? '#10B981' :
                     eval.status?.includes('ĐẮT') ? '#EF4444' :
                     eval.status?.includes('HỢPÝ') ? '#F59E0B' : '#6B7280';
    
    // P/B values
    const currentPb = stock.current_pb?.toFixed(2) || 'N/A';
    const avgPb = stats.mean?.toFixed(2) || 'N/A';
    const minPb = stats.min?.toFixed(2) || 'N/A';
    const maxPb = stats.max?.toFixed(2) || 'N/A';
    
    // Percentile
    const percentile = (eval.current_percentile || eval.percentile || 0).toFixed(0);
    
    // Current price (in thousands)
    const currentPrice = stock.current_price ? 
        (stock.current_price * 1000).toLocaleString('vi-VN') : 'N/A';
    
    return `
        <a href="stock.html?symbol=${stock.symbol}" class="bank-card block bg-gray-800 rounded-lg p-4 hover:bg-gray-700 transition-all hover:scale-[1.02]">
            <div class="flex justify-between items-start mb-3">
                <div>
                    <h3 class="text-xl font-bold text-white">${stock.symbol}</h3>
                    <p class="text-sm text-gray-400">${stock.name || ''}</p>
                </div>
                <span class="px-3 py-1 rounded-full text-sm font-bold" 
                      style="background-color: ${zoneColor}25; color: ${zoneColor}; border: 2px solid ${zoneColor}">
                    ${status}
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
                    <div class="text-gray-500 text-xs">P/B Min</div>
                    <div class="text-green-400 font-bold text-lg">${minPb}</div>
                    <div class="text-gray-500 text-xs">thấp nhất</div>
                </div>
                <div class="bg-gray-900/50 rounded p-2">
                    <div class="text-gray-500 text-xs">P/B Max</div>
                    <div class="text-red-400 font-bold text-lg">${maxPb}</div>
                    <div class="text-gray-500 text-xs">cao nhất</div>
                </div>
            </div>
            
            <div class="flex justify-between items-center text-xs pt-2 border-t border-gray-700">
                <span class="text-gray-500">💰 ${currentPrice}đ</span>
                <span class="text-gray-500">📊 ${eval.position || 'N/A'}</span>
            </div>
        </a>
    `;
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
