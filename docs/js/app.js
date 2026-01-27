/**
 * JP Stock Webapp - Dashboard V2
 * Phân tích P/B với Historical Backtest
 */

let banksData = null;
let sectorHeat = null;

// Fetch and display banks data
async function loadBanks() {
    try {
        const [banksRes, heatRes] = await Promise.all([
            fetch('data/banks_v2.json'),
            fetch('data/sector_heat.json').catch(() => null)
        ]);
        
        banksData = await banksRes.json();
        if (heatRes) {
            sectorHeat = await heatRes.json();
        }
        
        displayHeatIndex();
        displaySummary(banksData);
        displayBankList(banksData.banks);
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

// Display Sector Heat Index
function displayHeatIndex() {
    if (!sectorHeat) {
        document.getElementById('heat-index').innerHTML = '';
        return;
    }
    
    const current = sectorHeat.current;
    const trend = sectorHeat.trend;
    const metrics = current.metrics;
    const recs = sectorHeat.recommendations || [];
    
    // Heat gauge gradient
    const heatPercent = current.heat_index;
    const gaugeGradient = `linear-gradient(to right, 
        #8B5CF6 0%, #3B82F6 20%, #22C55E 40%, #EAB308 60%, #F97316 80%, #EF4444 100%)`;
    
    document.getElementById('heat-index').innerHTML = `
        <div class="bg-gradient-to-r from-gray-800 to-gray-900 rounded-lg p-6 mb-6 border border-gray-700">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-4">
                <div>
                    <h2 class="text-xl font-bold text-white flex items-center gap-2">
                        🌡️ Chỉ số Nhiệt độ Ngành Ngân hàng
                        <span class="text-sm font-normal text-gray-400">(Sector Heat Index)</span>
                    </h2>
                    <p class="text-gray-400 text-sm mt-1">Đo lường độ nóng/lạnh dựa trên P/B toàn ngành</p>
                </div>
                <div class="mt-3 md:mt-0 text-right">
                    <div class="text-4xl font-bold" style="color: ${current.color}">${current.heat_index}</div>
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
                    <div class="text-2xl font-bold" style="color: ${current.color}">${current.status}</div>
                    <div class="text-xs text-gray-500 mt-1">${current.description}</div>
                </div>
                <div class="bg-gray-900/50 rounded-lg p-4">
                    <div class="text-gray-400 text-sm mb-1">Xu hướng</div>
                    <div class="text-2xl font-bold text-white">${trend.emoji} ${trend.direction.replace('_', ' ')}</div>
                    <div class="text-xs text-gray-500 mt-1">${trend.description}</div>
                </div>
                <div class="bg-gray-900/50 rounded-lg p-4">
                    <div class="text-gray-400 text-sm mb-1">Tín hiệu</div>
                    <div class="text-2xl font-bold ${getSignalColor(current.signal)}">${current.signal}</div>
                    <div class="text-xs text-gray-500 mt-1">Dựa trên nhiệt độ hiện tại</div>
                </div>
            </div>
            
            <!-- Metrics -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                <div class="bg-gray-900/30 rounded p-3 text-center">
                    <div class="text-gray-400 text-xs">Avg P/B Percentile</div>
                    <div class="text-white font-bold">P${metrics.avg_pb_percentile}</div>
                </div>
                <div class="bg-gray-900/30 rounded p-3 text-center">
                    <div class="text-gray-400 text-xs">Avg P/B</div>
                    <div class="text-white font-bold">${metrics.avg_pb}x</div>
                </div>
                <div class="bg-gray-900/30 rounded p-3 text-center">
                    <div class="text-gray-400 text-xs">CP rẻ (P<35)</div>
                    <div class="text-green-400 font-bold">${metrics.cheap_count}/${metrics.total_banks} (${metrics.cheap_percent}%)</div>
                </div>
                <div class="bg-gray-900/30 rounded p-3 text-center">
                    <div class="text-gray-400 text-xs">CP đắt (P>65)</div>
                    <div class="text-red-400 font-bold">${metrics.expensive_count}/${metrics.total_banks} (${metrics.expensive_percent}%)</div>
                </div>
            </div>
            
            <!-- Recommendations -->
            ${recs.length > 0 ? `
                <div class="border-t border-gray-700 pt-4 mb-4">
                    <div class="text-sm font-semibold text-gray-300 mb-2">💡 Khuyến nghị:</div>
                    ${recs.map(r => `
                        <div class="flex items-start gap-2 text-sm mb-1">
                            <span class="${r.priority === 'HIGH' ? 'text-red-400' : r.priority === 'MEDIUM' ? 'text-yellow-400' : 'text-gray-400'}">[${r.priority}]</span>
                            <span class="text-gray-300">${r.message}</span>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
            
            <!-- Historical Heat Chart -->
            <div class="border-t border-gray-700 pt-4">
                <div class="flex justify-between items-center mb-3">
                    <div class="text-sm font-semibold text-gray-300">📈 Lịch sử Nhiệt độ ngành (${sectorHeat.history?.length || 0} quý)</div>
                    <div class="text-xs text-gray-500">
                        🔥 Max: <span class="text-red-400 font-bold">${sectorHeat.analysis?.max_heat}</span> (${sectorHeat.analysis?.max_heat_period}) | 
                        ❄️ Min: <span class="text-blue-400 font-bold">${sectorHeat.analysis?.min_heat}</span> (${sectorHeat.analysis?.min_heat_period}) |
                        📊 Avg: <span class="text-yellow-400">${sectorHeat.analysis?.avg_heat}</span>
                    </div>
                </div>
                <div id="heat-history-chart" style="height: 300px; background: rgba(17,24,39,0.5); border-radius: 8px;"></div>
                
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
                                        <th class="py-2 px-2 text-right text-gray-400">Banks</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${(sectorHeat.history || []).slice().reverse().map(h => `
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
        </div>
    `;
    
    // Draw heat history chart after DOM is ready
    setTimeout(() => {
        drawHeatHistoryChart();
    }, 100);
}

function getHeatColor(heat) {
    if (heat >= 85) return '#EF4444';
    if (heat >= 70) return '#F97316';
    if (heat >= 55) return '#EAB308';
    if (heat >= 45) return '#22C55E';
    if (heat >= 35) return '#14B8A6';
    if (heat >= 20) return '#3B82F6';
    return '#8B5CF6';
}

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

function drawHeatHistoryChart() {
    if (!sectorHeat || !sectorHeat.history || sectorHeat.history.length === 0) return;
    
    const history = sectorHeat.history;
    const periods = history.map(h => h.period);
    const heatValues = history.map(h => h.heat_index);
    const avgPBs = history.map(h => h.avg_pb);
    
    // Color based on heat level
    const colors = heatValues.map(h => {
        if (h >= 85) return '#EF4444';
        if (h >= 70) return '#F97316';
        if (h >= 55) return '#EAB308';
        if (h >= 45) return '#22C55E';
        if (h >= 35) return '#14B8A6';
        if (h >= 20) return '#3B82F6';
        return '#8B5CF6';
    });
    
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
        annotations: [
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
        ]
    };
    
    Plotly.newPlot('heat-history-chart', [trace1, overheatedLine, hotLine, coldLine, iceColdLine], layout, { 
        responsive: true,
        displayModeBar: false
    });
}

function getSignalColor(signal) {
    const colors = {
        'SELL_ALL': 'text-red-500',
        'REDUCE': 'text-orange-400',
        'HOLD': 'text-yellow-400',
        'NORMAL': 'text-green-400',
        'ACCUMULATE': 'text-blue-400',
        'BUY': 'text-blue-500',
        'BUY_HEAVY': 'text-purple-500'
    };
    return colors[signal] || 'text-gray-400';
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
