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
    st.session_state.view = 'landing' # Default start page
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = None

# 2. CUSTOM CSS (Professional Fintech Style)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    
    .stApp { background-color: #0b0e14; font-family: 'Inter', sans-serif; color: white; }

    /* Landing Page Styles */
    .hero-section {
        text-align: center;
        padding: 80px 20px;
        background: linear-gradient(180deg, #11141d 0%, #0b0e14 100%);
        border-radius: 20px;
    }
    .hero-title { font-size: 4rem; font-weight: 700; margin-bottom: 10px; letter-spacing: -2px; }
    .hero-subtitle { color: #8890a6; font-size: 1.2rem; margin-bottom: 30px; }
    
    .start-btn {
        background-color: #00ffcc;
        color: #0b0e14 !important;
        padding: 15px 40px;
        border-radius: 30px;
        font-weight: bold;
        text-decoration: none;
        font-size: 1.1rem;
        transition: 0.3s;
    }
    
    .feature-card {
        background: #161a25;
        padding: 30px;
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.05);
        text-align: center;
    }

    /* Dashboard Button Styles */
    div.stButton > button {
        background: #161a25;
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.1);
        color: white;
        height: 120px;
        transition: 0.3s;
    }
    div.stButton > button:hover { border-color: #00ffcc; transform: translateY(-3px); }
</style>
""", unsafe_allow_html=True)

# 3. Data Logic
stocks_list = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "TATAMOTORS.NS", "ZOMATO.NS", "BTC-USD"]

@st.cache_data(ttl=600)
def get_data(s):
    try: return yf.Ticker(s).history(period="1mo")
    except: return None

# --- UI LOGIC ---

# 🏠 PAGE 1: PROFESSIONAL LANDING PAGE
if st.session_state.view == 'landing':
    # Top Navbar (Simple)
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0;">
        <h2 style="margin:0;">MarketMind <span style="color:#00ffcc;">AI</span></h2>
        <div style="color:#8890a6;">Trusted by 500k+ Traders</div>
    </div>
    <hr style="opacity: 0.1; margin-bottom: 40px;">
    """, unsafe_allow_html=True)

    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <div style="background: rgba(0, 255, 204, 0.1); color: #00ffcc; display: inline-block; padding: 5px 15px; border-radius: 20px; font-size: 0.8rem; margin-bottom: 20px;">
            v3.0 GENERATIVE AI TERMINAL
        </div>
        <h1 class="hero-title">Trading made me the<br><span style="color:#00ffcc;">freedom</span> to focus on matters.</h1>
        <p class="hero-subtitle">A trusted service provider for over 25 years. Experience high-fidelity AI market predictions,<br>real-time dashboards, and secure technical analysis.</p>
    </div>
    """, unsafe_allow_html=True)

    # Get Started Button
    col1, col2, col3 = st.columns([2,1,2])
    with col2:
        if st.button("🚀 ENTER TERMINAL", use_container_width=True):
            st.session_state.view = 'grid'
            st.rerun()

    # Features Row
    st.markdown("<br><br>", unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1: st.markdown('<div class="feature-card"><h3>25 Years Trust</h3><p style="color:#8890a6;">Serving global markets with precision and security.</p></div>', unsafe_allow_html=True)
    with f2: st.markdown('<div class="feature-card"><h3>AI Predictions</h3><p style="color:#8890a6;">Advanced neural networks for accurate price forecasting.</p></div>', unsafe_allow_html=True)
    with f3: st.markdown('<div class="feature-card"><h3>Secure Trading</h3><p style="color:#8890a6;">Cybersecurity and data privacy are our top priorities.</p></div>', unsafe_allow_html=True)

# 📊 PAGE 2: THE GRID DASHBOARD
elif st.session_state.view == 'grid':
    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <h1>Dashboard Overview</h1>
        <p style="color:#8890a6;">Market Pulse: LIVE</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("⬅️ Back to Home"):
        st.session_state.view = 'landing'
        st.rerun()

    cols = st.columns(4)
    for i, s in enumerate(stocks_list):
        df = get_data(s)
        if df is None or df.empty: continue
        
        curr = round(df['Close'].iloc[-1], 2)
        prev = round(df['Close'].iloc[-2], 2)
        chg = round(((curr - prev) / prev) * 100, 2)
        color = "#00ffcc" if chg >= 0 else "#ff4b4b"
        
        with cols[i % 4]:
            btn_label = f"{s.replace('.NS','')}\n\n₹{curr}\n({chg}%)"
            if st.button(btn_html := f"{s.replace('.NS','')}\n{curr}", key=s):
                st.session_state.selected_stock = s
                st.session_state.view = 'detail'
                st.rerun()
            st.markdown(f"<p style='color:{color}; text-align:center; font-weight:bold; margin-top:-20px;'>{chg}%</p>", unsafe_allow_html=True)

# 🔍 PAGE 3: DETAIL VIEW
elif st.session_state.view == 'detail':
    s = st.session_state.selected_stock
    df = get_data(s)
    
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.view = 'grid'
        st.rerun()
        
    st.title(f"Analysis: {s}")
    # (Detail view code remains same as before)
    st.metric("Price", f"₹{round(df['Close'].iloc[-1], 2)}")
