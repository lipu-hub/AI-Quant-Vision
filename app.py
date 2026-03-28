import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="MarketMind AI", layout="wide")
st_autorefresh(interval=60 * 1000, key="datarefresh")

if 'view' not in st.session_state: st.session_state.view = 'landing'
if 'selected_stock' not in st.session_state: st.session_state.selected_stock = None

# 2. Styles
st.markdown("""
<style>
    .stApp { background: #0f172a; color: white; }
    .ticker-bar { background: rgba(56, 189, 248, 0.1); padding: 15px; border-radius: 12px; border: 1px solid #38bdf8; display: flex; justify-content: space-around; margin-bottom: 25px; }
    .card { background: rgba(255,255,255,0.05); padding: 25px; border-radius: 15px; border: 1px solid #38bdf8; text-align: center; }
    .prob-box { background: #1e293b; padding: 35px; border-radius: 20px; border-left: 10px solid #38bdf8; text-align: center; }
    .big-prob { font-size: 5rem; font-weight: 900; color: #38bdf8; margin: 0; }
    div.stButton > button { background: #38bdf81a !important; border: 1px solid #38bdf8 !important; color: #38bdf8 !important; border-radius: 10px; width: 100%; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 3. Engine
def get_clean_data(ticker):
    try:
        df = yf.download(ticker, period="1mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except: return None

# --- UI ---
if st.session_state.view == 'landing':
    st.markdown("<h1 style='text-align:center; padding-top:100px;'>MarketMind AI</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 1, 2])
    with c2:
        if st.button("🚀 ENTER TERMINAL"): st.session_state.view = 'grid'; st.rerun()

elif st.session_state.view == 'grid':
    # Top Ticker
    nifty = get_clean_data("^NSEI")
    if nifty is not None:
        n_p = round(float(nifty['Close'].iloc[-1]), 2)
        st.markdown(f'<div class="ticker-bar"><span>🇮🇳 NIFTY 50: <span style="color:#38bdf8;">{n_p}</span></span><span>🕒 LIVE SYNC</span></div>', unsafe_allow_html=True)
    
    if st.button("🏠 Home"): st.session_state.view = 'landing'; st.rerun()
    
    stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "TATAMOTORS.NS", "ZOMATO.NS", "BTC-USD", "ETH-USD"]
    cols = st.columns(4)
    for i, s in enumerate(stocks):
        df = get_clean_data(s)
        with cols[i % 4]:
            if df is not None:
                curr = round(float(df['Close'].iloc[-1]), 2)
                st.markdown(f'<div class="card"><p>{s}</p><h3>₹{curr}</h3></div>', unsafe_allow_html=True)
                if st.button(f"Analyze {s.split('.')[0]}", key=s):
                    st.session_state.selected_stock = s; st.session_state.view = 'detail'; st.rerun()

elif st.session_state.view == 'detail':
    s = st.session_state.selected_stock
    df = get_clean_data(s)
    if st.button("⬅️ Back"): st.session_state.view = 'grid'; st.rerun()

    if df is not None:
        curr = float(df['Close'].iloc[-1])
        sma20 = float(df['Close'].rolling(20).mean().iloc[-1])
        prob = int(max(10, min(95, 50 + (((curr - sma20) / sma20) * 1000))))
        
        # Fixed logic for Signal Text
        if prob > 60: status = "🚀 BUY SIGNAL"
        elif prob < 40: status = "📉 SELL ALERT"
        else: status = "⚖️ NEUTRAL"

        st.header(f"Intelligence: {s}")
        cl, cr = st.columns([2, 1])
        with cl:
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low
