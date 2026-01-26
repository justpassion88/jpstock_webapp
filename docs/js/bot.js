/**
 * JP Stock Webapp - BOT Dashboard
 * Hiển thị kết quả 5 BOT Trading
 */

let botResults = null;

async function loadBotResults() {
    try {
        const response = await fetch('data/bot_results.json');
        botResults = await response.json();
        displayBotComparison();
        displayBotDetails();
    } catch (error) {
        console.error('Error loading bot results:', error);
        document.getElementById('bot-comparison').innerHTML = `
            <div class="text-red-500 text-center py-8">
                <p>⚠️ Không thể tải dữ liệu BOT</p>
                <p class="text-sm mt-2">${error.message}</p>
            </div>
        `;
    }
}

function formatMoney(num) {
    if (num == null) return 'N/A';
    return new Intl.NumberFormat('vi-VN').format(Math.round(num));
}

function formatPercent(num, showSign = true) {
    if (num == null) return 'N/A';
    const sign = showSign && num > 0 ? '+' : '';
    return `${sign}${num.toFixed(1)}%`;
}

function getPerformanceClass(value, thresholds) {
    if (value >= thresholds.good) return 'text-green-400';
    if (value >= thresholds.ok) return 'text-yellow-400';
    return 'text-red-400';
}

function displayBotComparison() {
    const bots = Object.entries(botResults).sort((a, b) => {
        return (b[1].performance?.total_return_percent || 0) - (a[1].performance?.total_return_percent || 0);
    });
    
    let rows = bots.map(([botId, data], index) => {
        const perf = data.performance || {};
        const trades = data.trades || {};
        const config = data.config || {};
        
        const returnClass = getPerformanceClass(perf.total_return_percent || 0, {good: 100, ok: 50});
        const cagrClass = getPerformanceClass(perf.cagr_percent || 0, {good: 10, ok: 5});
        const ddClass = getPerformanceClass(-(perf.max_drawdown_percent || 0), {good: -20, ok: -30});
        const wrClass = getPerformanceClass(trades.win_rate_percent || 0, {good: 65, ok: 50});
        
        const medal = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : '';
        
        return `
            <tr class="border-b border-gray-700 hover:bg-gray-700/50">
                <td class="py-4 px-4">
                    <div class="flex items-center">
                        <span class="text-2xl mr-2">${medal}</span>
                        <div>
                            <div class="font-bold text-white">${data.bot_name || botId}</div>
                            <div class="text-xs text-gray-500">${data.bot_description?.substring(0, 40) || ''}...</div>
                        </div>
                    </div>
                </td>
                <td class="py-4 px-4 text-right">
                    <div class="${returnClass} font-bold text-xl">${formatPercent(perf.total_return_percent)}</div>
                    <div class="text-xs text-gray-500">${formatMoney(perf.final_value)}đ</div>
                </td>
                <td class="py-4 px-4 text-right">
                    <div class="${cagrClass} font-bold">${formatPercent(perf.cagr_percent)}</div>
                    <div class="text-xs text-gray-500">mỗi năm</div>
                </td>
                <td class="py-4 px-4 text-right">
                    <div class="${ddClass} font-bold">${formatPercent(-perf.max_drawdown_percent, false)}</div>
                </td>
                <td class="py-4 px-4 text-right">
                    <div class="${wrClass} font-bold">${formatPercent(trades.win_rate_percent, false)}</div>
                    <div class="text-xs text-gray-500">${trades.sell_trades || 0} trades</div>
                </td>
                <td class="py-4 px-4 text-right">
                    <div class="text-white font-bold">${(trades.profit_factor || 0).toFixed(2)}</div>
                </td>
                <td class="py-4 px-4 text-center">
                    <button onclick="showBotDetail('${botId}')" class="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm">
                        Chi tiết
                    </button>
                </td>
            </tr>
        `;
    }).join('');
    
    document.getElementById('bot-comparison').innerHTML = `
        <div class="bg-gray-800 rounded-lg p-6 mb-6">
            <h2 class="text-xl font-bold text-white mb-4">🏆 Bảng xếp hạng BOT (Backtest 2010-2024)</h2>
            <p class="text-gray-400 text-sm mb-4">
                Vốn ban đầu: <span class="text-white font-bold">100,000,000đ</span> | 
                Phí GD: 0.15% | Thuế bán: 0.1% | Lãi kép
            </p>
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead>
                        <tr class="border-b border-gray-600">
                            <th class="py-3 px-4 text-left text-gray-400">BOT</th>
                            <th class="py-3 px-4 text-right text-gray-400">Tổng Return</th>
                            <th class="py-3 px-4 text-right text-gray-400">CAGR</th>
                            <th class="py-3 px-4 text-right text-gray-400">Max DD</th>
                            <th class="py-3 px-4 text-right text-gray-400">Win Rate</th>
                            <th class="py-3 px-4 text-right text-gray-400">Profit Factor</th>
                            <th class="py-3 px-4 text-center text-gray-400">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rows}
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

function displayBotDetails() {
    const container = document.getElementById('bot-details');
    
    let cards = Object.entries(botResults).map(([botId, data]) => {
        const config = data.config || {};
        const positions = data.current_positions || [];
        
        let positionsHtml = positions.length > 0 ? positions.map(pos => `
            <div class="flex justify-between items-center bg-gray-900 rounded p-2 mb-1">
                <span class="font-bold text-white">${pos.symbol}</span>
                <span class="text-gray-400">${pos.quantity} CP @ ${formatMoney(pos.avg_price)}đ</span>
            </div>
        `).join('') : '<div class="text-gray-500 text-center py-2">Không có vị thế</div>';
        
        return `
            <div id="detail-${botId}" class="bg-gray-800 rounded-lg p-6 mb-4" style="display: none;">
                <h3 class="text-lg font-bold text-white mb-2">${data.bot_name}</h3>
                <p class="text-gray-400 text-sm mb-4">${data.bot_description}</p>
                
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div class="bg-gray-900 rounded p-3">
                        <div class="text-gray-500 text-xs">P/B Max Percentile</div>
                        <div class="text-white font-bold">P${config.pb_percentile_max}</div>
                    </div>
                    <div class="bg-gray-900 rounded p-3">
                        <div class="text-gray-500 text-xs">Min Win Rate</div>
                        <div class="text-white font-bold">${config.min_win_rate}%</div>
                    </div>
                    <div class="bg-gray-900 rounded p-3">
                        <div class="text-gray-500 text-xs">Take Profit</div>
                        <div class="text-green-400 font-bold">+${config.take_profit}%</div>
                    </div>
                    <div class="bg-gray-900 rounded p-3">
                        <div class="text-gray-500 text-xs">Stop Loss</div>
                        <div class="text-red-400 font-bold">-${config.stop_loss}%</div>
                    </div>
                </div>
                
                <div class="mb-4">
                    <h4 class="text-gray-300 font-semibold mb-2">📌 Vị thế hiện tại</h4>
                    ${positionsHtml}
                </div>
                
                <div id="chart-${botId}" style="height: 300px;"></div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = cards;
}

