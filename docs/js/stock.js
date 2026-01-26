/**
 * JP Stock Webapp - Stock Detail Page JavaScript
 */

// Global state
let bankData = null;
let currentStock = null;

// Get URL parameter
function getUrlParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

// Format helpers (same as app.js)
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

// Load data
async function loadData() {
    try {
        const response = await fetch('data/banks.json');
        if (!response.ok) throw new Error('Failed to load data');
        bankData = await response.json();
        
        const symbol = getUrlParam('symbol');
        if (!symbol) {
            showError('Không tìm thấy mã cổ phiếu');
            return;
        }
        
        currentStock = bankData.banks.find(b => b.symbol === symbol);
        if (!currentStock) {
            showError(`Không tìm thấy dữ liệu cho mã ${symbol}`);
            return;
        }
        
        renderStockDetail();
        renderPBChart();
        
    } catch (error) {
        console.error('Error loading data:', error);
        showError('Không thể tải dữ liệu');
    }
}

function showError(message) {
    document.getElementById('stockContent').innerHTML = `
        <div class="text-center py-12 text-red-500">
            <p class="text-xl">${message}</p>
            <a href="index.html" class="text-blue-600 hover:underline mt-4 inline-block">← Quay lại danh sách</a>
        </div>
    `;
}

// Render stock detail
function renderStockDetail() {
    const stock = currentStock;
    const valuation = stock.valuation || {};
    const expectedReturn = stock.expected_return || {};
    const risk = stock.risk || {};
    const pbStats = stock.pb_statistics || {};
    const meanReversion = stock.mean_reversion || {};
    
    // Update page title
    document.title = `${stock.symbol} - ${stock.name} | JP Stock Analysis`;
    document.getElementById('pageTitle').textContent = `${stock.symbol} - ${stock.name}`;
    
    // Valuation zone color
    const zoneColors = {
        'EXTREMELY_CHEAP': 'bg-green-700',
        'CHEAP': 'bg-green-500',
        'FAIR': 'bg-gray-500',
        'EXPENSIVE': 'bg-orange-500',
        'EXTREMELY_EXPENSIVE': 'bg-red-600',
        'UNKNOWN': 'bg-gray-400'
    };
    
    document.getElementById('stockContent').innerHTML = `
        <!-- Header Card -->
        <div class="bg-white rounded-xl shadow-lg p-6 mb-6">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between">
                <div>
                    <h1 class="text-3xl font-bold text-gray-900">${stock.symbol}</h1>
                    <p class="text-lg text-gray-600">${stock.name}</p>
                </div>
                <div class="mt-4 md:mt-0 text-right">
                    <div class="text-3xl font-bold text-gray-900">${formatPrice(stock.current_price)} đ</div>
                    <div class="text-lg">P/B: <span class="font-semibold">${formatNumber(stock.current_pb)}</span></div>
                </div>
            </div>
        </div>
        
        <!-- Main Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            <!-- Valuation Card -->
            <div class="bg-white rounded-xl shadow-lg p-6">
                <h3 class="text-lg font-semibold text-gray-700 mb-4">Đánh Giá Định Giá</h3>
                <div class="text-center">
                    <div class="inline-block ${zoneColors[valuation.zone] || 'bg-gray-400'} text-white px-6 py-3 rounded-full text-xl font-bold mb-4">
                        ${valuation.label || 'N/A'}
                    </div>
                    <div class="text-gray-600">
                        <p>Tín hiệu: <span class="font-semibold">${valuation.signal || 'N/A'}</span></p>
                        <p class="mt-2">Percentile: <span class="font-semibold text-2xl">${formatNumber(valuation.percentile, 0)}%</span></p>
                        <p class="text-sm text-gray-500 mt-1">
                            (P/B hiện tại cao hơn ${formatNumber(valuation.percentile, 0)}% lịch sử)
                        </p>
                    </div>
                </div>
            </div>
            
            <!-- Expected Return Card -->
            <div class="bg-white rounded-xl shadow-lg p-6">
                <h3 class="text-lg font-semibold text-gray-700 mb-4">Lợi Nhuận Kỳ Vọng</h3>
                <div class="text-center">
                    <div class="text-4xl font-bold ${(expectedReturn.expected_return || 0) >= 0 ? 'text-green-600' : 'text-red-600'}">
                        ${formatPercent(expectedReturn.expected_return)}
                    </div>
                    <p class="text-gray-500 mt-2">Độ tin cậy: ${expectedReturn.confidence || 'N/A'}</p>
                    <div class="mt-4 text-sm text-gray-600">
                        <p>Nếu P/B về trung bình: ${formatPercent(expectedReturn.return_to_mean)}</p>
                        <p>Nếu P/B về median: ${formatPercent(expectedReturn.return_to_median)}</p>
                    </div>
                </div>
            </div>
            
            <!-- Risk Card -->
            <div class="bg-white rounded-xl shadow-lg p-6">
                <h3 class="text-lg font-semibold text-gray-700 mb-4">Đánh Giá Rủi Ro</h3>
                <div class="text-center">
                    <div class="text-4xl font-bold text-gray-700">${formatNumber(risk.risk_score, 0)}/100</div>
                    <p class="text-lg font-semibold mt-2 ${getRiskColor(risk.risk_level)}">${getRiskLabel(risk.risk_level)}</p>
                    <p class="text-sm text-gray-500 mt-2">${risk.description || ''}</p>
                    <p class="text-sm text-gray-500 mt-1">Z-Score: ${formatNumber(risk.z_score)}</p>
                </div>
            </div>
        </div>
        
        <!-- P/B Statistics -->
        <div class="bg-white rounded-xl shadow-lg p-6 mb-6">
            <h3 class="text-lg font-semibold text-gray-700 mb-4">Thống Kê P/B (${pbStats.years_of_data || 0} năm)</h3>
            <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
                <div class="text-center p-3 bg-gray-50 rounded-lg">
                    <div class="text-sm text-gray-500">Trung bình</div>
                    <div class="text-xl font-bold text-gray-700">${formatNumber(pbStats.mean)}</div>
                </div>
                <div class="text-center p-3 bg-gray-50 rounded-lg">
                    <div class="text-sm text-gray-500">Median</div>
                    <div class="text-xl font-bold text-gray-700">${formatNumber(pbStats.median)}</div>
                </div>
                <div class="text-center p-3 bg-gray-50 rounded-lg">
                    <div class="text-sm text-gray-500">Độ lệch chuẩn</div>
                    <div class="text-xl font-bold text-gray-700">${formatNumber(pbStats.std)}</div>
                </div>
                <div class="text-center p-3 bg-green-50 rounded-lg">
                    <div class="text-sm text-gray-500">P10 (Rẻ)</div>
                    <div class="text-xl font-bold text-green-600">${formatNumber(pbStats.percentile_10)}</div>
                </div>
                <div class="text-center p-3 bg-gray-50 rounded-lg">
                    <div class="text-sm text-gray-500">P50</div>
                    <div class="text-xl font-bold text-gray-700">${formatNumber(pbStats.percentile_50)}</div>
                </div>
                <div class="text-center p-3 bg-red-50 rounded-lg">
                    <div class="text-sm text-gray-500">P90 (Đắt)</div>
                    <div class="text-xl font-bold text-red-600">${formatNumber(pbStats.percentile_90)}</div>
                </div>
                <div class="text-center p-3 bg-gray-50 rounded-lg">
                    <div class="text-sm text-gray-500">Min / Max</div>
                    <div class="text-xl font-bold text-gray-700">${formatNumber(pbStats.min)} / ${formatNumber(pbStats.max)}</div>
                </div>
            </div>
        </div>
        
        <!-- Mean Reversion -->
        <div class="bg-white rounded-xl shadow-lg p-6 mb-6">
            <h3 class="text-lg font-semibold text-gray-700 mb-4">Phân Tích Mean Reversion</h3>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="text-center p-3 bg-blue-50 rounded-lg">
                    <div class="text-sm text-gray-500">Half-life</div>
                    <div class="text-xl font-bold text-blue-600">
                        ${meanReversion.half_life_years ? formatNumber(meanReversion.half_life_years) + ' năm' : 'N/A'}
                    </div>
                    <div class="text-xs text-gray-500">Thời gian P/B về 50% mean</div>
                </div>
                <div class="text-center p-3 bg-blue-50 rounded-lg">
                    <div class="text-sm text-gray-500">Tốc độ hồi quy</div>
                    <div class="text-xl font-bold text-blue-600">${formatNumber(meanReversion.reversion_speed, 3)}</div>
                </div>
                <div class="text-center p-3 bg-blue-50 rounded-lg">
                    <div class="text-sm text-gray-500">AR(1) Coefficient</div>
                    <div class="text-xl font-bold text-blue-600">${formatNumber(meanReversion.ar1_coefficient, 3)}</div>
                </div>
                <div class="text-center p-3 bg-blue-50 rounded-lg">
                    <div class="text-sm text-gray-500">R²</div>
                    <div class="text-xl font-bold text-blue-600">${formatNumber(meanReversion.r_squared, 3)}</div>
                </div>
            </div>
        </div>
        
        <!-- P/B History Chart -->
        <div class="bg-white rounded-xl shadow-lg p-6">
            <h3 class="text-lg font-semibold text-gray-700 mb-4">Biểu Đồ P/B Lịch Sử</h3>
            <div id="pbChart" style="height: 400px;"></div>
        </div>
    `;
}

