import streamlit as st
import yfinance as tf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime
import pandas as pd

# Page Configuration
st.set_page_config(page_title="MarketMind AI - India", layout="wide")

# Custom CSS for Dynamic Dark Theme & Hover Effects
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .card {
        background: #1e2130;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }
    .card:hover { transform: scale(1.02); }
    hr { margin: 10px 0; border: 0.5px solid #444; }
</style>
""", unsafe_allow_html=True)

analyzer = SentimentIntensityAnalyzer()

# Title and Live Sync Info
st.title("🇮🇳 MarketMind AI Analyst (NSE)")
now = datetime.now().strftime('%H:%M:%S')
st.write(f"**Last Sync:** {now} IST | *Auto-refreshing every 10 mins*")

# Indian Stocks List
indian_stocks = ["RELIANCE.NS", "TATAMOTORS.NS", "ZOMATO.NS", "TCS.NS", "INFY.NS", "BTC-USD"]

cols = st.columns(3)

for i, s in enumerate(indian_stocks):
    try:
        t = tf.Ticker(s)
        # Fetch latest price
        hist = t.history(period="1d")
        if not hist.empty:
            price = round(hist['Close'].iloc[-1], 2)
        else:
            price = "Data Unavailable"

        # News & Sentiment Logic
        score = 0
        news_head = "No recent news available"
        if t.news:
            news_head = t.news[0].get('title', news_head)
            score = analyzer.polarity_scores(news_head)['compound']

        # Determine Sentiment and Border Color
        if score > 0.05:
            status = "BULLISH 🚀"
            border_color = "#00ff88" # Green
        elif score < -0.05:
            status = "BEARISH 📉"
            border_color = "#ff4b4b" # Red
        else:
            status = "STABLE ⚖️"
            border_color = "#f0f2f6" # White/Grey

        currency = "₹" if ".NS" in s else "$"

        # Card Rendering with Dynamic Border
        with cols[i % 3]:
            st.markdown(f"""
            <div class="card" style="border-top: 5px solid {border_color};">
                <h3 style="margin-bottom:0;">{s.replace('.NS', '')}</h3>
                <h2 style="color:{border_color}; margin-top:5px;">{currency}{price}</h2>
                <p>AI Sentiment: <b>{status}</b></p>
                <hr>
                <p style="font-size: 0.85rem; color: #ccc; min-height: 40px;">{news_head}</p>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        continue

# Optional: Auto-refresh component (Needs streamlit-autorefresh)
# Agar aapne requirements.txt mein dala hai toh niche wala line uncomment kar sakte ho
# from streamlit_autorefresh import st_autorefresh
# st_autorefresh(interval=600 * 1000, key="datarefresh")
