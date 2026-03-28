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

# 2. ADVANCED CSS (Professional Card Layout)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    .stApp { background-color: #0b0e14; font-family: 'Inter', sans-serif; color: white; }

    /* Modern Card Container */
    .stock-card {
        background: #161a25;
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        text-align: center;
        transition: 0.3s ease;
        margin-bottom: 20px;
    }
    .stock-card:hover {
        border-color: #00ffcc;
        background: #1c2130;
        transform: translateY(-5px);
    }

    /* Button Styling inside Card */
    div.stButton > button {
        background-color: transparent !important;
        border: 1px solid #00ffcc !important;
        color: #00ffcc !important;
        border-radius: 8px;
        font-weight: 700;
        width: 100%;
        margin-top: 10px;
    }
    div.stButton > button:hover {
        background-color: #00ffcc !important;
        color: #0b0e14 !important;
    }

    /* Text Sizes */
    .symbol-txt { color: #8890a6; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; margin-bottom: 5px;}
    .price-txt { font-size: 1.8rem; font-weight: 700; color: #ffffff; margin: 5px 0; }
    .change-txt { font-size: 1rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# 3. Data Logic
stocks_list = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "TATAMOTORS.NS", "ZOMATO.NS", "BTC-USD"]

@st.cache_data(ttl=600)
def get_market_data(s):
    try:
        data = yf.Ticker(s).history(period="1mo")
        return data
    except:
        return None

# --- UI LOGIC ---

# 🏠 PAGE 1: LANDING
if st.session_state.view == 'landing':
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 20px 0;">
        <h2 style="margin:0;">MarketMind <span style="color:#00ffcc;">AI</span></h2>
        <div style="color:#8890a6; font-size:0.9rem;">v3.0 GENERATIVE TERMINAL</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; padding: 100px 20px;">
        <h1 style="font-size: 4rem; font-weight: 800; letter-spacing: -2px; line-height: 1;">Trading made me the<br><span style="color:#00ffcc;">freedom</span> to focus on matters.</h1>
        <p style="color:#8890a6; font-size: 1.2rem; margin-top: 20px;">Experience institutional-grade AI predictions and real-time analytics.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([2, 1, 2])
    with c2:
        if st.button("🚀 ENTER TERMINAL", use_container_width=True):
            st.session_state.view = 'grid'
            st.rerun()

# 📊 PAGE 2: DASHBOARD
elif st.session_state.view == 'grid':
    col_h1, col_h2 = st.columns([5, 1])
    with col_h1:
        st.title("Market Overview")
    with col_h2:
        if st.button("🏠 Home"):
            st.session_state.view = 'landing'
            st.rerun()

    st.markdown("---")

    # Creating a 4-column Grid
    rows = [stocks_list[i:i + 4] for i in range(0, len(stocks_list), 4)]
    
    for row in rows:
        cols = st.columns(4)
        for idx, s in enumerate(row):
            df = get_market_data(s)
            if df is not None and not df.empty:
                curr = round(df['Close'].iloc[-1], 2)
                prev = round(df['Close'].iloc[-2], 2)
                chg = round(((curr - prev) / prev) * 100, 2)
                color = "#00ffcc" if chg >= 0 else "#ff4b4b"
                
                with cols[idx]:
                    # Professional Card UI
                    st.markdown(f"""
                    <div class="stock-card">
                        <div class="symbol-txt">{s.replace('.NS','')}</div>
                        <div class="price-txt">₹{curr}</div>
                        <div class="change-txt" style="color: {color};">
                            {'▲' if chg >= 0 else '▼'} {abs(chg)}%
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Selection Button
                    if st.button(f"Analyze {s.split('.')[0]}", key=f"btn_{s}"):
                        st.session_state.selected_stock = s
                        st.session_state.view = 'detail'
                        st.rerun()

# 🔍 PAGE 3: DETAIL
elif st.session_state.view == 'detail':
    s = st.session_state.selected_stock
    df = get_market_data(s)
    
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.view = 'grid'
        st.rerun()

    st.title(f"Live Analysis: {s}")
    
    c1, c2 = st.columns([2, 1])
    with c1:
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("AI Forecast")
        st.metric("Current Price", f"₹{round(df['Close'].iloc[-1], 2)}")
        # Simple Prediction Logic
        vol = (df['High'] - df['Low']).tail(10).mean()
        st.metric("Target", f"₹{round(df['Close'].iloc[-1] + vol*1.5, 2)}", delta=f"{round(vol*1.5, 2)}")
