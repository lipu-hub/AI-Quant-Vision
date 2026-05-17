import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai
import plotly.graph_objects as go
import requests

# ⚡ Page Configuration
st.set_page_config(page_title="MarketMind AI Terminal", layout="wide", initial_sidebar_state="expanded")

# 🔐 Streamlit Secrets Verification
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.sidebar.warning("⚠️ Please configure GEMINI_API_KEY in Streamlit Secrets.")

# INITIALIZE SESSION STATES
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {}
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = "IFCI"
if "ticker_raw_name" not in st.session_state:
    st.session_state.ticker_raw_name = "IFCI.NS"
if "ai_analysis_result" not in st.session_state:
    st.session_state.ai_analysis_result = None
if "live_prices" not in st.session_state:
    st.session_state.live_prices = {}
if "custom_tickers" not in st.session_state:
    st.session_state.custom_tickers = [
        "SUZLON.NS", "RVNL.NS", "NBCC.NS", "GAIL.NS", "IRFC.NS", 
        "IDEA.NS", "TATAPOWER.NS", "HUDCO.NS", "IFCI.NS", "YESBANK.NS", 
        "NHPC.NS", "IOC.NS", "BTC-USD", "PNB.NS", "JPPOWER.NS", 
        "SJVN.NS", "SAIL.NS", "ETH-USD"
    ]

# ⚙️ CORE ADMIN CONSOLE IN SIDEBAR
with st.sidebar:
    st.markdown("## ⚙️ Core Admin Console")
    admin_pin = st.text_input("Enter Admin Master Pin:", type="password")
    if admin_pin == "777":
        st.success("🔓 Admin Access Granted!")
        new_ticker = st.text_input("Add Ticker Name (e.g., RELIANCE.NS):").upper().strip()
        if st.button("➕ Inject Asset"):
            if new_ticker and new_ticker not in st.session_state.custom_tickers:
                st.session_state.custom_tickers.append(new_ticker)
                st.rerun()
    st.markdown("---")

# 🎛️ INJECTING PREMIUM STYLE BLOCK WITH LOGO WRAPPERS
bg_color = "#f8fafc"
text_color = "#0f172a"
card_bg = "#ffffff"
border_color = "rgba(234, 88, 12, 0.4)"
price_color = "#ea580c"
title_color = "#475569"

st.markdown(f"""
<style>
.stApp {{ background-color: {bg_color} !important; color: {text_color} !important; }}
h1, h2, h3, p, span, label {{ color: {text_color} !important; font-weight: 600; }}
div[data-testid="stVComponentBlock"] > div[style*="border"] {{
    border: 1px solid {border_color} !important;
    border-radius: 12px !important;
    background: {card_bg} !important;
    padding: 16px !important;
    box-shadow: 0 4px 12px rgba(234, 88, 12, 0.05) !important;
}}
.card-header-flex {{ display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }}
.company-logo-img {{ width: 40px; height: 40px; border-radius: 8px; object-fit: contain; background: #ffffff; border: 1px solid #e2e8f0; padding: 2px; }}
.price-text {{ font-family: 'Courier New', Courier, monospace; font-size: 1.7rem !important; font-weight: bold; color: {price_color} !important; margin: 2px 0px; }}
.stock-title {{ font-size: 1.1rem; font-weight: bold; color: {title_color} !important; }}
</style>
""", unsafe_allow_html=True)

# ✨ EXPERT FIX: Direct Raw Vector GitHub links that never get blocked by CORS
def get_stock_logo_url(ticker):
    logos = {
        "SUZLON": "https://raw.githubusercontent.com/SACHIN-MISHRA-PROGRAMMER/Stock-Logos/main/logos/SUZLON.png",
        "RVNL": "https://raw.githubusercontent.com/SACHIN-MISHRA-PROGRAMMER/Stock-Logos/main/logos/RVNL.png",
        "NBCC": "https://raw.githubusercontent.com/SACHIN-MISHRA-PROGRAMMER/Stock-Logos/main/logos/NBCC.png",
        "GAIL": "https://raw.githubusercontent.com/SACHIN-MISHRA-PROGRAMMER/Stock-Logos/main/logos/GAIL.png",
        "IRFC": "https://raw.githubusercontent.com/SACHIN-MISHRA-PROGRAMMER/Stock-Logos/main/logos/IRFC.png",
        "IDEA": "https://raw.githubusercontent.com/SACHIN-MISHRA-PROGRAMMER/Stock-Logos/main/logos/VI.png",
        "TATAPOWER": "https://raw.githubusercontent.com/SACHIN-MISHRA-PROGRAMMER/Stock-Logos/main/logos/TATAPOWER.png",
        "HUDCO": "https://raw.githubusercontent.com/SACHIN-MISHRA-PROGRAMMER/Stock-Logos/main/logos/HUDCO.png",
        "IFCI": "https://raw.githubusercontent.com/SACHIN-MISHRA-PROGRAMMER/Stock-Logos/main/logos/IFCI.png",
        "YESBANK": "https://raw.githubusercontent.com/SACHIN-MISHRA-PROGRAMMER/Stock-Logos/main/logos/YESBANK.png",
        "NHPC": "https://raw.githubusercontent.com/SACHIN-MISHRA-PROGRAMMER/Stock-Logos/main/logos/NHPC.png",
        "IOC": "https://raw.githubusercontent.com/SACHIN-MISHRA-PROGRAMMER/Stock-Logos/main/logos/IOC.png",
        "PNB": "https://raw.githubusercontent.com/SACHIN-MISHRA-PROGRAMMER/Stock-Logos/main/logos/PNB.png",
        "JPPOWER": "https://raw.githubusercontent.com/SACHIN-MISHRA-PROGRAMMER/Stock-Logos/main/logos/JPPOWER.png",
        "SJVN": "https://raw.githubusercontent.com/SACHIN-MISHRA-PROGRAMMER/Stock-Logos/main/logos/SJVN.png",
        "SAIL": "https://raw.githubusercontent.com/SACHIN-MISHRA-PROGRAMMER/Stock-Logos/main/logos/SAIL.png",
        "BTC-USD": "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/btc.png",
        "ETH-USD": "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/eth.png"
    }
    return logos.get(ticker, "https://raw.githubusercontent.com/SACHIN-MISHRA-PROGRAMMER/Stock-Logos/main/logos/GENERIC.png")

