import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="MarketMind AI", layout="wide")
st_autorefresh(interval=60 * 1000, key="datarefresh")

if 'view' not in st.session_state: st.session_state.view = 'landing'
if 'selected_stock' not in st.session_state: st.session_state.selected_stock = None

# 2. Styling
st.markdown("""
<style>
    .stApp { background: #0f172a; color: white; }
    .card { background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border: 1px solid #38bdf8; text-align: center; }
    .prob-box { background: #1e293b; padding: 30px; border-radius: 20px; border-left: 10px solid #38bdf8; text-align: center; }
    .big-prob { font-size: 5rem; font-weight: 900; color: #38bdf8; margin: 0; }
    div.stButton > button { background: #38bdf81a !important; border: 1px solid #38bdf8 !important; color: #38bdf8 !important; border-radius: 10px; width: 100%; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 3. Flattened Data Engine (Fixed for Graphs)
def get_clean_data(ticker):
    try:
        # Fetching data and flattening multi-index columns
        df = yf.download(ticker, period="1mo", interval="1d", progress=False)
        if df.empty: return None
        
        # FIX: Agar columns multi-index hain (yfinance 0.2.40+), toh unhe simple karo
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        return df
    except: return None

stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "TATAMOTORS.NS", "ZOMATO.NS", "BTC-USD"]

# --- UI Logic ---

if st.session_state.view == 'landing':
    st.markdown("<div style='text-align:center; padding-top:100px;'><h1>MarketMind <span style='color:#38bdf8;'>AI</span></h1></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 1, 2])
    with c2:
        if st.button("🚀 ENTER TERMINAL"): 
            st.session_state.view = 'grid'; st.rerun()

elif st.session_state.view == 'grid':
    st.title("Market Overview")
    if st.button("🏠 Home"): st.session_state.view = 'landing'; st.rerun()
    
    cols = st.columns(4)
    for i, s in enumerate(stocks):
        df = get_clean_data(s)
        with cols[i % 4]:
            if df is not None:
                curr = float(df['Close'].iloc[-1])
                st.markdown(f'<div class="card"><p>{s}</p><h3>₹{round(curr, 2)}</h3></div>', unsafe_allow_html=True)
                if st.button(f"Analyze {s.split('.')[0]}", key=s):
                    st.session_state.selected_stock = s
                    st.session_state.view = 'detail'; st.rerun()
            else:
                st.error(f"Syncing {s}...")

elif st.session_state.view == 'detail':
    s = st.session_state.selected_stock
    df = get_clean_data(s)
    if st.button("⬅️ Back"): st.session_state.view = 'grid'; st.rerun()

    if df is not None:
        curr = float(df['Close'].iloc[-1])
        sma20 = float(df['Close'].rolling(20).mean().iloc[-1])
        
        # SIMPLE PROBABILITY %
        diff = ((curr - sma20) / sma20) * 100
        prob_val = round(max(10, min(95, 50 + (diff * 10))), 0) # Whole number %
        
        st.header(f"AI Analysis: {s}")
        c1, c2 = st.columns([2, 1])
        
        with c1:
            # Candlestick Graph Fix
            fig = go.Figure(data=[go.Candlestick(
                x=df.index, 
                open=df['Open'], 
                high=df['High'], 
                low=df['Low'], 
                close=df['Close']
            )])
            fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.markdown(f"""
            <div class="prob-box">
                <p style="color:#94a3b8; font-weight:bold;">BULLISH PROBABILITY</p>
                <h1 class="big-prob">{int(prob_val)}%</h1>
                <p style="color:{'#22c55e' if prob_val > 50 else '#ef4444'}; font-weight:bold; font-size:1.2rem;">
                    {'UPTREND' if prob_val > 50 else 'DOWNTREND'}
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.metric("Live Price", f"₹{round(curr, 2)}")
