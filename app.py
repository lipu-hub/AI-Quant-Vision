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

# 2. Styling (Simple & Professional)
st.markdown("""
<style>
    .stApp { background: #0f172a; color: white; }
    .card { background: rgba(255,255,255,0.05); padding: 25px; border-radius: 15px; border: 1px solid #38bdf8; text-align: center; margin-bottom: 10px;}
    .prob-box { background: #1e293b; padding: 30px; border-radius: 20px; border-left: 10px solid #38bdf8; text-align: center; }
    .big-prob { font-size: 5rem; font-weight: 900; color: #38bdf8; margin: 0; }
    .status-tag { font-size: 1.5rem; font-weight: 700; padding: 5px 20px; border-radius: 50px; display: inline-block; margin-top: 10px; }
    div.stButton > button { background: #38bdf81a !important; border: 1px solid #38bdf8 !important; color: #38bdf8 !important; border-radius: 10px; width: 100%; height: 45px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 3. Safe Data Engine
def get_market_data(ticker):
    try:
        data = yf.download(ticker, period="1mo", interval="1d", progress=False)
        if data.empty or len(data) < 2: return None
        return data
    except: return None

stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "TATAMOTORS.NS", "ZOMATO.NS", "BTC-USD"]

# --- UI Logic ---

if st.session_state.view == 'landing':
    st.markdown("<div style='text-align:center; padding-top:100px;'><h1>MarketMind <span style='color:#38bdf8;'>AI</span></h1><p>Institutional-grade forecasting for everyone.</p></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 1, 2])
    with c2:
        if st.button("🚀 ENTER TERMINAL"): 
            st.session_state.view = 'grid'
            st.rerun()

elif st.session_state.view == 'grid':
    st.title("Market Overview")
    if st.button("🏠 Home"): 
        st.session_state.view = 'landing'; st.rerun()
    
    st.markdown("---")
    cols = st.columns(4)
    for i, s in enumerate(stocks):
        df = get_market_data(s)
        with cols[i % 4]:
            if df is not None:
                # Price extraction fixed for multi-index or single index
                curr = float(df['Close'].iloc[-1])
                st.markdown(f'<div class="card"><p style="color:#94a3b8; margin:0;">{s}</p><h2 style="margin:5px 0;">₹{round(curr, 2)}</h2></div>', unsafe_allow_html=True)
                if st.button(f"Analyze {s.split('.')[0]}", key=s):
                    st.session_state.selected_stock = s
                    st.session_state.view = 'detail'; st.rerun()
            else:
                st.error(f"⚠️ {s} Syncing...")

elif st.session_state.view == 'detail':
    s = st.session_state.selected_stock
    df = get_market_data(s)
    if st.button("⬅️ Back to Dashboard"): 
        st.session_state.view = 'grid'; st.rerun()

    if df is not None:
        curr = float(df['Close'].iloc[-1])
        sma20 = float(df['Close'].rolling(20).mean().iloc[-1])
        
        # PROBABILITY LOGIC
        diff = ((curr - sma20) / sma20) * 100
        prob_val = round(max(10, min(95, 55 + (diff * 8))), 1)
        
        st.header(f"Intelligence Report: {s}")
        
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.update_layout(template="plotly_dark", height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            
        with col_right:
            st.markdown(f"""
            <div class="prob-box">
                <p style="color:#94a3b8; font-weight:bold; margin-bottom:10px;">BULLISH PROBABILITY</p>
                <h1 class="big-prob">{prob_val}%</h1>
                <div class="status-tag" style="background:{'#22c55e33' if prob_val > 50 else '#ef444433'}; color:{'#22c55e' if prob_val > 50 else '#ef4444'};">
                    {'🚀 STRONG BUY' if prob_val > 65 else '📈 WEAK BULLISH' if prob_val > 50 else '📉 BEARISH ALERT'}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("---")
            st.metric("Current Market Price", f"₹{round(curr, 2)}")
            
            # Simple Forecast
            vol = float(df['Close'].pct_change().std())
            st.info(f"💡 AI Forecast: Expecting move towards ₹{round(curr * (1+vol), 2)}")
