import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="MarketMind AI - Pro", layout="wide")
st_autorefresh(interval=60 * 1000, key="datarefresh")

# --- 1. SESSION STATE FOR NAVIGATION ---
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = None

# --- 2. PREDICTION & RSI LOGIC ---
def get_detailed_analysis(df):
    if len(df) < 14: return "N/A", "#888", 50
    # RSI Calculation
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean().iloc[-1]
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().iloc[-1]
    rs = gain / (loss if loss != 0 else 0.1)
    rsi = round(100 - (100 / (1 + rs)), 2)
    
    # Trend Logic
    curr = df['Close'].iloc[-1]
    sma_20 = df['Close'].rolling(window=20).mean().iloc[-1]
    
    if rsi < 30: pred, col = "STRONG BUY 💎", "#00ff88"
    elif rsi > 70: pred, col = "OVERBOUGHT ⚠️", "#ff4b4b"
    elif curr > sma_20: pred, col = "BULLISH 🚀", "#00ff88"
    else: pred, col = "BEARISH 📉", "#ff4b4b"
    
    return pred, col, rsi

# --- 3. STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .main-card {
        background: #1e2130; padding: 15px; border-radius: 12px;
        border-top: 4px solid #444; text-align: center; margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. DATA FETCHING ---
stocks_list = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "TATAMOTORS.NS", "ZOMATO.NS", "BTC-USD"]

@st.cache_data(ttl=600)
def fetch_all():
    data = {}
    for s in stocks_list:
        try:
            t = yf.Ticker(s)
            df = t.history(period="1mo")
            if not df.empty: data[s] = df
        except: continue
    return data

all_data = fetch_all()

# --- 5. PAGE LOGIC ---

# BACK BUTTON
if st.session_state.selected_stock:
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.selected_stock = None
        st.rerun()

# --- DETAIL PAGE ---
if st.session_state.selected_stock:
    s = st.session_state.selected_stock
    df = all_data[s]
    pred, col, rsi = get_detailed_analysis(df)
    
    st.title(f"🔍 Deep Dive: {s.replace('.NS','')}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Current Price", f"₹{round(df['Close'].iloc[-1], 2)}")
    col2.metric("RSI (14)", rsi)
    col3.markdown(f"### Prediction: <span style='color:{col}'>{pred}</span>", unsafe_allow_html=True)
    
    # Big Interactive Chart
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Market Data"))
    fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Recent History")
    st.dataframe(df.tail(10), use_container_width=True)

# --- HOME DASHBOARD ---
else:
    st.title("📊 MarketMind AI Terminal")
    cols = st.columns(4)
    
    for i, s in enumerate(stocks_list):
        if s in all_data:
            df = all_data[s]
            curr = round(df['Close'].iloc[-1], 2)
            prev = round(df['Close'].iloc[-2], 2)
            chg = round(((curr - prev) / prev) * 100, 2)
            color = "#00ff88" if chg >= 0 else "#ff4b4b"
            
            with cols[i % 4]:
                st.markdown(f"""<div class="main-card" style="border-top-color:{color}">
                    <h3 style="margin:0;">{s.replace('.NS','')}</h3>
                    <h2 style="color:{color}; margin:5px 0;">{curr}</h2>
                    <p style="color:{color};">{chg}%</p>
                </div>""", unsafe_allow_html=True)
                
                # Yeh button click karne par naya page open hoga
                if st.button(f"Analyze {s.replace('.NS','')}", key=s):
                    st.session_state.selected_stock = s
                    st.rerun()
