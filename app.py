"""
Football Match Prediction Streamlit App - Beautiful UI Edition
Automates: today_matches.py → fetch_data.py → predict.py
"""

import streamlit as st
import pandas as pd
import subprocess
import os
import warnings
from datetime import datetime

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'

# Page configuration
st.set_page_config(
    page_title="Football Match Predictor",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean white and baby blue theme
st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary: #FFFFFF;
        --secondary: #E1F5FE;
        --accent: #81D4FA;
        --success: #4CAF50;
        --danger: #F44336;
        --warning: #FF9800;
    }
    
    /* System fonts */
    * {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    }
    
    /* Force text color to dark */
    body, p, div, span, h1, h2, h3, h4, h5, h6 {
        color: #263238 !important;
    }
    
    /* Links */
    a {
        color: #0097A7 !important;
    }
    
    /* Clean white background */
    [data-testid="stAppViewContainer"] { 
        background: white;
    }
    
    /* Light baby blue sections */
    [data-testid="stSidebar"] {
        background: #FAFBFC;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        background: #81D4FA !important;
        color: #01579B !important;
        height: 3.2em;
        border-radius: 6px;
        font-weight: 700;
        font-size: 1em;
        border: none;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(1, 87, 155, 0.12);
    }
    
    .stButton>button:hover {
        background: #4FC3F7 !important;
        box-shadow: 0 2px 6px rgba(1, 87, 155, 0.2) !important;
    }
    
    /* Success box */
    .success-box {
        padding: 1.5em;
        border-radius: 8px;
        background: #E8F5E9;
        border-left: 5px solid #4CAF50;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        color: #1B5E20;
        font-weight: 500;
    }
    
    /* Error box */
    .error-box {
        padding: 1.5em;
        border-radius: 8px;
        background: #FFEBEE;
        border-left: 5px solid #F44336;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        color: #B71C1C;
        font-weight: 500;
    }
    
    /* Info box */
    .info-box {
        padding: 1.5em;
        border-radius: 8px;
        background: #E0F2F1;
        border-left: 5px solid #4DB6AC;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        color: #004D40;
        font-weight: 500;
    }
    
    /* Card style */
    .metric-card {
        background: white;
        border-radius: 8px;
        padding: 1.5em;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        transform: translateY(-4px);
    }
    
    .metric-number {
        font-size: 2.8em;
        font-weight: 900;
        color: #0097A7;
    }
    
    .metric-label {
        color: #455A64;
        font-size: 0.75em;
        margin-top: 0.8em;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    
    /* Section header */
    .section-header {
        background: #E0F2F1;
        color: #004D40;
        padding: 1.25em 1.5em;
        border-radius: 6px;
        margin-bottom: 1.5em;
        border-left: 5px solid #4DB6AC;
        font-weight: 700;
        font-size: 1.05em;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
    }
    
    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 0.5em 1em;
        border-radius: 25px;
        font-size: 0.85em;
        font-weight: 600;
        margin: 0.3em;
    }
    
    .status-success {
        background: #4CAF50;
        color: white;
    }
    
    .status-pending {
        background: #FF9800;
        color: white;
    }
    
    .status-error {
        background: #F44336;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'pipeline_status' not in st.session_state:
    st.session_state.pipeline_status = {
        'step1': False,
        'step2': False,
        'step3': False
    }
if 'logs' not in st.session_state:
    st.session_state.logs = []

def clear_old_data():
    """Remove old data files to force fresh fetch"""
    data_files = [
        'live.csv',
        'extracted_features_complete.csv',
        'best_match_predictions.csv'
    ]
    
    cleared = []
    for filename in data_files:
        try:
            if os.path.exists(filename):
                os.remove(filename)
                cleared.append(filename)
        except Exception as e:
            pass
    
    return cleared

def run_script(script_name, step_name):
    """Run a Python script and capture output"""
    try:
        if not check_file_exists(script_name):
            error_msg = f"❌ Script '{script_name}' not found!"
            st.session_state.logs.append(error_msg)
            return False, error_msg
        
        env = os.environ.copy()
        env['PYTHONWARNINGS'] = 'ignore'
        env['PYTHONIOENCODING'] = 'utf-8'
        
        result = subprocess.run(
            ['python', '-X', 'utf8', script_name],
            capture_output=True,
            text=True,
            timeout=600,
            env=env,
            encoding='utf-8',
            errors='replace'
        )
        
        output = result.stdout + result.stderr
        
        if result.returncode == 0:
            return True, output
        else:
            return False, output
            
    except subprocess.TimeoutExpired:
        return False, "⏱️ Timeout after 10 minutes"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def check_file_exists(filename):
    """Check if a file exists"""
    return os.path.exists(filename)

def load_csv_safe(filename):
    """Safely load a CSV file"""
    try:
        if check_file_exists(filename):
            return pd.read_csv(filename), None
        else:
            return None, f"File '{filename}' not found"
    except Exception as e:
        return None, f"Error loading '{filename}': {str(e)}"

# ============================================================================
# HEADER
# ============================================================================
st.markdown("""
    <div style='background: white; padding: 2.5em 3em; border-radius: 6px; margin-bottom: 2.5em; text-align: center; color: #01579B; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08); border-top: 4px solid #81D4FA;'>
        <h1 style='font-size: 3.2em; margin: 0; font-weight: 900; letter-spacing: -0.5px;'>⚽ Football Prediction System</h1>
        <p style='font-size: 1.1em; margin: 0.8em 0 0 0; color: #0097A7; font-weight: 600;'>AI-Powered Match Analysis & Prediction Engine</p>
        <p style='font-size: 0.9em; margin: 0.5em 0 0 0; color: #546E7A; font-weight: 500;'>Fetch → Analyze → Predict</p>
    </div>
""", unsafe_allow_html=True)

# ============================================================================
# TOP STATS
# ============================================================================
col_stat1, col_stat2, col_stat3 = st.columns(3)

# Load match data
matches_df, _ = load_csv_safe('live.csv')
predictions_df, _ = load_csv_safe('best_match_predictions.csv')

with col_stat1:
    st.markdown("""
        <div class='metric-card'>
            <div class='metric-number'>"""+ (str(len(matches_df)) if matches_df is not None else "0") +"""</div>
            <div class='metric-label'>📅 Matches Loaded</div>
        </div>
    """, unsafe_allow_html=True)

with col_stat2:
    st.markdown("""
        <div class='metric-card'>
            <div class='metric-number'>"""+ (str(len(predictions_df)) if predictions_df is not None else "0") +"""</div>
            <div class='metric-label'>🎯 Predictions</div>
        </div>
    """, unsafe_allow_html=True)

with col_stat3:
    timestamp = datetime.now().strftime("%H:%M UTC")
    st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-number' style='font-size: 1.8em;'>{timestamp}</div>
            <div class='metric-label'>⏰ Last Updated</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# MAIN CONTENT - 3 COLUMNS
# ============================================================================
col_left, col_middle, col_right = st.columns([1, 1.5, 1.5])

# ============================================================================
# LEFT COLUMN - CONTROLS
# ============================================================================
with col_left:
    st.markdown("""
        <div class='section-header'>
            🎮 Pipeline Controls
        </div>
    """, unsafe_allow_html=True)
    
    # System Status
    st.markdown("**System Status**")
    
    model_files = ['ridge_home_model.pkl', 'ridge_away_model.pkl', 'scaler.pkl']
    script_files = ['today_matches.py', 'fetch_data.py', 'predict.py']
    
    models_ok = all(check_file_exists(f) for f in model_files)
    scripts_ok = all(check_file_exists(f) for f in script_files)
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        status = "✅" if models_ok else "❌"
        st.markdown(f"{status} **Models**")
    
    with col_l2:
        status = "✅" if scripts_ok else "❌"
        st.markdown(f"{status} **Scripts**")
    
    if models_ok and scripts_ok:
        st.markdown('<div class="success-box">✅ All systems ready</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="error-box">⚠️ Missing files</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Step-by-step buttons
    st.markdown("**⚙️ Pipeline Steps**")
    
    col_step1 = st.container()
    with col_step1:
        if st.button("1️⃣  FETCH MATCHES", use_container_width=True, key="btn_step1"):
            with st.spinner("🔄 Fetching matches from API..."):
                success, output = run_script('today_matches.py', 'Fetch Matches')
                st.session_state.pipeline_status['step1'] = success
                if success:
                    # Check if live.csv was actually created
                    if os.path.exists('live.csv'):
                        df = pd.read_csv('live.csv')
                        if len(df) > 0:
                            st.success(f"✅ Fetched {len(df)} matches!")
                        else:
                            st.warning("⚠️ API returned no matches. Try different dates.")
                    else:
                        st.warning("⚠️ No matches found for today. Try tomorrow's date.")
                        st.info("💡 Matches are available from 2026-01-24 onwards")
                else:
                    st.error("❌ Failed to fetch matches")
                    st.code(output[-500:] if len(output) > 500 else output)
    
    st.markdown("")
    
    col_step2 = st.container()
    with col_step2:
        # Check if step 1 has data before allowing step 2
        step2_disabled = not os.path.exists('live.csv')
        
        if step2_disabled:
            st.button("2️⃣  EXTRACT FEATURES", use_container_width=True, disabled=True)
            st.caption("⚠️ Run 'Fetch Matches' first")
        else:
            if st.button("2️⃣  EXTRACT FEATURES", use_container_width=True, key="btn_step2"):
                with st.spinner("🔄 Extracting features..."):
                    success, output = run_script('fetch_data.py', 'Extract Features')
                    st.session_state.pipeline_status['step2'] = success
                    if success:
                        st.success("✅ Features extracted!")
                    else:
                        st.error("❌ Failed to extract features")
                        st.code(output[-500:] if len(output) > 500 else output)
    
    st.markdown("")
    
    col_step3 = st.container()
    with col_step3:
        # Check if step 2 has data before allowing step 3
        step3_disabled = not os.path.exists('extracted_features_complete.csv')
        
        if step3_disabled:
            st.button("3️⃣  GENERATE PREDICTIONS", use_container_width=True, disabled=True)
            st.caption("⚠️ Run 'Extract Features' first")
        else:
            if st.button("3️⃣  GENERATE PREDICTIONS", use_container_width=True, key="btn_step3"):
                with st.spinner("🔄 Generating predictions..."):
                    success, output = run_script('predict.py', 'Generate Predictions')
                    st.session_state.pipeline_status['step3'] = success
                    if success:
                        st.success("✅ Predictions generated!")
                    else:
                        st.error("❌ Failed to generate predictions")
                        st.code(output[-500:] if len(output) > 500 else output)

# ============================================================================
# MIDDLE COLUMN - QUICK STATS
# ============================================================================
with col_middle:
    st.markdown("""
        <div class='section-header'>
            📊 Pipeline Status
        </div>
    """, unsafe_allow_html=True)
    
    # Status indicators
    col_status1, col_status2 = st.columns(2)
    
    with col_status1:
        status1 = "✅ Ready" if st.session_state.pipeline_status['step1'] else "⏳ Pending"
        st.markdown(f"**Step 1: Fetch**\n{status1}")
    
    with col_status2:
        status2 = "✅ Ready" if st.session_state.pipeline_status['step2'] else "⏳ Pending"
        st.markdown(f"**Step 2: Extract**\n{status2}")
    
    st.markdown(f"**Step 3: Predict**\n{'✅ Ready' if st.session_state.pipeline_status['step3'] else '⏳ Pending'}")
    
    st.markdown("---")
    
    # Predictions preview
    st.markdown("**📋 Latest Predictions**")
    
    if predictions_df is not None and len(predictions_df) > 0:
        # Show top 5 predictions
        display_cols = ['home_team_name', 'away_team_name', 'predicted_home_goals', 'predicted_away_goals', 'outcome_label']
        display_df = predictions_df[display_cols].head(5).copy()
        display_df.columns = ['Home', 'Away', 'H Goals', 'A Goals', 'Prediction']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.markdown('<div class="info-box">No predictions yet. Run the pipeline to generate predictions.</div>', unsafe_allow_html=True)

# ============================================================================
# RIGHT COLUMN - MATCH DETAILS
# ============================================================================
with col_right:
    st.markdown("""
        <div class='section-header'>
            🏟️  Today's Matches
        </div>
    """, unsafe_allow_html=True)
    
    if matches_df is not None and len(matches_df) > 0:
        st.markdown(f"**Total Matches:** {len(matches_df)}")
        st.markdown(f"**League:** {matches_df['league_name'].iloc[0] if 'league_name' in matches_df.columns else 'N/A'}")
        
        st.markdown("**Match List:**")
        for idx, match in matches_df.head(8).iterrows():
            home = match.get('home_name', 'Team')
            away = match.get('away_name', 'Team')
            st.markdown(f"⚽ {home} **vs** {away}")
    else:
        st.markdown('<div class="info-box">No matches loaded. Click "FETCH MATCHES" to start.</div>', unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# FOOTER - RUN ALL BUTTON
# ============================================================================
st.markdown("""
    <div class='section-header' style='text-align: center; margin-top: 2.5em; margin-bottom: 2em;'>
        🚀 Ready to Run the Full Pipeline?
    </div>
""", unsafe_allow_html=True)

col_run_left, col_run_center, col_run_right = st.columns([1, 2, 1])

with col_run_center:
    if st.button("▶️ RUN FULL PIPELINE", use_container_width=True, key="btn_run_all"):
        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        
        # Clear old data first
        status_placeholder.markdown("**🗑️ Clearing old data...**")
        cleared = clear_old_data()
        if cleared:
            st.info(f"🗑️ Removed old files: {', '.join(cleared)}")
        
        steps = [
            ('today_matches.py', 'Fetching Matches', 'live.csv'),
            ('fetch_data.py', 'Extracting Features', 'extracted_features_complete.csv'),
            ('predict.py', 'Generating Predictions', 'best_match_predictions.csv')
        ]
        
        for i, (script, label, output_file) in enumerate(steps):
            status_placeholder.markdown(f"**{label}...**")
            progress_bar.progress((i + 0.5) / len(steps))
            
            success, output = run_script(script, label)
            
            if success:
                # For fetch step, check if live.csv was created and has data
                if output_file == 'live.csv':
                    if not os.path.exists('live.csv'):
                        st.error("❌ Fetch step completed but no matches found")
                        st.info("💡 Matches are available from 2026-01-24 onwards. Try running with future dates.")
                        break
                    df = pd.read_csv('live.csv')
                    if len(df) == 0:
                        st.error("❌ API returned no matches for the requested dates")
                        st.info("💡 Try a different date range or check API availability")
                        break
                    st.success(f"✅ {label} - Found {len(df)} matches")
                else:
                    progress_bar.progress((i + 1) / len(steps))
                    st.success(f"✅ {label}")
            else:
                st.error(f"❌ {label} failed")
                st.code(output[-500:] if len(output) > 500 else output)
                break
        else:
            progress_bar.progress(1.0)
            status_placeholder.markdown("**✅ Pipeline Complete!**")
            st.balloons()
            st.success("🎉 All steps completed successfully!")

st.markdown("---")

# ============================================================================
# EXTENDED PREDICTIONS TABLE
# ============================================================================
st.markdown("""
    <div class='section-header'>
        📊 Complete Predictions Table
    </div>
""", unsafe_allow_html=True)

if predictions_df is not None and len(predictions_df) > 0:
    # Create tabs for different views
    tab1, tab2 = st.tabs(["Summary View", "Full Details"])
    
    with tab1:
        # Summary view with key columns
        summary_cols = ['home_team_name', 'away_team_name', 'predicted_home_goals', 'predicted_away_goals', 'outcome_label', 'CTMCL', 'confidence_category']
        available_cols = [col for col in summary_cols if col in predictions_df.columns]
        summary_df = predictions_df[available_cols].copy()
        
        # Rename for display
        summary_df.columns = [col.replace('_', ' ').title() for col in summary_df.columns]
        
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        st.download_button(
            label="📥 Download Summary (CSV)",
            data=summary_df.to_csv(index=False),
            file_name="predictions_summary.csv",
            mime="text/csv"
        )
    
    with tab2:
        # Full table with all columns
        full_df = predictions_df.copy()
        full_df.columns = [col.replace('_', ' ').title() for col in full_df.columns]
        
        st.dataframe(full_df, use_container_width=True, hide_index=True, height=600)
        
        st.download_button(
            label="📥 Download Full Details (CSV)",
            data=full_df.to_csv(index=False),
            file_name="predictions_full.csv",
            mime="text/csv"
        )
else:
    st.markdown('<div class="info-box">📊 No predictions available yet. Run the pipeline to generate predictions.</div>', unsafe_allow_html=True)

st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("🗑️ Clear Data", use_container_width=True):
            cleared = clear_old_data()
            if cleared:
                st.success(f"✅ Cleared: {len(cleared)} files")
            else:
                st.info("No old files to clear")
    
    with col_s2:
        if st.button("🗑️ Clear Logs", use_container_width=True):
            st.session_state.logs = []
            st.success("Logs cleared")
    
    st.markdown("---")
    st.markdown("### 📝 About")
    st.markdown("""
    This system automates football match predictions using:
    
    - **API:** FootyStats API for match data
    - **ML:** Ridge Regression models for predictions
    - **Features:** 40+ engineered match statistics
    """)
    
    st.markdown("---")
    st.markdown("### 📚 Documentation")
    st.markdown("""
    - [QUICK_START.md](QUICK_START.md)
    - [CODE_ANALYSIS.md](CODE_ANALYSIS.md)
    - [README.md](README.md)
    """)
