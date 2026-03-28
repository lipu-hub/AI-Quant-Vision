import streamlit as st
import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime
import pandas as pd

# Page Configuration
st.set_page_config(page_title="MarketMind AI - Pro Analyst", layout="wide")

# Custom CSS for Compact & Premium Look
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .compact-card {
        background: #1e2130;
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 15px;
        border-left: 5px solid #444;
        transition: 0.3s;
    }
    .compact-card:hover { transform: translateY(-3px); background: #25293d; }
    .stock-symbol { font-size: 1rem; font-weight: bold; margin: 0; }
    .price-text { font-size: 1.2rem; font-weight: bold; margin: 2px 0; }
    .signal-text { font-size: 0.75rem; font-weight: bold; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# RSI Calculation Logic
def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

analyzer = SentimentIntensityAnalyzer()

# Sidebar: Search & Filters
st.sidebar.title("🔍 Market Controls")
search_query = st.sidebar.text_input("Add Ticker (e.g. TATASTEEL.NS, ETH-USD)", "").upper()

# Default Stock List
default_stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "TATAMOTORS.NS", "ZOMATO.NS", "BTC-USD"]
if search_query:
    if search_query not in default_stocks:
        default_stocks.insert(0, search_query)

st.title("🚀 MarketMind AI: Pro Analyst Dashboard")
st.caption(f"Live Market Pulse | Last Sync: {datetime.now().strftime('%H:%M:%S')} IST")

cols = st.columns(4) # 4 columns for a balanced look

for i, s in enumerate(default_stocks):
    try:
        t = yf.Ticker(s)
        df = t.history(period="1mo") # Fetch 1 month for RSI
        
        if df.empty: continue
        
        current_price = round(df['Close'].iloc[-1], 2)
        # Calculate RSI
        rsi_values = calculate_rsi(df['Close'])
        current_rsi = round(rsi_values.iloc[-1], 2)
        
        # Sentiment
        status, color = "STABLE", "#888"
        if t.news:
            news_head = t.news[0].get('title', '')
            score = analyzer.polarity_scores(news_head)['compound']
            if score > 0.05: status, color = "BULLISH", "#00ff88"
            elif score < -0.05: status, color = "BEARISH", "#ff4b4b"

        # Trading Signal Logic
        if current_rsi < 30: signal = "🔥 BUY (Oversold)"
        elif current_rsi > 70: signal = "⚠️ SELL (Overbought)"
        else: signal = "⌛ HOLD (Neutral)"

        currency = "₹" if ".NS" in s else "$"

        with cols[i % 4]:
            st.markdown(f"""
            <div class="compact-card" style="border-left-color: {color};">
                <p class="stock-symbol">{s.replace('.NS', '')}</p>
                <p class="price-text" style="color:{color};">{currency}{current_price}</p>
                <p class="signal-text">{status} | RSI: {current_rsi}</p>
                <p style="font-size: 0.8rem; margin-top:5px; color: #ddd;">{signal}</p>
            </div>
            """, unsafe_allow_html=True)
            
    except:
        continue
