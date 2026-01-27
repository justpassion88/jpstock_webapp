/**
 * JP Stock Webapp - Stock Detail V2
 * Hiển thị chi tiết với Historical Backtest
 */

let stockData = null;

// Get symbol from URL
function getSymbol() {
    const params = new URLSearchParams(window.location.search);
    return params.get('symbol') || 'VCB';
}

// Sector to file mapping
const sectorFiles = {
    'banks': 'banks_v2.json',
    'realestate': 'realestate.json',
    'securities': 'securities.json',
    'retail': 'retail.json',
    'construction': 'construction.json',
    'energy': 'energy.json',
    'steel': 'steel.json',
    'technology': 'technology.json',
    'oilgas': 'oilgas.json',
    'insurance': 'insurance.json',
    'chemicals': 'chemicals.json'
};

// Fetch stock data
async function loadStock() {
    const symbol = getSymbol();
    
    try {
        // Try to find stock in all sector files
        let found = false;
        
        for (const [sector, filename] of Object.entries(sectorFiles)) {
            try {
                const response = await fetch(`data/${filename}`);
                if (!response.ok) continue;
                
                const data = await response.json();
                
                // Handle different JSON structures
                let stocksData = null;
                
                // Format 1: { "banks": { "VCB": {...}, "BID": {...} } } (banks_v2.json)
                if (data.banks && data.banks[symbol]) {
                    stocksData = data.banks[symbol];
                }
                // Format 2: { "stocks": { "HPG": {...} }, "sector_id": "steel", ... } (other sectors)
                else if (data.stocks && data.stocks[symbol]) {
                    stocksData = data.stocks[symbol];
                }
                // Format 3: { "realestate": { "VHM": {...} } } (if first key is sector name)
                else {
                    const firstKey = Object.keys(data)[0];
                    if (data[firstKey] && typeof data[firstKey] === 'object' && data[firstKey][symbol]) {
                        stocksData = data[firstKey][symbol];
                    }
                }
                
                if (stocksData) {
                    stockData = stocksData;
                    found = true;
                    break;
                }
            } catch (e) {
                continue;
            }
        }
        
        if (!found) {
            throw new Error(`Không tìm thấy dữ liệu cho ${symbol}`);
        }
        
        displayStockHeader();
        displayValuation();
        displayHistoricalReturns();
        displayPBChart();
        displayQuarterlyTable();
        
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('stock-header').innerHTML = `
            <div class="text-red-500 text-center py-8">
                <p class="text-xl">⚠️ ${error.message}</p>
            </div>
        `;
    }
}

// Display stock header
function displayStockHeader() {
    const valuation = stockData.valuation || {};
    const zoneColor = valuation.color || '#6b7280';
    const stats = stockData.pb_statistics || {};
    
    document.getElementById('stock-header').innerHTML = `
        <div class="bg-gray-800 rounded-lg p-6 mb-6">
            <div class="flex flex-wrap items-center justify-between mb-4">
                <div>
                    <h1 class="text-3xl font-bold text-white">${stockData.symbol}</h1>
                    <p class="text-gray-400">${stockData.name}</p>
                </div>
                <div class="text-right">
                    <span class="px-4 py-2 rounded-lg text-lg font-bold" 
                          style="background-color: ${zoneColor}25; color: ${zoneColor}; border: 2px solid ${zoneColor}">
                        ${valuation.zone_vi || 'N/A'}
                    </span>
                </div>
            </div>
            
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="bg-gray-900 rounded-lg p-4">
                    <div class="text-gray-500 text-sm">Giá hiện tại</div>
                    <div class="text-2xl font-bold text-white">${stockData.current_price ? (stockData.current_price * 1000).toLocaleString('vi-VN') : 'N/A'}đ</div>
                </div>
                <div class="bg-gray-900 rounded-lg p-4">
                    <div class="text-gray-500 text-sm">P/B hiện tại</div>
                    <div class="text-2xl font-bold text-white">${stockData.current_pb?.toFixed(2) || 'N/A'}</div>
                </div>
                <div class="bg-gray-900 rounded-lg p-4">
                    <div class="text-gray-500 text-sm">Percentile</div>
                    <div class="text-2xl font-bold" style="color: ${zoneColor}">P${valuation.percentile?.toFixed(0) || 'N/A'}</div>
                </div>
                <div class="bg-gray-900 rounded-lg p-4">
                    <div class="text-gray-500 text-sm">P/B trung bình</div>
                    <div class="text-2xl font-bold text-white">${stats.mean?.toFixed(2) || 'N/A'}</div>
                </div>
            </div>
        </div>
    `;
}

