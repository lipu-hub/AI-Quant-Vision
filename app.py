import streamlit as st
import yfinance as yf
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime

# --- UI DESIGN ---
st.set_page_config(page_title="AI Quant Vision", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .stock-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 255, 136, 0.3);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 10px;
        min-height: 250px;
    }
    .profit { color: #00ff88; font-weight: bold; font-size: 20px; }
    .loss { color: #ff4b4b; font-weight: bold; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

analyzer = SentimentIntensityAnalyzer()

def get_analysis(symbol):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="5d")
        
        if hist.empty:
            return None

        current_price = hist['Close'].iloc[-1]
        prev_price = hist['Close'].iloc[-2]
        change = current_price - prev_price
        
        # --- SAFE NEWS FETCHING ---
        sentiment_score = 0
        headlines = "No recent news found."
        
        # Check if news exists
        if hasattr(stock, 'news') and stock.news:
            headlines = ""
            for n in stock.news[:2]:
                title = n.get('title', 'No Title') # Safe way to get title
                headlines += f"• {title}<br>"
                sentiment_score += analyzer.polarity_scores(title)['compound']
        
        if sentiment_score > 0.05:
            verdict, v_class = "PROFIT (Bullish)", "profit"
        elif sentiment_score < -0.05:
            verdict, v_class = "LOSS (Bearish)", "loss"
        else:
            verdict, v_class = "NEUTRAL", ""

        return {
            "price": round(current_price, 2),
            "change": round(change, 2),
            "verdict": verdict,
            "class": v_class,
            "news": headlines
        }
    except Exception as e:
        return None

# --- MAIN APP ---
st.title("🤖 AI Autonomous Stock Analyst")
st.write(f"Last Sync: {datetime.now().strftime('%H:%M:%S')} UTC")

popular_stocks = ["TSLA", "AAPL", "NVDA", "MSFT", "GOOGL"]
cols = st.columns(len(popular_stocks))

for i, s in enumerate(popular_stocks):
    data = get_analysis(s)
    with cols[i]:
        if data:
            st.markdown(f"""
                <div class="stock-card">
                    <h3>{s}</h3>
                    <p>Price: ${data['price']}</p>
                    <p class="{data['class']}">{data['verdict']}</p>
                    <hr>
                    <p style="font-size: 11px; color: #aaa;">{data['news']}</p>
                </div>
            """, unsafe_allow_html=True)
            st.metric(label="Change", value=f"${data['price']}", delta=f"{data['change']}")
        else:
            st.error(f"Data for {s} unavailable")

st.success("✅ System is live and scanning the internet.")
