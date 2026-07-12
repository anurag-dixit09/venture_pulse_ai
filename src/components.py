"""Reusable UI and styling helpers for Venture Pulse AI."""

import streamlit as st

THEME_COLORS = {
    "background": "#0D0E15",
    "surface": "#0C0F0F",
    "border": "#4C4354",
    "purple": "#DBB8FF",
    "purple_accent": "#7928CA",
    "text": "#E2E2E2",
    "muted": "#CEC2D6",
    "success": "#10B981",
    "warning": "#EF4444",
}

PREMIMUM_CSS = """
<style>
    .stApp {
        background-color: #121414 !important;
        color: #E2E2E2 !important;
        font-family: 'Inter', sans-serif !important;
    }
    header, [data-testid="stHeader"] {
        background-color: #121414 !important;
        border-bottom: 1px solid #4C4354 !important;
    }
    [data-testid="stSidebar"] {
        background-color: #0C0F0F !important;
        border-right: 1px solid #4C4354 !important;
    }
    .sidebar-header {
        font-family: 'Hanken Grotesk', sans-serif !important;
        font-weight: 900 !important;
        font-size: 1.4rem !important;
        color: #DBB8FF !important;
        letter-spacing: -0.02em !important;
        margin-top: 10px;
        margin-bottom: 2px;
    }
    .sidebar-sub {
        font-family: 'Geist', sans-serif !important;
        font-size: 0.72rem !important;
        color: #CEC2D6 !important;
        opacity: 0.6;
        letter-spacing: 0.08em !important;
        margin-bottom: 30px;
    }
    .stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"], .stNumberInput input {
        background-color: #0D0E15 !important;
        color: #E2E2E2 !important;
        border: 1px solid #4C4354 !important;
        border-radius: 4px !important;
        padding: 10px 14px !important;
    }
    .stButton > button {
        background-color: #DBB8FF !important;
        color: #470083 !important;
        border: none !important;
        border-radius: 4px !important;
        font-weight: 700 !important;
        padding: 12px 24px !important;
    }
    .metric-card {
        background-color: #0D0E15;
        border: 1px solid #4C4354;
        border-radius: 4px;
        padding: 16px;
        text-align: left;
    }
    .metric-label {
        font-family: 'Geist', sans-serif;
        font-size: 0.72rem;
        color: #CEC2D6;
        opacity: 0.7;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .metric-value {
        font-family: 'Geist', sans-serif;
        font-size: 1.25rem;
        font-weight: 700;
    }
    .metric-value.positive { color: #10B981 !important; }
    .metric-value.negative { color: #EF4444 !important; }
    .metric-value.neutral { color: #DBB8FF !important; }
    .streamlit-expanderHeader {
        background-color: #0C0F0F !important;
        border: 1px solid #4C4354 !important;
        border-radius: 8px !important;
        color: #E2E2E2 !important;
        padding: 14px 20px !important;
    }
    .streamlit-expanderContent {
        background-color: #0C0F0F !important;
        border-left: 1px solid #4C4354 !important;
        border-right: 1px solid #4C4354 !important;
        border-bottom: 1px solid #4C4354 !important;
        border-bottom-left-radius: 8px !important;
        border-bottom-right-radius: 8px !important;
        padding: 24px !important;
    }
</style>
"""


def inject_premium_css() -> None:
    st.markdown(PREMIMUM_CSS, unsafe_allow_html=True)
