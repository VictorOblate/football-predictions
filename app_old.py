"""
Football Match Prediction Streamlit App
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

# Custom CSS for beautiful modern UI
st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary: #1f77d2;
        --success: #00b894;
        --danger: #ff6b6b;
        --warning: #ffa502;
        --dark: #2c3e50;
    }
    
    /* Typography */
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
    }
    
    /* Main container background */
    [data-testid="stAppViewContainer"] > .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Streamlit buttons - Primary */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        height: 3.5em;
        border-radius: 10px;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        font-size: 1.1em;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        transform: translateY(-2px);
    }
    
    .stButton>button:active {
        transform: translateY(0);
    }
    
    /* Cards and boxes */
    .success-box {
        padding: 1.5em;
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(0, 184, 148, 0.1) 0%, rgba(0, 184, 148, 0.05) 100%);
        border-left: 5px solid #00b894;
        box-shadow: 0 4px 12px rgba(0, 184, 148, 0.2);
    }
    
    .error-box {
        padding: 1.5em;
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(255, 107, 107, 0.05) 100%);
        border-left: 5px solid #ff6b6b;
        box-shadow: 0 4px 12px rgba(255, 107, 107, 0.2);
    }
    
    .info-box {
        padding: 1.5em;
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(31, 119, 210, 0.1) 0%, rgba(31, 119, 210, 0.05) 100%);
        border-left: 5px solid #1f77d2;
        box-shadow: 0 4px 12px rgba(31, 119, 210, 0.2);
    }
    
    .warning-box {
        padding: 1.5em;
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(255, 165, 2, 0.1) 0%, rgba(255, 165, 2, 0.05) 100%);
        border-left: 5px solid #ffa502;
        box-shadow: 0 4px 12px rgba(255, 165, 2, 0.2);
    }
    
    /* Section headers */
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5em;
        border-radius: 10px;
        margin-bottom: 1em;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Progress tracker */
    .progress-item {
        display: flex;
        align-items: center;
        padding: 1em;
        margin: 0.5em 0;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.95);
    }
    
    .progress-status {
        font-weight: 600;
        margin-left: auto;
    }
    
    /* Stats cards */
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 1.5em;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        transform: translateY(-4px);
    }
    
    .stat-number {
        font-size: 2.5em;
        font-weight: bold;
        color: #667eea;
    }
    
    .stat-label {
        color: #7f8c8d;
        font-size: 0.9em;
        margin-top: 0.5em;
    }
    
    /* Match table */
    .dataframe {
        border-collapse: collapse;
        width: 100%;
    }
    
    .dataframe th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1em;
        text-align: left;
        border-radius: 8px 8px 0 0;
    }
    
    .dataframe td {
        padding: 1em;
        border-bottom: 1px solid #ecf0f1;
    }
    
    .dataframe tbody tr:hover {
        background-color: #f8f9fa;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] button {
        background-color: transparent;
        border-radius: 8px 8px 0 0;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white;
        border-bottom: 3px solid #667eea;
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

def run_script(script_name, step_name):
    """Run a Python script and capture output"""
    try:
        # Check if script exists
        if not check_file_exists(script_name):
            error_msg = f"❌ Script '{script_name}' not found! Please ensure the file exists in the working directory."
            st.session_state.logs.append(error_msg)
            return False, error_msg
        
        st.session_state.logs.append(f"🔄 Starting {step_name}...")
        st.session_state.logs.append(f"   Running: {script_name}")
        
        # Set up environment to suppress warnings and handle encoding
        env = os.environ.copy()
        env['PYTHONWARNINGS'] = 'ignore'
        env['PYTHONIOENCODING'] = 'utf-8'  # Force UTF-8 encoding for Windows
        
        # Run the script
        result = subprocess.run(
            ['python', '-X', 'utf8', script_name],  # Force UTF-8 mode
            capture_output=True,
            text=True,
            timeout=300000,  # 5 minute timeout
            env=env,
            encoding='utf-8',  # Explicitly set encoding
            errors='replace'  # Replace problematic characters instead of crashing
        )
        
        # Store output
        output = result.stdout + result.stderr
        if output.strip():
            st.session_state.logs.append(output)
        
        if result.returncode == 0:
            st.session_state.logs.append(f"✅ {step_name} completed successfully!")
            return True, output
        else:
            st.session_state.logs.append(f"❌ {step_name} failed with error code {result.returncode}")
            if not output.strip():
                st.session_state.logs.append("   No error output captured")
            return False, output
            
    except subprocess.TimeoutExpired:
        error_msg = f"⏱️ {step_name} timed out after 5 minutes"
        st.session_state.logs.append(error_msg)
        return False, error_msg
    except FileNotFoundError:
        error_msg = f"❌ Python interpreter or script '{script_name}' not found"
        st.session_state.logs.append(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"❌ Error running {step_name}: {str(e)}"
        st.session_state.logs.append(error_msg)
        return False, error_msg

def check_file_exists(filename):
    """Check if a file exists"""
    return os.path.exists(filename)

def load_csv_safe(filename):
    """Safely load a CSV file"""
    try:
        if check_file_exists(filename):
            df = pd.read_csv(filename)
            return df, None
        else:
            return None, f"File '{filename}' not found"
    except Exception as e:
        return None, f"Error loading '{filename}': {str(e)}"

# Header with beautiful hero section
st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 3em; border-radius: 15px; margin-bottom: 2em; text-align: center; color: white; box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);'>
        <h1 style='font-size: 3em; margin: 0; font-weight: 800;'>⚽ Football Match Prediction System</h1>
        <p style='font-size: 1.3em; margin: 0.5em 0 0 0; opacity: 0.95;'>AI-Powered Match Analysis & Prediction Engine</p>
        <p style='font-size: 0.95em; margin: 0.8em 0 0 0; opacity: 0.85;'>Fetch Matches → Extract Features → Generate Predictions</p>
    </div>
""", unsafe_allow_html=True)

