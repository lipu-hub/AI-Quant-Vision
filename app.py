import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="MarketMind AI Terminal", layout="wide")
st_autorefresh(interval=60 * 1000, key="datarefresh")

if 'view' not in st.session_state: st.session_state.view = 'landing'
if 'selected_stock' not in st.session_state: st.session_state.selected_stock = None

# 2. Advanced Styling
st.markdown("""
<style>
    .stApp { background: #0f172a; color: white; font-family: 'Inter', sans-serif; }
    .ticker-bar { background: rgba(56, 189, 248, 0.1); padding: 10px; border-radius: 10px; border: 1px solid #38bdf8; display: flex; justify-content: space-around; margin-bottom: 20px; font-weight: bold; }
    .card { background: rgba(255,255,255,0.05); padding: 25px; border-radius: 15px; border: 1px solid #38bdf8; text-align: center; margin-bottom: 10px; transition: 0.3s; }
    .card:hover { transform: translateY(-5px); border-color: #ffffff; }
    .prob-box { background: #1e293b; padding: 35px; border-radius: 20px; border-left: 10px solid #38bdf8; text-align: center; }
    .big-prob { font-size: 5.5rem; font-weight: 900; color: #38bdf8; margin: 0; line-height: 1; }
    div.stButton > button { background: #38bdf81a !important; border: 1px solid #38bdf8 !important; color: #38bdf8 !important; border-radius: 10px; width: 100%; height: 45px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 3. Data Engine
def get_clean_data(ticker, p="1mo"):
    try:
        df = yf.download(ticker, period=p, interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except: return None

# --- TOP TICKER LOGIC ---
def show_market_ticker():
    nifty = get_clean_data("^NSEI")
    sensex = get_clean_data("^BSESN")
    if nifty is not None and sensex is not None:
        n_price = round(float(nifty['Close'].iloc[-1]), 2)
        s_price = round(float(sensex['Close'].iloc[-1]), 2)
        st.markdown(f"""
        <div class="ticker-bar">
            <span>🇮🇳 NIFTY 50: <span style="color:#38bdf8;">{n_price}</span></span>
            <span>📈 SENSEX: <span style="color:#38bdf8;">{s_price}</span></span>
            <span>🕒 LIVE SYNC ACTIVE</span>
        </div>
        """, unsafe_allow_html=True)

# --- UI LOGIC ---

if st.session_state.view == 'landing':
    st.markdown("<div style='text-align:center; padding-top:100px;'><h1>MarketMind <span style='color:#38bdf8;'>AI</span></h1><p>Institutional Analytics for 18-year-old Quants.</p></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 1, 2])
    with c2:
        if st.button("🚀 OPEN AI TERMINAL"): 
            st.session_state.view = 'grid'; st.rerun()

elif st.session_state.view == 'grid':
    show_market_ticker() # Top Bar
    col_t1, col_t2 = st.columns([5, 1])
    with col_t1: st.title("Market Overview")
    with col_t2: 
        if st.button("🏠 Home"): st.session_state.view = 'landing'; st.rerun()
    
    stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "TATAMOTORS.NS", "ZOMATO.NS", "BTC-USD", "ETH-USD"]
    cols = st.columns(4)
    for i, s in enumerate(stocks):
        df = get_clean_data(s)
        with cols[i % 4]:
            if df is not None:
                curr = float(df['Close'].iloc[-1])
                st.markdown(f'<div class="card"><p style="color:#94a3b8; margin:0;">{s}</p><h2>₹{round(curr, 2)}</h2></div>', unsafe_allow_html=True)
                if st.button(f"Analyze {s.split('.')[0]}", key=s):
                    st.session_state.selected_stock = s
                    st.session_state.view = 'detail'; st.rerun()
            else: st.error(f"Syncing {s}...")

elif st.session_state.view == 'detail':
    s = st.session_state.selected_stock
    df = get_clean_data(s, p="3mo")
    if st.button("⬅️ Back to Dashboard"): st.session_state.view = 'grid'; st.rerun()

    if df is not None:
        curr = float(df['Close'].iloc[-1])
        sma20 = float(df['Close'].rolling(20).mean().iloc[-1])
        diff = ((curr - sma20) / sma20) * 100
        prob_val = int(max(10, min(95, 50 + (diff * 10))))
        
        st.header(f"Intelligence Report: {s}")
        cl, cr = st.columns([2, 1])
        with cl:
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        with cr:
            st.markdown(f"""
            <div class="prob-box">
                <p style="color:#94a3b8; font-weight:bold; margin-bottom:10px;">BULLISH PROBABILITY</p>
                <h1 class="big-prob">{prob_val}%</h1>
                <div style="margin-top:20px; font-weight:bold; color:{'#22c55e' if prob_val > 50 else '#ef4444'};">
                    {'🚀 BUY SIGNAL' if prob_val > 60 else '📉 SELL ALERT' if prob_val < 40 else '