// Display valuation and expected returns
function displayValuation() {
    const expectedReturn = stockData.expected_return || {};
    const risk = stockData.risk || {};
    const valuation = stockData.valuation || {};
    
    const return1y = expectedReturn.expected_1y;
    const return1yClass = (return1y || 0) >= 20 ? 'text-green-400' : 
                          (return1y || 0) >= 0 ? 'text-yellow-400' : 'text-red-400';
    
    document.getElementById('valuation-section').innerHTML = `
        <div class="bg-gray-800 rounded-lg p-6 mb-6">
            <h2 class="text-xl font-bold text-white mb-4">📊 Phân tích định giá</h2>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <h3 class="text-lg text-gray-300 mb-3">Kỳ vọng lợi nhuận (từ Backtest)</h3>
                    <div class="space-y-3">
                        <div class="flex justify-between items-center bg-gray-900 rounded p-3">
                            <span class="text-gray-400">Lợi nhuận kỳ vọng 1 năm</span>
                            <span class="${return1yClass} font-bold text-xl">
                                ${return1y != null ? `${return1y > 0 ? '+' : ''}${return1y.toFixed(1)}%` : 'N/A'}
                            </span>
                        </div>
                        <div class="flex justify-between items-center bg-gray-900 rounded p-3">
                            <span class="text-gray-400">Median 1 năm</span>
                            <span class="text-white font-bold">
                                ${expectedReturn.expected_1y_median != null ? `${expectedReturn.expected_1y_median > 0 ? '+' : ''}${expectedReturn.expected_1y_median.toFixed(1)}%` : 'N/A'}
                            </span>
                        </div>
                        <div class="flex justify-between items-center bg-gray-900 rounded p-3">
                            <span class="text-gray-400">Tỷ lệ thắng 1 năm</span>
                            <span class="${(expectedReturn.win_rate_1y || 0) >= 70 ? 'text-green-400' : 'text-yellow-400'} font-bold text-xl">
                                ${expectedReturn.win_rate_1y?.toFixed(0) || 'N/A'}%
                            </span>
                        </div>
                        <div class="flex justify-between items-center bg-gray-900 rounded p-3">
                            <span class="text-gray-400">Số mẫu backtest</span>
                            <span class="text-white">${expectedReturn.sample_count || 'N/A'} quý</span>
                        </div>
                    </div>
                </div>
                
                <div>
                    <h3 class="text-lg text-gray-300 mb-3">Đánh giá rủi ro</h3>
                    <div class="space-y-3">
                        <div class="flex justify-between items-center bg-gray-900 rounded p-3">
                            <span class="text-gray-400">Mức rủi ro</span>
                            <span class="${risk.level === 'LOW' ? 'text-green-400' : risk.level === 'MEDIUM' ? 'text-yellow-400' : 'text-red-400'} font-bold">
                                ${risk.level_vi || 'N/A'}
                            </span>
                        </div>
                        <div class="flex justify-between items-center bg-gray-900 rounded p-3">
                            <span class="text-gray-400">Điểm rủi ro</span>
                            <span class="text-white">${risk.score || 'N/A'}/10</span>
                        </div>
                        <div class="bg-gray-900 rounded p-3">
                            <span class="text-gray-400 text-sm">${risk.description || ''}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Display historical returns by zone
function displayHistoricalReturns() {
    const returns = stockData.historical_returns || {};
    
    const zones = [
        { key: 'extremely_cheap', name: 'Cực rẻ', color: '#10B981' },
        { key: 'cheap', name: 'Rẻ', color: '#34D399' },
        { key: 'fair', name: 'Hợp lý', color: '#FBBF24' },
        { key: 'expensive', name: 'Đắt', color: '#F97316' },
        { key: 'extremely_expensive', name: 'Cực đắt', color: '#EF4444' }
    ];
    
    let tableRows = '';
    
    zones.forEach(zone => {
        const data = returns[zone.key];
        if (data) {
            const returnClass = (data.return_1y_avg || 0) >= 20 ? 'text-green-400' : 
                              (data.return_1y_avg || 0) >= 0 ? 'text-yellow-400' : 'text-red-400';
            const winClass = (data.win_rate_1y || 0) >= 70 ? 'text-green-400' : 
                           (data.win_rate_1y || 0) >= 50 ? 'text-yellow-400' : 'text-red-400';
            
            tableRows += `
                <tr class="border-b border-gray-700">
                    <td class="py-3 px-4">
                        <span class="px-2 py-1 rounded text-sm font-bold" style="background-color: ${zone.color}25; color: ${zone.color}">
                            ${zone.name}
                        </span>
                    </td>
                    <td class="py-3 px-4 text-white">${data.pb_min?.toFixed(2)} - ${data.pb_max?.toFixed(2)}</td>
                    <td class="py-3 px-4 text-white text-center">${data.count}</td>
                    <td class="py-3 px-4 ${returnClass} font-bold text-center">
                        ${data.return_1y_avg != null ? `${data.return_1y_avg > 0 ? '+' : ''}${data.return_1y_avg.toFixed(1)}%` : 'N/A'}
                    </td>
                    <td class="py-3 px-4 ${winClass} font-bold text-center">
                        ${data.win_rate_1y?.toFixed(0) || 'N/A'}%
                    </td>
                    <td class="py-3 px-4 text-gray-400 text-center">
                        ${data.return_2y_avg != null ? `${data.return_2y_avg > 0 ? '+' : ''}${data.return_2y_avg.toFixed(1)}%` : 'N/A'}
                    </td>
                </tr>
            `;
        }
    });
    
    document.getElementById('historical-returns').innerHTML = `
        <div class="bg-gray-800 rounded-lg p-6 mb-6">
            <h2 class="text-xl font-bold text-white mb-4">📈 Lợi nhuận lịch sử theo vùng P/B (Backtest)</h2>
            <p class="text-gray-400 text-sm mb-4">
                Dữ liệu thống kê từ ${stockData.pb_statistics?.years_of_data?.toFixed(1) || 'N/A'} năm lịch sử, 
                cho thấy lợi nhuận thực tế khi mua ở các vùng P/B khác nhau.
            </p>
            
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead>
                        <tr class="border-b border-gray-600">
                            <th class="py-3 px-4 text-left text-gray-400">Vùng P/B</th>
                            <th class="py-3 px-4 text-left text-gray-400">Khoảng P/B</th>
                            <th class="py-3 px-4 text-center text-gray-400">Số quý</th>
                            <th class="py-3 px-4 text-center text-gray-400">LN 1 năm</th>
                            <th class="py-3 px-4 text-center text-gray-400">Win Rate 1Y</th>
                            <th class="py-3 px-4 text-center text-gray-400">LN 2 năm</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${tableRows || '<tr><td colspan="6" class="py-4 text-center text-gray-500">Chưa có dữ liệu</td></tr>'}
                    </tbody>
                </table>
            </div>
            
            <div class="mt-4 p-4 bg-blue-900/30 rounded-lg">
                <p class="text-blue-300 text-sm">
                    💡 <strong>Cách đọc:</strong> Nếu mua khi P/B ở vùng "Rẻ", lịch sử cho thấy sau 1 năm bạn sẽ có 
                    lợi nhuận trung bình và tỷ lệ có lãi (win rate) như bảng trên. Số liệu này dựa trên dữ liệu thực tế, 
                    không phải dự đoán.
                </p>
            </div>
        </div>
    `;
}

// Display P/B chart
function displayPBChart() {
    let history = stockData.pb_history || [];
    const stats = stockData.pb_statistics || {};
    
    if (history.length === 0) {
        document.getElementById('pb-chart').innerHTML = '<div class="text-gray-500 text-center py-8">Không có dữ liệu biểu đồ</div>';
        return;
    }
    
    // Sort history by year and quarter (ascending: oldest to newest)
    history = history.slice().sort((a, b) => {
        if (a.year !== b.year) {
            return a.year - b.year;
        }
        return a.quarter - b.quarter;
    });
    
    const periods = history.map(h => h.period);
    const pbValues = history.map(h => h.pb);
    const priceValues = history.map(h => h.price ? h.price * 1000 : null);
    
    const trace1 = {
        x: periods,
        y: pbValues,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'P/B',
        line: { color: '#3B82F6', width: 2 },
        marker: { size: 6 },
        yaxis: 'y'
    };
    
    const trace2 = {
        x: periods,
        y: priceValues,
        type: 'scatter',
        mode: 'lines',
        name: 'Giá (nghìn đ)',
        line: { color: '#10B981', width: 1, dash: 'dot' },
        yaxis: 'y2',
        opacity: 0.7
    };
    
    // Add mean line as a trace (easier to see than shape)
    const trace3 = {
        x: periods,
        y: new Array(periods.length).fill(stats.mean),
        type: 'scatter',
        mode: 'lines',
        name: `Mean P/B (${stats.mean?.toFixed(2)})`,
        line: { color: '#FBBF24', width: 2, dash: 'dash' },
        yaxis: 'y',
        hoverinfo: 'y'
    };
    
    // Horizontal lines for percentiles
    // Handle both naming conventions: p10/p25 or percentile_10/percentile_25
    const p10 = stats.p10 ?? stats.percentile_10;
    const p25 = stats.p25 ?? stats.percentile_25;
    const p75 = stats.p75 ?? stats.percentile_75;
    const p90 = stats.p90 ?? stats.percentile_90;
    
    const shapes = [
        { y: p10, color: '#10B981', dash: 'dot', label: 'P10' },
        { y: p25, color: '#34D399', dash: 'dot', label: 'P25' },
        // Mean is now a trace, not a shape
        { y: p75, color: '#F97316', dash: 'dot', label: 'P75' },
        { y: p90, color: '#EF4444', dash: 'dot', label: 'P90' },
    ].filter(s => s.y != null).map(s => ({
        type: 'line',
        x0: periods[0],
        x1: periods[periods.length - 1],
        y0: s.y,
        y1: s.y,
        line: { color: s.color, width: 1, dash: s.dash },
        yref: 'y'
    }));
    
    const layout = {
        title: {
            text: `Biểu đồ P/B theo quý - ${stockData.symbol}`,
            font: { color: '#fff' }
        },
        paper_bgcolor: '#1f2937',
        plot_bgcolor: '#111827',
        font: { color: '#9ca3af' },
        xaxis: {
            title: 'Kỳ',
            gridcolor: '#374151',
            tickangle: -45
        },
        yaxis: {
            title: 'P/B',
            gridcolor: '#374151',
            side: 'left'
        },
        yaxis2: {
            title: 'Giá (đ)',
            overlaying: 'y',
            side: 'right',
            showgrid: false
        },
        legend: {
            x: 0,
            y: 1.1,
            orientation: 'h'
        },
        shapes: shapes,
        hovermode: 'x unified',
        margin: { t: 60, b: 80 }
    };
    
    const config = { responsive: true };
    
    Plotly.newPlot('pb-chart-container', [trace1, trace3, trace2], layout, config);
}

// Display quarterly data table
function displayQuarterlyTable() {
    const data = stockData.quarterly_data || [];
    
    let rows = data.reverse().slice(0, 20).map(q => `
        <tr class="border-b border-gray-700 hover:bg-gray-700">
            <td class="py-2 px-4 text-white">${q.period}</td>
            <td class="py-2 px-4 text-white text-right">${q.pb?.toFixed(2) || 'N/A'}</td>
            <td class="py-2 px-4 text-white text-right">${q.price ? (q.price * 1000).toLocaleString('vi-VN') : 'N/A'}</td>
        </tr>
    `).join('');
    
    document.getElementById('quarterly-table').innerHTML = `
        <div class="bg-gray-800 rounded-lg p-6">
            <h2 class="text-xl font-bold text-white mb-4">📋 Dữ liệu theo quý (gần nhất)</h2>
            <div class="overflow-x-auto max-h-96 overflow-y-auto">
                <table class="w-full">
                    <thead class="sticky top-0 bg-gray-800">
                        <tr class="border-b border-gray-600">
                            <th class="py-2 px-4 text-left text-gray-400">Kỳ</th>
                            <th class="py-2 px-4 text-right text-gray-400">P/B</th>
                            <th class="py-2 px-4 text-right text-gray-400">Giá</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rows || '<tr><td colspan="3" class="py-4 text-center text-gray-500">Chưa có dữ liệu</td></tr>'}
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

// Initialize
document.addEventListener('DOMContentLoaded', loadStock);
