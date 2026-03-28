import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. Page Configuration
st.set_page_config(page_title="MarketMind AI Terminal", layout="wide")
st_autorefresh(interval=60 * 1000, key="datarefresh")

# Initializing Session States
if 'view' not in st.session_state: st.session_state.view = 'landing'
if 'selected_stock' not in st.session_state: st.session_state.selected_stock = None

# 2. Advanced Styling (CSS)
st.markdown("""
<style>
    .stApp { background: #0f172a; color: white; font-family: 'Inter', sans-serif; }
    .ticker-bar { background: rgba(56, 189, 248, 0.1); padding: 15px; border-radius: 12px; border: 1px solid #38bdf8; display: flex; justify-content: space-around; margin-bottom: 25px; font-weight: bold; }
    .card { background: rgba(255,255,255,0.05); padding: 25px; border-radius: 15px; border: 1px solid #38bdf8; text-align: center; margin-bottom: 10px; transition: 0.3s; }
    .card:hover { transform: translateY(-5px); border-color: #ffffff; }
    .prob-box { background: #1e293b; padding: 35px; border-radius: 20px; border-left: 10px solid #38bdf8; text-align: center; }
    .big-prob { font-size: 5.5rem; font-weight: 900; color: #38bdf8; margin: 0; line-height: 1; }
    div.stButton > button { background: #38bdf81a !important; border: 1px solid #38bdf8 !important; color: #38bdf8 !important; border-radius: 10px; width: 100%; height: 45px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 3. Data Engine (Fixed for Multi-index and Errors)
def get_clean_data(ticker, p="1mo"):
    try:
        df = yf.download(ticker, period=p, interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except:
        return None

# --- UI LOGIC ---

# PAGE 1: LANDING
if st.session_state.view == 'landing':
    st.markdown("<div style='text-align:center; padding-top:100px;'><h1>MarketMind <span style='color:#38bdf8;'>AI</span></h1><p>Professional Analytics for Next-Gen Traders.</p></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 1, 2])
    with c2:
        if st.button("🚀 ENTER AI TERMINAL"): 
            st.session_state.view = 'grid'
            st.rerun()

# PAGE 2: DASHBOARD
elif st.session_state.view == 'grid':
    # Nifty Ticker at Top
    nifty_df = get_clean_data("^NSEI")
    if nifty_df is not None:
        nifty_p = round(float(nifty_df['Close'].iloc[-1]), 2)
        st.markdown(f'<div class="ticker-bar"><span>🇮🇳 NIFTY 50: <span style="color:#38bdf8;">{nifty_p}</span></span><span>🕒 LIVE SYNC ACTIVE</span></div>', unsafe_allow_html=True)
    
    col_h1, col_h2 = st.columns([5, 1])
    with col_h1: st.title("Market Overview")
    with col_h2: 
        if st.button("🏠 Home"): 
            st.session_state.view = 'landing'
            st.rerun()
    
    # Stock List
    stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "TATAMOTORS.NS", "ZOMATO.NS", "BTC-USD", "ETH-USD"]
    cols = st.columns(4)
    for i, s in enumerate(stocks):
        df = get_clean_data(s)
        with cols[i % 4]:
            if df is not None:
                curr_p = round(float(df['Close'].iloc[-1]), 2)
                st.markdown(f'<div class="card"><p style="color:#94a3b8; margin:0;">{s}</p><h2>₹{curr_p}</h2></div>', unsafe_allow_html=True)
                if st.button(f"Analyze {s.split('.')[0]}", key=s):
                    st.session_state.selected_stock = s
                    st.session_state.view = 'detail'
                    st.rerun()
            else:
                st.error(f"Syncing {s}...")

# PAGE 3: DETAIL VIEW
elif st.session_state.view == 'detail':
    s_stock = st.session_state.selected_stock
    df_detail = get_clean_data(s_stock, p="3mo")
    
    if st.button("⬅️ Back to Dashboard"): 
        st.session_state.view = 'grid'
        st.rerun()

    if df_detail is not None:
        # Probability & Signal Logic
        price_now = float(df_detail['Close'].iloc[-1])
        avg_20 = float(df_detail['Close'].rolling(20).mean().iloc[-1])
        diff_pct = ((price_now - avg_20) / avg_20) * 100
        prob_score = int(max(10, min(95, 50 + (diff_pct * 10))))
        
        if prob_score > 60: signal_msg = "🚀 BUY SIGNAL"
        elif prob_score < 40: signal_msg = "📉 SELL ALERT"
        else: signal_msg = "⚖️ NEUTRAL"

        st.header(f"Intelligence Report: {s_stock}")
        cl, cr = st.columns([2, 1])
        
        with cl:
            # Fixed Candlestick Graph
            fig_detail = go.Figure(data=[go.Candlestick(
                x=df_detail.index, 
                open=df_detail['Open'], 
                high=df_detail['High'], 
                low=df_detail['Low'], 
                close=df_detail['Close']
            )])
            fig_detail.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_detail, use_container_width=True)
            
        with cr:
            # Probability Card
            st.markdown(f"""
            <div class="prob-box">
                <p style="color:#94a3b8; font-weight:bold; margin-bottom:10px;">BULLISH PROBABILITY</p>
                <h1 class="big-prob">{prob_score}%</h1>
                <p style="margin-top:20px; font-weight:bold; color:{'#22c55e' if prob_score > 50 else '#ef4444'}; font-size:1.5rem;">
                    {signal_msg}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("---")
            st.metric("Current Market Price", f"₹{round(price_now, 2)}")
            
            # Simple Prediction
            std_dev = float(df_detail['Close'].pct_change().std())
            st.info(f"💡 AI Forecast: Expecting movement towards ₹{round(price_now * (1 + std_dev), 2)}")
