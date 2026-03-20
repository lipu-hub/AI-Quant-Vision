import streamlit as st
import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime

st.set_page_config(page_title="MarketMind AI - India", layout="wide")

# Custom CSS for Dark Theme
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .card {
        background: #1e2130;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #00ff88;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

analyzer = SentimentIntensityAnalyzer()

st.title("🇮🇳 MarketMind AI Analyst (NSE)")
st.write(f"Server Time: {datetime.now().strftime('%H:%M:%S')} UTC")

# Indian Stocks List
indian_stocks = ["RELIANCE.NS", "TATAMOTORS.NS", "ZOMATO.NS", "TCS.NS", "INFY.NS", "BTC-USD"]

cols = st.columns(3)

for i, s in enumerate(indian_stocks):
    try:
        t = yf.Ticker(s)
        price = round(t.history(period="1d")['Close'].iloc[-1], 2)
        
        # News Sentiment
        score = 0
        news_head = "No Recent News"
        if t.news:
            news_head = t.news[0].get('title', '')
            score = analyzer.polarity_scores(news_head)['compound']
        
        status = "BULLISH 🚀" if score > 0.05 else "BEARISH 📉" if score < -0.05 else "STABLE ⚖️"
        currency = "₹" if ".NS" in s else "$"
        
        with cols[i % 3]:
            st.markdown(f"""
                <div class="card">
                    <h3>{s.replace('.NS', '')}</h3>
                    <h2>{currency}{price}</h2>
                    <p>AI Sentiment: <b>{status}</b></p>
                    <hr>
                    <p style="font-size: 0.8rem;">{news_head}</p>
                </div>
            """, unsafe_allow_html=True)
    except:
        continue
