import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# 1. SETUP & NAVIGATION
st.set_page_config(page_title="MarketMind AI - Terminal", layout="wide")

if 'view' not in st.session_state: 
    st.session_state.view = 'grid'
if 'selected_stock' not in st.session_state: 
    st.session_state.selected_stock = None

# 2. ENHANCED PREDICTION LOGIC
def get_ai_forecast(symbol):
    try:
        data = yf.Ticker(symbol).history(period="60d")
        if len(data) < 20: 
            return None
        
        curr = data['Close'].iloc[-1]
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean().iloc[-1]
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().iloc[-1]
        rs = gain / (loss if loss != 0 else 0.1)
        rsi = 100 - (100 / (1 + rs))
        
        vol = (data['High'] - data['Low']).tail(10).mean()
        
        return {
            "price": round(curr, 2),
            "rsi": round(rsi, 2),
            "target": round(curr + (vol * 1.5), 2),
            "stoploss": round(curr - (vol * 1.2), 2),
            "signal": "STRONG BUY 🚀" if rsi < 35 else "SELL 📉" if rsi > 65 else "NEUTRAL ⚖️",
            "confidence": "88%" if rsi < 30 or rsi > 70 else "72%"
        }
    except: 
        return None

# 3. UI STYLE
st.markdown("""<style>
    .stApp { background-color: #0e1117; color: white; }
    .card { background: #1e2130; padding: 20px; border-radius: 10px; border-top: 3px solid #444; text-align: center; }
</style>""", unsafe_allow_html=True)

# --- NAVIGATION ---

if st.session_state.view == 'grid':
    st.title("📊 MarketMind AI Terminal")
    stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "TATAMOTORS.NS", "ZOMATO.NS", "BTC-USD"]
    
    cols = st.columns(4)
    for i, s in enumerate(stocks):
        with cols[i % 4]:
            try:
                d = yf.Ticker(s).history(period="2d")
                price = round(d['Close'].iloc[-1], 2)
                chg = round(((price - d['Close'].iloc[-2])/d['Close'].iloc[-2])*100, 2)
                color = "#00ff88" if chg >= 0 else "#ff4b4b"
                
                st.markdown(f'<div class="card" style="border-top-color:{color};"><p style="color:#888;">{s}</p><h2>{price}</h2><p style="color:{color};">{chg}%</p></div>', unsafe_allow_html=True)
                if st.button(f"Analyze {s.split('.')[0]}", key=f"btn_{s}"):
                    st.session_state.selected_stock = s
                    st.session_state.view = 'predict'
                    st.rerun()
            except: 
                continue

elif st.session_state.view == 'predict':
    s = st.session_state.selected_stock
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.view = 'grid'
        st.rerun()
    
    forecast = get_ai_forecast(s)
    if forecast:
        st.header(f"🔮 AI Analysis: {s}")
        
        # Dashboard Metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("AI Signal", forecast['signal'])
        c2.metric("Confidence", forecast['confidence'])
        c3.metric("Target", f"₹{forecast['target']}")
        c4.metric("Stop-Loss", f"₹{forecast['stoploss']}")
        
        # Charts
        col_l, col_r = st.columns([2, 1])
        with col_l:
            df_chart = yf.Ticker(s).history(period="1mo")
            fig = go.Figure(data=[go.Candlestick(x=df_chart.index, open=df_chart['Open'], high=df_chart['High'], low=df_chart['Low'], close=df_chart['Close'])])
            fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col_r:
            st.subheader("📰 Latest Insights")
            st.write(f"**RSI Strength:** {forecast['rsi']}")
            # Adding simple prediction line
            pred_fig = go.Figure(go.Scatter(x=['Current', 'Target'], y=[forecast['price'], forecast['target']], mode='lines+markers', line=dict(color='#00ff88', dash='dash')))
            pred_fig.update_layout(height=200, template="plotly_dark", margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(pred_fig, use_container_width=True)
    else:
        st.error("Technical error while fetching prediction data.")
