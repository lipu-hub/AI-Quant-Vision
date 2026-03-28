import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# 1. PAGE SETUP
st.set_page_config(page_title="MarketMind AI - Terminal", layout="wide")

# 2. SESSION STATE (Navigation)
if 'view' not in st.session_state:
    st.session_state.view = 'grid'
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = None

# 3. CSS (Screenshot wala same dark theme)
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .stock-card {
        background: #1e2130; 
        padding: 20px; 
        border-radius: 10px; 
        text-align: center;
        border-top: 4px solid #444;
    }
</style>
""", unsafe_allow_html=True)

# 4. PREDICTION LOGIC (Safe Version)
def get_prediction_data(df):
    if len(df) < 15: return None
    curr = df['Close'].iloc[-1]
    # Simple Technical Analysis
    rsi = 50 # Default
    try:
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean().iloc[-1]
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().iloc[-1]
        rsi = 100 - (100 / (1 + (gain/loss)))
    except: pass
    
    avg_move = (df['High'] - df['Low']).mean()
    return {
        "verdict": "BULLISH 🚀" if rsi < 40 else "BEARISH 📉" if rsi > 60 else "NEUTRAL ⚖️",
        "target": round(curr + avg_move, 2),
        "stoploss": round(curr - avg_move, 2),
        "rsi": round(rsi, 2),
        "conf": "82%" if rsi < 40 or rsi > 60 else "65%"
    }

# 5. STOCKS LIST
stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "BTC-USD", "ETH-USD"]

# --- APP NAVIGATION ---

if st.session_state.view == 'grid':
    st.title("📈 MarketMind AI Terminal")
    
    # Grid Layout (4 Columns)
    cols = st.columns(4)
    for i, s in enumerate(stocks):
        with cols[i % 4]:
            try:
                # 7 din ka data dashboard ke liye
                d = yf.Ticker(s).history(period="7d")
                if not d.empty:
                    price = round(d['Close'].iloc[-1], 2)
                    chg = round(((price - d['Close'].iloc[-2])/d['Close'].iloc[-2])*100, 2)
                    color = "#00ff88" if chg >= 0 else "#ff4b4b"
                    
                    st.markdown(f"""
                    <div class="stock-card" style="border-top-color: {color};">
                        <p style="color:#aaa; font-size:12px; margin-bottom:10px;">{s}</p>
                        <h2 style="margin:0;">₹{price}</h2>
                        <p style="color:{color}; font-weight:bold; margin-top:10px;">{chg}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Same button style as your screenshot
                    if st.button(f"Predict {s.split('.')[0]}", key=s):
                        st.session_state.selected_stock = s
                        st.session_state.view = 'predict'
                        st.rerun()
            except: continue

elif st.session_state.view == 'predict':
    # Detail Page
    s = st.session_state.selected_stock
    df = yf.Ticker(s).history(period="3mo") # Prediction ke liye zyada data
    analysis = get_prediction_data(df)
    
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.view = 'grid'
        st.rerun()
        
    st.title(f"AI Forecast: {s}")
    
    if analysis:
        # Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Verdict", analysis['verdict'])
        m2.metric("Confidence", analysis['conf'])
        m3.metric("Target Price", f"₹{analysis['target']}")
        m4.metric("Stop-Loss", f"₹{analysis['stoploss']}")
        
        col_l, col_r = st.columns([2, 1])
        with col_l:
            # Candlestick Chart
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
        with col_r:
            st.subheader("Indicator Insights")
            st.write(f"**RSI (Strength):** {analysis['rsi']}")
            # Prediction line graph
            p_fig = go.Figure(go.Scatter(x=['Today', 'Target'], y=[df['Close'].iloc[-1], analysis['target']], mode='lines+markers+text', text=["", analysis['target']], textposition="top center"))
            p_fig.update_layout(height=250, template="plotly_dark")
            st.plotly_chart(p_fig, use_container_width=True)
    else:
        st.error("Not enough historical data for AI prediction.")
