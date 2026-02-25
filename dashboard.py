import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import numpy as np

# ======================================================
# PAGE SETUP
# ======================================================

st.set_page_config(page_title="Structural AI Dashboard", layout="wide")

st.markdown("""
    <div style='text-align:center;'>
        <h2 style='color:#2E86C1; margin-bottom:5px;'>
            Walchand Institute Of Technology, Solapur
        </h2>
        <h4 style='margin-top:0px; margin-bottom:10px;'>
            Department of Civil Engineering
        </h4>
        <h1 style='color:#1F4E79; margin-top:10px;'>
            AI-Driven Structural Response Prediction and Trend Analysis
            for Multi-Storey RC Buildings
        </h1>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# ======================================================
# LOAD DATA
# ======================================================

df = pd.read_csv("Structural_ML_Combined_Dataset.csv")
df["Bay_Number"] = df["Plan_Size"].str.extract(r'(\d+)').astype(int)
df["Height_m"] = df["Storeys"] * 3
df["Aspect_Ratio"] = df["Height_m"] / df["Bay_Number"]

max_storeys = df["Storeys"].max()
max_bay = df["Bay_Number"].max()

trained_models = joblib.load("structural_models.pkl")


# ======================================================
# SECTION 2 — TREND ANALYSIS
# ======================================================

st.subheader("Trend Explorer")

soil = st.selectbox("Select Soil Profile", df["Soil_Profile"].unique())

output = st.selectbox(
    "Select Output Parameter",
    [
        "Roof_Displacement_mm",
        "Storey_Drift_mm",
        "Beam_Bending_Moment_kNm",
        "Column_Axial_Force_kN",
        "Base_Shear_kN"
    ]
)

filtered = df[df["Soil_Profile"] == soil]

col1, col2 = st.columns(2)

with col1:
    fig1 = px.line(
        filtered,
        x="Storeys",
        y=output,
        markers=True,
        title=f"{output} vs Storeys"
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.line(
        filtered,
        x="Bay_Number",
        y=output,
        markers=True,
        title=f"{output} vs Bay Number"
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ======================================================
# SECTION 3 — SOIL COMPARISON
# ======================================================

st.subheader("Soil Comparison (All Profiles)")

fig3 = px.line(
    df,
    x="Storeys",
    y=output,
    color="Soil_Profile",
    markers=True,
    title=f"{output} vs Storeys (All Soils)"
)

st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ======================================================
# SECTION 4 — CORRELATION HEATMAP
# ======================================================

st.subheader("Correlation Matrix")

corr = df.corr(numeric_only=True)
fig4 = px.imshow(corr, text_auto=True)
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ======================================================
# SECTION 5 — AI PREDICTION TOOL
# ======================================================

st.subheader("AI Structural Response Prediction (Up to 60 Storeys)")

storeys = st.number_input("Storeys", 1, 60, 20)
bay = st.number_input("Bay Number", 1, 20, 6)
soil = st.selectbox("Soil Profile (Prediction)", df["Soil_Profile"].unique())

height = storeys * 3
aspect_ratio = height / bay

st.write(f"Aspect Ratio (h/b): **{round(aspect_ratio,3)}**")

if st.button("Predict Structural Response"):

    clipped_storeys = min(storeys, max_storeys)
    clipped_bay = min(bay, max_bay)

    input_df = pd.DataFrame({
        "Storeys": [clipped_storeys],
        "Bay_Number": [clipped_bay],
        "Aspect_Ratio": [height/clipped_bay],
        "Soil_Profile": [soil]
    })

    preds = {}

    for target, model in trained_models.items():
        preds[target] = model.predict(input_df)[0]

    if storeys > max_storeys:
        height_ratio = storeys / max_storeys
        span_ratio = bay / max_bay
        area_ratio = (bay**2) / (max_bay**2)

        preds["Roof_Displacement_mm"] *= height_ratio**3
        preds["Storey_Drift_mm"] *= height_ratio
        preds["Column_Axial_Force_kN"] *= height_ratio
        preds["Base_Shear_kN"] *= area_ratio * height_ratio
        preds["Beam_Bending_Moment_kNm"] *= span_ratio**2

        st.warning("Physics-based extrapolation applied.")

    col1, col2 = st.columns(2)

    col1.metric("Roof Displacement (mm)", round(preds["Roof_Displacement_mm"],2))
    col1.metric("Storey Drift (mm)", round(preds["Storey_Drift_mm"],2))
    col1.metric("Beam Moment (kNm)", round(preds["Beam_Bending_Moment_kNm"],2))

    col2.metric("Column Axial Force (kN)", round(preds["Column_Axial_Force_kN"],2))
    col2.metric("Base Shear (kN)", round(preds["Base_Shear_kN"],2))

    drift_limit = (3/250)*1000

    if preds["Storey_Drift_mm"] > drift_limit:
        st.error("Drift exceeds IS 1893 limit (h/250)")
    else:
        st.success("Drift within IS 1893 permissible limit")
