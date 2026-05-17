import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai
import plotly.graph_objects as go
import time

st.set_page_config(layout="wide")

# 🔐 Streamlit Secrets Verification
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.sidebar.warning("⚠️ Please configure GEMINI_API_KEY in Streamlit Secrets.")

tickers = [
    "SUZLON.NS", "IRFC.NS", "ZOMATO.NS", "PNB.NS", "GMRINFRA.NS",
    "IDEA.NS", "YESBANK.NS", "JPPOWER.NS", "RVNL.NS", "TATAPOWER.NS",
    "NHPC.NS", "SJVN.NS", "NBCC.NS", "HUDCO.NS", "IOC.NS",
    "SAIL.NS", "GAIL.NS", "IFCI.NS", "BTC-USD", "ETH-USD"
]

st.title("🚀 MarketMind AI Trading Terminal")
st.subheader("Live 20-Asset Budget Scanner with Simulator & Filters")

# Initialize Session States for Portfolio
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {}
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = None
if "ai_analysis_result" not in st.session_state:
    st.session_state.ai_analysis_result = None
if "ticker_raw_name" not in st.session_state:
    st.session_state.ticker_raw_name = None

@st.cache_data(ttl=30)
def fetch_trading_data(ticker_name):
    try:
        df = yf.download(ticker_name, period="1mo", interval="15m", auto_adjust=True, progress=False)
        if not df.empty:
            df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
        return df
    except Exception as e:
        return None

# Dictionary to hold states for filters
live_status = {}

# 🚨 AUTO-SCANNER FRAGMENT WITH FILTER CAPABILITY
@st.fragment(run_every=15)
def live_alert_scanner():
    st.markdown("### 🚦 Immediate AI Whistleblower (Live Alerts)")
    buy_list = []
    exit_list = []
    
    for ticker in tickers:
        df = yf.download(ticker, period="1d", interval="1m", auto_adjust=True, progress=False)
        if not df.empty:
            close_series = df['Close'].squeeze()
            current_price = float(close_series.iloc[-1])
            prev_price = float(close_series.iloc[-2]) if len(close_series) > 1 else current_price
            
            clean_name = ticker.replace(".NS", "")
            price_change = ((current_price - prev_price) / prev_price) * 100
            
            # Store values for filtering and live tracking
            live_status[ticker] = {"price": current_price, "change": price_change, "status": "STABLE"}
            
            if price_change > 0.12:
                st.success(f"🚨 **IMMEDIATE BUY ALERT:** {clean_name} is spiking up! Price: {current_price:.2f} (+{price_change:.2f}%)")
                live_status[ticker]["status"] = "BUY"
                buy_list.append(ticker)
            elif price_change < -0.12:
                st.error(f"⚠️ **IMMEDIATE EXIT ALERT:** {clean_name} is dropping fast! Dump/Exit now! Price: {current_price:.2f} ({price_change:.2f}%)")
                live_status[ticker]["status"] = "EXIT"
                exit_list.append(ticker)
                
    if not buy_list and not exit_list:
        st.info("🔄 Scanning 1-minute order blocks... Penny assets are stable. No massive volatility alerts right now.")
    
    return live_status

current_market_snapshot = live_alert_scanner()
st.markdown("---")

# 🚦 SMART FILTER BUTTONS INTERFACE
st.markdown("### 🔍 Intelligent Asset Filter")
filter_choice = st.radio("Filter Dashboard Assets By:", ["Show All 20 Assets", "🔥 Show Only BUY Alerts", "⚠️ Show Only EXIT Alerts"], horizontal=True)

