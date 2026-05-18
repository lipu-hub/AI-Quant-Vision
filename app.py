import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai
import plotly.graph_objects as go

# ⚡ Page Configuration
st.set_page_config(page_title="MarketMind AI Terminal", layout="wide", initial_sidebar_state="expanded")

# 🔐 Streamlit Secrets Verification
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.sidebar.warning("⚠️ Please configure GEMINI_API_KEY in Streamlit Secrets.")

# INITIALIZE SESSION STATES
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {}
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = "IFCI"
if "ticker_raw_name" not in st.session_state:
    st.session_state.ticker_raw_name = "IFCI.NS"
if "ai_analysis_result" not in st.session_state:
    st.session_state.ai_analysis_result = None
if "live_prices" not in st.session_state:
    st.session_state.live_prices = {}
if "custom_tickers" not in st.session_state:
    st.session_state.custom_tickers = [
        "SUZLON.NS", "RVNL.NS", "NBCC.NS", "GAIL.NS", "IRFC.NS", 
        "IDEA.NS", "TATAPOWER.NS", "HUDCO.NS", "IFCI.NS", "YESBANK.NS", 
        "NHPC.NS", "IOC.NS", "BTC-USD", "PNB.NS", "JPPOWER.NS", 
        "SJVN.NS", "SAIL.NS", "ETH-USD"
    ]

# ⚙️ CORE ADMIN CONSOLE IN SIDEBAR
with st.sidebar:
    st.markdown("## ⚙️ Core Admin Console")
    admin_pin = st.text_input("Enter Admin Master Pin:", type="password")
    if admin_pin == "777":
        st.success("🔓 Admin Access Granted!")
        new_ticker = st.text_input("Add Ticker Name (e.g., RELIANCE.NS):").upper().strip()
        if st.button("➕ Inject Asset"):
            if new_ticker and new_ticker not in st.session_state.custom_tickers:
                st.session_state.custom_tickers.append(new_ticker)
                st.rerun()
    st.markdown("---")

# 🎛️ INJECTING ORIGINAL PREMIUM LIGHT STYLE BLOCK
bg_color = "#f8fafc"
text_color = "#0f172a"
card_bg = "#ffffff"
border_color = "rgba(234, 88, 12, 0.4)"
price_color = "#ea580c"
title_color = "#475569"

st.markdown(f"""
<style>
.stApp {{ background-color: {bg_color} !important; color: {text_color} !important; }}
h1, h2, h3, p, span, label {{ color: {text_color} !important; font-weight: 600; }}
div[data-testid="stVComponentBlock"] > div[style*="border"] {{
    border: 1px solid {border_color} !important;
    border-radius: 12px !important;
    background: {card_bg} !important;
    padding: 16px !important;
    box-shadow: 0 4px 12px rgba(234, 88, 12, 0.05) !important;
}}
.card-header-flex {{ display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }}
.company-logo-avatar {{ 
    width: 40px; 
    height: 40px; 
    border-radius: 8px; 
    display: flex; 
    align-items: center; 
    justify-content: center; 
    font-size: 1.5rem; 
    font-weight: bold; 
    color: white;
}}
.price-text {{ font-family: 'Courier New', Courier, monospace; font-size: 1.7rem !important; font-weight: bold; color: {price_color} !important; margin: 2px 0px; }}
.stock-title {{ font-size: 1.1rem; font-weight: bold; color: {title_color} !important; }}
.indicator-text {{ font-size: 0.85rem; font-weight: 600; margin-top: 4px; }}

.alert-box {{
    padding: 14px 20px;
    border-radius: 10px;
    font-size: 2rem !important;
    font-weight: 900 !important;
    text-align: center;
    margin-bottom: 15px;
    letter-spacing: 2px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}}
.alert-buy {{ background-color: #10b981 !important; color: white !important; }}
.alert-sell {{ background-color: #ef4444 !important; color: white !important; }}
.alert-hold {{ background-color: #f59e0b !important; color: white !important; }}
</style>
""", unsafe_allow_html=True)

def get_brand_avatar(ticker):
    brands = {
        "SUZLON": {"bg": "#0284c7", "txt": "SZ"}, "RVNL": {"bg": "#b91c1c", "txt": "RV"},
        "NBCC": {"bg": "#0f766e", "txt": "NB"}, "GAIL": {"bg": "#15803d", "txt": "GL"},
        "IRFC": {"bg": "#1e3a8a", "txt": "IF"}, "IDEA": {"bg": "#e11d48", "txt": "VI"},
        "TATAPOWER": {"bg": "#0369a1", "txt": "TP"}, "HUDCO": {"bg": "#4d7c0f", "txt": "HD"},
        "IFCI": {"bg": "#6d28d9", "txt": "IF"}, "YESBANK": {"bg": "#256
