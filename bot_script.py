import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. Setup
st.set_page_config(page_title="MarketMind AI - Pro Terminal", layout="wide")
st_autorefresh(interval=60 * 1000, key="datarefresh")

# 2. State Management (Navigation)
if 'view' not in st.session_state:
    st.session_state.view = 'grid'
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = None

# 3. CSS for Premium Look
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        background-color: #1e2130;
        color: white;
        border: 1px solid #333;
        padding: 10px;
        height: 150px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        border-color: #00ff88;
        background-color: #25293d;
    }
    .metric-card {
        background: #161925;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# 4. Data Logic
stocks_list = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", 
    "BHARTIARTL.NS", "SBIN.NS", "LICI.NS", "ITC.NS", "HINDUNILVR.NS",
    "LT.NS", "BAJFINANCE.NS", "TATAMOTORS.NS", "M&M.NS", "ADANIENT.NS",
    "SUNPHARMA.NS", "ASIANPAINT.NS", "TITAN.NS", "ZOMATO.NS", "NTPC.NS",
    "KOTAKBANK.NS", "AXISBANK.NS", "BTC-USD", "ETH-USD"
]

@st.cache_data(ttl=600)
def get_stock_info(s):
    try:
        df = yf.Ticker(s).history(period="3mo") # 3 months for better SMA/RSI
        return df
    except: return None

# --- UI LOGIC ---

# 🏠 PAGE: THE GRID
if st.session_state.view == 'grid':
    st.title("📈 MarketMind AI Terminal")
    st.caption(f"Click any stock for Deep AI Prediction | Last Sync: {datetime.now().strftime('%H:%M:%S')}")
    
    for i in range(0, len(stocks_list), 5):
        cols = st.columns(5)
        for j in range(5):
            if i + j < len(stocks_list):
                s = stocks_list[i + j]
                df = get_stock_info(s)
                if df is None or df.empty: continue
                
                curr = round(df['Close'].iloc[-1], 2)
                prev = round(df['Close'].iloc[-2], 2)
                chg = round(((curr - prev) / prev) * 100, 2)
                color = "#00ff88" if chg >= 0 else "#ff4b4b"
                
                with cols[j]:
                    button_label = f"{s.replace('.NS','')}\n\n₹{curr}\n({chg}%)"
                    if st.button(button_label, key=s):
                        st.session_state.selected_stock = s
                        st.session_state.view = 'detail'
                        st.rerun()
                    
                    # Sparkline logic
                    fig = go.Figure(go.Scatter(x=df.index[-10:], y=df['Close'][-10:], mode='lines', line=dict(color=color, width=2)))
                    fig.update_layout(margin=dict(l=5,r=5,t=0,b=0), height=40, xaxis=dict(visible=False), yaxis=dict(visible=False), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# 🔍 PAGE: DETAIL VIEW
elif st.session_state.view == 'detail':
    s = st.session_state.selected_stock
    ticker = yf.Ticker(s)
    df = get_stock_info(s)
    
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.view = 'grid'
        st.rerun()
        
    st.header(f"Deep Analysis: {s}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Candlestick Chart
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False, title="Technical Price Action")
        st.plotly_chart(fig, use_container_width=True)
        
        # News Section
        st.subheader("📰 Latest News & Sentiment")
        news = ticker.news[:3]
        if news:
            for n in news:
                st.markdown(f"**[{n['title']}]({n['link']})**")
                st.caption(f"Source: {n['publisher']}")
        else:
            st.info("No recent news available for this asset.")
        
    with col2:
        st.subheader("🤖 AI Smart Levels")
        curr = df['Close'].iloc[-1]
        
        # Volatility Based Target & Stop-Loss
        avg_range = (df['High'] - df['Low']).tail(14).mean()
        target = round(curr + (avg_range * 1.5), 2)
        stop_loss = round(curr - (avg_range * 1.2), 2)
        
        # Display Metrics in a cleaner way
        st.markdown(f"""
        <div class="metric-card">
            <p style="color:#aaa; margin-bottom:0;">Current Price</p>
            <h2 style="color:white; margin-top:0;">₹{round(curr,2)}</h2>
        </div><br>
        """, unsafe_allow_html=True)
        
        st.metric("AI Expected Target", f"₹{target}", delta=f"{round(target-curr,2)}")
        st.metric("Safety Stop-Loss", f"₹{stop_loss}", delta=f"{round(stop_loss-curr,2)}", delta_color="inverse")
        
        st.write("---")
        
        # Trend Logic
        sma10 = df['Close'].rolling(window=10).mean().iloc[-1]
        if curr > sma10:
            st.success("VERDICT: BULLISH 🚀")
            st.write("Positive momentum detected. Price is holding above short-term average.")
        else:
            st.error("VERDICT: BEARISH 📉")
            st.write("Price is under pressure. Trading below 10-day average.")

        # Target Chart (Small)
        pred_fig = go.Figure(go.Scatter(x=['Now', 'Target'], y=[curr, target], mode='lines+markers+text', text=['', f"₹{target}"], textposition="top center", line=dict(color='#00ff88', dash='dash')))
        pred_fig.update_layout(height=200, template="plotly_dark", margin=dict(l=10,r=10,t=30,b=10))
        st.plotly_chart(pred_fig, use_container_width=True)
