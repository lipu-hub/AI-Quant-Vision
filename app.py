import streamlit as st
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="MarketMind AI - Pro", layout="wide")

# 1. Clean CSS for the UI
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .compact-card {
        background: #1e2130;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #444;
        min-height: 220px;
        margin-bottom: 25px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .stock-symbol { font-size: 1.2rem; font-weight: bold; color: #ffffff; margin-bottom: 8px; }
    .price-text { font-size: 1.6rem; font-weight: bold; margin: 5px 0; color: #ffffff; }
    .rsi-tag { font-size: 0.85rem; background: #2d3248; padding: 4px 10px; border-radius: 6px; color: #bbb; display: inline-block; }
    .pnl-text { font-size: 1rem; font-weight: bold; margin-top: 12px; padding: 5px 0; }
    .signal-box { margin-top: 15px; font-weight: 800; font-size: 1.1rem; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# 2. Sidebar for Portfolio
st.sidebar.title("💰 My Portfolio")
stocks_list = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "TATAMOTORS.NS", "ZOMATO.NS", "BTC-USD", "ETH-USD"]
my_stock = st.sidebar.selectbox("Select Stock", stocks_list)
buy_price = st.sidebar.number_input("Your Buying Price", value=0.0, step=1.0)

st.title("🚀 MarketMind AI: Pro Analyst")
st.caption(f"Live Market Pulse | {datetime.now().strftime('%d %b, %Y | %H:%M:%S')} IST")

# 3. Grid Logic (4 Columns)
for i in range(0, len(stocks_list), 4):
    cols = st.columns(4)
    for j in range(4):
        if i + j < len(stocks_list):
            ticker_symbol = stocks_list[i + j]
            try:
                t = yf.Ticker(ticker_symbol)
                df = t.history(period="1mo")
                if df.empty: continue
                
                # Market Data
                curr = round(df['Close'].iloc[-1], 2)
                prev = round(df['Close'].iloc[-2], 2)
                p_change = round(((curr - prev) / prev) * 100, 2)
                change_color = "#00ff88" if p_change >= 0 else "#ff4b4b"
                
                # RSI Calculation
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean().iloc[-1]
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean().iloc[-1]
                rsi = round(100 - (100 / (1 + (gain / (loss if loss != 0 else 0.001)))), 2)

                # Signal Logic
                if rsi < 35: signal, s_color = "🔥 BUY", "#00ff88"
                elif rsi > 65: signal, s_color = "⚠️ SELL", "#ff4b4b"
                else: signal, s_color = "⌛ HOLD", "#888"

                # P&L Logic (Only for selected stock)
                pnl_content = ""
                if ticker_symbol == my_stock and buy_price > 0:
                    diff = round(curr - buy_price, 2)
                    p_pct = round((diff / buy_price) * 100, 2)
                    p_color = "#00ff88" if diff >= 0 else "#ff4b4b"
                    pnl_content = f'<div class="pnl-text" style="color:{p_color}; border-top: 1px solid #333;">P&L: {diff} ({p_pct}%)</div>'

                # FINAL RENDERING
                with cols[j]:
                    st.markdown(f"""
                    <div class="compact-card" style="border-left-color: {s_color};">
                        <div>
                            <div class="stock-symbol">{ticker_symbol.replace('.NS','')}</div>
                            <div class="price-text">{curr} <span style="font-size:0.9rem; color:{change_color};">({p_change}%)</span></div>
                            <div class="rsi-tag">RSI: {rsi}</div>
                        </div>
                        <div>
                            {pnl_content}
                            <div class="signal-box" style="color:{s_color};">{signal}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            except:
                continue
