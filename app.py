"""
Football Match Prediction Streamlit App - Premium UI Edition
Automates: today_matches.py → fetch_data.py → predict.py
"""

import streamlit as st
import pandas as pd
import subprocess
import os
import warnings
from datetime import datetime

# ============================================================================
# INITIAL CONFIG & FILTERS
# ============================================================================
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'

st.set_page_config(
    page_title="Pro-Stats | Football Predictor",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# PREMIUM CSS STYLING (Refined for depth and clarity)
# ============================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    }

    /* Main background - clean professional slate */
    [data-testid="stAppViewContainer"] { 
        background: #F8FAFC;
    }

    /* Hero Header Area */
    .hero-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        padding: 3.5rem 2rem;
        border-radius: 24px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255,255,255,0.1);
    }

    .hero-title {
        font-size: 3.2rem !important;
        font-weight: 800 !important;
        background: linear-gradient(to right, #38BDF8, #818CF8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 !important;
        letter-spacing: -1px;
    }

    .hero-subtitle {
        color: #94A3B8 !important;
        font-size: 1.1rem;
        font-weight: 500;
        margin-top: 0.5rem;
    }

    /* Metric Cards */
    .metric-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-4px);
        border-color: #38BDF8;
    }

    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0F172A;
    }

    .metric-label {
        color: #64748B;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Section Headers */
    .section-header {
        background: #F1F5F9;
        color: #1E293B;
        padding: 1rem 1.25rem;
        border-radius: 12px;
        margin-bottom: 1.25rem;
        font-weight: 700;
        font-size: 1rem;
        display: flex;
        align-items: center;
        gap: 8px;
        border-left: 4px solid #38BDF8;
    }

    /* Match List Items */
    .match-item-modern {
        background: white;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #E2E8F0;
        transition: all 0.2s ease;
    }

    .match-item-modern:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-color: #CBD5E1;
    }

    .vs-tag {
        background: #F1F5F9;
        color: #64748B;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 800;
    }

    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 0.4em 1em;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .status-ready { background: #DCFCE7; color: #166534; }
    .status-pending { background: #FEF3C7; color: #92400E; }
    .status-error { background: #FEE2E2; color: #991B1B; }

    /* Custom Buttons */
    .stButton>button {
        width: 100%;
        background: #0F172A !important;
        color: white !important;
        border-radius: 12px;
        padding: 0.7rem 1rem;
        font-weight: 600;
        border: none;
        transition: all 0.2s ease;
    }

    .stButton>button:hover {
        background: #38BDF8 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.4);
    }

    /* Streamlit UI Tweaks */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { background: transparent !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background: transparent; }
    .stTabs [data-baseweb="tab"] {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# CORE FUNCTIONS (Preserved Logic)
# ============================================================================
def clear_old_data():
    """Remove old data files to force fresh fetch"""
    data_files = ['live.csv', 'extracted_features_complete.csv', 'best_match_predictions.csv']
    cleared = []
    for filename in data_files:
        try:
            if os.path.exists(filename):
                os.remove(filename)
                cleared.append(filename)
        except Exception:
            pass
    return cleared

def run_script(script_name, step_name):
    """Run a Python script and capture output"""
    try:
        if not check_file_exists(script_name):
            error_msg = f"Script '{script_name}' not found!"
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
        return (result.returncode == 0, output)
    except subprocess.TimeoutExpired:
        return False, "⏱️ Timeout after 10 minutes"
    except Exception as e:
        return False, f"Error: {str(e)}"

def check_file_exists(filename):
    return os.path.exists(filename)

def load_csv_safe(filename):
    try:
        if check_file_exists(filename):
            return pd.read_csv(filename), None
        return None, f"File '{filename}' not found"
    except Exception as e:
        return None, f"Error: {str(e)}"

# ============================================================================
# INITIALIZATION
# ============================================================================
if 'pipeline_status' not in st.session_state:
    st.session_state.pipeline_status = {'step1': False, 'step2': False, 'step3': False}
if 'logs' not in st.session_state:
    st.session_state.logs = []

# ============================================================================
# HERO & METRICS
# ============================================================================
st.markdown("""
    <div class='hero-banner'>
        <h1 class='hero-title'>Football Match Predictor</h1>
        <p class='hero-subtitle'>AI-Powered Analytics & Strategic Forecasting Engine</p>
    </div>
""", unsafe_allow_html=True)

matches_df, _ = load_csv_safe('live.csv')
predictions_df, _ = load_csv_safe('best_match_predictions.csv')

m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(f"<div class='metric-card'><div class='metric-value'>{len(matches_df) if matches_df is not None else 0}</div><div class='metric-label'>Matches Found</div></div>", unsafe_allow_html=True)
with m2:
    st.markdown(f"<div class='metric-card'><div class='metric-value'>{len(predictions_df) if predictions_df is not None else 0}</div><div class='metric-label'>AI Predictions</div></div>", unsafe_allow_html=True)
with m3:
    st.markdown(f"<div class='metric-card'><div class='metric-value'>{datetime.now().strftime('%H:%M')}</div><div class='metric-label'>Last Sync (UTC)</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# MAIN INTERFACE
# ============================================================================
col_left, col_mid, col_right = st.columns([1.1, 1.3, 1.4], gap="medium")

# LEFT: PIPELINE CONTROLS
with col_left:
    st.markdown('<div class="section-header">⚙️ Pipeline Controls</div>', unsafe_allow_html=True)
    
    # System Health
    models_ok = all(check_file_exists(f) for f in ['ridge_home_model.pkl', 'ridge_away_model.pkl', 'scaler.pkl'])
    scripts_ok = all(check_file_exists(f) for f in ['today_matches.py', 'fetch_data.py', 'predict.py'])
    
    h1, h2 = st.columns(2)
    h1.markdown(f'<span class="status-badge {"status-ready" if models_ok else "status-error"}">Models</span>', unsafe_allow_html=True)
    h2.markdown(f'<span class="status-badge {"status-ready" if scripts_ok else "status-error"}">Scripts</span>', unsafe_allow_html=True)
    
    st.divider()

    # STEP 1
    if st.button("📡 FETCH MATCHES", key="btn_step1"):
        with st.spinner("Accessing API..."):
            success, output = run_script('today_matches.py', 'Fetch')
            st.session_state.pipeline_status['step1'] = success
            if success:
                st.toast("Matches fetched successfully!")
                st.rerun()

    # STEP 2
    s2_disabled = not check_file_exists('live.csv')
    if st.button("📊 EXTRACT FEATURES", key="btn_step2", disabled=s2_disabled):
        with st.spinner("Processing Stats..."):
            success, output = run_script('fetch_data.py', 'Extract')
            st.session_state.pipeline_status['step2'] = success
            if success: st.toast("Features generated!")

    # STEP 3
    s3_disabled = not check_file_exists('extracted_features_complete.csv')
    if st.button("🤖 PREDICT OUTCOMES", key="btn_step3", disabled=s3_disabled):
        with st.spinner("Running ML Models..."):
            success, output = run_script('predict.py', 'Predict')
            st.session_state.pipeline_status['step3'] = success
            if success: st.balloons()

# MID: STATUS & PREVIEW
with col_mid:
    st.markdown('<div class="section-header">📈 Pipeline Status</div>', unsafe_allow_html=True)
    
    for label, key in [("Step 1: Fetch", 'step1'), ("Step 2: Extract", 'step2'), ("Step 3: Predict", 'step3')]:
        status = st.session_state.pipeline_status[key]
        st.markdown(f'<div style="margin-bottom:8px;"><span class="status-badge {"status-ready" if status else "status-pending"}">{label}: {"Complete" if status else "Required"}</span></div>', unsafe_allow_html=True)
    
    st.divider()
    st.markdown("**Preview: Top Predictions**")
    if predictions_df is not None:
        st.dataframe(predictions_df[['home_team_name', 'away_team_name', 'outcome_label']].head(5), hide_index=True, use_container_width=True)
    else:
        st.caption("No prediction data available yet.")

# RIGHT: TODAY'S MATCHES
with col_right:
    st.markdown('<div class="section-header">📅 Today\'s Fixtures</div>', unsafe_allow_html=True)
    if matches_df is not None:
        for _, match in matches_df.head(10).iterrows():
            st.markdown(f"""
                <div class="match-item-modern">
                    <span style="font-weight:600; flex:1; text-align:right;">{match.get('home_name', 'Home')}</span>
                    <span class="vs-tag" style="margin: 0 15px;">VS</span>
                    <span style="font-weight:600; flex:1; text-align:left;">{match.get('away_name', 'Away')}</span>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No fixtures loaded. Run 'Fetch Matches' to begin.")

# ============================================================================
# FULL PIPELINE & RESULTS
# ============================================================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-header" style="justify-content: center;">🔥 Complete Automation Pipeline</div>', unsafe_allow_html=True)

if st.button("RUN FULL ANALYTICS SUITE", use_container_width=True):
    prog = st.progress(0)
    status_msg = st.empty()
    
    clear_old_data()
    steps = [('today_matches.py', 'Fetching Data'), ('fetch_data.py', 'Engineering Features'), ('predict.py', 'ML Forecasting')]
    
    for i, (script, msg) in enumerate(steps):
        status_msg.markdown(f"**Current Task:** {msg}...")
        success, out = run_script(script, msg)
        if not success:
            st.error(f"Failed at {msg}")
            with st.expander("Show Logs"): st.code(out)
            break
        prog.progress((i + 1) / len(steps))
    
    status_msg.markdown("**Pipeline Success!** Predictions are ready below.")
    st.balloons()
    st.rerun()

st.divider()

# PREDICTIONS TABLE
st.markdown('<div class="section-header">📊 Detailed Prediction Output</div>', unsafe_allow_html=True)

if predictions_df is not None:
    t1, t2 = st.tabs(["Summary View", "Technical Analysis"])
    with t1:
        cols = ['home_team_name', 'away_team_name', 'predicted_home_goals', 'predicted_away_goals', 'outcome_label']
        avail = [c for c in cols if c in predictions_df.columns]
        st.dataframe(predictions_df[avail], use_container_width=True, hide_index=True)
    with t2:
        st.dataframe(predictions_df, use_container_width=True, hide_index=True)
    
    st.download_button("📥 Export CSV", predictions_df.to_csv(index=False), "predictions.csv", use_container_width=True)
else:
    st.info("Run the pipeline to generate the analysis table.")

# ============================================================================
# SIDEBAR & FOOTER
# ============================================================================
with st.sidebar:
    st.markdown("### 🛠️ Workspace Tools")
    if st.button("Reset Everything", use_container_width=True):
        clear_old_data()
        st.session_state.pipeline_status = {'step1': False, 'step2': False, 'step3': False}
        st.rerun()
    
    st.divider()
    st.markdown("### 📝 About Pro-Stats")
    st.caption("Utilizes Ridge Regression models trained on historical performance, goal expectancy, and squad features.")
    st.caption(f"App Version: 1.2.0")

st.markdown("""
    <div style='text-align: center; padding: 2rem; color: #94A3B8; font-size: 0.85rem;'>
        Pro-Stats Prediction Engine &copy; 2026 | Data provided via FootyStats API
    </div>
""", unsafe_allow_html=True)