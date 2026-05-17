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

# Initialize Session States
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {}
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = None
if "ai_analysis_result" not in st.session_state:
    st.session_state.ai_analysis_result = None
if "ticker_raw_name" not in st.session_state:
    st.session_state.ticker_raw_name = None

# 🛠️ ADMIN PANEL: Dynamic Ticker List State Initialization
if "custom_tickers" not in st.session_state:
    st.session_state.custom_tickers = [
        "SUZLON.NS", "IRFC.NS", "ZOMATO.NS", "PNB.NS", "GMRINFRA.NS", 
        "IDEA.NS", "YESBANK.NS", "JPPOWER.NS", "RVNL.NS", "TATAPOWER.NS", 
        "NHPC.NS", "SJVN.NS", "NBCC.NS", "HUDCO.NS", "IOC.NS", 
        "SAIL.NS", "GAIL.NS", "IFCI.NS", "BTC-USD", "ETH-USD"
    ]

# 🌓 THEME CONTROL & ADMIN WORKBENCH IN SIDEBAR
with st.sidebar:
    st.markdown("## 🎨 Terminal Customization")
    ui_theme = st.selectbox("Select Display Theme:", ["🟠 Deep Dark Orange", "⚪ Classic Light Orange"])
    st.markdown("---")
    
    # ⚙️ SECURE ADMIN CONSOLE INTERFACE
    st.markdown("## ⚙️ Core Admin Console")
    admin_pin = st.text_input("Enter Admin Master Pin:", type="password", help="Enter pin to unlock stock controller database flow.")
    
    if admin_pin == "777":
        st.success("🔓 Admin Access Granted!")
        new_ticker = st.text_input("Add Ticker Name (e.g., RELIANCE.NS, DOGE-USD):").upper().strip()
        if st.button("➕ Inject Asset into Engine"):
            if new_ticker and new_ticker not in st.session_state.custom_tickers:
                st.session_state.custom_tickers.append(new_ticker)
                st.toast(f"Injected {new_ticker} successfully into the matrix grid flow!")
                st.rerun()
        
        st.markdown("---")
        ticker_to_remove = st.selectbox("Select Asset to Liquidate/Remove:", ["None"] + st.session_state.custom_tickers)
        if ticker_to_remove != "None" and st.button("❌ Terminate Asset"):
            st.session_state.custom_tickers.remove(ticker_to_remove)
            st.toast(f"Terminated {ticker_to_remove} entry configuration.")
            st.rerun()
    elif admin_pin != "":
        st.error("🔒 Incorrect Pin Token. Engine access locked.")
    st.markdown("---")

# 🎛️ DYNAMIC CSS INJECTION
if ui_theme == "🟠 Deep Dark Orange":
    bg_color = "#0b0f19"
    text_color = "#e2e8f0"
    card_bg = "linear-gradient(145deg, #111827, #0f172a)"
    border_color = "rgba(249, 115, 22, 0.3)"
    hover_border = "#f97316"
    price_color = "#f97316"
    title_color = "#94a3b8"
    plotly_template = "plotly_dark"
else:
    bg_color = "#f8fafc"
    text_color = "#0f172a"
    card_bg = "#ffffff"
    border_color = "rgba(234, 88, 12, 0.4)"
    hover_border = "#ea580c"
    price_color = "#ea580c"
    title_color = "#475569"
    plotly_template = "plotly_white"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color} !important; color: {text_color} !important; }}
    h1, h2, h3, p, span, label {{ color: {text_color} !important; font-weight: 600; }}
    div[data-testid="stMarkdownContainer"] p {{ color: {text_color} !important; }}
    div[data-testid="stVComponentBlock"] > div[style*="border"] {{
        border: 1px solid {border_color} !important;
        border-radius: 12px !important;
        background: {card_bg} !important;
        padding: 20px !important;
        box-shadow: 0 4px 15px rgba(249, 115, 22, 0.05) !important;
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }}
    div[data-testid="stVComponentBlock"] > div[style*="border"]:hover {{
        transform: translateY(-2px);
        border-color: {hover_border} !important;
        box-shadow: 0 4px 20px rgba(249, 115, 22, 0.25) !important;
    }}
    .price-text {{
        font-family: 'Courier New', Courier, monospace;
        font-size: 1.8rem !important;
        font-weight: bold;
        color: {price_color} !important;
        margin: 5px 0px;
    }}
    .stock-title {{ font-size: 1.2rem; font-weight: 600; color: {title_color} !important; }}
    button[data-testid="stBaseButton-secondary"] {{
        background-color: transparent !important;
        border: 1px solid {hover_border} !important;
        color: {text_color} !important;
        border-radius: 8px !important;
    }}
    button[data-testid="stBaseButton-secondary"]:hover {{
        background-color: {hover_border} !important;
        color: white !important;
    }}
</style>
""", unsafe_allow_html=True)

tickers = st.session_state.custom_tickers
st.title("🚀 MarketMind AI Trading Terminal")
st.subheader("Live Budget Scanner with Real-Time Admin Asset Control")

# Helper function to extract a single clean column from yfinance multi-index DataFrame
def get_clean_column(df, col_name, ticker):
    if col_name in df.columns:
        col_data = df[col_name]
        if isinstance(col_data, pd.DataFrame):
            if ticker in col_data.columns:
                return col_data[ticker]
            return col_data.iloc[:, 0]
        return col_data
    # Try multi-index direct lookup
    for col in df.columns:
        if isinstance(col, tuple) and col[0] == col_name:
            return df[col]
    return pd.Series(dtype='float64')

# 🧠 Advanced Quant Indicators Engine
@st.cache_data(ttl=30)
def fetch_trading_data(ticker_name):
    try:
        df = yf.download(ticker_name, period="1mo", interval="15m", auto_adjust=True, progress=False)
        if not df.empty:
            # Multi-index DataFrame को फ्लैट और सा