# 💰 VIRTUAL PORTFOLIO SIMULATOR DESK
st.markdown("---")
st.markdown("### 💰 Live Practice Simulator Portfolio (Fake Money)")
if st.session_state.portfolio:
    p_cols = st.columns(len(st.session_state.portfolio.keys()))
    for idx, (p_ticker, p_data) in enumerate(st.session_state.portfolio.items()):
        # Calculate current dynamic price
        live_p = current_market_snapshot.get(p_ticker, {}).get("price", p_data["buy_price"])
        current_pnl = (live_p - p_data["buy_price"]) * p_data["qty"]
        color = "green" if current_pnl >= 0 else "red"
        
        with st.sidebar: # Keep positions visual in a clean sidebar desk
            st.markdown(f"**📈 {p_ticker.replace('.NS','')} Position**")
            st.markdown(f"Qty: {p_data['qty']} | Avg: {p_data['buy_price']:.2f}")
            st.markdown(f"Current: {live_p:.2f} | P&L: <span style='color:{color}; font-weight:bold;'>₹{current_pnl:.2f}</span>", unsafe_allow_html=True)
            if st.button(f"Square Off ❌", key=f"sell_{p_ticker}"):
                del st.session_state.portfolio[p_ticker]
                st.rerun()

def generate_quant_signals(ticker_name, df, current_price):
    try:
        recent_data = df.tail(10)[['Close', 'High', 'Low']].to_string()
        ema_now = float(df['EMA_20'].iloc[-1])
        prompt = f"""
        You are an elite quantitative trading hedge-fund manager. Analyze this budget asset for Short-term/Daily Trading: {ticker_name}.
        Current Market Price: {current_price}
        20-Day EMA Value: {ema_now:.2f}
        Recent 10-day market movement:
        {recent_data}
        Provide a strategic trading action block in clean markdown formatting:
        1. 🚦 **TRADING SIGNAL**: Clear (STRONG BUY / BUY / HOLD / SELL).
        2. 🎯 **MATHEMATICAL TARGETS**: Provide an entry zone, Target 1, Target 2, and a strict Stop-Loss (SL) level.
        3. 🔍 **QUANTS RATIONALE**: Focus on retail traders setup. Why this trade makes sense.
        """
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Signal Generation Failed: {str(e)}"

# Filter tickers based on user radio button selection
filtered_tickers = tickers
if filter_choice == "🔥 Show Only BUY Alerts":
    filtered_tickers = [t for t in tickers if current_market_snapshot.get(t, {}).get("status") == "BUY"]
elif filter_choice == "⚠️ Show Only EXIT Alerts":
    filtered_tickers = [t for t in tickers if current_market_snapshot.get(t, {}).get("status") == "EXIT"]

# Grid Interface Layout
if not filtered_tickers:
    st.info("No stocks match this filter criteria right now. Check back during active movements!")
else:
    cols = st.columns(5)
    for i, ticker in enumerate(filtered_tickers):
        with cols[i % 5]:
            data_df = fetch_trading_data(ticker)
            if data_df is not None and not data_df.empty:
                try:
                    close_series = data_df['Close'].squeeze()
                    latest_price = float(close_series.iloc[-1])
                    symbol = "$" if "USD" in ticker else "₹"
                    clean_name = ticker.replace(".NS", "")
                    
                    with st.container(border=True):
                        st.markdown(f"### {clean_name}")
                        st.markdown(f"## {symbol}{latest_price:,.2f}")
                        
                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            if st.button(f"Scan 🎯", key=f"scan_{ticker}"):
                                st.session_state.selected_ticker = clean_name
                                st.session_state.ticker_raw_name = ticker
                                with st.spinner("AI calculating..."):
                                    st.session_state.ai_analysis_result = generate_quant_signals(ticker, data_df, latest_price)
                        with btn_col2:
                            if st.button(f"Sim Buy 🛍️", key=f"sim_{ticker}"):
                                st.session_state.portfolio[ticker] = {"buy_price": latest_price, "qty": 100}
                                st.toast(f"Added 100 shares of {clean_name} to Simulator!", icon="💰")
                                st.rerun()
                except Exception as e:
                    st.error(f"Error handling {ticker}")

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
            fig.add_trace(go.Scatter(
                x=raw_df.index, y=raw_df['EMA_20'].squeeze(), line=dict(color='orange', width=2), name='20 EMA Trend'
            ))
            fig.update_layout(xaxis_rangeslider_visible=False, height=400, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            
    with signal_col:
        with st.container(border=True):
            st.markdown("### 🤖 Executable AI Strategy")
            st.markdown(st.session_state.ai_analysis_result)
