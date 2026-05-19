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
    st.session_state.selected_ticker = None
if "ticker_raw_name" not in st.session_state:
    st.session_state.ticker_raw_name = None
if "ai_analysis_result" not in st.session_state:
    st.session_state.ai_analysis_result = None
if "live_prices" not in st.session_state:
    st.session_state.live_prices = {}

if "custom_tickers" not in st.session_state:
    st.session_state.custom_tickers = [
        "SUZLON.NS", "IRFC.NS", "ZOMATO.NS", "PNB.NS", "GMRINFRA.NS",
        "IDEA.NS", "YESBANK.NS", "JPPOWER.NS", "RVNL.NS", "TATAPOWER.NS",
        "NHPC.NS", "SJVN.NS", "NBCC.NS", "HUDCO.NS", "IOC.NS",
        "SAIL.NS", "GAIL.NS", "IFCI.NS", "BTC-USD", "ETH-USD"
    ]

# 🎛️ NAVIGATION CONTROLLER WITH ADMIN MASTER PIN
with st.sidebar:
    st.markdown("## 🧭 Terminal Navigation")
    page = st.radio("Select Workspace View:", ["🎯 Live Whistleblower", "💼 My Risk Portfolio", "⚙️ Core Admin Console"])
    st.markdown("---")
    
    if page == "⚙️ Core Admin Console":
        st.markdown("### ⚙️ Core Admin Console")
        admin_pin = st.text_input("Enter Admin Master Pin:", type="password")
        if admin_pin == "777": 
            st.success("🔓 Admin Access Granted!")
            new_ticker = st.text_input("Add Ticker Name (e.g., RELIANCE.NS):").upper().strip()
            if st.button("➕ Inject Asset"):
                if new_ticker and new_ticker not in st.session_state.custom_tickers:
                    st.session_state.custom_tickers.append(new_ticker)
                    st.rerun()
            ticker_to_remove = st.selectbox("Select Asset to Remove:", ["None"] + st.session_state.custom_tickers)
            if ticker_to_remove != "None" and st.button("❌ Terminate Asset"):
                st.session_state.custom_tickers.remove(ticker_to_remove)
                st.rerun()
        elif admin_pin != "":
            st.error("🔒 Incorrect Pin.")

# 🎛️ INJECTING STYLE BLOCK
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
        box-shadow: 0 4px 12px rgba(234, 88, 12, 0.05) !important;
    }}
    .price-text {{ font-family: 'Courier New', Courier, monospace; font-size: 1.8rem !important; font-weight: bold; color: {price_color} !important; margin: 5px 0px; }}
    .stock-title {{ font-size: 1.2rem; font-weight: 600; color: {title_color} !important; }}
</style>
""", unsafe_allow_html=True)

tickers = st.session_state.custom_tickers

@st.cache_data(ttl=20)
def fetch_trading_data(ticker_name):
    try:
        df = yf.download(ticker_name, period="1mo", interval="15m", auto_adjust=True, progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
        return df
    except:
        return None

# ==========================================
# PAGE 1: LIVE WHISTLEBLOWER PANEL
# ==========================================
if page == "🎯 Live Whistleblower":
    st.title("🚀 MarketMind AI Trading Terminal")
    st.subheader("Live Budget Scanner with Real-Time Data")
    
    # 🚨 AUTO-SCANNER FRAGMENT
    @st.fragment(run_every=15)
    def live_alert_scanner():
        st.markdown("### 🚦 Immediate AI Whistleblower (Live Alerts)")
        buy_list, exit_list = [], []
        
        for ticker in tickers:
            df = yf.download(ticker, period="1d", interval="1m", auto_adjust=True, progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                latest_time = df.index[-1]
                current_time = pd.Timestamp.now(tz=latest_time.tz)
                time_diff_minutes = (current_time - latest_time).total_seconds() / 60
                
                close_series = df['Close'].squeeze()
                current_price = float(close_series.iloc[-1])
                prev_price = float(close_series.iloc[-2]) if len(close_series) > 1 else current_price
                price_change = ((current_price - prev_price) / prev_price) * 100
                clean_name = ticker.replace(".NS", "")
                
                st.session_state.live_prices[ticker] = {"price": current_price, "change": price_change, "status": "STABLE"}
                
                if time_diff_minutes < 15:
                    if price_change > 0.12:
                        st.success(f"🔥 **IMMEDIATE BUY ALERT:** {clean_name} (+{price_change:.2f}%)")
                        st.session_state.live_prices[ticker]["status"] = "BUY"
                        buy_list.append(ticker)
                    elif price_change < -0.12:
                        st.error(f"⚠️ **IMMEDIATE EXIT ALERT:** {clean_name} ({price_change:.2
