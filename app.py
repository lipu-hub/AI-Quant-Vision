import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. Setup
st.set_page_config(page_title="MarketMind AI", layout="wide")
st_autorefresh(interval=60 * 1000, key="datarefresh")

if 'view' not in st.session_state: st.session_state.view = 'landing'
if 'selected_stock' not in st.session_state: st.session_state.selected_stock = None

# 2. Styles
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: white; }
    .card { background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border: 1px solid #38bdf8; text-align: center; }
    .prob-val { font-size: 4rem; font-weight: 800; color: #38bdf8; line-height: 1; }
    div.stButton > button { background: #38bdf81a !important; border: 1px solid #38bdf8 !important; color: #38bdf8 !important; border-radius: 10px; width: 100%; }
</style>
""", unsafe_allow_html=True)

# 3. Data Fetch with Error Handling
def get_safe_data(s):
    try:
        df = yf.Ticker(s).history(period="1mo")
        if df.empty: return None
        return df
    except: return None

stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "TATAMOTORS.NS", "ZOMATO.NS", "BTC-USD"]

# --- UI ---
if st.session_state.view == 'landing':
    st.markdown("<h1 style='text-align:center; padding-top:100px;'>MarketMind AI</h1>", unsafe_allow_html=True)
    if st.button("🚀 ENTER DASHBOARD"): 
        st.session_state.view = 'grid'
        st.rerun()

elif st.session_state.view == 'grid':
    st.title("Market Overview")
    if st.button("🏠 Home"): st.session_state.view = 'landing'; st.rerun()
    
    cols = st.columns(4)
    for i, s in enumerate(stocks):
        df = get_safe_data(s)
        with cols[i % 4]:
            if df is not None:
                curr = round(df['Close'].iloc[-1], 2)
                st.markdown(f'<div class="card"><p>{s}</p><h3>₹{curr}</h3></div>', unsafe_allow_html=True)
                if st.button(f"Analyze {s.split('.')[0]}", key=s):
                    st.session_state.selected_stock = s
                    st.session_state.view = 'detail'
                    st.rerun()
            else:
                st.error(f"{s} Data Error")

elif st.session_state.view == 'detail':
    s = st.session_state.selected_stock
    df = get_safe_data(s)
    if st.button("⬅️ Back"): st.session_state.view = 'grid'; st.rerun()

    if df is not None:
        curr = df['Close'].iloc[-1]
        sma20 = df['Close'].rolling(20).mean().iloc[-1]
        
        # Simple Probability Calculation
        diff = ((curr - sma20) / sma20) * 100
        prob = round(max(5, min(95, 50 + (diff * 10))), 1)
        
        c1, c2 = st.columns([2, 1])
        with c1:
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with c2:
            st.markdown(f"""
            <div class="card" style="border-left: 8px solid #38bdf8;">
                <p style="margin:0; color:#94a3b8;">Bullish Probability</p>
                <div class="prob-val">{prob}%</div>
                <p style="font-weight:bold; color:{'#22c55e' if prob > 50 else '#ef4444'}">
                    {'BULLISH MOOD' if prob > 50 else 'BEARISH MOOD'}
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.metric("Live Price", f"₹{round(curr, 2)}")
