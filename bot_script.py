import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import io

# 1. Setup
st.set_page_config(page_title="MarketMind AI - Pro Terminal", layout="wide")
st_autorefresh(interval=60 * 1000, key="datarefresh")

# --- BRANDING SECTION ---
# Yahan apna logo URL daalein
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/2422/2422796.png" 

# CSS for Logo and Premium UI
st.markdown(f"""
<style>
    .stApp {{ background-color: #0e1117; color: white; }}
    .header-container {{
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 10px 0;
        margin-bottom: 20px;
        border-bottom: 1px solid #333;
    }}
    .stButton>button {{
        width: 100%;
        border-radius: 12px;
        background-color: #1e2130;
        color: white;
        border: 1px solid #333;
        padding: 10px;
        height: 140px;
        transition: 0.3s;
        white-space: pre-wrap;
    }}
    .stButton>button:hover {{
        border-color: #00ff88;
        background-color: #25293d;
    }}
</style>
<div class="header-container">
    <img src="{LOGO_URL}" width="55">
    <h1 style="margin: 0; font-family: 'Inter', sans-serif; letter-spacing: -1px;">MarketMind AI <span style="color:#00ff88;">Terminal</span></h1>
</div>
""", unsafe_allow_html=True)

# 2. State Management
if 'view' not in st.session_state: st.session_state.view = 'grid'
if 'selected_stock' not in st.session_state: st.session_state.selected_stock = None

# 3. Data Fetching
stocks_list = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", 
    "BHARTIARTL.NS", "SBIN.NS", "LICI.NS", "ITC.NS", "TATAMOTORS.NS", 
    "ZOMATO.NS", "BTC-USD", "ETH-USD"
]

@st.cache_data(ttl=600)
def get_stock_data(s, period="1mo"):
    try:
        return yf.Ticker(s).history(period=period)
    except: return None

# --- UI LOGIC ---

# PAGE: GRID VIEW
if st.session_state.view == 'grid':
    st.caption(f"Real-time Intelligence Dashboard • {datetime.now().strftime('%H:%M:%S')} IST")
    
    for i in range(0, len(stocks_list), 4):
        cols = st.columns(4)
        for j in range(4):
            if i + j < len(stocks_list):
                s = stocks_list[i + j]
                df = get_stock_data(s)
                if df is None or df.empty: continue
                
                curr = round(df['Close'].iloc[-1], 2)
                prev = round(df['Close'].iloc[-2], 2)
                chg = round(((curr - prev) / prev) * 100, 2)
                color = "#00ff88" if chg >= 0 else "#ff4b4b"
                
                with cols[j]:
                    # Main Stock Card
                    btn_label = f"{s.replace('.NS','')}\n\n₹{curr}\n({chg}%)"
                    if st.button(btn_label, key=s):
                        st.session_state.selected_stock = s
                        st.session_state.view = 'detail'
                        st.rerun()
                    
                    # Mini Chart
                    fig = go.Figure(go.Scatter(x=df.index[-10:], y=df['Close'][-10:], mode='lines', line=dict(color=color, width=2)))
                    fig.update_layout(margin=dict(l=5,r=5,t=0,b=0), height=35, xaxis=dict(visible=False), yaxis=dict(visible=False), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# PAGE: DETAIL VIEW
elif st.session_state.view == 'detail':
    s = st.session_state.selected_stock
    df = get_stock_data(s, period="3mo")
    
    col_back, col_title = st.columns([1, 10])
    with col_back:
        if st.button("⬅️"):
            st.session_state.view = 'grid'
            st.rerun()
    with col_title:
        st.subheader(f"Deep Analysis: {s}")

    c1, c2 = st.columns([2, 1])
    
    with c1:
        # Technical Chart
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Download Report Feature
        csv = df.to_csv().encode('utf-8')
        st.download_button(label="📥 Download Data Report (CSV)", data=csv, file_name=f"{s}_report.csv", mime='text/csv')
        
    with c2:
        st.markdown("### 🤖 AI Intelligence")
        curr = df['Close'].iloc[-1]
        vol = (df['High'] - df['Low']).tail(10).mean()
        
        st.metric("Price", f"₹{round(curr,2)}")
        st.metric("Expected Target", f"₹{round(curr + vol*1.5, 2)}", delta=f"+{round(vol*1.5, 2)}")
        st.metric("Stop-Loss", f"₹{round(curr - vol*1.2, 2)}", delta=f"-{round(vol*1.2, 2)}", delta_color="inverse")
        
        st.write("---")
        st.info("💡 Analysis: Trend is showing consolidation. Monitor volume for breakout.")
