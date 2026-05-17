import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai
import plotly.graph_objects as go

# ⚡ Page Configuration
st.set_page_config(page_title="MarketMind AI Terminal", layout="wide", initial_sidebar_state="expanded")

# 🔐 Streamlit Secrets Verification
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.sidebar.warning("⚠️ Please configure GEMINI_API_KEY in Streamlit Secrets.")

# 🌓 MULTI-PAGE NAVIGATION & THEME CONTROL
with st.sidebar:
    st.markdown("## 🧭 Navigation Desk")
    app_page = st.radio("Go To Desk:", ["🏠 Terminal Dashboard", "🔍 Live AI Scanner"])
    st.markdown("---")
    st.markdown("## 🎨 Customization")
    ui_theme = st.selectbox("Select Display Theme:", ["🟠 Deep Dark Orange", "⚪ Classic Light Orange"])
    st.markdown("---")

# 🎛️ DYNAMIC CSS INJECTION
if ui_theme == "🟠 Deep Dark Orange":
    bg_color = "#0b0f19"
    text_color = "#e2e8f0"
    card_bg = "linear-gradient(145deg, #111827, #0f172a)"
    border_color = "rgba(249, 115, 22, 0.3)"
    hover_border = "#f97316"
    price_color = "#f97316"
    title_color = "#94a3b8"
    plotly_template = "plotly_dark"
else:
    bg_color = "#f8fafc"
    text_color = "#0f172a"
    card_bg = "#ffffff"
    border_color = "rgba(234, 88, 12, 0.4)"
    hover_border = "#ea580c"
    price_color = "#ea580c"
    title_color = "#475569"
    plotly_template = "plotly_white"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color} !important; color: {text_color} !important; }}
    h1, h2, h3, p, span, label {{ color: {text_color} !important; font-weight: 600; }}
    div[data-testid="stMarkdownContainer"] p {{ color: {text_color} !important; }}
    div[data-testid="stVComponentBlock"] > div[style*="border"] {{
        border: 1px solid {border_color} !important;
        border-radius: 12px !important;
        background: {card_bg} !important;
        padding: 20px !important;
        box-shadow: 0 4px 15px rgba(249, 115, 22, 0.05) !important;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }}
    div[data-testid="stVComponentBlock"] > div[style*="border"]:hover {{
        transform: translateY(-2px);
        border-color: {hover_border} !important;
        box-shadow: 0 4px 20px rgba(249, 115, 22, 0.25) !important;
    }}
    .price-text {{ font-family: 'Courier New', Courier, monospace; font-size: 1.8rem !important; font-weight: bold; color: {price_color} !important; margin: 5px 0px; }}
    .stock-title {{ font-size: 1.2rem; font-weight: 600; color: {title_color} !important; }}
    button[data-testid="stBaseButton-secondary"] {{ background-color: transparent !important; border: 1px solid {hover_border} !important; color: {text_color} !important; border-radius: 8px !important; }}
    button[data-testid="stBaseButton-secondary"]:hover {{ background-color: {hover_border} !important; color: white !important; }}
