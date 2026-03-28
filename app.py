import streamlit as st
import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime

st.set_page_config(page_title="MarketMind AI - Pro", layout="wide")

# CSS for Uniform Grid & Portfolio Styling
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .compact-card {
        background: #1e2130;
        padding: 15px;
        border-radius: 12px;
        border-left: 5px solid #444;
        height: 190px;
        margin-bottom: 20px;
        transition: 0.3s;
    }
    .compact-card:hover { transform: translateY(-5px); box-shadow: 0px 4px 15px rgba(0,0,0,0.3); }
    .stock-symbol { font-size: 1.1rem; font-weight: bold; color: #aaa; margin:0; }
    .price-text { font-size: 1.4rem; font-weight: bold; margin: 5px 0; }
    .rsi-tag { font-size: 0.75rem; background: #2d3248; padding: 3px 8px; border-radius: 5px; color: #bbb; }
    .pnl-text { font-size: 0.9rem; font-weight: bold; margin-top: 8px; }
</style>
""", unsafe_allow_html=True)

# Sidebar: Portfolio Input
st.sidebar.title("💰 My Portfolio")
my_stock = st.sidebar.selectbox("Select Stock", ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS"])
buy_price = st.sidebar.number_input("Your Buying Price", value=0.0)

# Main App
st.title("🚀 MarketMind AI: Pro Analyst")
st.caption(f"Live Market Pulse | {datetime.now().strftime('%H:%M:%S')} IST")

stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "TATAMOTORS.NS", "ZOMATO.NS", "BTC-USD", "ETH-USD"]
rows = [stocks[i:i + 4] for i in range(0, len(stocks), 4)]

for row in rows:
    cols = st.columns(4)
    for i, s in enumerate(row):
        try:
            t = yf.Ticker(s)
            df = t.history(period="1mo")
            if df.empty: continue
            
            curr = round(df['Close'].iloc[-1], 2)
            prev = round(df['Close'].iloc[-2], 2)
            p_change = round(((curr - prev) / prev) * 100, 2)
            
            # RSI Logic
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi = round(100 - (100 / (1 + (gain.iloc[-1]/loss.iloc[-1]))), 2)

            # Signal Logic
            signal, color = "⌛ HOLD", "#888"
            if rsi < 35: signal, color = "🔥 BUY", "#00ff88"
            elif rsi > 65: signal, color = "⚠️ SELL", "#ff4b4b"

            # Portfolio Profit/Loss Calculation
            pnl_html = ""
            if s == my_stock and buy_price > 0:
                diff = round(curr - buy_price, 2)
                pnl_color = "#00ff88" if diff >= 0 else "#ff4b4b"
                pnl_html = f"<p class='pnl-text' style='color:{pnl_color};'>P&L: {diff} ({round((diff/buy_price)*100,2)}%)</p>"

            with cols[i]:
                st.markdown(f"""
                <div class="compact-card" style="border-left-color: {color};">
                    <div>
                        <p class="stock-symbol">{s.replace('.NS','')}</p>
                        <p class="price-text">{curr} <span style="font-size:0.8rem; color:{'#00ff88' if p_change>0 else '#ff4b4b'};">({p_change}%)</span></p>
                        <span class="rsi-tag">RSI: {rsi}</span>
                    </div>
                    <div>
                        {pnl_html}
                        <p style="margin-top:10px; font-weight:bold; color:{color};">{signal}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        except:
            continue
