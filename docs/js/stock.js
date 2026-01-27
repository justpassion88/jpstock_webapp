/**
 * JP Stock Webapp - Stock Detail V2
 * Hiển thị chi tiết với Historical Backtest
 */

let stockData = null;

// Helper: Map English zone to Vietnamese
function getZoneVietnamese(zone) {
    const zoneMap = {
        'VERY_CHEAP': '🟢 CỰC RẺ',
        'CHEAP': '🟢 RẺ',
        'FAIR': '🟡 HỢP LÝ',
        'EXPENSIVE': '🔴 ĐẮT',
        'VERY_EXPENSIVE': '🔴 CỰC ĐẮT',
        'OVERVALUED': '🔴 QUÁ ĐẮT',
        'fair': '🟡 HỢP LÝ',
        'cheap': '🟢 RẺ',
        'expensive': '🔴 ĐẮT'
    };
    return zoneMap[zone] || zone || 'N/A';
}

// Helper: Get zone color
function getZoneColor(zone, zone_vi) {
    const zoneStr = (zone_vi || zone || '').toLowerCase();
    if (zoneStr.includes('rẻ') || zoneStr.includes('cheap')) return '#10B981';
    if (zoneStr.includes('đắt') || zoneStr.includes('expensive')) return '#EF4444';
    if (zoneStr.includes('hợp') || zoneStr.includes('fair')) return '#F59E0B';
    return '#6B7280';
}

