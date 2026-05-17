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

# 🤖 TELEGRAM BOT CONFIGURATION (Fetch from secrets or placeholders)
TELEGRAM_BOT_TOKEN = st.secrets.get("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
TELEGRAM_CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID_HERE")

def send_telegram_notification(message):
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or TELEGRAM_CHAT_ID == "YOUR_CHAT_ID_HERE":
        return False, "Telegram not configured in Secrets yet."
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return True, "Success"
        return False, response.text
    except Exception as e:
        return False, str(e)

# INITIALIZE SESSION STATES
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {}
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = None
if "ticker_raw_name" not in st.session_state:
    st.session_state.ticker_raw_name = None
if "ai_analysis_result" not in st.session_state:
    st.session_state.ai_analysis_result = None
if "live_prices" not in st.session_state:
    st.session_state.live_prices = {}

if "custom_tickers" not in st.session_state:
    st.session_state.custom_tickers = [
        "SUZLON.NS", "IRFC.NS", "ZOMATO.NS", "PNB.NS", "GMRINFRA.NS",
        "IDEA.NS", "YESBANK.NS", "JPPOWER.NS", "RVNL.NS", "TATAPOWER.NS",
        "NHPC.NS", "SJVN.NS", "NBCC.NS", "HUDCO.NS", "IOC.NS",
        "SAIL.NS", "GAIL.NS", "IFCI.NS", "BTC-USD", "ETH-USD"
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
                
        ticker_to_remove = st.selectbox("Select Asset to Remove:", ["None"] + st.session_state.custom_tickers)
        if ticker_to_remove != "None" and st.button("❌ Terminate Asset"):
            st.session_state.custom_tickers.remove(ticker_to_remove)
            st.rerun()
    elif admin_pin != "":
        st.error("🔒 Incorrect Pin.")
    st.markdown("---")

# 🎛️ INJECTING STYLE BLOCK
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
        box-shadow: 0 4px 12px rgba(234, 88, 12, 0.05) !important;
    }}
    .price-text {{ font-family: 'Courier New', Courier, monospace; font-size: 1.8rem !important; font-weight: bold; color: {price_color} !important; margin: 5px 0px; }}
    .stock-title {{ font-size: 1.2rem; font-weight: 600; color: {title_color} !important; }}
