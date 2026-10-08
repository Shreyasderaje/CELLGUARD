import streamlit as st

def inject_custom_css():
    st.markdown("""
    <style>
        /* ===================================================================
           1. GLOBAL INDUSTRIAL DARK THEME & ENGINEERING GRID
           =================================================================== */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap');

        .stApp {
            background-color: #060913;
            background-image: 
                radial-gradient(circle at 50% -10%, rgba(14, 165, 233, 0.12) 0%, rgba(6, 9, 19, 0.8) 70%),
                linear-gradient(rgba(30, 41, 59, 0.25) 1px, transparent 1px),
                linear-gradient(90deg, rgba(30, 41, 59, 0.25) 1px, transparent 1px);
            background-size: 100% 100%, 36px 36px, 36px 36px;
            background-position: center top, -1px -1px, -1px -1px;
            color: #E2E8F0;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif;
        }

        /* Hide Streamlit default elements */
        footer { visibility: hidden; }
        header[data-testid="stHeader"] { background-color: rgba(6, 9, 19, 0.8); backdrop-filter: blur(8px); }

        /* ===================================================================
           2. HERO / CONTROL ROOM HEADER WITH SCANNING & LIVE GLOW
           =================================================================== */
        .cellguard-hero-container {
            position: relative;
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(11, 19, 43, 0.95) 100%);
            border: 1px solid rgba(56, 189, 248, 0.2);
            border-radius: 12px;
            padding: 22px 28px;
            margin-bottom: 22px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(12px);
            overflow: hidden;
        }

        .cellguard-hero-container::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent 0%, #38BDF8 50%, transparent 100%);
            animation: scanline 4s ease-in-out infinite;
        }

        @keyframes scanline {
            0% { transform: translateX(-100%); }
            50% { transform: translateX(100%); }
            100% { transform: translateX(100%); }
        }

        .cellguard-hero-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
        }

        .cellguard-hero-title {
            color: #F8FAFC;
            font-size: 26px;
            font-weight: 900;
            letter-spacing: 2px;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 12px;
            text-shadow: 0 2px 10px rgba(56, 189, 248, 0.3);
        }

        .cellguard-hero-tagline {
            color: #38BDF8;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin-top: 4px;
        }

        .live-badge-glow {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(16, 185, 129, 0.12);
            border: 1px solid rgba(16, 185, 129, 0.4);
            color: #34D399;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1.2px;
            box-shadow: 0 0 12px rgba(16, 185, 129, 0.2);
        }

        .live-dot-pulse {
            width: 8px;
            height: 8px;
            background-color: #10B981;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
            animation: pulse-ring 2s infinite;
        }

        @keyframes pulse-ring {
            0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            70% { box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
            100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }

        /* ===================================================================
           3. KPI METRIC CARDS
           =================================================================== */
        .metric-card-scada {
            background: linear-gradient(145deg, rgba(15, 23, 42, 0.8) 0%, rgba(30, 41, 59, 0.5) 100%);
            border: 1px solid rgba(56, 189, 248, 0.15);
            border-radius: 10px;
            padding: 18px 20px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
            transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.25s ease, box-shadow 0.25s ease;
            backdrop-filter: blur(10px);
        }

        .metric-card-scada:hover {
            transform: translateY(-3px);
            border-color: rgba(56, 189, 248, 0.4);
            box-shadow: 0 12px 28px rgba(56, 189, 248, 0.15);
        }

        .metric-card-scada::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: #38BDF8;
        }

        .metric-card-scada.card-alert::before { background: #EF4444; }
        .metric-card-scada.card-warning::before { background: #F59E0B; }
        .metric-card-scada.card-success::before { background: #10B981; }

        .metric-value-large {
            font-size: 32px;
            font-weight: 800;
            color: #F8FAFC;
            letter-spacing: -0.5px;
            margin-top: 8px;
            line-height: 1.1;
            font-family: 'JetBrains Mono', monospace;
        }

        .metric-label-scada {
            font-size: 11px;
            color: #94A3B8;
            text-transform: uppercase;
            letter-spacing: 1.3px;
            font-weight: 700;
        }

        .metric-subtext {
            font-size: 11px;
            color: #64748B;
            margin-top: 8px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 5px;
        }

        /* ===================================================================
           4. MACHINE LINE STATUS & WORKSTATION HUD
           =================================================================== */
        .machine-card-hud {
            background: rgba(15, 23, 42, 0.75);
            border: 1px solid rgba(56, 189, 248, 0.15);
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            transition: all 0.2s ease;
            backdrop-filter: blur(8px);
        }

        .machine-card-hud:hover {
            border-color: rgba(56, 189, 248, 0.35);
            box-shadow: 0 6px 20px rgba(56, 189, 248, 0.12);
        }

        .machine-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .machine-title {
            font-size: 14px;
            font-weight: 800;
            color: #F1F5F9;
            letter-spacing: 0.5px;
        }

        .badge-critical {
            background-color: rgba(127, 29, 29, 0.7);
            color: #FCA5A5;
            border: 1px solid #EF4444;
            padding: 3px 9px;
            border-radius: 4px;
            font-weight: 700;
            font-size: 10px;
            letter-spacing: 0.8px;
        }

        .badge-warning {
            background-color: rgba(120, 53, 15, 0.7);
            color: #FDE68A;
            border: 1px solid #F59E0B;
            padding: 3px 9px;
            border-radius: 4px;
            font-weight: 700;
            font-size: 10px;
            letter-spacing: 0.8px;
        }

        .badge-healthy {
            background-color: rgba(6, 78, 59, 0.7);
            color: #A7F3D0;
            border: 1px solid #10B981;
            padding: 3px 9px;
            border-radius: 4px;
            font-weight: 700;
            font-size: 10px;
            letter-spacing: 0.8px;
        }

        .machine-progress-track {
            height: 5px;
            background: #1E293B;
            border-radius: 3px;
            overflow: hidden;
            margin-top: 10px;
        }

        .machine-progress-fill {
            height: 100%;
            border-radius: 3px;
            transition: width 0.5s ease;
        }

        /* ===================================================================
           5. SYSTEM SCADA BANNER & STATUS HUD
           =================================================================== */
        .system-banner-scada {
            background: linear-gradient(90deg, rgba(6, 78, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
            border: 1px solid #059669;
            border-left: 5px solid #10B981;
            color: #34D399;
            padding: 12px 20px;
            border-radius: 8px;
            font-weight: 700;
            font-size: 13px;
            letter-spacing: 0.8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 22px;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.15);
        }

        .hud-stat-pill {
            background-color: rgba(15, 23, 42, 0.9);
            border: 1px solid #334155;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11px;
            color: #94A3B8;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        /* ===================================================================
           6. TRANSPARENCY & RESULT CARDS
           =================================================================== */
        .transparency-box {
            background-color: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(56, 189, 248, 0.15);
            border-radius: 8px;
            padding: 16px;
            font-size: 12px;
            color: #94A3B8;
            margin-top: 20px;
            backdrop-filter: blur(8px);
        }

        .result-card-defect {
            background-color: rgba(69, 10, 10, 0.85);
            border: 1px solid #DC2626;
            border-radius: 8px;
            padding: 16px;
            color: #FECACA;
            margin-top: 15px;
        }

        .result-card-good {
            background-color: rgba(6, 78, 59, 0.85);
            border: 1px solid #059669;
            border-radius: 8px;
            padding: 16px;
            color: #A7F3D0;
            margin-top: 15px;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #090E1A;
            border-right: 1px solid rgba(56, 189, 248, 0.12);
        }
    </style>
    """, unsafe_allow_html=True)