</style>
""", unsafe_allow_html=True)

tickers = [
    "SUZLON.NS", "IRFC.NS", "ZOMATO.NS", "PNB.NS", "GMRINFRA.NS",
    "IDEA.NS", "YESBANK.NS", "JPPOWER.NS", "RVNL.NS", "TATAPOWER.NS",
    "NHPC.NS", "SJVN.NS", "NBCC.NS", "HUDCO.NS", "IOC.NS",
    "SAIL.NS", "GAIL.NS", "IFCI.NS", "BTC-USD", "ETH-USD"
]

# Initialize Session States
if "portfolio" not in st.session_state: st.session_state.portfolio = {}
if "selected_ticker" not in st.session_state: st.session_state.selected_ticker = None
if "ai_analysis_result" not in st.session_state: st.session_state.ai_analysis_result = None
if "ticker_raw_name" not in st.session_state: st.session_state.ticker_raw_name = None

@st.cache_data(ttl=30)
def fetch_trading_data(ticker_name):
    try:
        df = yf.download(ticker_name, period="1mo", interval="15m", auto_adjust=True, progress=False)
        if not df.empty: df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
        return df
    except: return None

def generate_quant_signals(ticker_name, df, current_price):
    try:
        recent_data = df.tail(10)[['Close', 'High', 'Low']].to_string()
        ema_now = float(df['EMA_20'].iloc[-1])
        prompt = f"Analyze this budget asset for Short-term Trading: {ticker_name}. Price: {current_price}, EMA_20: {ema_now:.2f}. Data: {recent_data}. Provide Clear Signal (STRONG BUY/BUY/HOLD/SELL), targets, entry zone, and strict stop loss."
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        return model.generate_content(prompt).text
    except Exception as e: return f"Failed: {str(e)}"

# ---------------- NAVIGATION LOGIC ----------------
if app_page == "🏠 Terminal Dashboard":
    st.title("🚀 MarketMind AI Trading Terminal")
    st.subheader("Live 20-Asset Budget Matrix Desk")
    
    # Render Sidebar Simulator positions
    with st.sidebar:
        st.markdown("## 💰 Simulator Positions")
        if st.session_state.portfolio:
            for p_ticker, p_data in list(st.session_state.portfolio.items()):
                with st.container(border=True):
                    st.markdown(f"### {p_ticker.replace('.NS','')}")
                    st.markdown(f"Qty: **{p_data['qty']}** | Avg: **{p_data['buy_price']:.2f}**")
                    if st.button("Square Off ❌", key=f"sell_{p_ticker}"):
                        del st.session_state.portfolio[p_ticker]
                        st.rerun()
        else: st.info("No active virtual trades.")

    # Grid Display
    cols = st.columns(4)
    for i, ticker in enumerate(tickers):
        with cols[i % 4]:
            data_df = fetch_trading_data(ticker)
            if data_df is not None and not data_df.empty:
                latest_price = float(data_df['Close'].squeeze().iloc[-1])
                symbol = "$" if "USD" in ticker else "₹"
                clean_name = ticker.replace(".NS", "")
                
                with st.container(border=True):
                    st.markdown(f"<div class='stock-title'>{clean_name}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='price-text'>{symbol}{latest_price:,.2f}</div>", unsafe_allow_html=True)
                    
                    b_col1, b_col2 = st.columns(2)
                    with b_col1:
                        if st.button("Scan 🎯", key=f"s_{ticker}", use_container_width=True):
                            st.session_state.selected_ticker = clean_name
                            st.session_state.ticker_raw_name = ticker
                            with st.spinner("AI analyzing..."):
                                st.session_state.ai_analysis_result = generate_quant_signals(ticker, data_df, latest_price)
                    with b_col2:
                        if st.button("Sim 🛍️", key=f"p_{ticker}", use_container_width=True):
                            st.session_state.portfolio[ticker] = {"buy_price": latest_price, "qty": 100}
                            st.rerun()

    # Dynamic Analysis Output Block Below Grid Matrix
    if st.session_state.selected_ticker and st.session_state.ai_analysis_result:
        st.markdown("---")
        st.subheader(f"⚡ Live Execution Desk: {st.session_state.selected_ticker}")
        c_col, s_col = st.columns([3, 2])
        with c_col:
            raw_df = fetch_trading_data(st.session_state.ticker_raw_name)
            if raw_df is not None and not raw_df.empty:
                fig = go.Figure()
                fig.add_trace(go.Candlestick(x=raw_df.index, open=raw_df['Open'].squeeze(), high=raw_df['High'].squeeze(), low=raw_df['Low'].squeeze(), close=raw_df['Close'].squeeze()))
                fig.add_trace(go.Scatter(x=raw_df.index, y=raw_df['EMA_20'].squeeze(), line=dict(color='#f97316', width=2)))
                fig.update_layout(xaxis_rangeslider_visible=False, height=400, template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
        with s_col:
            with st.container(border=True): st.markdown(st.session_state.ai_analysis_result)

elif app_page == "🔍 Live AI Scanner":
    st.title("🔍 Real-Time Intelligent Whistleblower Engine")
    st.subheader("Background Order Flows & Automated 1-Minute Momentum Radar")
    
    @st.fragment(run_every=15)
    def separate_live_scanner():
        alert_count = 0
        for ticker in tickers:
            df = yf.download(ticker, period="1d", interval="1m", auto_adjust=True, progress=False)
            if not df.empty:
                close_series = df['Close'].squeeze()
                current_price = float(close_series.iloc[-1])
                prev_price = float(close_series.iloc[-2]) if len(close_series) > 1 else current_price
                price_change = ((current_price - prev_price) / prev_price) * 100
                clean_name = ticker.replace(".NS", "")
                
                if price_change > 0.12:
                    st.success(f"🔥 **IMMEDIATE BUY ALERT:** {clean_name} is spiking up! Price: {current_price:.2f} (+{price_change:.2f}%)")
                    alert_count += 1
                elif price_change < -0.12:
                    st.error(f"⚠️ **IMMEDIATE EXIT ALERT:** {clean_name} is dropping fast! Dump/Exit now! Price: {current_price:.2f} ({price_change:.2f}%)")
                    alert_count += 1
        if alert_count == 0:
            st.info("🔄 Order flows are stable. Continuously listening to 1-minute tick variations on all 20 assets...")
            
    separate_live_scanner()
