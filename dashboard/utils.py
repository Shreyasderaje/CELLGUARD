import os
import sys
from pathlib import Path
import pandas as pd
import joblib
from ultralytics import YOLO
import streamlit as st

# Compute workspace base directory (D:\CELLGUARD\cellguard)
BASE_DIR = Path(__file__).resolve().parent.parent

# Change CWD to BASE_DIR so relative paths inside src/ models load properly
if os.getcwd() != str(BASE_DIR):
    os.chdir(str(BASE_DIR))

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Import backend inference functions without modifying backend files
from src.root_cause_inference import predict_root_cause
from src.risk_inference import predict_risk

YOLO_MODEL_PATH = BASE_DIR / "runs" / "detect" / "models" / "defect_detector" / "cellguard_yolo-3" / "weights" / "best.pt"
DATA_PATH = BASE_DIR / "data" / "factory_process_data.csv"
VALID_IMAGES_DIR = BASE_DIR / "data" / "raw" / "weld_defect" / "valid" / "images"

@st.cache_resource
def load_yolo_model():
    """Loads and caches the trained YOLO defect detection model."""
    if not YOLO_MODEL_PATH.exists():
        st.error(f"YOLO model file not found at: {YOLO_MODEL_PATH}")
        return None
    try:
        model = YOLO(str(YOLO_MODEL_PATH))
        return model
    except Exception as e:
        st.error(f"Failed to load YOLO model: {e}")
        return None

@st.cache_data
def load_factory_data():
    """Loads and caches the factory process CSV dataset."""
    if not DATA_PATH.exists():
        st.error(f"Factory data not found at: {DATA_PATH}")
        return pd.DataFrame()
    try:
        df = pd.read_csv(DATA_PATH)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        st.error(f"Error loading factory process dataset: {e}")
        return pd.DataFrame()

def get_sample_images():
    """Returns a list of sample image paths from the validation directory."""
    if not VALID_IMAGES_DIR.exists():
        return []
    return sorted(list(VALID_IMAGES_DIR.glob("*.jpg")) + list(VALID_IMAGES_DIR.glob("*.png")))

def run_root_cause(sample_dict):
    """Wrapper around predict_root_cause with error handling."""
    try:
        return predict_root_cause(sample_dict)
    except Exception as e:
        st.error(f"Root cause inference error: {e}")
        return {
            "predicted_cause": "Unknown",
            "confidence": 0.0,
            "explanation": f"Inference error: {e}",
            "evidence": []
        }

def run_risk_predict(sample_dict):
    """Wrapper around predict_risk with error handling."""
    try:
        return predict_risk(sample_dict)
    except Exception as e:
        st.error(f"Risk prediction error: {e}")
        return {
            "risk_probability": 0.0,
            "risk_level": "UNKNOWN",
            "contributors": []
        }
