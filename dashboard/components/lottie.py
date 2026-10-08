import streamlit as st
from streamlit_lottie import st_lottie
import requests

@st.cache_data(show_spinner=False)
def load_lottie_url(url: str):
    """
    Fetches a Lottie animation JSON from URL safely.
    Returns None if fetch fails.
    """
    try:
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

def render_lottie_status(key="status_lottie", height=40, width=40):
    """
    Renders a subtle, high-tech pulse Lottie micro-animation or fallback.
    """
    # High-tech pulse / radar signal Lottie animation URL
    lottie_url = "https://assets5.lottiefiles.com/packages/lf20_96bov88g.json"
    lottie_json = load_lottie_url(lottie_url)
    if lottie_json:
        st_lottie(lottie_json, height=height, width=width, key=key)
    else:
        st.markdown("<span class='live-pulse-dot'></span>", unsafe_allow_html=True)
