import streamlit as st
import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime

# Page Setup
st.set_page_config(page_title="MarketMind AI - NSE Overview", layout="wide")

# CSS for Ultra-Compact Cards
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .compact-card {
        background: #1e2130;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 4px solid #444;
        transition: 0.2s;
    }
    .compact-card:hover { background: #25293d; }
    .stock-name { font-size: 0.9rem; font-weight: bold; margin: 0; color: #fff; }
    .stock-price { font-size: 1.1rem; margin: 2px 0; font-weight: bold; }
    .stock-sent { font-size: 0.7rem; margin: 0; text-transform: uppercase; letter-spacing: 1px; }
</style>
""", unsafe_allow_html=True)

analyzer = SentimentIntensityAnalyzer()

st.title("📊 NSE Market Overview - AI Analyst")
st.caption(f"Last Updated: {datetime.now().strftime('%H:%M:%S')} IST")

# Badi Stock List (Top NSE Stocks)
stocks = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", 
    "BHARTIARTL.NS", "SBI-N.NS", "LICI.NS", "ITC.NS", "HINDUNILVR.NS",
    "LT.NS", "BAJFINANCE.NS", "TATAMOTORS.NS", "M&M.NS", "ADANIENT.NS",
    "SUNPHARMA.NS", "ASIANPAINT.NS", "TITAN.NS", "ZOMATO.NS", "NTPC.NS",
    "BTC-USD", "ETH-USD" # Thoda Crypto bhi
]

# Grid Layout: 5 columns taaki ek screen par 15-20 stocks dikhein
cols = st.columns(5)

for i, s in enumerate(stocks):
    try:
        t = yf.Ticker(s)
        # Fast Fetch for current price
        data = t.history(period="1d")
        if data.empty: continue
        
        price = round(data['Close'].iloc[-1], 2)
        prev_close = data['Open'].iloc[-1]
        change = round(((price - prev_close) / prev_close) * 100, 2)
        
        # Simple Sentiment from News
        status, color = "STABLE", "#888"
        if t.news:
            news_head = t.news[0].get('title', '')
            score = analyzer.polarity_scores(news_head)['compound']
            if score > 0.05: status, color = "BULLISH", "#00ff88"
            elif score < -0.05: status, color = "BEARISH", "#ff4b4b"

        symbol = s.replace('.NS', '')
        currency = "₹" if ".NS" in s else "$"

        with cols[i % 5]:
            st.markdown(f"""
            <div class="compact-card" style="border-left-color: {color};">
                <p class="stock-name">{symbol}</p>
                <p class="stock-price">{currency}{price}</p>
                <p class="stock-sent" style="color:{color};">{status} ({change}%)</p>
            </div>
            """, unsafe_allow_html=True)
            
    except:
        continue
