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

# 💸 BUDGET-FRIENDLY TICKERS LIST FOR EVERYONE
tickers = ["SUZLON.NS", "IRFC.NS", "ZOMATO.NS", "PNB.NS", "GMRINFRA.NS", "BTC-USD", "ETH-USD"]

st.title("🚀 MarketMind AI Trading Terminal")
st.subheader("Live Budget Market Scanner & Immediate Alerts")

@st.cache_data(ttl=30)
def fetch_trading_data(ticker_name):
    try:
        df = yf.download(ticker_name, period="1mo", interval="15m", auto_adjust=True, progress=False)
        if not df.empty:
            df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
        return df
    except Exception as e:
        return None

# 🚨 DYNAMIC LIVE SCANNER FRAGMENT
@st.fragment(run_every=15)
def live_alert_scanner():
    st.markdown("### 🚦 Immediate AI Whistleblower (Live Alerts)")
    alert_triggered = False
    
    for ticker in tickers:
        df = yf.download(ticker, period="1d", interval="1m", auto_adjust=True, progress=False)
        if not df.empty:
            close_series = df['Close'].squeeze()
            current_price = float(close_series.iloc[-1])
            prev_price = float(close_series.iloc[-2]) if len(close_series) > 1 else current_price
            
            clean_name = ticker.replace(".NS", "")
            price_change = ((current_price - prev_price) / prev_price) * 100
            
            # Algorithmic Spike Detection
            if price_change > 0.15:
                st.toast(f"🔥 ALERT: Buy Momentum in {clean_name}!", icon="🚀")
                st.success(f"🚨 **IMMEDIATE BUY ALERT:** {clean_name} is spiking up! Current Price: {current_price:.2f} (+{price_change:.2f}%)")
                alert_triggered = True
            elif price_change < -0.15:
                st.toast(f"⚠️ ALERT: Exit/Short {clean_name} immediately!", icon="💥")
                st.error(f"⚠️ **IMMEDIATE EXIT ALERT:** {clean_name} is dropping fast! Dump/Exit now! Current Price: {current_price:.2f} ({price_change:.2f}%)")
                alert_triggered = True
                
    if not alert_triggered:
        st.info("🔄 Scanning 1-minute order flows... Markets are stable. No immediate breakout alerts right now.")

# Render Live Scanner
live_alert_scanner()
st.markdown("---")

# Session State Initialize
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = None
if "ai_analysis_result" not in st.session_state:
    st.session_state.ai_analysis_result = None
if "ticker_raw_name" not in st.session_state:
    st.session_state.ticker_raw_name = None

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
        3. 🔍 **QUANTS RATIONALE**: Focus on low-budget retail traders setup. Why this trade makes sense. Do not include financial advice disclaimers.
        """
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Signal Generation Failed: {str(e)}"

# Grid Interface Layout
cols = st.columns(4)
for i, ticker in enumerate(tickers):
    with cols[i % 4]:
        data_df = fetch_trading_data(ticker)
        
        if data_df is not None and not data_df.empty:
            try:
                close_series = data_df['Close'].squeeze()
                latest_price = float(close_series.iloc[-1])
                
                symbol = "$" if "USD" in ticker else "₹"
                clean_name = ticker.replace(".NS", "")
                display_name = clean_name
                
                with st.container(border=True):
                    st.markdown(f"### {display_name}")
                    st.markdown(f"# {symbol}{latest_price:,.2f}")
                    
                    if st.button(f"Generate Signal 🎯", key=ticker):
                        st.session_state.selected_ticker = display_name
                        st.session_state.ticker_raw_name = ticker
                        with st.spinner(f"Scanning market algorithms for {display_name}..."):
                            analysis = generate_quant_signals(ticker, data_df, latest_price)
                            st.session_state.ai_analysis_result = analysis
                        
            except Exception as e:
                st.error(f"Error handling ticker {ticker}")

# Display Interactive Technical Charts & Signals dynamically below
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
            fig.update_layout(title=f"{st.session_state.selected_ticker} Technical Chart", xaxis_rangeslider_visible=False, height=450, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            
    with signal_col:
        with st.container(border=True):
            st.markdown("### 🤖 Executable AI Strategy")
            st.markdown(st.session_state.ai_analysis_result)
