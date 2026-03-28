import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. Setup
st.set_page_config(page_title="MarketMind AI - Pro", layout="wide")
st_autorefresh(interval=60 * 1000, key="datarefresh")

# 2. State Management (Navigation)
if 'view' not in st.session_state:
    st.session_state.view = 'grid'
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = None

# 3. CSS for Premium Look
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        background-color: #1e2130;
        color: white;
        border: 1px solid #333;
        padding: 10px;
        height: 150px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        border-color: #00ff88;
        background-color: #25293d;
    }
</style>
""", unsafe_allow_html=True)

# 4. Data Logic
stocks_list = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", 
    "BHARTIARTL.NS", "SBIN.NS", "LICI.NS", "ITC.NS", "HINDUNILVR.NS",
    "LT.NS", "BAJFINANCE.NS", "TATAMOTORS.NS", "M&M.NS", "ADANIENT.NS",
    "SUNPHARMA.NS", "ASIANPAINT.NS", "TITAN.NS", "ZOMATO.NS", "NTPC.NS",
    "KOTAKBANK.NS", "AXISBANK.NS", "BTC-USD", "ETH-USD"
]

@st.cache_data(ttl=600)
def get_stock_info(s):
    try:
        df = yf.Ticker(s).history(period="1mo")
        return df
    except: return None

# --- UI LOGIC ---

# 🏠 PAGE: THE GRID (Wahi 20+ Stocks)
if st.session_state.view == 'grid':
    st.title("📈 MarketMind AI Terminal")
    st.caption(f"Click any stock for Deep AI Prediction | {datetime.now().strftime('%H:%M:%S')}")
    
    for i in range(0, len(stocks_list), 5):
        cols = st.columns(5)
        for j in range(5):
            if i + j < len(stocks_list):
                s = stocks_list[i + j]
                df = get_stock_info(s)
                if df is None or df.empty: continue
                
                curr = round(df['Close'].iloc[-1], 2)
                prev = round(df['Close'].iloc[-2], 2)
                chg = round(((curr - prev) / prev) * 100, 2)
                color = "#00ff88" if chg >= 0 else "#ff4b4b"
                
                with cols[j]:
                    # Har card ek button hai
                    button_label = f"{s.replace('.NS','')}\n\n{curr}\n({chg}%)"
                    if st.button(button_label, key=s):
                        st.session_state.selected_stock = s
                        st.session_state.view = 'detail'
                        st.rerun()
                    
                    # Small Trend Line niche
                    fig = go.Figure(go.Scatter(x=df.index[-7:], y=df['Close'][-7:], mode='lines', line=dict(color=color, width=2)))
                    fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=30, xaxis=dict(visible=False), yaxis=dict(visible=False), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# 🔍 PAGE: DETAIL VIEW (Jab click karein)
elif st.session_state.view == 'detail':
    s = st.session_state.selected_stock
    df = get_stock_info(s)
    
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.view = 'grid'
        st.rerun()
        
    st.header(f"Deep Analysis: {s}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Candlestick Chart
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("AI Prediction")
        # Simple Logic for RSI/Trend
        curr = df['Close'].iloc[-1]
        sma = df['Close'].rolling(window=10).mean().iloc[-1]
        
        if curr > sma:
            st.success("TREND: BULLISH 🚀")
            st.write("Stock is performing above its 10-day average. Strong momentum detected.")
        else:
            st.error("TREND: BEARISH 📉")
            st.write("Stock is struggling below its average. Caution advised.")
            
        st.metric("Current Price", f"₹{round(curr,2)}")
        st.write("---")
        st.subheader("Recent Stats")
        st.table(df['Close'].tail(5))
