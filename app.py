import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="MarketMind AI - Classic", layout="wide")

# Custom CSS for Clean Cards
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .compact-card {
        background: #1e2130;
        padding: 15px;
        border-radius: 12px;
        border-top: 4px solid #444;
        margin-bottom: 5px;
    }
    .stock-symbol { font-size: 1.1rem; font-weight: bold; color: #aaa; }
    .price-text { font-size: 1.4rem; font-weight: bold; margin: 5px 0; }
    .pnl-text { font-size: 0.85rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("💰 Portfolio Settings")
stocks_list = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "TATAMOTORS.NS", "ZOMATO.NS", "BTC-USD", "ETH-USD"]
my_stock = st.sidebar.selectbox("Track My Stock", stocks_list)
buy_price = st.sidebar.number_input("Buying Price", value=0.0)

st.title("📈 MarketMind AI: Classic Dashboard")
st.caption(f"Live 7-Day Trend Charts | {datetime.now().strftime('%H:%M:%S')} IST")

# Grid Logic
for i in range(0, len(stocks_list), 4):
    cols = st.columns(4)
    for j in range(4):
        if i + j < len(stocks_list):
            s = stocks_list[i + j]
            try:
                t = yf.Ticker(s)
                df = t.history(period="7d") # 7 days for the graph
                if df.empty: continue
                
                curr = round(df['Close'].iloc[-1], 2)
                prev = round(df['Close'].iloc[-2], 2)
                p_change = round(((curr - prev) / prev) * 100, 2)
                
                # Simple RSI for Signal
                delta = df['Close'].diff()
                gain = delta.where(delta > 0, 0).rolling(5).mean().iloc[-1]
                loss = -delta.where(delta < 0, 0).rolling(5).mean().iloc[-1]
                rsi = round(100 - (100 / (1 + (gain/(loss if loss != 0 else 0.1)))), 2)
                
                color = "#00ff88" if p_change >= 0 else "#ff4b4b"
                
                with cols[j]:
                    # Info Card
                    pnl_str = ""
                    if s == my_stock and buy_price > 0:
