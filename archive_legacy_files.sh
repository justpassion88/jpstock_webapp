#!/bin/bash
# Archive legacy quarterly JSON files
# These files are no longer used - daily data is the new standard

echo "📦 Archiving legacy quarterly JSON files..."

# Create archive directory
mkdir -p docs/data/archive_quarterly

# List of legacy quarterly files to archive
LEGACY_FILES=(
    "banks.json"
    "banks_v2.json"
    "raw_bank_data.json"
    "raw_bank_data_v2.json"
    "realestate.json"
    "securities.json"
    "energy.json"
    "oilgas.json"
    "steel.json"
    "construction.json"
    "insurance.json"
    "retail.json"
    "technology.json"
    "chemicals.json"
)

# Move files to archive
for file in "${LEGACY_FILES[@]}"; do
    if [ -f "docs/data/$file" ]; then
        echo "  ✓ Archiving $file"
        mv "docs/data/$file" "docs/data/archive_quarterly/"
    else
        echo "  ⚠ $file not found (already removed?)"
    fi
done

echo ""
echo "✅ Archive complete!"
echo "   Moved files to: docs/data/archive_quarterly/"
echo ""
echo "📊 Current data structure:"
echo "   ✅ Keep: *_daily.json (11 files - full data)"
echo "   ✅ Keep: *_daily_summary.json (11 files - frontend)"
echo "   ✅ Keep: market_heat.json, bot_results.json, recommendations.json"
echo "   📦 Archived: 14 quarterly files"
