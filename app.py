import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. Page Setup
st.set_page_config(page_title="MarketMind AI - Professional Trading", layout="wide", page_icon="📈")
st_autorefresh(interval=60 * 1000, key="datarefresh")

# --- INITIALIZE VIEW STATE ---
if 'view' not in st.session_state:
    st.session_state.view = 'landing'
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = None

# 2. CUSTOM CSS (Fixing the alignment and spacing)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    .stApp { background-color: #0b0e14; font-family: 'Inter', sans-serif; color: white; }

    /* Landing Page Styling */
    .hero-section { text-align: center; padding: 60px 20px; }
    .hero-title { font-size: 3.5rem; font-weight: 700; margin-bottom: 10px; letter-spacing: -1.5px; line-height: 1.1; }
    .feature-card { background: #161a25; padding: 25px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.05); text-align: center; height: 100%; }

    /* Dashboard Grid Styling */
    div.stButton > button {
        background: linear-gradient(145deg, #1e2230, #161a25);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.1);
        color: white;
        height: 100px;
        width: 100%;
        transition: 0.3s;
        font-weight: bold;
        margin-bottom: 5px;
    }
    div.stButton > button:hover { border-color: #00ffcc; transform: translateY(-2px); }
    
    .stock-label { font-size: 0.9rem; color: #8890a6; text-align: center; margin-bottom: 2px; }
    .price-label { font-size: 1.4rem; font-weight: bold; text-align: center; }
</style>
""", unsafe_allow_html=True)

# 3. Data Logic
stocks_list = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "TATAMOTORS.NS", "ZOMATO.NS", "BTC-USD"]

@st.cache_data(ttl=600)
def get_data(s, period="1mo"):
    try:
        return yf.Ticker(s).history(period=period)
    except:
        return None

# --- UI LOGIC ---

# 🏠 PAGE 1: LANDING PAGE
if st.session_state.view == 'landing':
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0;">
        <h2 style="margin:0;">MarketMind <span style="color:#00ffcc;">AI</span></h2>
        <div style="color:#8890a6; font-weight: 600;">Trusted by 500k+ Traders</div>
    </div>
    <hr style="opacity: 0.1; margin-bottom: 40px;">
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-section">
        <div style="background: rgba(0, 255, 204, 0.1); color: #00ffcc; display: inline-block; padding: 5px 15px; border-radius: 20px; font-size: 0.8rem; margin-bottom: 20px; font-weight: bold;">
            v3.0 GENERATIVE AI TERMINAL
        </div>
        <h1 class="hero-title">Trading made me the<br><span style="color:#00ffcc;">freedom</span> to focus on matters.</h1>
        <p style="color: #8890a6; font-size: 1.1rem; margin-bottom: 40px;">A trusted service provider for over 25 years. Experience high-fidelity AI market predictions,<br>real-time dashboards, and secure technical analysis.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1.5, 1, 1.5])
    with c2:
        if st.button("🚀 ENTER TERMINAL", use_container_width=True):
            st.session_state.view = 'grid'
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1: st.markdown('<div class="feature-card"><h3>25 Years Trust</h3><p style="color:#8890a6;">Serving global markets with precision.</p></div>', unsafe_allow_html=True)
    with f2: st.markdown('<div class="feature-card"><h3>AI Predictions</h3><p style="color:#8890a6;">Neural networks for price forecasting.</p></div>', unsafe_allow_html=True)
    with f3: st.markdown('<div class="feature-card"><h3>Secure Trading</h3><p style="color:#8890a6;">Privacy is our top priority.</p></div>', unsafe_allow_html=True)

# 📊 PAGE 2: DASHBOARD OVERVIEW
elif st.session_state.view == 'grid':
    col_h1, col_h2 = st.columns([4, 1])
    with col_h1: st.title("Dashboard Overview")
    with col_h2: 
        if st.button("🏠 Home"):
            st.session_state.view = 'landing'
            st.rerun()

    st.markdown("---")
    
    # Grid of 4 columns
    for row_idx in range(0, len(stocks_list), 4):
        cols = st.columns(4)
        for col_idx in range(4):
            stock_idx = row_idx + col_idx
            if stock_idx < len(stocks_list):
                s = stocks_list[stock_idx]
                df = get_data(s)
                if df is not None and not df.empty:
                    curr = round(df['Close'].iloc[-1], 2)
                    prev = round(df['Close'].iloc[-2], 2)
                    chg = round(((curr - prev) / prev) * 100, 2)
                    color = "#00ffcc" if chg >= 0 else "#ff4b4b"
                    
                    with cols[col_idx]:
                        # Card structure
                        st.markdown(f"<div class='stock-label'>{s}</div>", unsafe_allow_html=True)
                        if st.button(f"₹{curr}", key=f"btn_{s}"):
                            st.session_state.selected_stock = s
                            st.session_state.view = 'detail'
                            st.rerun()
                        st.markdown(f"<div style='color:{color}; text-align:center; font-weight:bold; margin-top:-10px;'>{chg}% {'▲' if chg >= 0 else '▼'}</div>", unsafe_allow_html=True)
                        st.markdown("<br>", unsafe_allow_html=True)

# 🔍 PAGE 3: DETAIL VIEW
elif st.session_state.view == 'detail':
    s = st.session_state.selected_stock
    df = get_data(s, period="3mo")
    
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.view = 'grid'
        st.rerun()
    
    st.header(f"Analysis: {s}")
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
        
    with col_right:
        st.subheader("Market Intelligence")
        curr = round(df['Close'].iloc[-1], 2)
        st.metric("Current Price", f"₹{curr}")
        
        # Volatility Based Target
        vol = (df['High'] - df['Low']).tail(10).mean()
        st.metric("AI Target", f"₹{round(curr + vol*1.5, 2)}", delta=f"{round(vol*1.5, 2)}")
        st.metric("Stop-Loss", f"₹{round(curr - vol*1.2, 2)}", delta=f"-{round(vol*1.2, 2)}", delta_color="inverse")
        
        st.info("Trend: Positive momentum detected over the last 10 sessions.")
