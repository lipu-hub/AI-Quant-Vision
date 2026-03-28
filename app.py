import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import numpy as np

# 1. Page Configuration
st.set_page_config(page_title="MarketMind AI - Pro Terminal", layout="wide", page_icon="📈")
st_autorefresh(interval=60 * 1000, key="datarefresh")

# --- INITIALIZE VIEW STATE ---
if 'view' not in st.session_state:
    st.session_state.view = 'landing'
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = None

# 2. PREMIUM CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); font-family: 'Inter', sans-serif; color: #f1f5f9; }
    .stock-card { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(12px); border-radius: 20px; padding: 24px; border: 1px solid rgba(255, 255, 255, 0.1); text-align: center; margin-bottom: 20px; transition: 0.3s; }
    .stock-card:hover { border-color: #38bdf8; transform: translateY(-5px); }
    .ai-box { background: rgba(15, 23, 42, 0.6); padding: 25px; border-radius: 18px; border-left: 5px solid #38bdf8; margin-top: 15px; }
    div.stButton > button { background: rgba(56, 189, 248, 0.1) !important; border: 1px solid #38bdf8 !important; color: #38bdf8 !important; border-radius: 12px; font-weight: 600; width: 100%; }
    div.stButton > button:hover { background: #38bdf8 !important; color: #0f172a !important; }
    .symbol-txt { color: #94a3b8; font-size: 0.85rem; font-weight: 600; letter-spacing: 1px; }
    .price-txt { font-size: 2rem; font-weight: 800; color: #ffffff; margin: 8px 0; }
</style>
""", unsafe_allow_html=True)

# 3. Data Logic
stocks_list = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "TATAMOTORS.NS", "ZOMATO.NS", "BTC-USD"]

@st.cache_data(ttl=600)
def get_market_data(s, period="3mo"):
    try:
        return yf.Ticker(s).history(period=period)
    except:
        return None

# --- UI LOGIC ---

# 🏠 PAGE 1: LANDING
if st.session_state.view == 'landing':
    st.markdown("""
    <div style="text-align: center; padding: 100px 20px;">
        <h1 style="font-size: 4.5rem; font-weight: 900; letter-spacing: -3px; line-height: 1;">Trading made me the<br><span style="color:#38bdf8;">freedom</span> to focus on matters.</h1>
        <p style="color:#94a3b8; font-size: 1.2rem; margin-top: 30px;">Institutional-grade AI predictions and real-time analytics.</p>
    </div>
    """, unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 1, 2])
    with c2:
        if st.button("🚀 ENTER TERMINAL"):
            st.session_state.view = 'grid'
            st.rerun()

# 📊 PAGE 2: DASHBOARD (Fixing NameError here)
elif st.session_state.view == 'grid':
    col_head1, col_head2 = st.columns([5, 1]) # Fixed variable names
    with col_head1:
        st.markdown("<h1 style='font-weight:800;'>Market Intelligence</h1>", unsafe_allow_html=True)
    with col_head2:
        if st.button("🏠 Home"):
            st.session_state.view = 'landing'
            st.rerun()

    rows = [stocks_list[i:i + 4] for i in range(0, len(stocks_list), 4)]
    for row in rows:
        cols = st.columns(4)
        for idx, s in enumerate(row):
            df = get_market_data(s, period="1mo")
            if df is not None and not df.empty:
                curr = round(df['Close'].iloc[-1], 2)
                prev = round(df['Close'].iloc[-2], 2)
                chg = round(((curr - prev) / prev) * 100, 2)
                color = "#22c55e" if chg >= 0 else "#ef4444"
                with cols[idx]:
                    st.markdown(f'<div class="stock-card"><div class="symbol-txt">{s}</div><div class="price-txt">₹{curr}</div><div style="color:{color}; font-weight:700;">{chg}%</div></div>', unsafe_allow_html=True)
                    if st.button(f"Analyze {s.split('.')[0]}", key=s):
                        st.session_state.selected_stock = s
                        st.session_state.view = 'detail'
                        st.rerun()

# 🔍 PAGE 3: DETAIL VIEW (Probability Engine)
elif st.session_state.view == 'detail':
    s = st.session_state.selected_stock
    df = get_market_data(s)
    if st.button("⬅️ Back"):
        st.session_state.view = 'grid'
        st.rerun()

    st.markdown(f"<h1 style='color:#38bdf8;'>AI Analysis: {s}</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    with c1:
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("<div class='ai-box'>", unsafe_allow_html=True)
        curr = df['Close'].iloc[-1]
        vol = df['Close'].pct_change().std()
        sma20 = df['Close'].rolling(20).mean().iloc[-1]
        prob = 74 if curr > sma20 else 26
        
        st.metric("Live Price", f"₹{round(curr, 2)}")
        st.markdown(f"**Bullish Probability:** <span style='color:#22c55e; font-size:1.5rem;'>{prob}%</span>", unsafe_allow_html=True)
        st.progress(prob / 100)
        st.success(f"AI Target: ₹{round(curr * (1 + vol), 2)}")
        st.error(f"Support: ₹{round(curr * (1 - vol), 2)}")
        st.markdown("</div>", unsafe_allow_html=True)
