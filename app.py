import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. Page Setup
st.set_page_config(page_title="MarketMind AI - Pro Terminal", layout="wide", page_icon="📈")
st_autorefresh(interval=60 * 1000, key="datarefresh")

# --- INITIALIZE VIEW STATE ---
if 'view' not in st.session_state:
    st.session_state.view = 'landing'
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = None

# 2. PREMIUM CSS (Blue-Grey Gradient & Glassmorphism)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    /* Background Gradient (Not pure black) */
    .stApp { 
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); 
        font-family: 'Inter', sans-serif; 
        color: #f1f5f9; 
    }

    /* Glassmorphic Card Styling */
    .stock-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        margin-bottom: 20px;
    }
    .stock-card:hover {
        background: rgba(255, 255, 255, 0.07);
        border-color: #38bdf8; /* Sky Blue Accent */
        transform: translateY(-8px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }

    /* Professional Selection Button */
    div.stButton > button {
        background: rgba(56, 189, 248, 0.1) !important;
        border: 1px solid #38bdf8 !important;
        color: #38bdf8 !important;
        border-radius: 12px;
        font-weight: 600;
        width: 100%;
        margin-top: 15px;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background: #38bdf8 !important;
        color: #0f172a !important;
    }

    /* Typography */
    .symbol-txt { color: #94a3b8; font-size: 0.85rem; font-weight: 600; letter-spacing: 1px; }
    .price-txt { font-size: 2rem; font-weight: 800; color: #ffffff; margin: 8px 0; }
    .change-txt { font-size: 1.1rem; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# 3. Data Logic
stocks_list = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "TATAMOTORS.NS", "ZOMATO.NS", "BTC-USD"]

@st.cache_data(ttl=600)
def get_market_data(s):
    try:
        return yf.Ticker(s).history(period="1mo")
    except:
        return None

# --- UI LOGIC ---

# 🏠 PAGE 1: LANDING
if st.session_state.view == 'landing':
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 20px 0;">
        <h2 style="margin:0; font-weight:800;">MarketMind <span style="color:#38bdf8;">AI</span></h2>
        <div style="background: rgba(56, 189, 248, 0.1); color: #38bdf8; padding: 5px 15px; border-radius: 20px; font-size: 0.8rem; font-weight: bold;">TRUSTED BY 500K+ TRADERS</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; padding: 120px 20px;">
        <h1 style="font-size: 4.5rem; font-weight: 900; letter-spacing: -3px; line-height: 1; color: #f8fafc;">
            Trading made me the<br><span style="color:#38bdf8;">freedom</span> to focus on matters.
        </h1>
        <p style="color:#94a3b8; font-size: 1.3rem; margin-top: 30px; max-width: 700px; margin-left: auto; margin-right: auto;">
            The ultimate institutional-grade AI terminal for real-time analytics and predictive forecasting.
        </p>
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
        st.markdown("<h1 style='font-weight:800;'>Market Overview</h1>", unsafe_allow_html=True)
    with col_h2:
        if st.button("🏠 Home"):
            st.session_state.view = 'landing'
            st.rerun()

    st.markdown("<hr style='border: 0.5px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

    # 4-column Grid
    rows = [stocks_list[i:i + 4] for i in range(0, len(stocks_list), 4)]
    
    for row in rows:
        cols = st.columns(4)
        for idx, s in enumerate(row):
            df = get_market_data(s)
            if df is not None and not df.empty:
                curr = round(df['Close'].iloc[-1], 2)
                prev = round(df['Close'].iloc[-2], 2)
                chg = round(((curr - prev) / prev) * 100, 2)
                color = "#22c55e" if chg >= 0 else "#ef4444" # Emerald Green / Rose Red
                
                with cols[idx]:
                    st.markdown(f"""
                    <div class="stock-card">
                        <div class="symbol-txt">{s.replace('.NS','')}</div>
                        <div class="price-txt">₹{curr}</div>
                        <div class="change-txt" style="color: {color};">
                            {'▲' if chg >= 0 else '▼'} {abs(chg)}%
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Analyze {s.split('.')[0]}", key=f"btn_{s}"):
                        st.session_state.selected_stock = s
                        st.session_state.view = 'detail'
                        st.rerun()
