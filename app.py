import streamlit as st
import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime

st.set_page_config(page_title="MarketMind AI - Pro", layout="wide")

# Enhanced CSS for Uniform Grid & Animations
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .compact-card {
        background: #1e2130;
        padding: 15px;
        border-radius: 12px;
        border-left: 5px solid #444;
        height: 180px; /* Fixed height for uniformity */
        margin-bottom: 20px;
        transition: 0.3s;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .compact-card:hover { transform: translateY(-5px); background: #25293d; box-shadow: 0px 4px 15px rgba(0,0,0,0.3); }
    .stock-symbol { font-size: 1.1rem; font-weight: bold; color: #aaa; margin:0; }
    .price-text { font-size: 1.4rem; font-weight: bold; margin: 5px 0; }
    .rsi-text { font-size: 0.8rem; background: #2d3248; padding: 2px 8px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

analyzer = SentimentIntensityAnalyzer()

# Sidebar Control
st.sidebar.title("🔍 Search Market")
search_query = st.sidebar.text_input("Add NSE Stock (e.g. SBIN.NS)", "").upper()

# Extended Stock List
stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "TATAMOTORS.NS", "ZOMATO.NS", "BTC-USD", "ETH-USD"]
if search_query:
    if search_query not in stocks: stocks.insert(0, search_query)

st.title("🚀 MarketMind AI: Pro Analyst")
st.caption(f"Live Updates | {datetime.now().strftime('%d %b, %Y | %H:%M:%S')} IST")

# Create Grid (4 columns)
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
            rsi = round(100 - (100 / (1 + (gain/loss))).iloc[-1], 2)

            # Signal & Color
            color = "#888"
            signal = "⌛ HOLD"
            if rsi < 35: signal, color = "🔥 BUY", "#00ff88"
            elif rsi > 65: signal, color = "⚠️ SELL", "#ff4b4b"

            with cols[i]:
                st.markdown(f"""
                <div class="compact-card" style="border-left-color: {color};">
                    <div>
                        <p class="stock-symbol">{s.replace('.NS','')}</p>
                        <p class="price-text">{curr} <span style="font-size:0.9rem; color:{'#00ff88' if p_change>0 else '#ff4b4b'};">({p_change}%)</span></p>
                    </div>
                    <div>
                        <span class="rsi-text">RSI: {rsi}</span>
                        <p style="margin-top:10px; font-weight:bold; color:{color};">{signal}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        except:
            continue