# Main layout with 3-column design
col1, col2, col3 = st.columns([1, 1.5, 1.5])

# ============================================================================
# LEFT COLUMN - PIPELINE CONTROLS
# ============================================================================
with col1:
    st.markdown("""
        <div class='section-header'>
            <h2 style='margin: 0; font-size: 1.5em;'>🎮 Pipeline Controls</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Check for required files
    st.markdown("**📋 System Status**")
    
    col1a, col1b = st.columns(2)
    
    # Model files
    required_files = {
        'Models': ['ridge_home_model.pkl', 'ridge_away_model.pkl', 'scaler.pkl'],
        'Scripts': ['today_matches.py', 'fetch_data.py', 'predict.py']
    }
    
    all_files_present = True
    for category, files in required_files.items():
        st.markdown(f"**{category}:**")
        for f in files:
            exists = check_file_exists(f)
            icon = "✅" if exists else "❌"
            st.text(f"{icon} {f}")
            if not exists:
                all_files_present = False
    
    if not all_files_present:
        st.markdown('<div class="error-box">⚠️ Some required files are missing. Please upload them to continue.</div>', 
                   unsafe_allow_html=True)
    else:
        st.markdown('<div class="success-box">✅ All required files found</div>', 
                   unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Step-by-step execution
    st.markdown("#### Manual Step Execution")
    
    # Check if today_matches.py exists
    step1_available = check_file_exists('today_matches.py')
    
    if st.button("1️⃣ Fetch Today's Matches", key="step1", 
                disabled=not step1_available):
        with st.spinner("Fetching matches..."):
            success, output = run_script('today_matches.py', 'Step 1: Fetch Matches')
            st.session_state.pipeline_status['step1'] = success
            if success:
                st.success("✅ Matches fetched successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to fetch matches. Check logs for details.")
    
    if not step1_available:
        st.caption("⚠️ today_matches.py not found")
    
    if st.button("2️⃣ Extract Features", key="step2", 
                disabled=not check_file_exists('live.csv') or not check_file_exists('fetch_data.py')):
        with st.spinner("Extracting features..."):
            success, output = run_script('fetch_data.py', 'Step 2: Extract Features')
            st.session_state.pipeline_status['step2'] = success
            if success:
                st.success("✅ Features extracted successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to extract features. Check logs for details.")
    
    if not check_file_exists('live.csv'):
        st.caption("⚠️ Requires live.csv from Step 1")
    
    if st.button("3️⃣ Generate Predictions", key="step3",
                disabled=not check_file_exists('extracted_features_complete.csv') or not check_file_exists('predict.py')):
        with st.spinner("Generating predictions..."):
            success, output = run_script('predict.py', 'Step 3: Predict Results')
            st.session_state.pipeline_status['step3'] = success
            if success:
                st.success("✅ Predictions generated successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to generate predictions. Check logs for details.")
    
    if not check_file_exists('extracted_features_complete.csv'):
        st.caption("⚠️ Requires extracted_features_complete.csv from Step 2")
    
    st.markdown("---")
    
    # Full pipeline execution
    st.markdown("#### 🚀 Run Full Pipeline")
    
    can_run_pipeline = (check_file_exists('today_matches.py') and 
                       check_file_exists('fetch_data.py') and 
                       check_file_exists('predict.py') and
                       all_files_present)
    
    if st.button("▶️ RUN ALL STEPS", key="run_all", disabled=not can_run_pipeline):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1
        status_text.text("1/3: Fetching today's matches...")
        progress_bar.progress(10)
        success1, _ = run_script('today_matches.py', 'Step 1: Fetch Matches')
        st.session_state.pipeline_status['step1'] = success1
        
        if success1:
            progress_bar.progress(33)
            
            # Step 2
            status_text.text("2/3: Extracting features...")
            success2, _ = run_script('fetch_data.py', 'Step 2: Extract Features')
            st.session_state.pipeline_status['step2'] = success2
            
            if success2:
                progress_bar.progress(66)
                
                # Step 3
                status_text.text("3/3: Generating predictions...")
                success3, _ = run_script('predict.py', 'Step 3: Predict Results')
                st.session_state.pipeline_status['step3'] = success3
                
                if success3:
                    progress_bar.progress(100)
                    status_text.text("✅ Pipeline completed successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    status_text.text("❌ Failed at Step 3 - Check logs")
            else:
                status_text.text("❌ Failed at Step 2 - Check logs")
        else:
            status_text.text("❌ Failed at Step 1 - Check logs")
    
    if not can_run_pipeline:
        st.caption("⚠️ All scripts and model files must be present to run the full pipeline")
    
    # Clear logs button
    if st.button("🗑️ Clear Logs"):
        st.session_state.logs = []
        st.rerun()
    
    # Show recent logs in sidebar
    if st.session_state.logs:
        st.markdown("---")
        st.markdown("#### 📋 Recent Activity")
        # Show last 5 log entries
        recent_logs = st.session_state.logs[-5:]
        for log in recent_logs:
            if "✅" in log:
                st.success(log, icon="✅")
            elif "❌" in log or "Error" in log or "Failed" in log:
                st.error(log, icon="❌")
            elif "⚠️" in log or "Warning" in log:
                st.warning(log, icon="⚠️")
            elif "🔄" in log:
                st.info(log, icon="🔄")
            else:
                # Only show first 100 chars of detailed logs
                if len(log) > 100:
                    with st.expander("View details"):
                        st.text(log)
                else:
                    st.text(log)

with col2:
    st.markdown("### 📊 Results Viewer")
    
    # Tabs for different CSV files
    tabs = st.tabs(["1️⃣ Live Matches", "2️⃣ Extracted Features", "3️⃣ Predictions", "📝 Execution Logs"])
    
    # Tab 1: Live Matches
    with tabs[0]:
        st.markdown("#### Today's Matches (live.csv)")
        df, error = load_csv_safe('live.csv')
        
        if df is not None:
            st.markdown(f'<div class="info-box">📋 Total Matches: {len(df)}</div>', 
                       unsafe_allow_html=True)
            
            # Display options
            col_a, col_b = st.columns(2)
            with col_a:
                show_all = st.checkbox("Show all columns", key="live_all")
            with col_b:
                if st.button("⬇️ Download CSV", key="download_live"):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download live.csv",
                        data=csv,
                        file_name="live.csv",
                        mime="text/csv"
                    )
            
            if show_all:
                st.dataframe(df, use_container_width=True, height=400)
            else:
                # Show key columns
                key_cols = ['match_id', 'homeID', 'awayID', 'league_id', 'date_GMT']
                available_cols = [col for col in key_cols if col in df.columns]
                if available_cols:
                    st.dataframe(df[available_cols], use_container_width=True, height=400)
                else:
                    st.dataframe(df, use_container_width=True, height=400)
        else:
            st.markdown(f'<div class="info-box">ℹ️ {error}</div>', unsafe_allow_html=True)
            st.info("Run **Step 1: Fetch Today's Matches** to generate this file")
    
    # Tab 2: Extracted Features
    with tabs[1]:
        st.markdown("#### Extracted Features (extracted_features_complete.csv)")
        df, error = load_csv_safe('extracted_features_complete.csv')
        
        if df is not None:
            st.markdown(f'<div class="info-box">📋 Total Matches: {len(df)} | Features: {len(df.columns)}</div>', 
                       unsafe_allow_html=True)
            
            # Display options
            col_a, col_b = st.columns(2)
            with col_a:
                show_all = st.checkbox("Show all columns", key="features_all")
            with col_b:
                if st.button("⬇️ Download CSV", key="download_features"):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download extracted_features_complete.csv",
                        data=csv,
                        file_name="extracted_features_complete.csv",
                        mime="text/csv"
                    )
            
            if show_all:
                st.dataframe(df, use_container_width=True, height=400)
            else:
                # Show key columns
                key_cols = ['match_id', 'home_team_name', 'away_team_name', 
                           'team_a_xg_prematch', 'team_b_xg_prematch', 'CTMCL']
                available_cols = [col for col in key_cols if col in df.columns]
                if available_cols:
                    st.dataframe(df[available_cols], use_container_width=True, height=400)
                else:
                    st.dataframe(df.head(100), use_container_width=True, height=400)
        else:
            st.markdown(f'<div class="info-box">ℹ️ {error}</div>', unsafe_allow_html=True)
            st.info("Run **Step 2: Extract Features** to generate this file")
    
    # Tab 3: Predictions
    with tabs[2]:
        st.markdown("#### Match Predictions (best_match_predictions.csv)")
        df, error = load_csv_safe('best_match_predictions.csv')
        
        if df is not None:
            st.markdown(f'<div class="success-box">🎯 Total Predictions: {len(df)}</div>', 
                       unsafe_allow_html=True)
            
            # Summary statistics
            if 'outcome_label' in df.columns:
                col_s1, col_s2, col_s3 = st.columns(3)
                with col_s1:
                    home_wins = len(df[df['outcome_label'] == 'Home Win'])
                    st.metric("🏠 Home Wins", home_wins)
                with col_s2:
                    draws = len(df[df['outcome_label'] == 'Draw'])
                    st.metric("🤝 Draws", draws)
                with col_s3:
                    away_wins = len(df[df['outcome_label'] == 'Away Win'])
                    st.metric("✈️ Away Wins", away_wins)
            
            if 'predicted_total_goals' in df.columns:
                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    avg_goals = df['predicted_total_goals'].mean()
                    st.metric("⚽ Avg Total Goals", f"{avg_goals:.2f}")
                with col_g2:
                    over_25 = len(df[df['predicted_total_goals'] > 2.5])
                    st.metric("📈 Over 2.5 Goals", f"{over_25} ({over_25/len(df)*100:.1f}%)")
            
            st.markdown("---")
            
            # Display options
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                show_all = st.checkbox("Show all columns", key="pred_all")
            with col_b:
                filter_conf = st.selectbox("Filter by confidence", 
                                          ["All", "High", "Medium", "Low"],
                                          key="conf_filter")
            with col_c:
                if st.button("⬇️ Download CSV", key="download_pred"):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download best_match_predictions.csv",
                        data=csv,
                        file_name="best_match_predictions.csv",
                        mime="text/csv"
                    )
            
            # Apply confidence filter
            if filter_conf != "All" and 'confidence_category' in df.columns:
                df = df[df['confidence_category'] == filter_conf]
            
            if show_all:
                st.dataframe(df, use_container_width=True, height=400)
            else:
                # Show key prediction columns
                key_cols = ['match_id', 'home_team_name', 'away_team_name',
                           'predicted_home_goals', 'predicted_away_goals',
                           'predicted_total_goals', 'outcome_label', 'confidence_category']
                available_cols = [col for col in key_cols if col in df.columns]
                if available_cols:
                    st.dataframe(df[available_cols], use_container_width=True, height=400)
                else:
                    st.dataframe(df, use_container_width=True, height=400)
            
            # High confidence recommendations
            if 'confidence_category' in df.columns:
                st.markdown("---")
                st.markdown("#### 🎯 High Confidence Predictions")
                high_conf = df[df['confidence_category'] == 'High']
                if len(high_conf) > 0:
                    for _, row in high_conf.iterrows():
                        with st.expander(f"⚽ {row.get('home_team_name', 'Home')} vs {row.get('away_team_name', 'Away')}"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.write(f"**Prediction:** {row.get('outcome_label', 'N/A')}")
                            with col2:
                                st.write(f"**Score:** {row.get('predicted_home_goals', 0):.2f} - {row.get('predicted_away_goals', 0):.2f}")
                            with col3:
                                st.write(f"**Total Goals:** {row.get('predicted_total_goals', 0):.2f}")
                else:
                    st.info("No high confidence predictions found")
        else:
            st.markdown(f'<div class="info-box">ℹ️ {error}</div>', unsafe_allow_html=True)
            st.info("Run **Step 3: Generate Predictions** to generate this file")
    
    # Tab 4: Logs
    with tabs[3]:
        st.markdown("#### Execution Logs")
        
        if st.session_state.logs:
            log_text = "\n".join(st.session_state.logs)
            st.text_area("Logs", log_text, height=400)
        else:
            st.info("No logs yet. Run the pipeline to see execution logs.")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>⚽ Football Match Prediction System | Built with Streamlit</p>
    </div>
""", unsafe_allow_html=True)