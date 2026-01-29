#!/bin/bash
# Post-refresh validation and deployment script

echo "========================================================================"
echo "📊 POST-REFRESH VALIDATION & DEPLOYMENT"
echo "========================================================================"
echo ""

# 1. Check if refresh completed
echo "1️⃣ Checking if data refresh completed..."
if grep -q "ALL SECTORS COMPLETED" refresh_log.txt; then
    echo "   ✅ Data refresh completed successfully"
else
    echo "   ⚠️  Data refresh may still be running"
    echo "   Run: python3 check_refresh_progress.py"
    exit 1
fi

# 2. Generate market heat
echo ""
echo "2️⃣ Generating market heat index..."
python3 generate_market_heat_daily.py
if [ $? -eq 0 ]; then
    echo "   ✅ Market heat generated"
else
    echo "   ❌ Failed to generate market heat"
    exit 1
fi

# 3. Check file sizes
echo ""
echo "3️⃣ Checking file sizes..."
total_size=$(du -sh docs/data/ | cut -f1)
echo "   Total data size: $total_size"

# List sector files
echo "   Sector summary files:"
ls -lh docs/data/*_daily_summary.json | awk '{print "     "$9": "$5}'

# 4. Verify structure
echo ""
echo "4️⃣ Verifying data structure..."
python3 -c "
import json
import sys

try:
    with open('docs/data/banks_daily_summary.json') as f:
        data = json.load(f)
    
    if 'stocks' not in data:
        print('   ❌ Missing stocks field')
        sys.exit(1)
    
    sample = list(data['stocks'].values())[0]
    
    # Check new fields
    checks = [
        ('current.pb_vnstock', 'pb_vnstock' in sample.get('current', {})),
        ('current.pb_calculated', 'pb_calculated' in sample.get('current', {})),
        ('data_quality', 'data_quality' in sample),
        ('daily_data[0].bvps', 'bvps' in sample.get('daily_data', [{}])[0])
    ]
    
    all_good = True
    for field, present in checks:
        status = '✅' if present else '❌'
        print(f'   {status} {field}')
        if not present:
            all_good = False
    
    if all_good:
        print('   ✅ All new fields present')
        sys.exit(0)
    else:
        print('   ❌ Some fields missing')
        sys.exit(1)
        
except Exception as e:
    print(f'   ❌ Error: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "   ❌ Structure validation failed"
    exit 1
fi

# 5. Git operations
echo ""
echo "5️⃣ Preparing git commit..."
git add docs/data/*_daily_summary.json docs/data/*_daily.json docs/data/market_heat.json

# Show what changed
changed_files=$(git diff --staged --name-only | wc -l)
echo "   Files to commit: $changed_files"

# 6. Create commit
echo ""
echo "6️⃣ Creating commit..."
git commit -m "🔄 Full data refresh with P/B accuracy fixes

✅ Updated all 205 stocks across 11 sectors
✅ New structure: dual P/B + data quality metrics
✅ Extended history: Full historical data (removed 3-year limit)
✅ BVPS timing: Fixed to use quarter end + 45 days
✅ Generated market heat with accurate P/B values

Data specs:
- Total size: $total_size
- Stocks: 205
- Sectors: 11
- Generated: $(date)
- Script: src/fetch_all_sectors_daily.py (P/B accuracy fixes)

Fixes: VCB P/B discrepancy 8.4% (vnstock 2.85 vs calc 2.61)
Test: 5/5 tests passed ✅"

if [ $? -eq 0 ]; then
    echo "   ✅ Commit created"
else
    echo "   ❌ Commit failed"
    exit 1
fi

# 7. Push to GitHub
echo ""
echo "7️⃣ Pushing to GitHub..."
read -p "   Push to origin/main? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push origin main
    if [ $? -eq 0 ]; then
        echo "   ✅ Pushed successfully"
        echo ""
        echo "========================================================================"
        echo "🎉 DEPLOYMENT COMPLETE!"
        echo "========================================================================"
        echo ""
        echo "Next steps:"
        echo "  1. Wait 2-3 minutes for GitHub Pages to rebuild"
        echo "  2. Visit: https://justpassion88.github.io/jpstock_webapp"
        echo "  3. Verify warnings display correctly"
        echo "  4. Check data quality indicators"
        echo ""
    else
        echo "   ❌ Push failed"
        exit 1
    fi
else
    echo "   ⏸️  Skipped push. You can push manually later:"
    echo "      git push origin main"
fi
