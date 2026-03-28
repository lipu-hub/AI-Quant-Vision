import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. Config & Auto-refresh
st.set_page_config(page_title="MarketMind AI - Pro Terminal", layout="wide")
st_autorefresh(interval=60 * 1000, key="datarefresh")

# 2. Session State for Navigation
if 'view' not in st.session_state:
    st.session_state.view = 'dashboard'
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = None

# 3. Custom CSS
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .compact-card {
        background: #1e2130; padding: 10px; border-radius: 10px;
        border-top: 3px solid #444; margin-bottom: 2px; text-align: center;
    }
    .stock-symbol { font-size: 0.9rem; font-weight: bold; color: #aaa; }
    .price-text { font-size: 1.1rem; font-weight: bold; margin: 2px 0; }
</style>
""", unsafe_allow_html=True)

# 4. Stocks List
stocks_list = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", 
    "BHARTIARTL.NS", "SBIN.NS", "LICI.NS", "ITC.NS", "HINDUNILVR.NS",
    "LT.NS", "BAJFINANCE.NS", "TATAMOTORS.NS", "M&M.NS", "ADANIENT.NS",
    "SUNPHARMA.NS", "ASIANPAINT.NS", "TITAN.NS", "ZOMATO.NS", "NTPC.NS",
    "KOTAKBANK.NS", "AXISBANK.NS", "BTC-USD", "ETH-USD"
]

# 5. Functions
@st.cache_data(ttl=600)
def get_data(symbol, period="7d"):
    try:
        df = yf.Ticker(symbol).history(period=period)
        return df
    except: return pd.DataFrame()

def get_rsi(df):
    if len(df) < 14: return 50
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean().iloc[-1]
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().iloc[-1]
    rs = gain / (loss if loss != 0 else 0.1)
    return round(100 - (100 / (1 + rs)), 2)

# --- NAVIGATION LOGIC ---

# 🏠 PAGE: DASHBOARD (20+ Stocks Grid)
if st.session_state.view == 'dashboard':
    st.title("📊 MarketMind AI: Terminal")
    st.caption(f"Last Updated: {datetime.now().strftime('%H:%M:%S')} IST")

    for i in range(0, len(stocks_list), 5):
        cols = st.columns(5)
        for j in range(5):
            if i + j < len(stocks_list):
                s = stocks_list[i + j]
                df = get_data(s)
                if df.empty: continue
                
                curr = round(df['Close'].iloc[-1], 2)
                prev = round(df['Close'].iloc[-2], 2)
                p_chg = round(((curr - prev) / prev) * 100, 2)
                color = "#00ff88" if p_chg >= 0 else "#ff4b4b"
                
                with cols[j]:
                    st.markdown(f"""
                    <div class="compact-card" style="border-top-color: {color};">
                        <div class="stock-symbol">{s.replace('.NS','')}</div>
                        <div class="price-text">{curr} <span style="font-size:0.75rem; color:{color};">({p_chg}%)</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Sparkline Graph
                    fig = go.Figure(go.Scatter(x=df.index, y=df['Close'], mode='lines', line=dict(color=color, width=1.5)))
                    fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=40, xaxis=dict(visible=False), yaxis=dict(visible=False), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                    
                    if st.button(f"Analyze {s.split('.')[0]}", key=s):
                        st.session_state.selected_stock = s
                        st.session_state.view = 'detail'
                        st.rerun()

# 🔍 PAGE: DEEP ANALYSIS
elif st.session_state.view == 'detail':
    s = st.session_state.selected_stock
    df_long = get_data(s, period="1mo")
    
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.view = 'dashboard'
        st.rerun()
    
    st.title(f"🚀 Analysis: {s.replace('.NS','')}")
    
    # KPIs
    rsi_val = get_rsi(df_long)
    curr_price = round(df_long['Close'].iloc[-1], 2)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Current Price", f"₹{curr_price}")
    c2.metric("RSI Indicator", rsi_val)
    
    if rsi_val < 35: signal, sig_col = "Strong Buy 💎", "#00ff88"
    elif rsi_val > 65: signal, sig_col = "Sell/Overbought ⚠️", "#ff4b4b"
    else: signal, sig_col = "Neutral/Hold ⚖️", "#aaa"
    
    c3.markdown(f"### AI Signal: <span style='color:{sig_col}'>{signal}</span>", unsafe_allow_html=True)

    # Main Chart
    fig = go.Figure(data=[go.Candlestick(x=df_long.index, open=df_long['Open'], high=df_long['High'], low=df_long['Low'], close=df_long['Close'])])
    fig.update_layout(title=f"{s} 30-Day Performance", template="plotly_dark", height=500, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📊 Fundamental Data (Raw)")
    st.write(df_long.tail(5))