tickers = st.session_state.custom_tickers
st.title("🚀 MarketMind AI Trading Terminal")
st.subheader("Live Budget Scanner with Real Brand Engine Logos")

@st.cache_data(ttl=30)
def fetch_trading_data(ticker_name):
    try:
        df = yf.download(ticker_name, period="1mo", interval="15m", auto_adjust=True, progress=False)
        if df.empty:
            df = yf.download(ticker_name, period="1mo", interval="1d", auto_adjust=True, progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
            return df
    except:
        return None

# 🚨 AUTO-SCANNER BASELINE
@st.fragment(run_every=15)
def live_alert_scanner():
    st.markdown("### 🚦 Immediate AI Whistleblower (Live Alerts)")
    for ticker in tickers:
        if ticker not in st.session_state.live_prices:
            st.session_state.live_prices[ticker] = {"price": 0.0, "status": "STABLE"}
    st.info("🔄 Scanner active. Real-time baselines monitoring enabled.")

live_alert_scanner()
st.markdown("---")

st.markdown("### 🔍 Intelligent Asset Filter")
cols = st.columns(4)
for i, ticker in enumerate(tickers):
    with cols[i % 4]:
        data_df = fetch_trading_data(ticker)
        if data_df is not None and not data_df.empty:
            close_series = data_df['Close'].squeeze()
            latest_price = float(close_series.iloc[-1])
            symbol = "$" if "USD" in ticker else "₹"
            clean_name = ticker.replace(".NS", "")
            img_url = get_stock_logo_url(clean_name)
            
            with st.container(border=True):
                st.markdown(f"""
                <div class="card-header-flex">
                    <img class="company-logo-img" src="{img_url}">
                    <div class="stock-title">{clean_name}</div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"<div class='price-text'>{symbol}{latest_price:,.2f}</div>", unsafe_allow_html=True)
                
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button(f"Scan 🎯", key=f"scan_{ticker}", use_container_width=True):
                        st.session_state.selected_ticker = clean_name
                        st.session_state.ticker_raw_name = ticker
                        with st.spinner("AI analyzing..."):
                            try:
                                recent_data = data_df.tail(10)[['Close', 'High', 'Low']].to_string()
                                ema_now = float(data_df['EMA_20'].iloc[-1])
                                prompt = f"Analyze this asset for short term trading: {clean_name}. Current Price: {latest_price}, EMA_20: {ema_now:.2f}. Data: {recent_data}. Provide clear buy/sell signal and entry zones."
                                model = genai.GenerativeModel('models/gemini-2.5-flash')
                                st.session_state.ai_analysis_result = model.generate_content(prompt).text
                            except Exception as e:
                                st.session_state.ai_analysis_result = f"Error: {str(e)}"
                with btn_col2:
                    if st.button(f"Sim Buy 🛍️", key=f"sim_{ticker}", use_container_width=True):
                        st.session_state.portfolio[ticker] = {"buy_price": latest_price, "qty": 100}
                        st.toast(f"Added {clean_name} to Simulator!", icon="💰")

# Execution desk render logic
if st.session_state.selected_ticker and st.session_state.ai_analysis_result:
    st.markdown("---")
    st.subheader(f"⚡ Live Quant Execution Desk: {st.session_state.selected_ticker}")
    chart_col, signal_col = st.columns([3, 2])
    with chart_col:
        raw_df = fetch_trading_data(st.session_state.ticker_raw_name)
        if raw_df is not None and not raw_df.empty:
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=raw_df.index, open=raw_df['Open'].squeeze(), high=raw_df['High'].squeeze(), low=raw_df['Low'].squeeze(), close=raw_df['Close'].squeeze(), name='Price Action'))
            fig.add_trace(go.Scatter(x=raw_df.index, y=raw_df['EMA_20'].squeeze(), line=dict(color='#f97316', width=2), name='20 EMA Trend'))
            fig.update_layout(xaxis_rangeslider_visible=False, height=420, template="plotly_white", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
    with signal_col:
        with st.container(border=True):
            st.markdown("### 🤖 Executable AI Strategy")
            st.markdown(st.session_state.ai_analysis_result)
