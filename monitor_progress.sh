#!/bin/bash
while true; do
  clear
  echo "═══════════════════════════════════════════════════════════"
  echo "📊 THEO DÕI TIẾN ĐỘ - $(date '+%H:%M:%S')"
  echo "═══════════════════════════════════════════════════════════"
  
  success=$(grep -c "đã được thêm thành công" add_stocks.log 2>/dev/null || echo 0)
  errors=$(grep -c "Không lấy được dữ liệu" add_stocks.log 2>/dev/null || echo 0)
  skipped=$(grep -c "đã tồn tại, bỏ qua" add_stocks.log 2>/dev/null || echo 0)
  
  echo "✅ Thành công: $success/68"
  echo "❌ Lỗi: $errors"
  echo "⏭️  Bỏ qua: $skipped"
  echo ""
  echo "Mã đang xử lý:"
  tail -3 add_stocks.log | grep -E "Processing|thành công"
  
  total=$((success + errors))
  if [ $total -ge 68 ]; then
    echo ""
    echo "✨ HOÀN THÀNH!"
    break
  fi
  
  if ! pgrep -f "add_icopy_missing_stocks.py" > /dev/null; then
    echo ""
    echo "⚠️  Script đã dừng"
    break
  fi
  
  sleep 30
done

echo ""
tail -20 add_stocks.log | grep -A 5 "TỔNG KẾT"
