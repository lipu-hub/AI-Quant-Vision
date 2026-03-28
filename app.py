import streamlit as st
import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime

st.set_page_config(page_title="MarketMind AI - Pro", layout="wide")

# CSS - No changes needed here, it's already good
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .compact-card {
        background: #1e2130;
        padding: 15px;
        border-radius: 12px;
        border-left: 5px solid #444;
        min-height: 200px;
        margin-bottom: 20px;
    }
    .stock-symbol { font-size: 1.1rem; font-weight: bold; color: #aaa; margin-bottom: 5px; }
    .price-text { font-size: 1.4rem; font-weight: bold; margin: 5px 0; }
    .rsi-tag { font-size: 0.75rem; background: #2d3248; padding: 3px 8px; border-radius: 5px; color: #bbb; }
    .pnl-text { font-size: 0.9rem; font-weight: bold; margin-top: 10px; }
    .signal-box { margin-top: 10px; font-weight: bold; font-size: 1rem; }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("💰 My Portfolio")
stocks_list = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "TATAMOTORS.NS", "ZOMATO.NS", "BTC-USD", "ETH-USD"]
my_stock = st.sidebar.selectbox("Select Stock", stocks_list)
buy_price = st.sidebar.number_input("Your Buying Price", value=0.0, step=0.1)

st.title("🚀 MarketMind AI: Pro Analyst")
st.caption(f"Live Market Pulse | {datetime.now().strftime('%H:%M:%S')} IST")

# Logic to handle 4 columns
for i in range(0, len(stocks_list), 4):
    cols = st.columns(4)
    for j in range(4):
        if i + j < len(stocks_list):
            s = stocks_list[i + j]
            try:
                t = yf.Ticker(s)
                df = t.history(period="1mo")
                if df.empty: continue
                
                curr = round(df['Close'].iloc[-1], 2)
                prev = round(df['Close'].iloc[-2], 2)
                p_change = round(((curr - prev) / prev) * 100, 2)
                
                # Simple RSI Calculation
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean().iloc[-1]
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean().iloc[-1]
                rs = gain / (loss if loss != 0 else 0.001)
                rsi = round(100 - (100 / (1 + rs)), 2)

                # Signal Logic
                signal, s_color = "⌛ HOLD", "#888"
                if rsi < 35: signal, s_color = "🔥 BUY", "#00ff88"
                elif rsi > 65: signal, s_color = "⚠️ SELL", "#ff4b4b"

                # P&L Calculation
                pnl_html = ""
                if s == my_stock and buy_price > 0:
                    diff = round(curr - buy_price, 2)
                    p_pct = round((diff / buy_price) * 100, 2)
                    p_color = "#00ff88" if diff >= 0 else "#ff4b4b"
                    pnl_html = f'<div class="pnl-text" style="color:{p_color};">P&L: {diff} ({p_pct}%)</div>'

                # The "Magic" Render: Pure HTML string with no complex logic inside
                change_color = "#00ff88" if p_change > 0 else "#ff4b4b"
                
                with cols[j]:
                    st.markdown(f"""
                    <div class="compact-card" style="border-left-color: {s_color};">
                        <div class="stock-symbol">{s.replace('.NS','')}</div>
                        <div class="price-text">{curr} <span style="font-size:0.8rem; color:{change_color};">({p_change}%)</span></div>
                        <span class="rsi-tag">RSI: {rsi}</span>
                        {pnl_html}
                        <div class="signal-box" style="color:{s_color};">{signal}</div>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                continue
