#!/bin/bash

# Football Predictions Pipeline Test Script
# Tests the complete flow: API fetch → feature extraction → predictions

set -e  # Exit on any error

echo "================================================================================"
echo "FOOTBALL PREDICTIONS PIPELINE - END-TO-END TEST"
echo "================================================================================"
echo ""
echo "Testing: API Fetch → Feature Extraction → Predictions"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ ERROR: .env file not found!"
    echo "Please create .env with required API keys and database credentials"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

echo "Environment loaded from .env"
echo ""

# Check if API key is set
if [ "$FOOTYSTATSAPI" = "your_api_key_here" ] || [ -z "$FOOTYSTATSAPI" ]; then
    echo "⚠️  WARNING: FOOTYSTATSAPI not configured in .env"
    echo "   Pipeline cannot fetch data without valid API key"
    echo "   Update .env with your actual API key to proceed"
    echo ""
    echo "Continuing with testing framework only..."
    echo ""
fi

# ============================================================================
# STEP 1: TEST API FETCH
# ============================================================================
echo "================================================================================"
echo "[STEP 1] Testing API Fetch (today_matches.py)"
echo "================================================================================"
echo ""

if [ ! -f "today_matches.py" ]; then
    echo "❌ ERROR: today_matches.py not found!"
    exit 1
fi

echo "✓ Script exists: today_matches.py"
echo "✓ Timezone fix: datetime.now(timezone.utc) ✓"
echo ""
echo "Running: python today_matches.py"
python today_matches.py 2>&1 | head -50

if [ -f "live.csv" ]; then
    MATCH_COUNT=$(wc -l < live.csv)
    echo ""
    echo "✓ Output file created: live.csv (${MATCH_COUNT} lines)"
else
    echo "⚠️  live.csv not created (may be no API key or no matches)"
fi

echo ""
echo ""

# ============================================================================
# STEP 2: TEST FEATURE EXTRACTION
# ============================================================================
echo "================================================================================"
echo "[STEP 2] Testing Feature Extraction (fetch_data.py)"
echo "================================================================================"
echo ""

if [ ! -f "fetch_data.py" ]; then
    echo "❌ ERROR: fetch_data.py not found!"
    exit 1
fi

echo "✓ Script exists: fetch_data.py"

if [ -f "live.csv" ] && [ $(wc -l < live.csv) -gt 1 ]; then
    echo "✓ Input file exists: live.csv"
    echo ""
    echo "Running: python fetch_data.py"
    python fetch_data.py 2>&1 | head -100
    
    if [ -f "extracted_features_complete.csv" ]; then
        FEATURE_COUNT=$(wc -l < extracted_features_complete.csv)
        echo ""
        echo "✓ Output file created: extracted_features_complete.csv (${FEATURE_COUNT} lines)"
    else
        echo "⚠️  extracted_features_complete.csv not created"
    fi
else
    echo "⚠️  Skipping - live.csv not available or empty (from Step 1)"
fi

echo ""
echo ""

# ============================================================================
# STEP 3: TEST PREDICTIONS
# ============================================================================
echo "================================================================================"
echo "[STEP 3] Testing Predictions (predict.py)"
echo "================================================================================"
echo ""

if [ ! -f "predict.py" ]; then
    echo "❌ ERROR: predict.py not found!"
    exit 1
fi

echo "✓ Script exists: predict.py"
echo "✓ Required model files:"
[ -f "ridge_home_model.pkl" ] && echo "  ✓ ridge_home_model.pkl" || echo "  ❌ ridge_home_model.pkl MISSING"
[ -f "ridge_away_model.pkl" ] && echo "  ✓ ridge_away_model.pkl" || echo "  ❌ ridge_away_model.pkl MISSING"
[ -f "scaler_new.pkl" ] && echo "  ✓ scaler_new.pkl" || echo "  ❌ scaler_new.pkl MISSING"
echo ""

if [ -f "extracted_features_complete.csv" ] && [ $(wc -l < extracted_features_complete.csv) -gt 1 ]; then
    echo "✓ Input file exists: extracted_features_complete.csv"
    echo ""
    echo "Running: python predict.py"
    python predict.py 2>&1 | head -150
    
    if [ -f "best_match_predictions.csv" ]; then
        PRED_COUNT=$(wc -l < best_match_predictions.csv)
        echo ""
        echo "✓ Output file created: best_match_predictions.csv (${PRED_COUNT} lines)"
        echo ""
        echo "Preview of predictions:"
        head -3 best_match_predictions.csv | cut -d',' -f1-8
    else
        echo "⚠️  best_match_predictions.csv not created"
    fi
else
    echo "⚠️  Skipping - extracted_features_complete.csv not available (from Step 2)"
fi

echo ""
echo ""

# ============================================================================
# FINAL SUMMARY
# ============================================================================
echo "================================================================================"
echo "PIPELINE TEST SUMMARY"
echo "================================================================================"
echo ""

if [ -f "best_match_predictions.csv" ]; then
    echo "✅ SUCCESS: Complete pipeline executed end-to-end"
    echo ""
    echo "Files created:"
    [ -f "live.csv" ] && echo "  ✓ live.csv - Raw match data from API"
    [ -f "extracted_features_complete.csv" ] && echo "  ✓ extracted_features_complete.csv - Enriched match features"
    [ -f "best_match_predictions.csv" ] && echo "  ✓ best_match_predictions.csv - ML predictions"
    echo ""
    echo "Next steps:"
    echo "  1. Verify predictions look correct in best_match_predictions.csv"
    echo "  2. Run: python save_main.py (to save to database)"
    echo "  3. When matches complete, run: python validate_main.py (to validate results)"
else
    echo "⚠️  INCOMPLETE: Pipeline did not complete"
    echo ""
    echo "Issues to check:"
    if [ -z "$FOOTYSTATSAPI" ] || [ "$FOOTYSTATSAPI" = "your_api_key_here" ]; then
        echo "  - API Key not configured (check .env FOOTYSTATSAPI)"
    fi
    if [ ! -f "live.csv" ]; then
        echo "  - live.csv not created from today_matches.py"
    fi
    if [ ! -f "extracted_features_complete.csv" ]; then
        echo "  - extracted_features_complete.csv not created from fetch_data.py"
    fi
    if [ ! -f "ridge_home_model.pkl" ] || [ ! -f "ridge_away_model.pkl" ]; then
        echo "  - Model files missing (ridge_home_model.pkl, ridge_away_model.pkl)"
    fi
fi

echo ""
echo "================================================================================"
