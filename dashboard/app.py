import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
    
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import streamlit as st

# Configure page layout and style
st.set_page_config(
    page_title="CELLGUARD — AI Quality Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import utils helpers (which handle path resolution and cached loading)
from dashboard.utils import (
    load_yolo_model,
    load_factory_data,
    get_sample_images,
    run_root_cause,
    run_risk_predict
)
from dashboard.styles import inject_custom_css
from dashboard.pages import (
    render_command_center,
    render_visual_inspection,
    render_root_cause,
    render_risk_prediction,
    render_quality_time_machine,
    render_what_if_simulator
)

# Inject custom dark theme styles
inject_custom_css()
# -----------------------------------------------------------------------------
# GLOBAL DATA & MODEL INITIALIZATION
# -----------------------------------------------------------------------------
df_process = load_factory_data()
yolo_model = load_yolo_model()

# -----------------------------------------------------------------------------
# SIDEBAR NAVIGATION & SYSTEM STATUS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color:#38BDF8; margin-bottom:0;'>CELLGUARD</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748B; font-size:11px; margin-top:0;'>EV BATTERY QUALITY INTELLIGENCE</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    page = st.radio(
        "NAVIGATION",
        [
            "● Command Center",
            "● Visual Inspection",
            "● Root Cause Intelligence",
            "● Risk Prediction",
            "● Quality Time Machine",
            "● What-If Simulator"
        ]
    )
    
    st.markdown("---")
    st.markdown("<p style='color:#94A3B8; font-size:12px; font-weight:700; letter-spacing:1px;'>SYSTEM STATUS</p>", unsafe_allow_html=True)
    
    status_yolo = "🟢 ONLINE" if yolo_model is not None else "🔴 OFFLINE"
    status_data = "🟢 ONLINE" if not df_process.empty else "🔴 OFFLINE"
    
    st.markdown(f"""
    <div style='font-size:13px; line-height:2.0; color:#CBD5E1;'>
        Vision AI: <b style='float:right;'>{status_yolo}</b><br/>
        Root Cause AI: <b style='float:right;'>🟢 ONLINE</b><br/>
        Risk Engine: <b style='float:right;'>🟢 ONLINE</b><br/>
        Process Data: <b style='float:right;'>{status_data}</b>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("<p style='color:#94A3B8; font-size:11px; font-weight:700;'>DATA & MODEL TRANSPARENCY</p>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:11px; color:#64748B; line-height:1.4;'>
        • <b>Visual Model:</b> Public weld-defect imagery.<br/>
        • <b>Process Data:</b> Synthetic factory telemetry.<br/>
        • <b>Root Cause:</b> Probable contributing cause based on learned patterns.<br/>
        • <b>Risk Model:</b> Estimated failure probability.<br/>
        • <b>What-If:</b> Predictive simulation, not physical guarantee.
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# HEADER COMPONENT
# -----------------------------------------------------------------------------
st.markdown("""
<div class="cellguard-hero-container">
    <div class="cellguard-hero-header">
        <div>
            <div class="cellguard-hero-title">
                ⚡ CELLGUARD <span style="font-size:16px; color:#94A3B8; font-weight:600;">| AI QUALITY CONTROL ROOM</span>
            </div>
            <div class="cellguard-hero-tagline">
                AUTOMOTIVE BATTERY WELDING • REAL-TIME QUALITY INTELLIGENCE ENGINE
            </div>
        </div>
        <div class="live-badge-glow">
            <span class="live-dot-pulse"></span>
            <span>LIVE MANUFACTURING TELEMETRY</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PAGE ROUTING
# -----------------------------------------------------------------------------
if page == "● Command Center":
    render_command_center(df_process)
elif page == "● Visual Inspection":
    render_visual_inspection(yolo_model)
elif page == "● Root Cause Intelligence":
    render_root_cause()
elif page == "● Risk Prediction":
    render_risk_prediction(df_process)
elif page == "● Quality Time Machine":
    render_quality_time_machine(df_process)
elif page == "● What-If Simulator":
    render_what_if_simulator()
