import streamlit as st

def inject_custom_css():
    st.markdown("""
    <style>
        /* Global Page Styling */
        .stApp {
            background-color: #0A0E17;
            color: #E2E8F0;
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
        }
        
        /* Header Card */
        .cellguard-header {
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
            border: 1px solid #1E3A8A;
            border-left: 6px solid #38BDF8;
            padding: 20px 24px;
            border-radius: 8px;
            margin-bottom: 24px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        }
        .cellguard-title {
            color: #F8FAFC;
            font-size: 28px;
            font-weight: 800;
            letter-spacing: 1.5px;
            margin: 0;
            padding: 0;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .cellguard-subtitle {
            color: #38BDF8;
            font-size: 13px;
            font-weight: 600;
            letter-spacing: 1.2px;
            margin-top: 6px;
            text-transform: uppercase;
        }
        
        /* System Banner */
        .system-banner {
            background-color: #064E3B;
            border: 1px solid #059669;
            color: #34D399;
            padding: 10px 16px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 14px;
            letter-spacing: 1px;
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
        }

        /* Metric Card Styling */
        .metric-card {
            background-color: #1E293B;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 16px 20px;
            text-align: left;
        }
        .metric-value {
            font-size: 32px;
            font-weight: 800;
            color: #38BDF8;
            margin-top: 4px;
        }
        .metric-label {
            font-size: 12px;
            color: #94A3B8;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }

        /* Status Badges */
        .badge-critical {
            background-color: #7F1D1D;
            color: #FCA5A5;
            border: 1px solid #EF4444;
            padding: 4px 10px;
            border-radius: 4px;
            font-weight: 700;
            font-size: 12px;
        }
        .badge-warning {
            background-color: #78350F;
            color: #FDE68A;
            border: 1px solid #F59E0B;
            padding: 4px 10px;
            border-radius: 4px;
            font-weight: 700;
            font-size: 12px;
        }
        .badge-healthy {
            background-color: #064E3B;
            color: #A7F3D0;
            border: 1px solid #10B981;
            padding: 4px 10px;
            border-radius: 4px;
            font-weight: 700;
            font-size: 12px;
        }
        
        /* Result Cards */
        .result-card-defect {
            background-color: #450A0A;
            border: 1px solid #DC2626;
            border-radius: 8px;
            padding: 16px;
            color: #FECACA;
            margin-top: 15px;
        }
        .result-card-good {
            background-color: #064E3B;
            border: 1px solid #059669;
            border-radius: 8px;
            padding: 16px;
            color: #A7F3D0;
            margin-top: 15px;
        }

        /* Honesty Box */
        .transparency-box {
            background-color: #0F172A;
            border: 1px solid #1E293B;
            border-radius: 6px;
            padding: 14px;
            font-size: 12px;
            color: #94A3B8;
            margin-top: 20px;
        }

        /* Hide default Streamlit footer */
        footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
