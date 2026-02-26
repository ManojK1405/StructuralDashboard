import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import joblib
import numpy as np
import os

# ======================================================
# PAGE SETUP & STYLING
# ======================================================
st.set_page_config(
    page_title="Structural AI Dashboard",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a beautiful, premium design
st.markdown("""
<style>
    /* Global font and background */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #090e17 0%, #111827 100%);
        color: #f3f4f6;
    }
    
    /* Header styling */
    .main-header {
        background: rgba(17, 24, 39, 0.4);
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    
    h1, h2, h3 {
        color: #f9fafb !important;
    }
    
    .gradient-text {
        background: linear-gradient(120deg, #14b8a6, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.75rem;
        letter-spacing: -0.5px;
    }
    
    .sub-text {
        color: #9ca3af;
        font-size: 1.15rem;
        margin-top: 8px;
        font-weight: 400;
    }
    
    .stSelectbox label, .stNumberInput label {
        color: #d1d5db !important;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    
    /* Metrics cards */
    [data-testid="stMetricValue"] {
        color: #14b8a6 !important;
        font-weight: 800;
        font-size: 2.2rem;
    }
    [data-testid="stMetricLabel"] {
        color: #9ca3af !important;
        font-size: 1.05rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    [data-testid="stMetricDelta"] {
        font-size: 0.95rem;
    }
    div[data-testid="metric-container"] {
        background: rgba(30, 41, 59, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 1.75rem;
        border-radius: 16px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 25px rgba(0, 0, 0, 0.3);
        border-color: rgba(20, 184, 166, 0.5);
        background: rgba(30, 41, 59, 0.5);
    }
    
    /* Button style */
    .stButton > button {
        background: linear-gradient(135deg, #0d9488, #2563eb);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.8rem 2.5rem;
        font-weight: 600;
        font-size: 1.05rem;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.25);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #14b8a6, #3b82f6);
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.4);
        transform: translateY(-2px);
    }
    
    hr {
        border-color: rgba(255,255,255,0.1);
        margin: 3rem 0;
    }
    
    .info-box {
        background: rgba(56, 189, 248, 0.1);
        border-left: 4px solid #38bdf8;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Custom header
st.markdown("""
<div class="main-header">
    <h2 style="font-weight:400; font-size:1.2rem; color:#94a3b8; text-transform:uppercase; letter-spacing:2px; margin-bottom:0.5rem;">Walchand Institute Of Technology</h2>
    <div class="gradient-text">AI Structural Predictor</div>
    <div class="sub-text">Advanced Response Prediction & Trend Analysis for Multi-Storey RC Buildings</div>
</div>
""", unsafe_allow_html=True)

# ======================================================
# LOAD DATA & MODELS
# ======================================================
@st.cache_data
def load_data():
    try:
        # Load the augmented data for the best trends view!
        data_file = "Structural_ML_Combined_Dataset_Augmented.csv"
        if not os.path.exists(data_file):
            data_file = "Structural_ML_Combined_Dataset.csv"
            
        df = pd.read_csv(data_file)
        if "Aspect_Ratio" not in df.columns:
            df["Bay_Number"] = df["Plan_Size"].str.extract(r'(\d+)').astype(int)
            df["Height_m"] = df["Storeys"] * 3
            df["Aspect_Ratio"] = df["Height_m"] / df["Bay_Number"]
        return df
    except Exception:
        return None

df = load_data()

@st.cache_resource
def load_models():
    model_path = "structural_models.pkl"
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None

trained_models = load_models()

if df is None:
    st.error("Could not load the dataset. Please ensure 'Structural_ML_Combined_Dataset.csv' exists.")
    st.stop()

max_storeys = df["Storeys"].max()
max_bay = df["Bay_Number"].max()

# Use sidebar for navigation/controls
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2830/2830302.png", width=60)
    st.markdown("### 🎛️ Dashboard Controls")
    
    st.markdown("---")
    st.markdown("### 📊 Analysis Mode")
    mode = st.radio("Select View:", ["AI Prediction Tool", "Data Trends & Insights"])
    
    st.markdown("---")
    st.markdown("""
    <div style='background: rgba(255,255,255,0.05); padding:15px; border-radius:10px; font-size:0.9rem;'>
        <b>About this Dashboard:</b><br><br>
        Predicts key structural parameters (drift, displacement, base shear) using advanced Machine Learning models trained on varied RC building configurations.
    </div>
    """, unsafe_allow_html=True)

# Template for Plotly charts (dark mode)
plotly_template = "plotly_dark"
chart_bg = 'rgba(0,0,0,0)'
paper_bg = 'rgba(0,0,0,0)'
colors = px.colors.qualitative.Pastel

if mode == "Data Trends & Insights":
    st.markdown("### 📈 Data Trends Explorer")
    st.markdown("<div class='sub-text' style='margin-bottom:2rem;'>Explore how different structural configurations affect the building response under various soil conditions.</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        soil = st.selectbox("Select Soil Profile", df["Soil_Profile"].unique())
    with col2:
        output_param_map = {
            "Roof Displacement (mm)": "Roof_Displacement_mm",
            "Storey Drift (mm)": "Storey_Drift_mm",
            "Beam Bending Moment (kNm)": "Beam_Bending_Moment_kNm",
            "Column Axial Force (kN)": "Column_Axial_Force_kN",
            "Base Shear (kN)": "Base_Shear_kN"
        }
        display_output = st.selectbox("Select Output Parameter", list(output_param_map.keys()))
        output = output_param_map[display_output]

    filtered = df[df["Soil_Profile"] == soil]
    
    # CHARTS (Row 1)
    ch1, ch2 = st.columns(2)
    with ch1:
        fig1 = px.line(
            filtered, x="Storeys", y=output, markers=True,
            title=f"{display_output} vs Storeys",
            color_discrete_sequence=[colors[0]]
        )
        fig1.update_layout(template=plotly_template, plot_bgcolor=chart_bg, paper_bgcolor=paper_bg, 
                           margin=dict(l=20, r=20, t=50, b=20), hovermode="x unified")
        st.plotly_chart(fig1, use_container_width=True)

    with ch2:
        fig2 = px.line(
            filtered, x="Bay_Number", y=output, markers=True,
            title=f"{display_output} vs Bay Number",
            color_discrete_sequence=[colors[1]]
        )
        fig2.update_layout(template=plotly_template, plot_bgcolor=chart_bg, paper_bgcolor=paper_bg,
                           margin=dict(l=20, r=20, t=50, b=20), hovermode="x unified")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    
    # CHARTS (Row 2)
    ch3, ch4 = st.columns(2)
    with ch3:
        st.markdown("#### Soil Profile Comparison")
        fig3 = px.line(
            df, x="Storeys", y=output, color="Soil_Profile", markers=True,
            color_discrete_sequence=colors
        )
        fig3.update_layout(template=plotly_template, plot_bgcolor=chart_bg, paper_bgcolor=paper_bg)
        st.plotly_chart(fig3, use_container_width=True)
        
    with ch4:
        st.markdown("#### Parameter Correlation")
        # Compute correlation
        corr = df.select_dtypes(include=[np.number]).corr()
        # Clean up labels for display
        corr.columns = [c.replace('_', ' ') for c in corr.columns]
        corr.index = [c.replace('_', ' ') for c in corr.index]
        
        fig4 = px.imshow(
            corr, text_auto=".2f", aspect="auto",
            color_continuous_scale="RdBu_r"
        )
        fig4.update_layout(template=plotly_template, plot_bgcolor=chart_bg, paper_bgcolor=paper_bg,
                           margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig4, use_container_width=True)


elif mode == "AI Prediction Tool":
    st.markdown("### 🤖 Neural Engine Predictor")
    st.markdown("<div class='sub-text' style='margin-bottom:2rem;'>Provide structural configurations below to instantly estimate architectural response using the trained AI ensemble.</div>", unsafe_allow_html=True)
    
    if trained_models is None:
        st.warning("⚠️ Predictive models are not trained yet! Please run the training script to generate 'structural_models.pkl'.")
    else:
        # Input Section
        with st.container():
            st.markdown("#### Building Configuration")
            input_col1, input_col2, input_col3 = st.columns(3)
            
            with input_col1:
                storeys = st.number_input("Number of Storeys", 1, 60, 20, help="E.g., 20 floors")
            with input_col2:
                bay = st.number_input("Bay Number", 1, 30, 6, help="E.g., 6 bays")
            with input_col3:
                soil = st.selectbox("Soil Profile", df["Soil_Profile"].unique())
            
            height = storeys * 3
            aspect_ratio = height / bay
            
            st.markdown(f"<div class='info-box'>📐 <b>Calculated Aspect Ratio (h/b):</b> {round(aspect_ratio,2)} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Est. Height:</b> {height}m</div>", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        predict_btn = st.button("🚀 Generate Structural Prediction")
        
        if predict_btn:
            with st.spinner("Analyzing structural dynamics..."):
                # Handle boundaries for the model input
                clipped_storeys = min(storeys, max_storeys)
                clipped_bay = min(bay, max_bay)

                # Ensure order of columns matches the training features
                input_df = pd.DataFrame({
                    "Storeys": [clipped_storeys],
                    "Bay_Number": [clipped_bay],
                    "Aspect_Ratio": [height/clipped_bay],
                    "Soil_Profile": [soil]
                })

                preds = {}
                for target, model in trained_models.items():
                    preds[target] = model.predict(input_df)[0]

                # Physics-based extrapolation if exceeding training bounds
                extrapolated = False
                if storeys > max_storeys:
                    extrapolated = True
                    height_ratio = storeys / max_storeys
                    span_ratio = bay / max_bay
                    area_ratio = (bay**2) / (max_bay**2)

                    preds["Roof_Displacement_mm"] *= height_ratio**3
                    preds["Storey_Drift_mm"] *= height_ratio
                    preds["Column_Axial_Force_kN"] *= height_ratio
                    preds["Base_Shear_kN"] *= area_ratio * height_ratio
                    preds["Beam_Bending_Moment_kNm"] *= span_ratio**2

                st.markdown("### 📊 Prediction Dashboard")
                if extrapolated:
                    st.warning("⚠️ Note: Storeys exceed training data range. Physics-based extrapolation applied to predictions.")
                
                # Highlight drift limits
                drift_limit = (3/250)*1000  # Based on IS 1893 (approx)
                drift_status = "🔴 Exceeds Limit" if preds["Storey_Drift_mm"] > drift_limit else "🟢 Within Permissible Limits"
                
                # Metrics layout
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric("Roof Displacement", f"{preds['Roof_Displacement_mm']:.2f} mm")
                with m2:
                    st.metric("Storey Drift", f"{preds['Storey_Drift_mm']:.2f} mm", delta=drift_status, delta_color="inverse" if preds["Storey_Drift_mm"] > drift_limit else "normal")
                with m3:
                    st.metric("Base Shear", f"{preds['Base_Shear_kN']:.2f} kN")
                
                st.markdown("<br>", unsafe_allow_html=True)
                m4, m5, m6 = st.columns(3)
                with m4:
                    st.metric("Beam Bending Moment", f"{preds['Beam_Bending_Moment_kNm']:.2f} kNm")
                with m5:
                    st.metric("Column Axial Force", f"{preds['Column_Axial_Force_kN']:.2f} kN")
                
                # Add a viz of drift
                progress = min(((preds['Storey_Drift_mm'] / drift_limit) * 100), 100)
                st.markdown("#### Drift Limit Capacity")
                st.progress(int(progress))
                st.caption(f"Drift is at {progress:.1f}% of the maximum permissible limit ({drift_limit:.2f} mm)")