function showBotDetail(botId) {
    // Hide all details
    document.querySelectorAll('[id^="detail-"]').forEach(el => el.style.display = 'none');
    
    // Show selected
    const detail = document.getElementById(`detail-${botId}`);
    if (detail) {
        detail.style.display = 'block';
        
        // Draw chart
        const data = botResults[botId];
        drawEquityCurve(botId, data.equity_curve || []);
        
        // Scroll to detail
        detail.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function drawEquityCurve(botId, equityCurve) {
    if (!equityCurve || equityCurve.length === 0) return;
    
    const dates = equityCurve.map(e => e.date);
    const values = equityCurve.map(e => e.value);
    const returns = equityCurve.map(e => e.return);
    
    const trace1 = {
        x: dates,
        y: values,
        type: 'scatter',
        mode: 'lines',
        name: 'Portfolio Value',
        line: { color: '#3B82F6', width: 2 },
        fill: 'tozeroy',
        fillcolor: 'rgba(59, 130, 246, 0.1)'
    };
    
    // Add benchmark (initial capital)
    const benchmark = {
        x: [dates[0], dates[dates.length-1]],
        y: [100000000, 100000000],
        type: 'scatter',
        mode: 'lines',
        name: 'Vốn ban đầu',
        line: { color: '#6B7280', width: 1, dash: 'dash' }
    };
    
    const layout = {
        title: {
            text: 'Equity Curve',
            font: { color: '#fff', size: 14 }
        },
        paper_bgcolor: '#1f2937',
        plot_bgcolor: '#111827',
        font: { color: '#9ca3af' },
        xaxis: {
            gridcolor: '#374151',
            tickangle: -45
        },
        yaxis: {
            title: 'Giá trị (VND)',
            gridcolor: '#374151',
            tickformat: ',.0f'
        },
        legend: {
            x: 0,
            y: 1.1,
            orientation: 'h'
        },
        margin: { t: 40, b: 60 }
    };
    
    Plotly.newPlot(`chart-${botId}`, [trace1, benchmark], layout, { responsive: true });
}

// Initialize
document.addEventListener('DOMContentLoaded', loadBotResults);