// Helper to get current price
function getCurrentPrice() {
    if (stockData.current_price) {
        return (stockData.current_price * 1000).toLocaleString('vi-VN');
    }
    if (stockData.pb_history && stockData.pb_history.length > 0) {
        // Find the most recent entry by sorting by year and quarter
        const sortedHistory = [...stockData.pb_history].sort((a, b) => {
            if (a.year !== b.year) return b.year - a.year;
            return b.quarter - a.quarter;
        });
        const latestEntry = sortedHistory[0];
        if (latestEntry && latestEntry.price) {
            // Price in JSON is in tiny units, multiply by 1,000,000 to get VND
            return (latestEntry.price * 1000000).toLocaleString('vi-VN');
        }
    }
    return 'N/A';
}

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
    const stats = stockData.pb_statistics || {};
    
    // Get zone display - try zone_vi first, then convert from zone
    const zoneDisplay = valuation.zone_vi || getZoneVietnamese(valuation.zone);
    const zoneColor = valuation.color || getZoneColor(valuation.zone, valuation.zone_vi);
    
    document.getElementById('stock-header').innerHTML = `
        <div class="bg-gray-800 rounded-lg p-6 mb-6">
            <div class="flex flex-wrap items-center justify-between mb-4">
                <div>
                    <h1 class="text-3xl font-bold text-white">${stockData.symbol}</h1>
                    <p class="text-gray-400">${stockData.name || ''}</p>
                </div>
                <div class="text-right">
                    <span class="px-4 py-2 rounded-lg text-lg font-bold" 
                          style="background-color: ${zoneColor}25; color: ${zoneColor}; border: 2px solid ${zoneColor}">
                        ${zoneDisplay}
                    </span>
                </div>
            </div>
            
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="bg-gray-900 rounded-lg p-4">
                    <div class="text-gray-500 text-sm">Giá hiện tại</div>
                       <div class="text-2xl font-bold text-white">${getCurrentPrice()}đ</div>
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

// Calculate simple backtest from pb_history when no official backtest available
function calculateSimpleBacktest(pbHistory, currentPB, currentPercentile) {
    // Sort by year and quarter
    const sorted = [...pbHistory].sort((a, b) => {
        if (a.year !== b.year) return a.year - b.year;
        return a.quarter - b.quarter;
    });
    
    // Calculate returns for 1 year and 2 years
    const returns1y = [];
    const returns2y = [];
    
    for (let i = 0; i < sorted.length - 4; i++) {
        const startPrice = sorted[i].price;
        const price1y = sorted[i + 4]?.price; // 4 quarters = 1 year
        const price2y = sorted[i + 8]?.price; // 8 quarters = 2 years
        
        if (startPrice && price1y) {
            const return1y = ((price1y - startPrice) / startPrice) * 100;
            returns1y.push(return1y);
        }
        
        if (startPrice && price2y) {
            const return2y = ((price2y - startPrice) / startPrice) * 100;
            returns2y.push(return2y);
        }
    }
    
    if (returns1y.length === 0) return null;
    
    // Calculate stats
    const avgReturn1y = returns1y.reduce((a, b) => a + b, 0) / returns1y.length;
    const avgReturn2y = returns2y.length > 0 ? returns2y.reduce((a, b) => a + b, 0) / returns2y.length : null;
    const winRate1y = (returns1y.filter(r => r > 0).length / returns1y.length) * 100;
    const winRate2y = returns2y.length > 0 ? (returns2y.filter(r => r > 0).length / returns2y.length) * 100 : 0;
    
    return {
        return1y: avgReturn1y,
        return2y: avgReturn2y,
        winRate1y: winRate1y,
        winRate2y: winRate2y,
        sampleCount: returns1y.length,
        expected_1y_min: Math.min(...returns1y),
        expected_1y_max: Math.max(...returns1y),
        expected_1y_median: returns1y.sort((a, b) => a - b)[Math.floor(returns1y.length / 2)],
        isSimple: true
    };
}

// Display valuation and expected returns
function displayValuation() {
    const expectedReturn = stockData.expected_return || {};
    const risk = stockData.risk || {};
    const valuation = stockData.valuation || {};
    const hasBacktest = expectedReturn.expected_1y != null;
    
    // If no backtest, calculate simple stats from pb_history
    let simpleBacktest = null;
    if (!hasBacktest && stockData.pb_history && stockData.pb_history.length > 0) {
        simpleBacktest = calculateSimpleBacktest(stockData.pb_history, stockData.current_pb, valuation.percentile);
    }
    
    const return1y = expectedReturn.expected_1y || simpleBacktest?.return1y;
    const return2y = expectedReturn.expected_2y || simpleBacktest?.return2y;
    const winRate1y = expectedReturn.win_rate_1y || simpleBacktest?.winRate1y || 0;
    const winRate2y = expectedReturn.win_rate_2y || simpleBacktest?.winRate2y || 0;
    const sampleCount = expectedReturn.sample_count || simpleBacktest?.sampleCount || 0;
    
    // Get min/max values
    const return1yMin = expectedReturn.expected_1y_min || simpleBacktest?.expected_1y_min;
    const return1yMax = expectedReturn.expected_1y_max || simpleBacktest?.expected_1y_max;
    const return1yMedian = expectedReturn.expected_1y_median || simpleBacktest?.expected_1y_median;
    
    // Check if we have any data to display
    if (!return1y && return1y !== 0) {
        document.getElementById('valuation-section').innerHTML = `
            <div class="bg-gray-800 rounded-lg p-6 mb-6">
                <h2 class="text-xl font-bold text-white mb-4">📊 Phân tích Backtest P/B</h2>
                
                <div class="bg-yellow-900/20 border-2 border-yellow-500/50 rounded-lg p-6 text-center">
                    <div class="text-4xl mb-3">⚠️</div>
                    <h3 class="text-lg font-bold text-yellow-300 mb-2">Chưa có dữ liệu Backtest</h3>
                    <p class="text-gray-300 text-sm mb-4">
                        Mã <strong class="text-white">${stockData.symbol}</strong> chưa có đủ dữ liệu lịch sử để tính toán backtest P/B.
                        Có thể do:
                    </p>
                    <ul class="text-left text-sm text-gray-400 space-y-1 max-w-md mx-auto">
                        <li>• Cổ phiếu mới niêm yết, chưa đủ lịch sử</li>
                        <li>• Dữ liệu P/B không đủ ổn định để backtest</li>
                        <li>• Hệ thống chưa cập nhật backtest cho mã này</li>
                    </ul>
                    
                    <div class="mt-6 p-4 bg-blue-900/30 rounded-lg">
                        <p class="text-sm text-blue-300 mb-2"><strong>💡 Bạn vẫn có thể:</strong></p>
                        <ul class="text-left text-xs text-gray-300 space-y-1">
                            <li>✓ Xem vị thế P/B hiện tại (Percentile P${valuation.percentile?.toFixed(0) || 'N/A'})</li>
                            <li>✓ Xem biểu đồ lịch sử P/B bên dưới</li>
                            <li>✓ So sánh với các mã khác trong ngành</li>
                            <li>✓ Tự đánh giá dựa trên zone: ${getZoneVietnamese(valuation.zone || valuation.zone_vi)}</li>
                        </ul>
                    </div>
                </div>
            </div>
        `;
        return;
    }
    
    // Determine if this is a good opportunity
    const isGoodBuy = return1y >= 15 && winRate1y >= 70;
    const isOkBuy = return1y >= 10 && winRate1y >= 60;
    
    const opportunityLevel = isGoodBuy ? 'Cơ hội TỐT' : isOkBuy ? 'Cơ hội KHẢ QUAN' : 'CÂN NHẮC';
    const opportunityColor = isGoodBuy ? '#10B981' : isOkBuy ? '#F59E0B' : '#6B7280';
    
    // Tính toán ví dụ đầu tư với 100 triệu
    const investment = 100; // triệu
    const expected1yAmount = investment * (1 + return1y / 100);
    const expected2yAmount = investment * (1 + return2y / 100);
    const savingsRate = 5.0; // Lãi suất tiết kiệm giả định 5%/năm
    const savings1yAmount = investment * (1 + savingsRate / 100);
    const savings2yAmount = investment * Math.pow(1 + savingsRate / 100, 2);
    
    document.getElementById('valuation-section').innerHTML = `
        <div class="bg-gray-800 rounded-lg p-6 mb-6">
            <h2 class="text-xl font-bold text-white mb-4">📊 Phân tích Backtest P/B</h2>
            
            ${simpleBacktest ? `
            <div class="mb-4 p-3 bg-blue-900/20 border border-blue-500/30 rounded-lg">
                <div class="flex items-center gap-2 text-sm text-blue-300">
                    <span>ℹ️</span>
                    <span><strong>Backtest Đơn Giản:</strong> Mã này chưa có backtest chính thức. Dữ liệu dưới đây được tính toán tự động từ ${sampleCount} mẫu lịch sử, chỉ mang tính tham khảo.</span>
                </div>
            </div>
            ` : ''}
            
            <!-- Opportunity Summary -->
            <div class="mb-6 p-4 rounded-lg border-2" style="background-color: ${opportunityColor}15; border-color: ${opportunityColor}">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-lg font-bold" style="color: ${opportunityColor}">
                        ${opportunityLevel}
                    </span>
                    <span class="text-sm text-gray-400">Dựa trên ${sampleCount} mẫu lịch sử</span>
                </div>
                <div class="text-sm text-gray-300">
                    ${isGoodBuy ? '✅ Kỳ vọng lợi nhuận cao và tỷ lệ thắng tốt' : 
                      isOkBuy ? '⚠️ Kỳ vọng lợi nhuận trung bình' : 
                      '⚠️ Cần thận trọng, kỳ vọng lợi nhuận thấp hoặc tỷ lệ thắng không cao'}
                </div>
            </div>
            
            <!-- Ví dụ Đầu tư Thực tế -->
            <div class="mb-6 p-5 rounded-lg bg-gradient-to-br from-blue-900/40 to-purple-900/40 border border-blue-500/30">
                <h3 class="text-lg font-bold text-white mb-3">💰 Ví dụ: Đầu tư 100 triệu đồng</h3>
                <div class="text-sm text-gray-300 mb-4">
                    Nếu bạn mua <strong class="text-white">${stockData.symbol}</strong> ở mức P/B hiện tại <strong class="text-yellow-400">P${valuation.percentile?.toFixed(0) || 'N/A'}</strong>, theo lịch sử:
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <!-- 1 năm -->
                    <div class="bg-gray-900/60 rounded-lg p-4 border border-gray-700">
                        <div class="text-gray-400 text-xs mb-2">📅 Sau 1 năm</div>
                        <div class="flex items-baseline justify-between mb-2">
                            <div>
                                <div class="text-2xl font-bold ${return1y >= 15 ? 'text-green-400' : return1y >= 0 ? 'text-yellow-400' : 'text-red-400'}">
                                    ${expected1yAmount.toFixed(1)}tr
                                </div>
                                <div class="text-xs text-gray-500">Giá trị dự kiến</div>
                            </div>
                            <div class="text-right">
                                <div class="text-lg font-bold ${return1y >= 0 ? 'text-green-400' : 'text-red-400'}">
                                    ${return1y > 0 ? '+' : ''}${(expected1yAmount - investment).toFixed(1)}tr
                                </div>
                                <div class="text-xs text-gray-500">${return1y > 0 ? 'Lãi' : 'Lỗ'}: ${return1y > 0 ? '+' : ''}${return1y.toFixed(1)}%</div>
                            </div>
                        </div>
                        <div class="text-xs text-gray-400 pt-2 border-t border-gray-700">
                            Tỷ lệ thắng: <strong class="text-white">${winRate1y.toFixed(0)}%</strong>
                        </div>
                        <div class="mt-3 pt-3 border-t border-gray-700">
                            <div class="text-xs text-gray-400 mb-1">So với gửi tiết kiệm ${savingsRate}%/năm:</div>
                            <div class="flex items-center justify-between text-xs">
                                <span class="text-gray-400">Tiết kiệm: ${savings1yAmount.toFixed(1)}tr</span>
                                <span class="${(expected1yAmount - savings1yAmount) >= 0 ? 'text-green-400' : 'text-red-400'} font-bold">
                                    ${(expected1yAmount - savings1yAmount) >= 0 ? '+' : ''}${(expected1yAmount - savings1yAmount).toFixed(1)}tr
                                </span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- 2 năm -->
                    <div class="bg-gray-900/60 rounded-lg p-4 border border-gray-700">
                        <div class="text-gray-400 text-xs mb-2">📅 Sau 2 năm</div>
                        <div class="flex items-baseline justify-between mb-2">
                            <div>
                                <div class="text-2xl font-bold ${return2y >= 30 ? 'text-green-400' : return2y >= 0 ? 'text-yellow-400' : 'text-red-400'}">
                                    ${expected2yAmount.toFixed(1)}tr
                                </div>
                                <div class="text-xs text-gray-500">Giá trị dự kiến</div>
                            </div>
                            <div class="text-right">
                                <div class="text-lg font-bold ${return2y >= 0 ? 'text-green-400' : 'text-red-400'}">
                                    ${return2y > 0 ? '+' : ''}${(expected2yAmount - investment).toFixed(1)}tr
                                </div>
                                <div class="text-xs text-gray-500">${return2y > 0 ? 'Lãi' : 'Lỗ'}: ${return2y > 0 ? '+' : ''}${return2y.toFixed(1)}%</div>
                            </div>
                        </div>
                        <div class="text-xs text-gray-400 pt-2 border-t border-gray-700">
                            Tỷ lệ thắng: <strong class="text-white">${winRate2y?.toFixed(0) || 'N/A'}%</strong>
                        </div>
                        <div class="mt-3 pt-3 border-t border-gray-700">
                            <div class="text-xs text-gray-400 mb-1">So với gửi tiết kiệm ${savingsRate}%/năm:</div>
                            <div class="flex items-center justify-between text-xs">
                                <span class="text-gray-400">Tiết kiệm: ${savings2yAmount.toFixed(1)}tr</span>
                                <span class="${(expected2yAmount - savings2yAmount) >= 0 ? 'text-green-400' : 'text-red-400'} font-bold">
                                    ${(expected2yAmount - savings2yAmount) >= 0 ? '+' : ''}${(expected2yAmount - savings2yAmount).toFixed(1)}tr
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="mt-4 text-xs text-gray-400 italic">
                    💡 Số liệu trên là kỳ vọng trung bình dựa trên lịch sử. Thực tế có thể khác, từ ${return1yMin?.toFixed(1)}% đến ${return1yMax?.toFixed(1)}%
                </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Key Metrics -->
                <div>
                    <h3 class="text-base font-semibold text-gray-300 mb-3">📈 Chỉ số chính</h3>
                    <div class="space-y-3">
                        <div class="bg-gray-900 rounded-lg p-4">
                            <div class="flex justify-between items-center mb-2">
                                <span class="text-gray-400 text-sm">Lợi nhuận TB 1 năm</span>
                                <span class="font-bold text-2xl ${return1y >= 20 ? 'text-green-400' : return1y >= 10 ? 'text-yellow-400' : 'text-gray-400'}">
                                    ${return1y != null ? `${return1y > 0 ? '+' : ''}${return1y.toFixed(1)}%` : 'N/A'}
                                </span>
                            </div>
                            <div class="text-xs text-gray-500">
                                ${return1y >= 20 ? '🟢 Rất tốt (≥20%)' : return1y >= 15 ? '🟡 Tốt (≥15%)' : return1y >= 10 ? '🟠 Khá (≥10%)' : '⚪ Thấp (<10%)'}
                            </div>
                        </div>
                        
                        <div class="bg-gray-900 rounded-lg p-4">
                            <div class="flex justify-between items-center mb-2">
                                <span class="text-gray-400 text-sm">Tỷ lệ thắng</span>
                                <span class="font-bold text-2xl ${winRate1y >= 80 ? 'text-green-400' : winRate1y >= 70 ? 'text-yellow-400' : 'text-gray-400'}">
                                    ${winRate1y.toFixed(0)}%
                                </span>
                            </div>
                            <div class="text-xs text-gray-500">
                                ${winRate1y >= 80 ? '🟢 Rất cao (≥80%)' : winRate1y >= 70 ? '🟡 Cao (≥70%)' : winRate1y >= 60 ? '🟠 Trung bình (≥60%)' : '⚪ Thấp (<60%)'}
                            </div>
                        </div>
                        
                        <div class="bg-gray-900 rounded-lg p-4">
                            <div class="text-gray-400 text-sm mb-1">Phạm vi lợi nhuận</div>
                            <div class="flex justify-between items-center">
                                <span class="text-red-400 text-sm">
                                    ${return1yMin != null ? `${return1yMin.toFixed(1)}%` : 'N/A'}
                                </span>
                                <span class="text-gray-500 text-xs">đến</span>
                                <span class="text-green-400 text-sm">
                                    ${return1yMax != null ? `+${return1yMax.toFixed(1)}%` : 'N/A'}
                                </span>
                            </div>
                            <div class="text-xs text-gray-500 mt-1">
                                Median: ${return1yMedian != null ? `${return1yMedian.toFixed(1)}%` : 'N/A'}
                            </div>
                            <div class="mt-3 pt-3 border-t border-gray-700">
                                <div class="text-xs text-gray-400 mb-2">📊 Phân bổ kết quả:</div>
                                <div class="text-xs space-y-1">
                                    <div class="flex justify-between">
                                        <span class="text-gray-500">Kịch bản tốt nhất:</span>
                                        <span class="text-green-400 font-semibold">+${return1yMax?.toFixed(1)}%</span>
                                    </div>
                                    <div class="flex justify-between">
                                        <span class="text-gray-500">Trung bình:</span>
                                        <span class="text-yellow-400 font-semibold">+${return1y?.toFixed(1)}%</span>
                                    </div>
                                    <div class="flex justify-between">
                                        <span class="text-gray-500">Kịch bản tệ nhất:</span>
                                        <span class="text-red-400 font-semibold">${return1yMin?.toFixed(1)}%</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Backtest 2 năm -->
                        <div class="bg-gray-900 rounded-lg p-4 border-l-4 border-purple-500">
                            <div class="flex justify-between items-center mb-2">
                                <span class="text-gray-400 text-sm">Lợi nhuận TB 2 năm</span>
                                <span class="font-bold text-2xl ${return2y >= 40 ? 'text-green-400' : return2y >= 20 ? 'text-yellow-400' : 'text-gray-400'}">
                                    ${return2y != null ? `${return2y > 0 ? '+' : ''}${return2y.toFixed(1)}%` : 'N/A'}
                                </span>
                            </div>
                            <div class="text-xs text-gray-500 mb-2">
                                ${return2y >= 40 ? '🟢 Rất tốt (≥40%)' : return2y >= 30 ? '🟡 Tốt (≥30%)' : return2y >= 20 ? '🟠 Khá (≥20%)' : '⚪ Thấp (<20%)'}
                            </div>
                            <div class="text-xs text-gray-400 pt-2 border-t border-gray-700">
                                Tỷ lệ thắng 2 năm: <strong class="text-white">${winRate2y?.toFixed(0) || 'N/A'}%</strong>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Risk & Explanation -->
                <div>
                    <h3 class="text-base font-semibold text-gray-300 mb-3">⚠️ Rủi ro & Giải thích</h3>
                    <div class="space-y-3">
                        <div class="bg-gray-900 rounded-lg p-4">
                            <div class="flex justify-between items-center mb-2">
                                <span class="text-gray-400 text-sm">Mức độ rủi ro</span>
                                <span class="font-bold text-lg ${risk.level === 'LOW' ? 'text-green-400' : risk.level === 'MEDIUM' ? 'text-yellow-400' : 'text-red-400'}">
                                    ${risk.level_vi || (simpleBacktest ? 'Chưa đánh giá' : 'N/A')}
                                </span>
                            </div>
                            <div class="text-xs text-gray-500">
                                ${risk.description || (simpleBacktest ? 'Chưa có đánh giá rủi ro chính thức cho mã này' : '')}
                            </div>
                        </div>
                        
                        <div class="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
                            <div class="text-blue-300 text-sm space-y-2">
                                <p><strong>💡 Backtest là gì?</strong></p>
                                <p>Kiểm tra xem trong lịch sử, nếu mua ở mức P/B tương tự (percentile ${valuation.percentile?.toFixed(0) || 'N/A'}), sau 1-2 năm có lãi bao nhiêu.</p>
                                
                                <p class="mt-3"><strong>📊 Cách đọc chỉ số:</strong></p>
                                <ul class="list-disc list-inside space-y-1 text-xs">
                                    <li><strong>Lợi nhuận TB:</strong> Trung bình cộng ${sampleCount} lần trong lịch sử</li>
                                    <li><strong>Tỷ lệ thắng:</strong> Có bao nhiêu % lần có lãi sau 1/2 năm</li>
                                    <li><strong>Phạm vi:</strong> Từ kịch bản tệ nhất đến tốt nhất có thể xảy ra</li>
                                    <li><strong>Median:</strong> Giá trị nằm giữa (50% tốt hơn, 50% tệ hơn)</li>
                                </ul>
                                
                                <p class="mt-3"><strong>🎯 Kịch bản thực tế:</strong></p>
                                <div class="text-xs space-y-1 bg-gray-900/40 p-2 rounded">
                                    <div>• Nếu <strong>${winRate1y.toFixed(0)}%</strong> lần có lãi → Cứ 10 lần mua, có ${Math.round(winRate1y/10)} lần lãi</div>
                                    <div>• Lợi nhuận trung bình <strong>${return1y > 0 ? '+' : ''}${return1y.toFixed(1)}%</strong> → 100 triệu thành ${expected1yAmount.toFixed(1)} triệu sau 1 năm</div>
                                    <div>• Tệ nhất từng là <strong>${return1yMin?.toFixed(1)}%</strong>, tốt nhất <strong>+${return1yMax?.toFixed(1)}%</strong></div>
                                </div>
                                
                                <p class="mt-3 text-yellow-300"><strong>⚠️ Lưu ý:</strong> ${simpleBacktest ? 'Đây là backtest đơn giản, chỉ tính toán từ giá lịch sử. ' : ''}Quá khứ không đảm bảo tương lai. Chỉ tham khảo, không phải khuyến nghị đầu tư.</p>
                            </div>
                        </div>
                        
                        <div class="bg-gray-900 rounded-lg p-4">
                            <div class="text-gray-400 text-sm mb-2">Vị thế hiện tại</div>
                            <div class="flex items-center justify-between">
                                <span class="text-white">P/B: <strong>${stockData.current_pb?.toFixed(2) || 'N/A'}</strong></span>
                                <span class="text-white">Percentile: <strong>P${valuation.percentile?.toFixed(0) || 'N/A'}</strong></span>
                            </div>
                            <div class="text-xs text-gray-500 mt-2">
                                ${valuation.description || ''}
                            </div>
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
        name: 'Giá',
        line: { color: '#10B981', width: 1, dash: 'dot' },
        yaxis: 'y2',
        opacity: 0.7,
        customdata: priceValues.map(p => p ? p.toLocaleString('vi-VN') : 'N/A'),
        hovertemplate: '<b>%{x}</b><br>Giá: %{customdata}đ<extra></extra>'
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