function getRiskColor(level) {
    const colors = {
        'VERY_LOW': 'text-green-600',
        'LOW': 'text-green-500',
        'MEDIUM': 'text-yellow-600',
        'HIGH': 'text-orange-500',
        'VERY_HIGH': 'text-red-600',
        'UNKNOWN': 'text-gray-500'
    };
    return colors[level] || 'text-gray-500';
}

function getRiskLabel(level) {
    const labels = {
        'VERY_LOW': 'Rất thấp',
        'LOW': 'Thấp',
        'MEDIUM': 'Trung bình',
        'HIGH': 'Cao',
        'VERY_HIGH': 'Rất cao',
        'UNKNOWN': 'N/A'
    };
    return labels[level] || 'N/A';
}

// Render P/B Chart using Plotly
function renderPBChart() {
    const stock = currentStock;
    const pbHistory = stock.pb_history || [];
    const pbStats = stock.pb_statistics || {};
    
    if (pbHistory.length === 0) {
        document.getElementById('pbChart').innerHTML = '<p class="text-center text-gray-500">Không có dữ liệu P/B lịch sử</p>';
        return;
    }
    
    // Sort by year
    const sortedHistory = [...pbHistory].sort((a, b) => a.year - b.year);
    
    const years = sortedHistory.map(h => h.year);
    const pbValues = sortedHistory.map(h => h.pb);
    
    // Create bands
    const mean = pbStats.mean || 0;
    const std = pbStats.std || 0;
    
    const traces = [
        // P/B line
        {
            x: years,
            y: pbValues,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'P/B',
            line: { color: '#2563eb', width: 3 },
            marker: { size: 8 }
        },
        // Mean line
        {
            x: years,
            y: Array(years.length).fill(mean),
            type: 'scatter',
            mode: 'lines',
            name: `Mean (${formatNumber(mean)})`,
            line: { color: '#6b7280', width: 2, dash: 'dash' }
        },
        // +1 std (expensive zone)
        {
            x: years,
            y: Array(years.length).fill(mean + std),
            type: 'scatter',
            mode: 'lines',
            name: `+1σ (${formatNumber(mean + std)})`,
            line: { color: '#f97316', width: 1, dash: 'dot' }
        },
        // -1 std (cheap zone)
        {
            x: years,
            y: Array(years.length).fill(mean - std),
            type: 'scatter',
            mode: 'lines',
            name: `-1σ (${formatNumber(mean - std)})`,
            line: { color: '#22c55e', width: 1, dash: 'dot' }
        },
        // Current P/B marker
        {
            x: [years[years.length - 1]],
            y: [stock.current_pb],
            type: 'scatter',
            mode: 'markers',
            name: `Hiện tại (${formatNumber(stock.current_pb)})`,
            marker: { 
                size: 15, 
                color: '#dc2626',
                symbol: 'star'
            }
        }
    ];
    
    const layout = {
        title: `Lịch sử P/B - ${stock.symbol}`,
        xaxis: {
            title: 'Năm',
            tickmode: 'linear'
        },
        yaxis: {
            title: 'P/B Ratio'
        },
        legend: {
            orientation: 'h',
            y: -0.15
        },
        hovermode: 'x unified',
        shapes: [
            // Cheap zone (green area below -1 std)
            {
                type: 'rect',
                xref: 'paper',
                yref: 'y',
                x0: 0,
                x1: 1,
                y0: 0,
                y1: Math.max(0, mean - std),
                fillcolor: 'rgba(34, 197, 94, 0.1)',
                line: { width: 0 }
            },
            // Expensive zone (red area above +1 std)
            {
                type: 'rect',
                xref: 'paper',
                yref: 'y',
                x0: 0,
                x1: 1,
                y0: mean + std,
                y1: Math.max(...pbValues) * 1.1,
                fillcolor: 'rgba(239, 68, 68, 0.1)',
                line: { width: 0 }
            }
        ]
    };
    
    const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['lasso2d', 'select2d']
    };
    
    Plotly.newPlot('pbChart', traces, layout, config);
}

// Initialize
document.addEventListener('DOMContentLoaded', loadData);
