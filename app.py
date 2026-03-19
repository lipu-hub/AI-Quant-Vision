import streamlit as st
import yfinance as yf
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime

# --- UI SETTINGS ---
st.set_page_config(page_title="AI Quant Vision 2026", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .stock-card {
        background: rgba(255, 255, 255, 0.07);
        border: 1px solid #00ff88;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 10px;
    }
    .profit { color: #00ff88; font-weight: bold; }
    .loss { color: #ff4b4b; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

analyzer = SentimentIntensityAnalyzer()

def get_analysis(symbol):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="5d")
        if hist.empty: return None

        current_price = round(hist['Close'].iloc[-1], 2)
        prev_price = round(hist['Close'].iloc[-2], 2)
        change = round(current_price - prev_price, 2)
        
        # AI Sentiment
        sentiment_score = 0
        news_text = "No News Found"
        if hasattr(stock, 'news') and stock.news:
            title = stock.news[0].get('title', 'No Title')
            news_text = title
            sentiment_score = analyzer.polarity_scores(title)['compound']
        
        verdict = "PROFIT ✅" if sentiment_score > 0.05 else "LOSS ❌" if sentiment_score < -0.05 else "NEUTRAL 🔍"
        v_class = "profit" if "PROFIT" in verdict else "loss" if "LOSS" in verdict else ""

        return {"price": current_price, "change": change, "verdict": verdict, "class": v_class, "news": news_text}
    except: return None

# --- MAIN PAGE ---
st.title("🤖 AI Autonomous Analyst")
st.write(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")

stocks = ["TSLA", "AAPL", "NVDA", "BTC-USD", "MSFT"]
cols = st.columns(len(stocks))

for i, s in enumerate(stocks):
    data = get_analysis(s)
    with cols[i]:
        if data:
            st.markdown(f"""
                <div class="stock-card">
                    <h3>{s}</h3>
                    <p>Price: ${data['price']}</p>
                    <p class="{data['class']}">{data['verdict']}</p>
                    <hr>
                    <p style="font-size: 0.8rem; color: #aaa;">{data['news']}</p>
                </div>
            """, unsafe_allow_html=True)
            st.metric("Change", f"${data['price']}", f"{data['change']}")
