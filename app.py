import streamlit as st
import yfinance as yf
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime

# --- UI DESIGN (Attractive Look) ---
st.set_page_config(page_title="AI Quant Vision", layout="wide")

# Dark Theme aur Sundar Cards ke liye CSS
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .stock-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 255, 136, 0.3);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 10px;
    }
    .profit { color: #00ff88; font-weight: bold; font-size: 24px; }
    .loss { color: #ff4b4b; font-weight: bold; font-size: 24px; }
    </style>
    """, unsafe_allow_html=True)

# AI Sentiment Analyzer Setup
analyzer = SentimentIntensityAnalyzer()

# --- THE BRAIN (Intelligence) ---
def get_analysis(symbol):
    stock = yf.Ticker(symbol)
    
    # 1. Price Data uthao
    hist = stock.history(period="5d")
    current_price = hist['Close'].iloc[-1]
    prev_price = hist['Close'].iloc[-2]
    change = current_price - prev_price
    
    # 2. News uthao (Intelligence part)
    news = stock.news[:2] 
    sentiment_score = 0
    headlines = ""
    for n in news:
        headlines += f"• {n['title']}<br>"
        sentiment_score += analyzer.polarity_scores(n['title'])['compound']
    
    # 3. Decision Logic
    if sentiment_score > 0.05:
        verdict = "PROFIT (Bullish View)"
        v_class = "profit"
    elif sentiment_score < -0.05:
        verdict = "LOSS (Bearish View)"
        v_class = "loss"
    else:
        verdict = "NEUTRAL (No Big News)"
        v_class = ""

    return {
        "price": round(current_price, 2),
        "change": round(change, 2),
        "verdict": verdict,
        "class": v_class,
        "news": headlines
    }

# --- WEBSITE MAIN PAGE ---
st.title("🤖 AI Autonomous Stock Analyst")
st.write(f"Updated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
st.divider()

# Automatic List (Aapko input dene ki zaroorat nahi)
popular_stocks = ["TSLA", "AAPL", "NVDA", "MSFT", "GOOGL"]

# Display Cards
cols = st.columns(len(popular_stocks))

for i, s in enumerate(popular_stocks):
    data = get_analysis(s)
    with cols[i]:
        st.markdown(f"""
            <div class="stock-card">
                <h3>{s}</h3>
                <p>Price: ${data['price']}</p>
                <p class="{data['class']}">{data['verdict']}</p>
                <hr>
                <p style="font-size: 12px; color: #aaa;">Recent News:<br>{data['news']}</p>
            </div>
        """, unsafe_allow_html=True)
        st.metric(label="Daily Change", value=f"${data['price']}", delta=f"{data['change']}")

st.info("💡 Tip: Ye system har ghante khud internet check karta hai aur decision badalta hai.")
