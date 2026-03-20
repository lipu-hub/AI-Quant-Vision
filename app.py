import streamlit as st
import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime
import plotly.graph_objects as go

st.set_page_config(page_title="MarketMind AI - India", layout="wide")

# Custom CSS for Dark Theme (Enhanced)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .card {
        background: #1e2130;
        padding: 20px;
        border-radius: 12px;
        border-top: 4px solid #00ff88;
        margin-bottom: 10px;
        transition: 0.3s;
    }
    .card:hover { transform: translateY(-5px); border-top: 4px solid #00d4ff; }
    h3 { margin-bottom: 5px; color: #00ff88; font-size: 1.2rem; }
    h2 { margin-top: 0px; margin-bottom: 10px; font-size: 1.8rem; }
    </style>
    """, unsafe_allow_html=True)

analyzer = SentimentIntensityAnalyzer()

st.title("🇮🇳 MarketMind AI Analyst (NSE)")
st.write(f"Last Sync: {datetime.now().strftime('%H:%M:%S')} IST")

# Updated Indian Stocks List
indian_stocks = ["RELIANCE.NS", "TATAMOTORS.NS", "ZOMATO.NS", "TCS.NS", "INFY.NS", "BTC-USD"]

# Setup Columns
cols = st.columns(3)

for i, s in enumerate(indian_stocks):
    try:
        t = yf.Ticker(s)
        # 1-day data with 15-min interval
        hist = t.history(period="1d", interval="15m")
        if hist.empty:
            continue
            
        price = round(hist['Close'].iloc[-1], 2)

        # News Sentiment logic
        score = 0
        news_head = "No Recent News Found"
        try:
            news_data = t.news
            if news_data and len(news_data) > 0:
                news_head = news_data[0].get('title', 'No Title Available')
                score = analyzer.polarity_scores(news_head)['compound']
        except:
            pass 

        status = "BULLISH 🚀" if score > 0.1 else "BEARISH 📉" if score < -0.1 else "STABLE ⚖️"
        color = "#00ff88" if score > 0.1 else "#ff4b4b" if score < -0.1 else "#888"
        currency = "₹" if ".NS" in s else "$"

        with cols[i % 3]:
            # Card Display
            st.markdown(f"""
                <div class="card">
                    <h3>{s.replace('.NS', '')}</h3>
                    <h2>{currency}{price}</h2>
                    <p>AI Sentiment: <b style="color:{color}">{status}</b></p>
                    <hr style="opacity: 0.1">
                    <p style="font-size: 0.8rem; height: 40px; overflow: hidden;">{news_head}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Sparkline Chart
            fig = go.Figure(data=go.Scatter(x=hist.index, y=hist['Close'], line=dict(color=color, width=2)))
            fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=60, xaxis_visible=False, yaxis_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    except Exception as e:
        continue
