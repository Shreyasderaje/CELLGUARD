import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import streamlit as st

from dashboard.utils import (
    get_sample_images,
    run_root_cause,
    run_risk_predict
)
from dashboard.components.charts import (
    create_defect_rate_chart,
    create_defect_pareto_chart,
    create_quality_trend_chart,
    create_parameter_dist_chart
)
from dashboard.components.lottie import render_lottie_status

# =============================================================================
# PAGE 1: COMMAND CENTER
# =============================================================================
def render_command_center(df_process):
    total_inspections = len(df_process) if not df_process.empty else 5000
    defect_count = len(df_process[df_process["defect_status"] == "Defect"]) if not df_process.empty else 0
    defect_rate = (defect_count / total_inspections * 100) if total_inspections > 0 else 0.0
    yield_rate = 100.0 - defect_rate
    
    if not df_process.empty:
        high_risk_count = len(df_process[(df_process["current"] > 210) | (df_process["temperature"] > 100) | (df_process["pressure"] < 3.8)])
    else:
        high_risk_count = 0

    st.markdown(f"""
    <div class="system-banner-scada">
        <div style="display:flex; align-items:center; gap:10px;">
            <span class="live-dot-pulse"></span>
            <span>CELLGUARD COMMAND CENTER — AI QUALITY MONITORING ACTIVE</span>
        </div>
        <div style="display:flex; gap:12px;">
            <div class="hud-stat-pill">Yield: <b style="color:#10B981;">{yield_rate:.1f}%</b></div>
            <div class="hud-stat-pill">Target Defect: <b style="color:#38BDF8;">&lt; 2.0%</b></div>
            <div class="hud-stat-pill">Lines Active: <b style="color:#34D399;">4 / 4</b></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card-scada card-success">
            <div class="metric-label-scada">Total Inspections</div>
            <div class="metric-value-large">{total_inspections:,}</div>
            <div class="metric-subtext">🟢 100% Automated QC Telemetry Scan</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        card_class = "card-alert" if defect_rate > 10 else "card-success"
        val_color = "#EF4444" if defect_rate > 10 else "#34D399"
        st.markdown(f"""
        <div class="metric-card-scada {card_class}">
            <div class="metric-label-scada">Defect Rate</div>
            <div class="metric-value-large" style="color:{val_color};">{defect_rate:.1f}%</div>
            <div class="metric-subtext">🎯 QC Target Benchmark: &lt; 2.0%</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card-scada card-warning">
            <div class="metric-label-scada">High Risk Batches</div>
            <div class="metric-value-large" style="color:#F59E0B;">{high_risk_count:,}</div>
            <div class="metric-subtext">⚠️ Out-of-Spec Parameter Triggers</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="metric-card-scada card-success">
            <div class="metric-label-scada">Active Workstations</div>
            <div class="metric-value-large" style="color:#38BDF8;">4 / 4</div>
            <div class="metric-subtext">⚡ Laser Weld Lines Operational</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    
    st.markdown("#### 🏭 Machine Line Status & Operational Risk Board")
    if not df_process.empty:
        m_cols = st.columns(4)
        m_ids = sorted(df_process["machine_id"].unique())
        for idx, m_id in enumerate(m_ids):
            m_df = df_process[df_process["machine_id"] == m_id]
            m_total = len(m_df)
            m_defects = len(m_df[m_df["defect_status"] == "Defect"])
            m_rate = (m_defects / m_total * 100) if m_total > 0 else 0.0
            health_pct = max(5.0, 100.0 - m_rate * 2.5)
            
            if m_rate > 18:
                status_badge = '<span class="badge-critical">CRITICAL</span>'
                bar_color = "#EF4444"
            elif m_rate > 12:
                status_badge = '<span class="badge-warning">WARNING</span>'
                bar_color = "#F59E0B"
            else:
                status_badge = '<span class="badge-healthy">HEALTHY</span>'
                bar_color = "#10B981"
                
            with m_cols[idx % 4]:
                st.markdown(f"""
                <div class="machine-card-hud">
                    <div class="machine-card-header">
                        <span class="machine-title">Workstation {m_id}</span>
                        {status_badge}
                    </div>
                    <div style="font-size:12px; color:#CBD5E1; line-height:1.9;">
                        Total Batches: <b style="float:right; color:#F8FAFC;">{m_total:,}</b><br/>
                        Defect Count: <b style="float:right; color:#EF4444;">{m_defects:,}</b><br/>
                        Defect Rate: <b style="float:right; color:{'#EF4444' if m_rate > 15 else ('#F59E0B' if m_rate > 10 else '#34D399')};">{m_rate:.1f}%</b>
                    </div>
                    <div class="machine-progress-track">
                        <div class="machine-progress-fill" style="width:{health_pct:.1f}%; background-color:{bar_color};"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("#### 📊 Defect Rate by Machine Workstation (Interactive Plotly)")
        if not df_process.empty:
            fig_rates = create_defect_rate_chart(df_process)
            st.plotly_chart(fig_rates, use_container_width=True)
        else:
            st.warning("No process telemetry dataset loaded.")

    with col_right:
        st.markdown("#### 🔎 Weld Defect Pareto Breakdown (Interactive Plotly)")
        if not df_process.empty:
            fig_pareto = create_defect_pareto_chart(df_process)
            st.plotly_chart(fig_pareto, use_container_width=True)
        else:
            st.warning("No process telemetry dataset loaded.")

    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("#### ⚡ Real-Time Process Telemetry Stream & SCADA Alarm Log")
    if not df_process.empty:
        recent_df = df_process[["batch_id", "machine_id", "timestamp", "current", "temperature", "pressure", "defect_status", "defect_type"]].tail(10).copy()
        st.dataframe(recent_df, use_container_width=True)

# =============================================================================
# PAGE 2: VISUAL INSPECTION
# =============================================================================
def render_visual_inspection(yolo_model):
    st.markdown("### 📷 Visual Weld Defect Detection (Vision AI)")
    st.caption("Inspect weld surface imagery for cracks, porosity, spatters, or bad welding using fine-tuned YOLO v11.")
    
    col_input, col_display = st.columns([1, 2])
    
    selected_img_path = None
    input_source = None
    
    with col_input:
        st.markdown("#### Input Image Source")
        source_type = st.radio("Choose Input Type:", ["Select Sample Validation Image", "Upload Custom Weld Image"])
        
        if source_type == "Select Sample Validation Image":
            sample_files = get_sample_images()
            if sample_files:
                sample_names = [f.name for f in sample_files]
                selected_name = st.selectbox("Select Sample Image:", sample_names)
                selected_img_path = sample_files[sample_names.index(selected_name)]
                input_source = "sample"
            else:
                st.warning("No sample images found in validation directory.")
        else:
            uploaded_file = st.file_uploader("Upload Image (JPG/PNG):", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                selected_img_path = uploaded_file
                input_source = "upload"

        conf_thresh = st.slider("Detection Confidence Threshold:", min_value=0.10, max_value=0.90, value=0.25, step=0.05)
        
        st.markdown("""
        <div class="transparency-box">
            <b>Vision Model Transparency:</b><br/>
            Vision model trained on public weld-defect dataset.<br/>
            Identifies visual surface anomalies (crack, porosity, spatters, bad welding, excess reinforcement).
        </div>
        """, unsafe_allow_html=True)

    with col_display:
        if selected_img_path is not None:
            try:
                image = Image.open(selected_img_path)

                if yolo_model is None:
                    st.error("YOLO model is not loaded. Cannot run inference.")
                    st.image(image, caption="Uploaded Image", use_column_width=True)
                else:
                    with st.spinner("Running Vision AI defect detection..."):
                        results = yolo_model.predict(source=image, conf=conf_thresh)
                        res = results[0]
                        
                        annotated_img_arr = res.plot()
                        annotated_img = Image.fromarray(annotated_img_arr[:, :, ::-1])
                        
                        col_orig, col_pred = st.columns(2)
                        with col_orig:
                            st.markdown("<b>Original Image</b>", unsafe_allow_html=True)
                            st.image(image, use_column_width=True)
                        with col_pred:
                            st.markdown("<b>AI Detection Bounding Boxes</b>", unsafe_allow_html=True)
                            st.image(annotated_img, use_column_width=True)
                        
                        boxes = res.boxes
                        num_detections = len(boxes)
                        
                        if num_detections > 0:
                            detected_classes = [yolo_model.names[int(c.item())] for c in boxes.cls]
                            defects_found = [c for c in detected_classes if c != "Good Welding"]
                            
                            if defects_found:
                                st.markdown(f"""
                                <div class="result-card-defect">
                                    <h4 style="margin:0; color:#FCA5A5;">⚠️ DEFECT DETECTED ({len(defects_found)} anomaly found)</h4>
                                    <p style="margin-top:5px; margin-bottom:0;">Detected Class(es): <b>{', '.join(set(defects_found))}</b></p>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown("""
                                <div class="result-card-good">
                                    <h4 style="margin:0; color:#A7F3D0;">✅ GOOD WELDING DETECTED</h4>
                                    <p style="margin-top:5px; margin-bottom:0;">No structural defects identified above threshold.</p>
                                </div>
                                """, unsafe_allow_html=True)

                            det_data = []
                            for i, box in enumerate(boxes):
                                cls_id = int(box.cls.item())
                                cls_name = yolo_model.names[cls_id]
                                conf_score = float(box.conf.item()) * 100
                                xyxy = [round(v, 1) for v in box.xyxy[0].tolist()]
                                det_data.append({
                                    "Detection #": i + 1,
                                    "Defect Class": cls_name,
                                    "Confidence": f"{conf_score:.1f}%",
                                    "Bounding Box [x1, y1, x2, y2]": str(xyxy)
                                })
                            st.markdown("##### Detection Breakdown")
                            st.dataframe(pd.DataFrame(det_data), use_container_width=True)
                        else:
                            st.markdown("""
                            <div class="result-card-good">
                                <h4 style="margin:0; color:#A7F3D0;">✅ NO DEFECTS DETECTED</h4>
                                <p style="margin-top:5px; margin-bottom:0;">No bounding boxes exceeded confidence threshold.</p>
                            </div>
                            """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error processing image: {e}")
        else:
            st.info("👈 Please select a sample validation image or upload a custom weld image from the left panel to begin inspection.")

# =============================================================================
# PAGE 3: ROOT CAUSE INTELLIGENCE
# =============================================================================
def render_root_cause():
    st.markdown("### 🔍 Root Cause Intelligence (EXPLAIN)")
    st.caption("Correlate welding process telemetry deviations against baseline physics to explain probable contributing defect causes.")

    col_form, col_res = st.columns([1, 1.2])

    with col_form:
        st.markdown("#### Process Telemetry Parameters")
        
        st.markdown("<b>Quick Presets:</b>", unsafe_allow_html=True)
        p_col1, p_col2, p_col3, p_col4 = st.columns(4)
        preset = None
        if p_col1.button("Normal"):
            preset = "normal"
        if p_col2.button("Porosity"):
            preset = "porosity"
        if p_col3.button("Crack"):
            preset = "crack"
        if p_col4.button("Burn-Thru"):
            preset = "burn_through"
            
        def_curr, def_volt, def_temp = 190.0, 24.5, 85.0
        def_pres, def_time, def_speed = 4.5, 3.2, 12.0

        if preset == "porosity":
            def_curr, def_temp, def_pres = 225.0, 110.0, 3.2
        elif preset == "crack":
            def_temp, def_time = 120.0, 2.3
        elif preset == "burn_through":
            def_curr, def_volt, def_temp = 235.0, 28.0, 125.0

        val_current = st.slider("Welding Current (A):", 120.0, 260.0, def_curr, 1.0)
        val_voltage = st.slider("Welding Voltage (V):", 15.0, 35.0, def_volt, 0.5)
        val_temperature = st.slider("Welding Temp (°C):", 50.0, 150.0, def_temp, 1.0)
        val_pressure = st.slider("Welding Pressure (bar):", 2.0, 7.0, def_pres, 0.1)
        val_time = st.slider("Welding Time (s):", 1.5, 5.0, def_time, 0.1)
        val_speed = st.slider("Welding Speed (mm/s):", 5.0, 20.0, def_speed, 0.5)

        telemetry_sample = {
            "current": val_current,
            "voltage": val_voltage,
            "temperature": val_temperature,
            "pressure": val_pressure,
            "welding_time": val_time,
            "speed": val_speed
        }

    with col_res:
        st.markdown("#### Root Cause Analysis Result")
        result = run_root_cause(telemetry_sample)

        cause = result.get("predicted_cause", "Unknown")
        conf = result.get("confidence", 0.0) * 100
        explanation = result.get("explanation", "")
        evidence = result.get("evidence", [])

        st.markdown(f"""
        <div style="background-color:#1E293B; border:1px solid #3B82F6; border-left:6px solid #3B82F6; padding:16px; border-radius:8px;">
            <div style="font-size:12px; color:#94A3B8; text-transform:uppercase; font-weight:700;">Probable Contributing Cause</div>
            <div style="font-size:26px; font-weight:800; color:#F8FAFC; margin-top:2px;">
                {cause.replace('_', ' ')} <span style="font-size:16px; color:#38BDF8; font-weight:600;">({conf:.1f}% confidence)</span>
            </div>
            <p style="margin-top:10px; color:#CBD5E1; font-size:13px; line-height:1.5;">{explanation}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("##### Parameter Deviation vs Normal Baseline")
        baseline_data = {
            "current": 190.0,
            "voltage": 24.5,
            "temperature": 85.0,
            "pressure": 4.5,
            "welding_time": 3.2,
            "speed": 12.0
        }

        dev_table = []
        for param, obs in telemetry_sample.items():
            base = baseline_data[param]
            diff = obs - base
            diff_pct = (diff / base) * 100
            
            is_deviating = False
            for ev in evidence:
                if ev.get("parameter") == param:
                    is_deviating = True
                    break
            
            status_str = "⚠️ ABNORMAL DEVIATION" if is_deviating else "OK"
            dev_table.append({
                "Parameter": param,
                "Observed": f"{obs:.2f}",
                "Baseline": f"{base:.2f}",
                "Shift (%)": f"{diff_pct:+.1f}%",
                "Status": status_str
            })

        st.table(pd.DataFrame(dev_table))
        
        st.markdown("""
        <div class="transparency-box">
            <b>Technical Honesty Note:</b><br/>
            The Root Cause AI identifies <b>statistically learned contributing process patterns</b>. It estimates the most probable contributing cause based on process parameter deviations, but does not prove physical root causality.
        </div>
        """, unsafe_allow_html=True)
# =============================================================================
# PAGE 4: RISK PREDICTION
# =============================================================================
def render_risk_prediction(df_process):
    st.markdown("### 🔮 Defect Risk Prediction Engine (PREDICT)")
    st.caption("Predict future defect probability for active welding machines before physical inspection.")

    col_in, col_out = st.columns([1, 1.2])

    with col_in:
        st.markdown("#### Input Process Telemetry")
        r_current = st.slider("Current (A):", 120.0, 260.0, 230.0, 1.0, key="r_curr")
        r_voltage = st.slider("Voltage (V):", 15.0, 35.0, 27.0, 0.5, key="r_volt")
        r_temperature = st.slider("Temperature (°C):", 50.0, 150.0, 120.0, 1.0, key="r_temp")
        r_pressure = st.slider("Pressure (bar):", 2.0, 7.0, 4.2, 0.1, key="r_pres")
        r_time = st.slider("Welding Time (s):", 1.5, 5.0, 2.8, 0.1, key="r_time")
        r_speed = st.slider("Speed (mm/s):", 5.0, 20.0, 12.0, 0.5, key="r_speed")

        risk_sample = {
            "current": r_current,
            "voltage": r_voltage,
            "temperature": r_temperature,
            "pressure": r_pressure,
            "welding_time": r_time,
            "speed": r_speed
        }

    with col_out:
        st.markdown("#### Machine Defect Risk Assessment")
        risk_res = run_risk_predict(risk_sample)

        prob = risk_res.get("risk_probability", 0.0)
        level = risk_res.get("risk_level", "LOW")
        contributors = risk_res.get("contributors", [])

        if level == "HIGH":
            border_color, text_color = "#EF4444", "#FCA5A5"
        elif level == "MEDIUM":
            border_color, text_color = "#F59E0B", "#FDE68A"
        else:
            border_color, text_color = "#10B981", "#A7F3D0"

        st.markdown(f"""
        <div style="background-color:#1E293B; border:1px solid {border_color}; border-left:6px solid {border_color}; padding:20px; border-radius:8px;">
            <div style="font-size:12px; color:#94A3B8; text-transform:uppercase; font-weight:700;">Estimated Defect Risk Score</div>
            <div style="font-size:38px; font-weight:900; color:{border_color}; margin-top:2px;">
                {prob:.1f}% <span style="font-size:18px; color:{text_color}; font-weight:700;">[{level} RISK]</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("##### Top Defect Risk Drivers (Feature Importance)")
        if contributors:
            contrib_df = pd.DataFrame(contributors)
            st.dataframe(contrib_df, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 🏭 Factory-Wide Machine Risk Matrix (5,000 Process Batches)")
    
    if not df_process.empty:
        col_m1, col_m2 = st.columns([1, 1])
        with col_m1:
            st.markdown("<b>Machine Risk Breakdown</b>", unsafe_allow_html=True)
            m_grp = df_process.groupby("machine_id").agg(
                Total_Batches=("batch_id", "count"),
                Defects=("defect_status", lambda x: (x == "Defect").sum()),
                Avg_Temperature=("temperature", "mean"),
                Avg_Current=("current", "mean")
            ).reset_index()
            m_grp["Defect_Rate_%"] = (m_grp["Defects"] / m_grp["Total_Batches"] * 100).round(1)
            st.dataframe(m_grp, use_container_width=True)
        with col_m2:
            st.markdown("<b>Average Defect Rate by Machine</b>", unsafe_allow_html=True)
            chart_df = m_grp.set_index("machine_id")[["Defect_Rate_%"]]
            st.bar_chart(chart_df)

# =============================================================================
# PAGE 5: QUALITY TIME MACHINE
# =============================================================================
def render_quality_time_machine(df_process):
    st.markdown("### ⏳ Quality Time Machine (Historical Analytics)")
    st.caption("Explore historical production quality trends, parameter drift, and defect patterns over time.")

    if not df_process.empty:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            selected_machine = st.selectbox("Filter Machine:", ["ALL"] + sorted(list(df_process["machine_id"].unique())))
        with col_f2:
            defect_types = sorted([str(x) for x in df_process["defect_type"].dropna().unique()])
            selected_defect = st.selectbox("Filter Defect Type:", ["ALL"] + defect_types)

        df_filtered = df_process.copy()
        if selected_machine != "ALL":
            df_filtered = df_filtered[df_filtered["machine_id"] == selected_machine]
        if selected_defect != "ALL":
            df_filtered = df_filtered[df_filtered["defect_type"] == selected_defect]

        st.markdown(f"**Showing {len(df_filtered):,} filtered batch records**")

        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown("#### Quality Trend Over Time (Interactive Line Chart)")
            fig_trend = create_quality_trend_chart(df_filtered)
            st.plotly_chart(fig_trend, use_container_width=True)

        with col_t2:
            st.markdown("#### Defect Type Distribution")
            defect_dist = df_filtered[df_filtered["defect_type"] != "None"]["defect_type"].value_counts()
            if not defect_dist.empty:
                st.bar_chart(defect_dist)
            else:
                st.info("No defects matching selected filter criteria.")

        st.markdown("#### Process Parameter Distribution (Normal vs Defect)")
        param_choice = st.selectbox("Select Parameter to Plot:", ["current", "voltage", "temperature", "pressure", "welding_time", "speed"])
        
        fig_dist = create_parameter_dist_chart(df_filtered, param_choice)
        st.plotly_chart(fig_dist, use_container_width=True)
    else:
        st.warning("Factory process dataset is not available.")

# =============================================================================
# PAGE 6: WHAT-IF SIMULATOR
# =============================================================================
def render_what_if_simulator():
    st.markdown("### 🎛️ What-If Process Simulator (PREVENT)")
    st.caption("Simulate process parameter adjustments in real time to calculate risk reduction and prevent future failures.")

    col_sim_left, col_sim_right = st.columns([1, 1.2])

    with col_sim_left:
        st.markdown("#### Initial Baseline Operating Conditions")
        base_c = st.number_input("Current (A):", 120.0, 260.0, 235.0, 1.0)
        base_v = st.number_input("Voltage (V):", 15.0, 35.0, 27.5, 0.5)
        base_t = st.number_input("Temperature (°C):", 50.0, 150.0, 125.0, 1.0)
        base_p = st.number_input("Pressure (bar):", 2.0, 7.0, 3.4, 0.1)
        base_tm = st.number_input("Welding Time (s):", 1.5, 5.0, 2.5, 0.1)
        base_s = st.number_input("Speed (mm/s):", 5.0, 20.0, 12.0, 0.5)

        base_sample = {
            "current": base_c,
            "voltage": base_v,
            "temperature": base_t,
            "pressure": base_p,
            "welding_time": base_tm,
            "speed": base_s
        }
        base_risk = run_risk_predict(base_sample)["risk_probability"]

    with col_sim_right:
        st.markdown("#### Adjust Simulated Parameters (Sliders)")
        sim_c = st.slider("Simulated Current (A):", 120.0, 260.0, base_c, 1.0, key="sim_c")
        sim_v = st.slider("Simulated Voltage (V):", 15.0, 35.0, base_v, 0.5, key="sim_v")
        sim_t = st.slider("Simulated Temp (°C):", 50.0, 150.0, base_t, 1.0, key="sim_t")
        sim_p = st.slider("Simulated Pressure (bar):", 2.0, 7.0, base_p, 0.1, key="sim_p")
        sim_tm = st.slider("Simulated Time (s):", 1.5, 5.0, base_tm, 0.1, key="sim_tm")
        sim_s = st.slider("Simulated Speed (mm/s):", 5.0, 20.0, base_s, 0.5, key="sim_s")

        sim_sample = {
            "current": sim_c,
            "voltage": sim_v,
            "temperature": sim_t,
            "pressure": sim_p,
            "welding_time": sim_tm,
            "speed": sim_s
        }
        sim_risk = run_risk_predict(sim_sample)["risk_probability"]

        risk_delta = sim_risk - base_risk

        st.markdown("---")
        st.markdown("#### 📉 Simulation Results")

        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Initial Risk</div>
                <div class="metric-value" style="color:#EF4444;">{base_risk:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        with col_r2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Simulated Risk</div>
                <div class="metric-value" style="color:{'#10B981' if sim_risk < 40 else '#F59E0B'};">{sim_risk:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        with col_r3:
            delta_color = "#10B981" if risk_delta < 0 else ("#EF4444" if risk_delta > 0 else "#94A3B8")
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Risk Change</div>
                <div class="metric-value" style="color:{delta_color};">{risk_delta:+.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)
        if risk_delta < -5:
            st.success(f"✅ PARAMETER ADJUSTMENT SUCCESSFUL: Predicted risk reduced by {abs(risk_delta):.1f}%!")
        elif risk_delta > 5:
            st.error(f"⚠️ WARNING: Parameter adjustment increased defect risk by {risk_delta:.1f}%!")
        else:
            st.info("ℹ️ Minimal risk change detected with current slider adjustments.")

        st.markdown("##### 🛠️ Preventive Action Recommendations")
        recs = []
        if sim_t > 95:
            recs.append("• <b>Temperature Reduction:</b> Lower welding temp towards ~85°C to reduce thermal stress and cracking.")
        if sim_c > 210:
            recs.append("• <b>Current Reduction:</b> Reduce current towards ~190A to eliminate burn-through risks.")
        if sim_p < 4.0:
            recs.append("• <b>Pressure Increase:</b> Increase pressure towards ~4.5 bar to reduce porosity formation.")
        if sim_tm < 2.8:
            recs.append("• <b>Extend Welding Time:</b> Increase welding time towards 3.2s to prevent incomplete welds.")

        if recs:
            for r in recs:
                st.markdown(f"<div style='color:#CBD5E1; margin-bottom:6px;'>{r}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#34D399;'>Process parameters are operating within optimal safe boundaries.</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="transparency-box">
            <b>Model-based Simulation Disclaimer:</b><br/>
            This simulation estimates defect risk reduction using the trained Random Forest surrogate model. It serves as an operational decision support tool and is not a guaranteed physical outcome.
        </div>
        """, unsafe_allow_html=True)