</style>
""", unsafe_allow_html=True)

tickers = st.session_state.custom_tickers

st.title("🚀 MarketMind AI Trading Terminal")
st.subheader("Live Budget Scanner with Phone Notification Engine")

@st.cache_data(ttl=30)
def fetch_trading_data(ticker_name):
    try:
        df = yf.download(ticker_name, period="1mo", interval="15m", auto_adjust=True, progress=False)
        if not df.empty:
            df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
        return df
    except:
        return None

# 🚨 AUTO-SCANNER FRAGMENT
@st.fragment(run_every=15)
def live_alert_scanner():
    st.markdown("### 🚦 Immediate AI Whistleblower (Live Alerts)")
    buy_list = []
    exit_list = []
    
    for ticker in tickers:
        df = yf.download(ticker, period="1d", interval="1m", auto_adjust=True, progress=False)
        if not df.empty:
            latest_time = df.index[-1]
            current_time = pd.Timestamp.now(tz=latest_time.tz)
            time_diff_minutes = (current_time - latest_time).total_seconds() / 60
            
            close_series = df['Close'].squeeze()
            current_price = float(close_series.iloc[-1])
            prev_price = float(close_series.iloc[-2]) if len(close_series) > 1 else current_price
            price_change = ((current_price - prev_price) / prev_price) * 100
            clean_name = ticker.replace(".NS", "")
            
            st.session_state.live_prices[ticker] = {"price": current_price, "change": price_change, "status": "STABLE"}
            
            if time_diff_minutes < 15:
                if price_change > 0.12:
                    st.success(f"🔥 **IMMEDIATE BUY ALERT:** {clean_name} (+{price_change:.2f}%)")
                    st.session_state.live_prices[ticker]["status"] = "BUY"
                    buy_list.append(ticker)
                elif price_change < -0.12:
                    st.error(f"⚠️ **IMMEDIATE EXIT ALERT:** {clean_name} ({price_change:.2f}%)")
                    st.session_state.live_prices[ticker]["status"] = "EXIT"
                    exit_list.append(ticker)
                
    if not buy_list and not exit_list:
        st.info("🔄 Scanner is waiting for Live Market or Data Stream is Paused (Market Closed).")

live_alert_scanner()
st.markdown("---")

st.markdown("### 🔍 Intelligent Asset Filter")
filter_choice = st.radio("Filter Dashboard Assets By:", ["Show All Active Assets", "🔥 Show Only BUY Alerts", "⚠️ Show Only EXIT Alerts"], horizontal=True)

filtered_tickers = tickers
if filter_choice == "🔥 Show Only BUY Alerts":
    filtered_tickers = [t for t in tickers if st.session_state.live_prices.get(t, {}).get("status") == "BUY"]
elif filter_choice == "⚠️ Show Only EXIT Alerts":
    filtered_tickers = [t for t in tickers if st.session_state.live_prices.get(t, {}).get("status") == "EXIT"]

if not filtered_tickers:
    st.info("No stocks match this filter criteria right now.")
else:
    cols = st.columns(4)
    for i, ticker in enumerate(filtered_tickers):
        with cols[i % 4]:
            data_df = fetch_trading_data(ticker)
            if data_df is not None and not data_df.empty:
                try:
                    close_series = data_df['Close'].squeeze()
                    latest_price = float(close_series.iloc[-1])
                    symbol = "$" if "USD" in ticker else "₹"
                    clean_name = ticker.replace(".NS", "")
                    
                    if ticker not in st.session_state.live_prices:
                        st.session_state.live_prices[ticker] = {"price": latest_price, "change": 0.0, "status": "STABLE"}
                    
                    with st.container(border=True):
                        st.markdown(f"<div class='stock-title'>{clean_name}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='price-text'>{symbol}{latest_price:,.2f}</div>", unsafe_allow_html=True)
                        
                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            if st.button(f"Scan 🎯", key=f"scan_{ticker}", use_container_width=True):
                                st.session_state.selected_ticker = clean_name
                                st.session_state.ticker_raw_name = ticker
                                with st.spinner("AI analyzing..."):
                                    st.session_state.ai_analysis_result = None
                                    try:
                                        recent_data = data_df.tail(10)[['Close', 'High', 'Low']].to_string()
                                        ema_now = float(data_df['EMA_20'].iloc[-1])
                                        prompt = f"Analyze this asset for short term trading: {clean_name}. Current Price: {latest_price}, EMA_20: {ema_now:.2f}. Data: {recent_data}. Provide clear buy/sell signal and entry zones."
                                        model = genai.GenerativeModel('models/gemini-2.5-flash')
                                        st.session_state.ai_analysis_result = model.generate_content(prompt).text
                                    except Exception as e:
                                        st.session_state.ai_analysis_result = f"Failed to generate strategy: {str(e)}"
                        with btn_col2:
                            if st.button(f"Sim Buy 🛍️", key=f"sim_{ticker}", use_container_width=True):
                                st.session_state.portfolio[ticker] = {"buy_price": latest_price, "qty": 100}
                                st.toast(f"Added 100 shares of {clean_name} to Practice Portfolio!", icon="💰")
                                st.rerun()
                except Exception as e:
                    st.error(f"Error handling {ticker}")

# 💰 VIRTUAL PORTFOLIO SIMULATOR SIDEBAR DESK
with st.sidebar:
    st.markdown("## 💰 Live Practice Portfolio")
    st.markdown("---")
    if st.session_state.portfolio:
        for p_ticker, p_data in list(st.session_state.portfolio.items()):
            live_p = st.session_state.live_prices.get(p_ticker, {}).get("price", p_data["buy_price"])
            current_pnl = (live_p - p_data["buy_price"]) * p_data["qty"]
            color = "#10b981" if current_pnl >= 0 else "#ef4444"
            
            with st.container(border=True):
                st.markdown(f"### {p_ticker.replace('.NS','')}")
                st.markdown(f"Qty: **{p_data['qty']}** | Avg: **{p_data['buy_price']:.2f}**")
                st.markdown(f"Current: **{live_p:.2f}**")
                st.markdown(f"P&L: <span style='color:{color}; font-weight:bold;'>₹{current_pnl:.2f}</span>", unsafe_allow_html=True)
                
                # 📲 TELEGRAM PUSH FOR INDIVIDUAL SQUARE OFF
                if st.button(f"Square Off ❌", key=f"sell_{p_ticker}", use_container_width=True):
                    tg_msg = f"🚨 *SQUARE OFF ALERT* 🚨\n\nAsset: {p_ticker.replace('.NS','')}\nExit Price: {live_p:.2f}\nFinal P&L: ₹{current_pnl:.2f}\n\nPosition Closed Successfully!"
                    send_telegram_notification(tg_msg)
                    del st.session_state.portfolio[p_ticker]
                    st.rerun()
    else:
        st.info("No active simulator positions.")

# Charts & Signals Execution Desk
if st.session_state.selected_ticker and st.session_state.ai_analysis_result:
    st.markdown("---")
    st.subheader(f"⚡ Live Quant Execution Desk: {st.session_state.selected_ticker}")
    chart_col, signal_col = st.columns([3, 2])
    
    with chart_col:
        raw_df = fetch_trading_data(st.session_state.ticker_raw_name)
        if raw_df is not None and not raw_df.empty:
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=raw_df.index, open=raw_df['Open'].squeeze(), high=raw_df['High'].squeeze(),
                low=raw_df['Low'].squeeze(), close=raw_df['Close'].squeeze(), name='Price Action'
            ))
            fig.add_trace(go.Scatter(x=raw_df.index, y=raw_df['EMA_20'].squeeze(), line=dict(color='#f97316', width=2), name='20 EMA Trend'))
            fig.update_layout(xaxis_rangeslider_visible=False, height=420, template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            
    with signal_col:
        with st.container(border=True):
            st.markdown("### 🤖 Executable AI Strategy")
            st.markdown(st.session_state.ai_analysis_result)
            st.markdown("---")
            
            # 🔥 MANUAL TELEGRAM SIGNAL TRIGGER BUTTON
            if st.button("📲 Send Signal Alert to Phone", use_container_width=True):
                with st.spinner("Sending alert..."):
                    clean_tg_text = f"🎯 *MARKETMIND QUANT SIGNAL* 🎯\n\nAsset: {st.session_state.selected_ticker}\n\n{st.session_state.ai_analysis_result}"
                    success, error_msg = send_telegram_notification(clean_tg_text)
                    if success:
                        st.success("🚀 Alert sent to your phone Telegram app!")
                    else:
                        st.error(f"Failed to send: {error_msg}. Check Secrets configuration.")
