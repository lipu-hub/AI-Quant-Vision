import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# 1. PAGE SETUP
st.set_page_config(page_title="MarketMind AI - Terminal", layout="wide")

# 2. SESSION STATE (Page Control)
if 'view' not in st.session_state:
    st.session_state.view = 'grid'
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = None

# 3. CSS (Dark Theme & Cards)
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .stock-card {
        background: #1e2130; 
        padding: 20px; 
        border-radius: 12px; 
        text-align: center;
        border-top: 4px solid #444;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 4. PREDICTION LOGIC
def get_prediction_data(symbol):
    try:
        # Prediction ke liye 60 din ka data chahiye (RSI ke liye)
        df = yf.Ticker(symbol).history(period="60d")
        if len(df) < 20: return None
        
        curr = df['Close'].iloc[-1]
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean().iloc[-1]
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().iloc[-1]
        rs = gain / (loss if loss != 0 else 0.1)
        rsi = 100 - (100 / (1 + rs))
        
        volatility = (df['High'] - df['Low']).tail(10).mean()
        
        return {
            "price": round(curr, 2),
            "rsi": round(rsi, 2),
            "target": round(curr + (volatility * 1.5), 2),
            "stoploss": round(curr - (volatility * 1.2), 2),
            "signal": "STRONG BUY 🚀" if rsi < 35 else "STRONG SELL 📉" if rsi > 65 else "NEUTRAL ⚖️"
        }
    except:
        return None

# 5. STOCKS LIST
stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "TATAMOTORS.NS", "ZOMATO.NS", "BTC-USD"]

# --- NAVIGATION LOGIC ---

# 🏠 PAGE 1: GRID VIEW (Market Overview)
if st.session_state.view == 'grid':
    st.title("📊 MarketMind AI Terminal")
    
    cols = st.columns(4)
    for i, s in enumerate(stocks):
        with cols[i % 4]:
            try:
                # Dashboard ke liye sirf 7 din ka data
                d = yf.Ticker(s).history(period="7d")
                if not d.empty:
                    curr_p = round(d['Close'].iloc[-1], 2)
                    prev_p = round(d['Close'].iloc[-2], 2)
                    chg = round(((curr_p - prev_p) / prev_p) * 100, 2)
                    color = "#00ff88" if chg >= 0 else "#ff4b4b"
                    
                    st.markdown(f"""
                    <div class="stock-card" style="border-top-color: {color};">
                        <p style="color:#888; font-size:14px; margin-bottom:5px;">{s}</p>
                        <h2 style="margin:0;">₹{curr_p}</h2>
                        <p style="color:{color}; font-weight:bold;">{chg}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Predict {s.split('.')[0]}", key=f"btn_{s}"):
                        st.session_state.selected_stock = s
                        st.session_state.view = 'predict'
                        st.rerun()
            except:
                continue

# 🔮 PAGE 2: PREDICTION VIEW (Detailed Analysis)
elif st.session_state.view == 'predict':
    s = st.session_state.selected_stock
    
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.view =
