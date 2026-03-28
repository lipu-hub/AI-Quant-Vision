import streamlit as st
import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(page_title="MarketMind AI - India", layout="wide")

# Custom CSS for Premium Look
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .card {
        background: #1e2130;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
        transition: transform 0.2s ease;
    }
    .card:hover { transform: scale(1.02); border: 1px solid #444; }
    .news-text { font-size: 0.8rem; color: #bbb; min-height: 40px; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

analyzer = SentimentIntensityAnalyzer()

st.title("🇮🇳 MarketMind AI Analyst (NSE)")
now = datetime.now().strftime('%H:%M:%S')
st.caption(f"Last Sync: {now} IST | 7-Day Trend Charts Active")

# Indian Stocks List
indian_stocks = ["RELIANCE.NS", "TATAMOTORS.NS", "ZOMATO.NS", "TCS.NS", "INFY.NS", "BTC-USD"]

cols = st.columns(3)

for i, s in enumerate(indian_stocks):
    try:
        t = yf.Ticker(s)
        # Fetch 7 days of data for the chart
        hist = t.history(period="7d")
        
        if not hist.empty:
            current_price = round(hist['Close'].iloc[-1], 2)
            prev_price = round(hist['Close'].iloc[-2], 2)
            change = round(current_price - prev_price, 2)
            pct_change = round((change / prev_price) * 100, 2)
        else:
            continue

        # Sentiment Analysis
        news_head = "No recent news available"
        score = 0
        if t.news:
            news_head = t.news[0].get('title', news_head)
            score = analyzer.polarity_scores(news_head)['compound']

        # Colors & Status
        if score > 0.05:
            status, color = "BULLISH 🚀", "#00ff88"
        elif score < -0.05:
            status, color = "BEARISH 📉", "#ff4b4b"
        else:
            status, color = "STABLE ⚖️", "#f0f2f6"

        currency = "₹" if ".NS" in s else "$"

        with cols[i % 3]:
            # Render Card Info
            st.markdown(f"""
            <div class="card" style="border-top: 4px solid {color};">
                <h4 style="margin:0;">{s.replace('.NS', '')}</h4>
                <h2 style="margin:0; color:{color};">{currency}{current_price} <span style="font-size:1rem;">({pct_change}%)</span></h2>
                <p style="margin:0; font-size:0.9rem;">AI: <b>{status}</b></p>
                <p class="news-text">{news_head[:80]}...</p>
            </div>
            """, unsafe_allow_html=True)

            # Create Mini Chart (Sparkline)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist['Close'],
                mode='lines',
                line=dict(color=color, width=2),
                fill='tozeroy',
                fillcolor=f"rgba({ '0,255,136,0.1' if score > 0 else '255,75,75,0.1' })"
            ))
            fig.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                height=80,
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    except Exception as e:
        st.error(f"Error loading {s}")
