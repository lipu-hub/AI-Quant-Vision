import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import numpy as np

# 1. Page Configuration
st.set_page_config(page_title="MarketMind AI", layout="wide", page_icon="📈")
st_autorefresh(interval=60 * 1000, key="datarefresh")

# --- INITIALIZE VIEW ---
if 'view' not in st.session_state:
    st.session_state.view = 'landing'
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = None

# 2. PREMIUM CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); font-family: 'Inter', sans-serif; color: #f1f5f9; }
    
    /* Card & Box Styling */
    .stock-card { background: rgba(255, 255, 255, 0.03); border-radius: 20px; padding: 20px; border: 1px solid rgba(255, 255, 255, 0.1); text-align: center; margin-bottom: 15px; }
    .ai-engine-box { background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 20px; border: 1px solid #38bdf8; }
    
    /* Probability Text */
    .prob-percent { font-size: 3rem; font-weight: 800; color: #38bdf8; margin: 0; }
    .prob-label { font-size: 1.2rem; color: #94a3b8; font-weight: 600; }
    
    /* Buttons */
    div.stButton > button { background: rgba(56, 189, 248, 0.1) !important; border: 1px solid #38bdf8 !important; color: #38bdf8 !important; border-radius: 12px; width: 100%; font-weight: bold; }
    div.stButton > button:hover { background: #38bdf8 !important; color: #0f172a !important; }
</style>
""", unsafe_allow_html=True)

# 3. Data Fetch
@st.cache_data(ttl=600)
def get_data(s, p="3mo"):
    try: return yf.Ticker(s).history(period=p)
    except: return None

stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "TATAMOTORS.NS", "ZOMATO.NS", "BTC-USD"]

# --- NAVIGATION ---

if st.session_state.view == 'landing':
    st.markdown("<div style='text-align:center; padding-top:100px;'><h1>MarketMind <span style='color:#38bdf8;'>AI</span></h1><p style='color:#94a3b8;'>Simple. Smart. Profitable.</p></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 1, 2])
    with c2:
        if st.button("🚀 OPEN DASHBOARD"):
            st.session_state.view = 'grid'; st.rerun()

elif st.session_state.view == 'grid':
    st.title("Live Markets")
    if st.button("🏠 Home", key="home_btn"): st.session_state.view = 'landing'; st.rerun()
    
    grid = [stocks[i:i+4] for i in range(0, len(stocks), 4)]
    for row in grid:
        cols = st.columns(4)
        for idx, s in enumerate(row):
            df = get_data(s)
            if df is not None:
                curr = round(df['Close'].iloc[-1], 2)
                with cols[idx]:
                    st.markdown(f'<div class="stock-card"><div style="color:#94a3b8; font-size:0.8rem;">{s}</div><div style="font-size:1.8rem; font-weight:800;">₹{curr}</div></div>', unsafe_allow_html=True)
                    if st.button(f"View Analysis", key=s):
                        st.session_state.selected_stock = s
                        st.session_state.view = 'detail'; st.rerun()

elif st.session_state.view == 'detail':
    s = st.session_state.selected_stock
    df = get_data(s)
    if st.button("⬅️ Back to Dashboard"): st.session_state.view = 'grid'; st.rerun()
    
    st.header(f"AI Analysis: {s.split('.')[0]}")
    
    col_chart, col_ai = st.columns([2, 1])
    
    with col_chart:
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        
    with col_ai:
        st.markdown("<div class='ai-engine-box'>", unsafe_allow_html=True)
        
        # --- SIMPLE PROBABILITY LOGIC ---
        curr = df['Close'].iloc[-1]
        sma20 = df['Close'].rolling(20).mean().iloc[-1]
        
        # Calculation: How much price is above/below the average
        diff = ((curr - sma20) / sma20) * 100
        prob = 50 + (diff * 5) # Scale to percentage
        prob = max(10, min(95, round(prob, 1))) # Keep between 10% and 95%
        
        st.markdown(f"<p class='prob-label'>Bullish Probability</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='prob-percent'>{prob}%</p>", unsafe_allow_html=True)
        
        # Color coding for probability
        p_color = "#22c55e" if prob > 50 else "#ef4444"
        st.markdown(f"<div style='background:{p_color}; height:8px; width:{prob}%; border-radius:10px;'></div>", unsafe_allow_html=True)
        
        st.write("---")
        
        # Simple Language Forecasting
        vol = df['Close'].pct_change().std()
        target = round(curr * (1 + vol), 2)
        
        st.subheader("AI Prediction")
        if prob > 60:
            st.success(f"📈 UPWARD TREND: Likely to hit ₹{target}")
        elif prob < 40:
            st.error(f"📉 DOWNWARD TREND: High risk of falling.")
        else:
            st.info("⚖️ SIDEWAYS: Market is currently neutral.")
            
        st.markdown("</div>", unsafe_allow_html=True)
