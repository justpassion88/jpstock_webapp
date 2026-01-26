/**
 * JP Stock Webapp - BOT Dashboard (Enhanced)
 * Hiển thị kết quả 5 BOT Trading với chi tiết Position Sizing & Trade History
 */

let botResults = null;
let selectedBot = null;

async function loadBotResults() {
    try {
        const response = await fetch('data/bot_results.json');
        botResults = await response.json();
        displayBotComparison();
        displayBotCards();
        
        // Auto-show first bot
        const firstBot = Object.keys(botResults)[0];
        if (firstBot) showBotDetail(firstBot);
        
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
        return (b[1].performance?.cagr_percent || 0) - (a[1].performance?.cagr_percent || 0);
    });
    
    let rows = bots.map(([botId, data], index) => {
        const perf = data.performance || {};
        const trades = data.trades || {};
        const sizing = data.position_sizing_summary || {};
        
        const returnClass = getPerformanceClass(perf.total_return_percent || 0, {good: 100, ok: 50});
        const cagrClass = getPerformanceClass(perf.cagr_percent || 0, {good: 8, ok: 5});
        const ddClass = getPerformanceClass(-(perf.max_drawdown_percent || 0), {good: -25, ok: -35});
        const wrClass = getPerformanceClass(trades.win_rate_percent || 0, {good: 60, ok: 50});
        
        const medal = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : '';
        
        return `
            <tr class="border-b border-gray-700 hover:bg-gray-700/50 cursor-pointer" onclick="showBotDetail('${botId}')">
                <td class="py-4 px-4">
                    <div class="flex items-center">
                        <span class="text-2xl mr-2">${medal}</span>
                        <div>
                            <div class="font-bold text-white">${data.bot_name || botId}</div>
                            <div class="text-xs text-gray-500">${data.bot_description?.substring(0, 50) || ''}...</div>
                        </div>
                    </div>
                </td>
                <td class="py-4 px-4 text-right">
                    <div class="${returnClass} font-bold text-lg">${formatPercent(perf.total_return_percent)}</div>
                    <div class="text-xs text-gray-500">${formatMoney(perf.final_value)}đ</div>
                </td>
                <td class="py-4 px-4 text-right">
                    <div class="${cagrClass} font-bold">${formatPercent(perf.cagr_percent)}</div>
                </td>
                <td class="py-4 px-4 text-right">
                    <div class="${ddClass} font-bold">${formatPercent(-perf.max_drawdown_percent, false)}</div>
                </td>
                <td class="py-4 px-4 text-right">
                    <div class="text-white font-bold">${trades.total_trades || 0}</div>
                    <div class="text-xs text-gray-500">${trades.buy_trades || 0}B / ${trades.sell_trades || 0}S</div>
                </td>
                <td class="py-4 px-4 text-right">
                    <div class="${wrClass} font-bold">${formatPercent(trades.win_rate_percent, false)}</div>
                </td>
                <td class="py-4 px-4 text-right">
                    <div class="text-cyan-400 font-bold">${(sizing.avg_allocation || 0).toFixed(1)}%</div>
                    <div class="text-xs text-gray-500">${sizing.method || 'equal'}</div>
                </td>
            </tr>
        `;
    }).join('');
    
    document.getElementById('bot-comparison').innerHTML = `
        <div class="bg-gray-800 rounded-lg p-6 mb-6">
            <h2 class="text-xl font-bold text-white mb-4">🏆 Bảng xếp hạng BOT (Backtest 2010-2024)</h2>
            <p class="text-gray-400 text-sm mb-4">
                Vốn ban đầu: <span class="text-white font-bold">100,000,000đ</span> | 
                Phí GD: 0.15% | Thuế bán: 0.1% | 
                <span class="text-cyan-400">Lãi kép (compound returns)</span> | 
                Click vào BOT để xem chi tiết
            </p>
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead>
                        <tr class="border-b border-gray-600">
                            <th class="py-3 px-4 text-left text-gray-400">BOT</th>
                            <th class="py-3 px-4 text-right text-gray-400">Tổng Return</th>
                            <th class="py-3 px-4 text-right text-gray-400">CAGR</th>
                            <th class="py-3 px-4 text-right text-gray-400">Max DD</th>
                            <th class="py-3 px-4 text-right text-gray-400">Trades</th>
                            <th class="py-3 px-4 text-right text-gray-400">Win Rate</th>
                            <th class="py-3 px-4 text-right text-gray-400">Avg Position</th>
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

function displayBotCards() {
    const container = document.getElementById('bot-details');
    container.innerHTML = `
        <div id="bot-detail-content"></div>
        <div id="trade-history-section"></div>
    `;
}

function showBotDetail(botId) {
    selectedBot = botId;
    const data = botResults[botId];
    if (!data) return;
    
    const config = data.config || {};
    const perf = data.performance || {};
    const trades = data.trades || {};
    const sizing = data.position_sizing_summary || {};
    const analysis = data.trade_analysis || {};
    const positions = data.current_positions || [];
    const detailedTrades = data.detailed_trades || [];
    
    const detailHtml = `
        <div class="bg-gray-800 rounded-lg p-6 mb-6">
            <div class="flex justify-between items-start mb-6">
                <div>
                    <h2 class="text-2xl font-bold text-white">${data.bot_name}</h2>
                    <p class="text-gray-400">${data.bot_description}</p>
                </div>
                <div class="text-right">
                    <div class="text-3xl font-bold ${perf.total_return_percent >= 0 ? 'text-green-400' : 'text-red-400'}">
                        ${formatPercent(perf.total_return_percent)}
                    </div>
                    <div class="text-gray-500">CAGR: ${formatPercent(perf.cagr_percent)}</div>
                </div>
            </div>
            
            <!-- Config Parameters -->
            <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3 mb-6">
                <div class="bg-gray-900 rounded p-3">
                    <div class="text-gray-500 text-xs">P/B Max Percentile</div>
                    <div class="text-white font-bold">P${config.pb_percentile_max}</div>
                </div>
                <div class="bg-gray-900 rounded p-3">
                    <div class="text-gray-500 text-xs">Min Win Rate</div>
                    <div class="text-white font-bold">${config.min_win_rate}%</div>
                </div>
                <div class="bg-gray-900 rounded p-3">
                    <div class="text-gray-500 text-xs">Min Expected Return</div>
                    <div class="text-white font-bold">${config.min_expected_return}%</div>
                </div>
                <div class="bg-gray-900 rounded p-3">
                    <div class="text-gray-500 text-xs">Take Profit</div>
                    <div class="text-green-400 font-bold">+${config.take_profit}%</div>
                </div>
                <div class="bg-gray-900 rounded p-3">
                    <div class="text-gray-500 text-xs">Stop Loss</div>
                    <div class="text-red-400 font-bold">-${config.stop_loss}%</div>
                </div>
                <div class="bg-gray-900 rounded p-3">
                    <div class="text-gray-500 text-xs">Max Positions</div>
                    <div class="text-white font-bold">${config.max_positions}</div>
                </div>
            </div>
            
            <!-- Position Sizing Section -->
            <div class="bg-gradient-to-r from-cyan-900/30 to-blue-900/30 rounded-lg p-4 mb-6">
                <h3 class="text-lg font-bold text-cyan-400 mb-3">💰 Position Sizing - Cách chia vốn</h3>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                        <div class="text-gray-400 text-sm">Phương pháp</div>
                        <div class="text-white font-bold capitalize">${sizing.method || config.position_sizing_method || 'equal'}</div>
                    </div>
                    <div>
                        <div class="text-gray-400 text-sm">TB mỗi vị thế</div>
                        <div class="text-cyan-400 font-bold text-xl">${(sizing.avg_allocation || 0).toFixed(1)}%</div>
                    </div>
                    <div>
                        <div class="text-gray-400 text-sm">Vị thế nhỏ nhất</div>
                        <div class="text-white font-bold">${(sizing.min_allocation || 0).toFixed(1)}%</div>
                    </div>
                    <div>
                        <div class="text-gray-400 text-sm">Vị thế lớn nhất</div>
                        <div class="text-white font-bold">${(sizing.max_allocation || 0).toFixed(1)}%</div>
                    </div>
                </div>
                
                <!-- Heat Allocation Map -->
                ${sizing.heat_allocation_map && Object.keys(sizing.heat_allocation_map).length > 0 ? `
                <div class="mt-4 p-3 bg-gray-900/50 rounded">
                    <h4 class="text-sm font-bold text-orange-400 mb-2">🌡️ Heat-Aware Allocation</h4>
                    <p class="text-gray-400 text-xs mb-2">Điều chỉnh vị thế dựa trên nhiệt độ ngành ngân hàng:</p>
                    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2">
                        ${Object.entries(sizing.heat_allocation_map).map(([level, info]) => {
                            const colors = {
                                'ICE_COLD': 'bg-purple-600',
                                'COLD': 'bg-blue-600',
                                'COOL': 'bg-teal-600',
                                'NEUTRAL': 'bg-green-600',
                                'WARM': 'bg-yellow-600',
                                'HOT': 'bg-orange-600',
                                'OVERHEATED': 'bg-red-600'
                            };
                            const icons = {
                                'ICE_COLD': '🥶',
                                'COLD': '❄️',
                                'COOL': '🌤️',
                                'NEUTRAL': '😐',
                                'WARM': '☀️',
                                'HOT': '🌡️',
                                'OVERHEATED': '🔥'
                            };
                            return `
                            <div class="${colors[level] || 'bg-gray-600'} bg-opacity-30 rounded p-2 text-center">
                                <div class="text-lg">${icons[level] || ''}</div>
                                <div class="text-white text-xs font-bold">${level}</div>
                                <div class="text-cyan-300 text-sm font-bold">${(info.multiplier * 100).toFixed(0)}%</div>
                                <div class="text-gray-400 text-xs">Cash: ${info.cash_reserve}%</div>
                            </div>
                        `}).join('')}
                    </div>
                    <p class="text-gray-500 text-xs mt-2">
                        📊 Khi ngành <span class="text-blue-400">lạnh</span> → Mua mạnh hơn | 
                        Khi ngành <span class="text-red-400">nóng</span> → Giảm vị thế, giữ cash
                    </p>
                </div>
                ` : `
                <div class="mt-3 p-3 bg-gray-800/50 rounded">
                    <p class="text-gray-300 text-sm">
                        ${sizing.method === 'kelly' ? 
                            '🎲 <b>Kelly Criterion</b>: Chia vốn theo công thức Kelly dựa trên xác suất thắng và kỳ vọng return của mỗi zone P/B.' :
                            '⚖️ <b>Equal Weight</b>: Chia đều vốn cho tối đa ' + config.max_positions + ' vị thế.'
                        }
                    </p>
                </div>
                `}
            </div>
            
            <!-- Trade Analysis Section -->
            <div class="bg-gradient-to-r from-purple-900/30 to-pink-900/30 rounded-lg p-4 mb-6">
                <h3 class="text-lg font-bold text-purple-400 mb-3">📊 Trade Analysis</h3>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                        <div class="text-gray-400 text-sm">Tổng giao dịch</div>
                        <div class="text-white font-bold text-xl">${trades.total_trades || 0}</div>
                        <div class="text-gray-500 text-xs">${trades.buy_trades || 0} mua / ${trades.sell_trades || 0} bán</div>
                    </div>
                    <div>
                        <div class="text-gray-400 text-sm">Win Rate</div>
                        <div class="${(trades.win_rate_percent || 0) >= 60 ? 'text-green-400' : 'text-yellow-400'} font-bold text-xl">${formatPercent(trades.win_rate_percent, false)}</div>
                        <div class="text-gray-500 text-xs">${analysis.wins || 0} thắng / ${analysis.losses || 0} thua</div>
                    </div>
                    <div>
                        <div class="text-gray-400 text-sm">Avg Win</div>
                        <div class="text-green-400 font-bold">+${formatMoney(analysis.avg_win_pnl || 0)}đ</div>
                        <div class="text-gray-500 text-xs">${(analysis.avg_win_percent || 0).toFixed(1)}%</div>
                    </div>
                    <div>
                        <div class="text-gray-400 text-sm">Avg Loss</div>
                        <div class="text-red-400 font-bold">${formatMoney(analysis.avg_loss_pnl || 0)}đ</div>
                        <div class="text-gray-500 text-xs">${(analysis.avg_loss_percent || 0).toFixed(1)}%</div>
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-4 mt-4">
                    <div>
                        <div class="text-gray-400 text-sm">Lãi lớn nhất</div>
                        <div class="text-green-400 font-bold">+${formatMoney(analysis.largest_win || 0)}đ</div>
                    </div>
                    <div>
                        <div class="text-gray-400 text-sm">Lỗ lớn nhất</div>
                        <div class="text-red-400 font-bold">${formatMoney(analysis.largest_loss || 0)}đ</div>
                    </div>
                </div>
            </div>
            
            <!-- Current Positions -->
            <div class="mb-6">
                <h3 class="text-lg font-bold text-white mb-3">📌 Vị thế hiện tại (${positions.length})</h3>
                ${positions.length > 0 ? `
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                        ${positions.map(pos => {
                            const unrealizedPnl = ((pos.current_price || pos.avg_price) / pos.avg_price - 1) * 100;
                            return `
                            <div class="bg-gray-900 rounded-lg p-4">
                                <div class="flex justify-between items-center mb-2">
                                    <span class="font-bold text-white text-lg">${pos.symbol}</span>
                                    <span class="${unrealizedPnl >= 0 ? 'text-green-400' : 'text-red-400'} font-bold">
                                        ${unrealizedPnl >= 0 ? '+' : ''}${unrealizedPnl.toFixed(1)}%
                                    </span>
                                </div>
                                <div class="text-sm text-gray-400">
                                    <div class="flex justify-between">
                                        <span>Số lượng:</span>
                                        <span class="text-white">${formatMoney(pos.quantity)} CP</span>
                                    </div>
                                    <div class="flex justify-between">
                                        <span>Giá mua:</span>
                                        <span class="text-white">${formatMoney(pos.avg_price)}đ</span>
                                    </div>
                                    <div class="flex justify-between">
                                        <span>P/B lúc mua:</span>
                                        <span class="text-cyan-400">${(pos.buy_pb || 0).toFixed(2)}</span>
                                    </div>
                                    <div class="flex justify-between">
                                        <span>Heat lúc mua:</span>
                                        <span class="text-orange-400">${(pos.buy_heat || 0).toFixed(0)}</span>
                                    </div>
                                    <div class="flex justify-between">
                                        <span>Ngày mua:</span>
                                        <span class="text-gray-300">${pos.buy_date || 'N/A'}</span>
                                    </div>
                                </div>
                            </div>
                        `}).join('')}
                    </div>
                ` : '<div class="text-gray-500 text-center py-4 bg-gray-900 rounded">Không có vị thế đang nắm giữ</div>'}
            </div>
            
            <!-- Equity Curve Chart -->
            <div id="equity-chart" style="height: 350px;"></div>
        </div>
    `;
    
    document.getElementById('bot-detail-content').innerHTML = detailHtml;
    displayTradeHistory(detailedTrades);
    drawEquityCurve(data.equity_curve || []);
    document.getElementById('bot-detail-content').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function displayTradeHistory(detailedTrades) {
    if (!detailedTrades || detailedTrades.length === 0) {
        document.getElementById('trade-history-section').innerHTML = '';
        return;
    }
    
    const sortedTrades = [...detailedTrades].reverse();
    const buyTrades = sortedTrades.filter(t => t.action === 'BUY');
    const sellTrades = sortedTrades.filter(t => t.action === 'SELL');
    
    const html = `
        <div class="bg-gray-800 rounded-lg p-6 mb-6">
            <h3 class="text-xl font-bold text-white mb-4">📜 Lịch sử giao dịch đầy đủ</h3>
            
            <div class="flex mb-4 border-b border-gray-700">
                <button onclick="showTradeTab('all')" id="tab-all" class="px-4 py-2 text-gray-400 hover:text-white border-b-2 border-transparent">
                    Tất cả (${sortedTrades.length})
                </button>
                <button onclick="showTradeTab('buy')" id="tab-buy" class="px-4 py-2 text-gray-400 hover:text-white border-b-2 border-transparent">
                    Mua (${buyTrades.length})
                </button>
                <button onclick="showTradeTab('sell')" id="tab-sell" class="px-4 py-2 text-gray-400 hover:text-white border-b-2 border-transparent">
                    Bán (${sellTrades.length})
                </button>
            </div>
            
            <div id="trades-all" class="trade-table hidden">
                <div class="overflow-x-auto max-h-96 overflow-y-auto">
                    <table class="w-full text-sm">
                        <thead class="sticky top-0 bg-gray-800">
                            <tr class="border-b border-gray-600">
                                <th class="py-2 px-3 text-left text-gray-400">Ngày</th>
                                <th class="py-2 px-3 text-left text-gray-400">Mã</th>
                                <th class="py-2 px-3 text-center text-gray-400">Loại</th>
                                <th class="py-2 px-3 text-right text-gray-400">SL</th>
                                <th class="py-2 px-3 text-right text-gray-400">Giá</th>
                                <th class="py-2 px-3 text-right text-gray-400">P/B</th>
                                <th class="py-2 px-3 text-right text-gray-400">Heat</th>
                                <th class="py-2 px-3 text-right text-gray-400">P&L</th>
                                <th class="py-2 px-3 text-left text-gray-400">Lý do</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${sortedTrades.map(t => renderTradeRow(t)).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div id="trades-buy" class="trade-table hidden">
                <div class="overflow-x-auto max-h-96 overflow-y-auto">
                    <table class="w-full text-sm">
                        <thead class="sticky top-0 bg-gray-800">
                            <tr class="border-b border-gray-600">
                                <th class="py-2 px-3 text-left text-gray-400">Ngày</th>
                                <th class="py-2 px-3 text-left text-gray-400">Mã</th>
                                <th class="py-2 px-3 text-right text-gray-400">SL</th>
                                <th class="py-2 px-3 text-right text-gray-400">Giá mua</th>
                                <th class="py-2 px-3 text-right text-gray-400">P/B</th>
                                <th class="py-2 px-3 text-right text-gray-400">P/B %ile</th>
                                <th class="py-2 px-3 text-right text-gray-400">Tỷ trọng</th>
                                <th class="py-2 px-3 text-right text-gray-400">Zone WR</th>
                                <th class="py-2 px-3 text-left text-gray-400">Lý do</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${buyTrades.map(t => `
                                <tr class="border-b border-gray-700 hover:bg-gray-700/50">
                                    <td class="py-2 px-3 text-gray-300">${t.date}</td>
                                    <td class="py-2 px-3 font-bold text-white">${t.symbol}</td>
                                    <td class="py-2 px-3 text-right text-white">${formatMoney(t.quantity)}</td>
                                    <td class="py-2 px-3 text-right text-white">${formatMoney(t.price)}đ</td>
                                    <td class="py-2 px-3 text-right text-cyan-400">${(t.pb || 0).toFixed(2)}</td>
                                    <td class="py-2 px-3 text-right text-gray-400">P${(t.pb_percentile || 0).toFixed(0)}</td>
                                    <td class="py-2 px-3 text-right text-yellow-400">${(t.allocation_percent || 0).toFixed(1)}%</td>
                                    <td class="py-2 px-3 text-right text-green-400">${(t.zone_win_rate || 0).toFixed(0)}%</td>
                                    <td class="py-2 px-3 text-gray-400 text-xs">${t.reason || '-'}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div id="trades-sell" class="trade-table hidden">
                <div class="overflow-x-auto max-h-96 overflow-y-auto">
                    <table class="w-full text-sm">
                        <thead class="sticky top-0 bg-gray-800">
                            <tr class="border-b border-gray-600">
                                <th class="py-2 px-3 text-left text-gray-400">Ngày bán</th>
                                <th class="py-2 px-3 text-left text-gray-400">Mã</th>
                                <th class="py-2 px-3 text-right text-gray-400">SL</th>
                                <th class="py-2 px-3 text-right text-gray-400">Giá mua</th>
                                <th class="py-2 px-3 text-right text-gray-400">Giá bán</th>
                                <th class="py-2 px-3 text-right text-gray-400">P/B mua</th>
                                <th class="py-2 px-3 text-right text-gray-400">P/B bán</th>
                                <th class="py-2 px-3 text-right text-gray-400">P&L</th>
                                <th class="py-2 px-3 text-right text-gray-400">%</th>
                                <th class="py-2 px-3 text-left text-gray-400">Lý do</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${sellTrades.map(t => `
                                <tr class="border-b border-gray-700 hover:bg-gray-700/50">
                                    <td class="py-2 px-3 text-gray-300">${t.date}</td>
                                    <td class="py-2 px-3 font-bold text-white">${t.symbol}</td>
                                    <td class="py-2 px-3 text-right text-white">${formatMoney(t.quantity)}</td>
                                    <td class="py-2 px-3 text-right text-gray-400">${formatMoney(t.buy_price || 0)}đ</td>
                                    <td class="py-2 px-3 text-right text-white">${formatMoney(t.sell_price || 0)}đ</td>
                                    <td class="py-2 px-3 text-right text-cyan-400">${(t.buy_pb || 0).toFixed(2)}</td>
                                    <td class="py-2 px-3 text-right text-cyan-400">${(t.sell_pb || 0).toFixed(2)}</td>
                                    <td class="py-2 px-3 text-right ${(t.pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'} font-bold">
                                        ${(t.pnl || 0) >= 0 ? '+' : ''}${formatMoney(t.pnl || 0)}đ
                                    </td>
                                    <td class="py-2 px-3 text-right ${(t.pnl_percent || 0) >= 0 ? 'text-green-400' : 'text-red-400'} font-bold">
                                        ${(t.pnl_percent || 0) >= 0 ? '+' : ''}${(t.pnl_percent || 0).toFixed(1)}%
                                    </td>
                                    <td class="py-2 px-3 text-gray-400 text-xs">${t.reason || '-'}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('trade-history-section').innerHTML = html;
    showTradeTab('all');
}

function renderTradeRow(t) {
    const isBuy = t.action === 'BUY';
    const pnl = t.pnl || 0;
    const pnlPercent = t.pnl_percent || 0;
    const heat = t.heat || 50;
    
    const heatColor = heat >= 70 ? 'text-red-400' : heat >= 55 ? 'text-yellow-400' : heat >= 35 ? 'text-green-400' : 'text-blue-400';
    
    return `
        <tr class="border-b border-gray-700 hover:bg-gray-700/50">
            <td class="py-2 px-3 text-gray-300">${t.date}</td>
            <td class="py-2 px-3 font-bold text-white">${t.symbol}</td>
            <td class="py-2 px-3 text-center">
                <span class="${isBuy ? 'bg-green-600' : 'bg-red-600'} px-2 py-1 rounded text-xs font-bold">
                    ${isBuy ? 'MUA' : 'BÁN'}
                </span>
            </td>
            <td class="py-2 px-3 text-right text-white">${formatMoney(t.quantity)}</td>
            <td class="py-2 px-3 text-right text-white">${formatMoney(t.price || t.sell_price)}đ</td>
            <td class="py-2 px-3 text-right text-cyan-400">${(t.pb || t.sell_pb || 0).toFixed(2)}</td>
            <td class="py-2 px-3 text-right ${heatColor} font-bold">${heat.toFixed(0)}</td>
            <td class="py-2 px-3 text-right ${pnl >= 0 ? 'text-green-400' : 'text-red-400'} font-bold">
                ${!isBuy ? (pnl >= 0 ? '+' : '') + formatMoney(pnl) + 'đ (' + (pnlPercent >= 0 ? '+' : '') + pnlPercent.toFixed(1) + '%)' : '-'}
            </td>
            <td class="py-2 px-3 text-gray-400 text-xs max-w-xs truncate">${t.reason || '-'}</td>
        </tr>
    `;
}

function showTradeTab(tab) {
    document.querySelectorAll('.trade-table').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('[id^="tab-"]').forEach(el => {
        el.classList.remove('text-white', 'border-blue-500');
        el.classList.add('text-gray-400', 'border-transparent');
    });
    
    document.getElementById(`trades-${tab}`).classList.remove('hidden');
    const activeTab = document.getElementById(`tab-${tab}`);
    activeTab.classList.remove('text-gray-400', 'border-transparent');
    activeTab.classList.add('text-white', 'border-blue-500');
}

function drawEquityCurve(equityCurve) {
    if (!equityCurve || equityCurve.length === 0) return;
    
    const dates = equityCurve.map(e => e.date);
    const values = equityCurve.map(e => e.value);
    const heats = equityCurve.map(e => e.heat || 50);
    
    const trace1 = {
        x: dates,
        y: values,
        type: 'scatter',
        mode: 'lines',
        name: 'Portfolio Value',
        line: { color: '#3B82F6', width: 2 },
        fill: 'tozeroy',
        fillcolor: 'rgba(59, 130, 246, 0.1)',
        yaxis: 'y'
    };
    
    const trace2 = {
        x: dates,
        y: heats,
        type: 'scatter',
        mode: 'lines',
        name: 'Heat Index',
        line: { color: '#F97316', width: 1, dash: 'dot' },
        yaxis: 'y2'
    };
    
    const benchmark = {
        x: [dates[0], dates[dates.length-1]],
        y: [1000000000, 1000000000],
        type: 'scatter',
        mode: 'lines',
        name: 'Vốn ban đầu (1B)',
        line: { color: '#6B7280', width: 1, dash: 'dash' },
        yaxis: 'y'
    };
    
    const layout = {
        title: {
            text: 'Equity Curve + Sector Heat Index',
            font: { color: '#fff', size: 14 }
        },
        paper_bgcolor: '#1f2937',
        plot_bgcolor: '#111827',
        font: { color: '#9ca3af' },
        xaxis: { gridcolor: '#374151', tickangle: -45 },
        yaxis: { 
            title: 'Giá trị (VND)', 
            gridcolor: '#374151', 
            tickformat: ',.0f',
            side: 'left'
        },
        yaxis2: {
            title: 'Heat Index',
            overlaying: 'y',
            side: 'right',
            range: [0, 100],
            tickcolor: '#F97316',
            titlefont: { color: '#F97316' },
            tickfont: { color: '#F97316' }
        },
        legend: { x: 0, y: 1.15, orientation: 'h' },
        margin: { t: 50, b: 60 },
        shapes: [
            // Hot zone
            {
                type: 'rect',
                xref: 'paper',
                yref: 'y2',
                x0: 0,
                x1: 1,
                y0: 70,
                y1: 100,
                fillcolor: 'rgba(239, 68, 68, 0.1)',
                line: { width: 0 }
            },
            // Cold zone
            {
                type: 'rect',
                xref: 'paper',
                yref: 'y2',
                x0: 0,
                x1: 1,
                y0: 0,
                y1: 35,
                fillcolor: 'rgba(59, 130, 246, 0.1)',
                line: { width: 0 }
            }
        ]
    };
    
    Plotly.newPlot('equity-chart', [trace1, trace2, benchmark], layout, { responsive: true });
}

document.addEventListener('DOMContentLoaded', loadBotResults);
