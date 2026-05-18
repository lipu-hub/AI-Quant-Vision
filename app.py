import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai
import plotly.graph_objects as go

# ⚡ Page Configuration
st.set_page_config(page_title="MarketMind AI Terminal", layout="wide", initial_sidebar_state="expanded")

# 🔄 AUTOMATIC 30-SECOND TOTAL TERMINAL REFRESH ENGINE
if "refresh_counter" not in st.session_state:
    st.session_state.refresh_counter = 0

st.components.v1.html("""
<script>
    window.parent.document.addEventListener('DOMContentLoaded', (event) => {
        setInterval(() => {
            window.parent.document.querySelector('.stDeployButton').click();
        }, 30000);
    });
</script>
""", height=0)

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

# 🎛️ NAVIGATION CONTROLLER (MULTIPAGE INTERACTIVE UI)
with st.sidebar:
    st.markdown("## 🧭 Terminal Navigation")
    page = st.radio(
        "Select Workspace View:",
        ["🎯 Live Whistleblower", "💼 My Risk Portfolio", "⚙️ Core Admin Console"]
    )
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
</style>
""", unsafe_allow_html=True)

def get_brand_avatar(ticker):
    brands = {
        "SUZLON": {"bg": "#0284c7", "txt": "SZ"}, "RVNL": {"bg": "#b91c1c", "txt": "RV"},
        "NBCC": {"bg": "#0f766e", "txt": "NB"}, "GAIL": {"bg": "#15803d", "txt": "GL"},
        "IRFC": {"bg": "#1e3a8a", "txt": "IF"}, "IDEA": {"bg": "#e11d48", "txt": "VI"},
        "TATAPOWER": {"bg": "#0369a1", "txt": "TP"}, "HUDCO": {"bg": "#4d7c0f", "txt": "HD"},
        "IFCI": {"bg": "#6d28d9", "txt": "IF"}, "YESBANK": {"bg": "#2563eb", "txt": "YB"},
        "NHPC": {"bg": "#0369a1", "txt": "NH"}, "IOC": {"bg": "#ea580c", "txt": "IO"},
        "PNB": {"bg": "#991b1b", "txt": "PB"}, "JPPOWER": {"bg": "#d97706", "txt": "JP"},
        "SJVN": {"bg": "#475569", "txt": "SJ"}, "SAIL": {"bg": "#1e40af", "txt": "SL"},
        "BTC-USD": {"bg": "#f59e0b", "txt": "₿"}, "ETH-USD": {"bg": "#6366f1", "txt": "Ξ"}
    }
    return brands.get(ticker, {"bg": "#475569", "txt": "ST"})

@st.cache_data(ttl=10)
def fetch_trading_data(ticker_name):
    try:
        df = yf.download(ticker_name, period="1mo", interval="15m", auto_adjust=True, progress=False)
        if df.empty:
            df = yf.download(ticker_name, period="1mo", interval="1d", auto_adjust=True, progress=False)
        
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            close_prices = df['Close'].squeeze()
            df['EMA_20'] = close_prices.ewm(span=20, adjust=False).mean()
            
            delta = close_prices.diff()
            gain = (delta.where(delta > 0, 0)).ewm(alpha=1/14, adjust=False).mean()
            loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
            rs = gain / (loss + 1e-10)
            df['RSI'] = 100 - (100 / (1 + rs))
            return df
    except:
        return None
    return None

tickers = st.session_state.custom_tickers

# ==========================================
# PAGE 1: LIVE WHISTLEBLOWER PANEL
# ==========================================
if page == "🎯 Live Whistleblower":
    st.title("🚀 MarketMind AI Trading Terminal")
    st.subheader("Live Budget Scanner with Real-Time Risk & News Sentiment Tracker")

    buy_alerts, sell_alerts, hold_alerts = [], [], []

    for tick in tickers:
        t_df = fetch_trading_data(tick)
        if t_df is not None and not t_df.empty:
            r_val = float(t_df['RSI'].iloc[-1]) if 'RSI' in t_df.columns else 50.0
            c_price = float(t_df['Close'].iloc[-1])
            c_name = tick.replace(".NS", "")
            base_text = f"**{c_name}** at ₹{c_price:,.2f} (RSI: {r_val:.1f})"
            
            if r_val <= 30:
                buy_alerts.append(f"🟢 **[BUY]** {base_text} -> Strong bounce setup!")
            elif r_val >= 65:
                sell_alerts.append(f"🔴 **[SELL]** {base_text} -> Profit booking zone.")
            else:
                hold_alerts.append(f"⚠️ **[HOLD]** {base_text} -> Range bound trend.")

    st.markdown("### 🚦 Immediate AI Whistleblower (Live Action Panel)")
    b_col, s_col, h_col = st.columns(3)
    with b_col:
        st.markdown("#### 🟢 IMMEDIATE BUY DECK")
        if buy_alerts:
            for al in buy_alerts[:5]: st.success(al)
        else: st.info("No active buy levels.")
    with s_col:
        st.markdown("#### 🔴 IMMEDIATE SELL DECK")
        if sell_alerts:
            for al in sell_alerts[:5]: st.error(al)
        else: st.info("No heavy sell overheads.")
    with h_col:
        st.markdown("#### 🟡 ACTIVE HOLD DECK")
        if hold_alerts:
            for al in hold_alerts[:5]: st.warning(al)
        else: st.info("No range assets.")

    st.markdown("---")
    st.markdown("### 🔍 Intelligent Asset Filter")
    cols = st.columns(4)
    for i, ticker in enumerate(tickers):
        with cols[i % 4]:
            data_df = fetch_trading_data(ticker)
            if data_df is not None and not data_df.empty:
                close_series = data_df['Close'].squeeze()
                latest_price = float(close_series.iloc[-1])
                symbol = "$" if "USD" in ticker else "₹"
                clean_name = ticker.replace(".NS", "")
                meta = get_brand_avatar(clean_name)
                
                st.session_state.live_prices[ticker] = latest_price
                rsi_val = float(data_df['RSI'].iloc[-1]) if 'RSI' in data_df.columns else 50.0
                rsi_color = "#ef4444" if rsi_val >= 70 else ("#10b981" if rsi_val <= 30 else "#475569")
                rsi_status = "OVERBOUGHT" if rsi_val >= 70 else ("OVERSOLD" if rsi_val <= 30 else "NEUTRAL")
