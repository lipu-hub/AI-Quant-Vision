import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
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

# 2. PREMIUM CSS (Midnight Blue & Glassmorphism)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    .stApp { 
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); 
        font-family: 'Inter', sans-serif; 
        color: #f1f5f9; 
    }

    /* Glassmorphic Card Styling */
    .stock-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        transition: all 0.4s ease;
        margin-bottom: 20px;
    }
    .stock-card:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: #38bdf8;
        transform: translateY(-8px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.4);
    }

    /* AI Stats Container */
    .ai-box {
        background: rgba(15, 23, 42, 0.6);
        padding: 25px;
        border-radius: 18px;
        border-left: 5px solid #38bdf8;
        margin-top: 15px;
    }

    /* Professional Selection Button */
    div.stButton > button {
        background: rgba(56, 189, 248, 0.1) !important;
        border: 1px solid #38bdf8 !important;
        color: #38bdf8 !important;
        border-radius: 12px;
        font-weight: 600;
        width: 100%;
        margin-top: 10px;
    }
    div.stButton > button:hover {
        background: #38bdf8 !important;
        color: #0f172a !important;
    }

    .symbol-txt { color: #94a3b8; font-size: 0.85rem; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; }
    .price-txt { font-size: 2rem; font-weight: 800; color: #ffffff; margin: 8px 0; }
</style>
""", unsafe_allow_html=True)

# 3. Data Logic (Optimized)
stocks_list = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "TATAMOTORS.NS", "ZOMATO.NS", "BTC-USD"]

@st.cache_data(ttl=600)
def get_market_data(s, period="1mo"):
    try:
        return yf.Ticker(s).history(period=period)
    except:
        return None

# --- UI LOGIC ---

# 🏠 PAGE 1: LANDING PAGE
if st.session_state.view == 'landing':
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 20px 0;">
        <h2 style="margin:0; font-weight:800;">MarketMind <span style="color:#38bdf8;">AI</span></h2>
        <div style="background: rgba(56, 189, 248, 0.1); color: #38bdf8; padding: 5px 15px; border-radius: 20px; font-size: 0.8rem; font-weight: bold;">v3.0 GENERATIVE ENGINE</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; padding: 100px 20px;">
        <h1 style="font-size: 4.5rem; font-weight: 900; letter-spacing: -3px; line-height: 1; color: #f8fafc;">
            Trading made me the<br><span style="color:#38bdf8;">freedom</span> to focus on matters.
        </h1>
        <p style="color:#94a3b8; font-size: 1.3rem; margin-top: 30px; max-width: 800px; margin-left: auto; margin-right: auto;">
            Our AI-driven terminal processes millions of data points to give you real-time forecasts, probability scores, and institutional-grade analytics.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([2, 1, 2])
    with c2:
        if st.button("🚀 ENTER TERMINAL", use_container_width=True):
            st.session_state.view = 'grid'
            st.rerun()

# 📊 PAGE 2: DASHBOARD (GRID VIEW)
elif st.session_state.view == 'grid':
    col_h1, col_h
