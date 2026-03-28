import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import requests

# 1. PAGE CONFIG
st.set_page_config(page_title="MarketMind AI - Pro Terminal", layout="wide")

# 2. SESSION STATE (Navigation & Safety)
if 'view' not in st.session_state:
    st.session_state.view = 'grid'
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = None

# 3. ADVANCED PREDICTION LOGIC (No-Error Version)
def calculate_prediction(df):
    try:
        if len(df) < 20:
            return {"status": "Not Enough Data", "color": "#888", "rsi": 50, "target": 0, "stoploss": 0}
        
        # RSI Calculation
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean().iloc[-1]
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().iloc[-1]
        rs = gain / (loss if loss != 0 else 0.1)
        rsi = 100 - (100 / (1 + rs))
        
        curr_price = df['Close'].iloc[-1]
        avg_volatility = (df['High'] - df['Low']).tail(10).mean()
        
        # Verdict Logic
        if rsi < 35:
            res = {"status": "STRONG BUY 💎", "color": "#00ff88", "conf": "85%"}
        elif rsi > 65:
            res = {"status": "STRONG SELL 📉", "color": "#ff4b4b", "conf": "80%"}
        elif curr_price > df['Close'].rolling(20).mean().iloc[-1]:
            res = {"status": "BULLISH 🚀", "color": "#00ff88", "conf": "65%"}
        else:
            res = {"status": "BEARISH ⚠️", "color": "#ff4b4b", "conf": "60%"}
            
        res.update({
            "rsi": round(rsi, 2),
            "target": round(curr_price + (avg_volatility * 1.5), 2),
            "stoploss": round(curr_price - (avg_volatility * 1.2), 2)
        })
        return res
    except Exception:
        return None

# 4. STOCKS LIST
stocks_list = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "TATAMOTORS.NS", "ZOMATO.NS", "BTC-USD", "ETH-USD"]

# 🏠 PAGE: GRID DASHBOARD
if st.session_state.view == 'grid':
    st.title("📈 MarketMind AI Terminal")
    cols = st.columns(4)
    for i, s in enumerate(stocks_list):
        with cols[i % 4]:
            try:
                data = yf.Ticker(s).history(period="7d")
                if not data.empty:
                    curr = round(data['Close'].iloc[-1], 2)
                    chg = round(((curr - data['Close'].iloc[-2])/data['Close'].iloc[-2])*100, 2)
                    color = "#00ff88" if chg >= 0 else "#ff4b4b"
                    
                    st.markdown(f"""
                    <div style="background:#1e2130; padding:15px; border-radius:10px; border-top:3px solid {color}; text-align:center;">
                        <small style="color:#aaa;">{s}</small>
                        <h2 style="margin:5px 0;">₹{curr}</h2>
                        <span style="color:{color}; font-weight:bold;">{chg}%</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Predict {s.split('.')[0]}", key=s):
                        st.session_state.selected_stock = s
                        st.session_state.view = 'predict'
                        st.rerun()
            except: continue

# 🔮 PAGE: AI PREDICTION (Detailed)
elif st.session_state.view == 'predict':
    s = st.session_state.selected_stock
    st.button("⬅️ Back", on_click=lambda: st.session_state.update({"view": 'grid'}))
    
    with st.spinner(f"AI Analyzing {s}..."):
        df = yf.Ticker(s).history(period="1mo")
        pred = calculate_prediction(df)
        
    if pred:
        st.header(f"AI Forecast: {s}")
        
        # Row 1: Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Verdict", pred['status'])
        m2.metric("Confidence", pred.get('conf', 'N/A'))
        m3.metric("Target Price", f"₹{pred['target']}")
        m4.metric("Stop-Loss", f"₹{pred['stoploss']}")

        # Row 2: Charts
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.update_layout(template="plotly_dark", title="Technical Candlestick Chart", xaxis_rangeslider_visible=False, height=450)
            st.plotly_chart(fig, use_container_width=True)
            
        with col_right:
            st.subheader("Indicator Insights")
            st.write(f"**RSI (Strength):** {pred['rsi']}")
            if pred['rsi'] < 30: st.info("Oversold: Potential Bounce Back Expected.")
            elif pred['rsi'] > 70: st.warning("Overbought: Price might cool down soon.")
            
            # Simple Prediction Trend Graph
            pred_df = pd.DataFrame({'Day': ['Today', 'Tomorrow (Target)'], 'Price': [df['Close'].iloc[-1], pred['target']]})
            fig_p = go.Figure(go.Scatter(x=pred_df['Day'], y=pred_df['Price'], mode='lines+markers+text', text=pred_df['Price'], textposition="top center", line=dict(color=pred['color'], dash='dash')))
            fig_p.update_layout(height=250, template="plotly_dark", margin=dict(l=0,r=0,t=30,b=0))
            st.plotly_chart(fig_p, use_container_width=True)
    else:
        st.error("Error fetching detailed prediction. Please try again.")
