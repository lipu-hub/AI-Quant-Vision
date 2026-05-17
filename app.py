import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# 🔐 Streamlit Secrets Verification
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.sidebar.warning("⚠️ Please configure GEMINI_API_KEY in Streamlit Secrets.")

tickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "LICI.NS", "BTC-USD", "ETH-USD"]

st.title("🚀 MarketMind AI Trading Terminal")
st.subheader("Live Market Scanner & Core Signals")

@st.cache_data(ttl=60)
def fetch_trading_data(ticker_name):
    try:
        # Fetching 3 months data for dynamic technical indicators
        df = yf.download(ticker_name, period="3mo", interval="1d", auto_adjust=True, progress=False)
        if not df.empty:
            # 📈 20-Day EMA Trend Line Calculation
            df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
        return df
    except Exception as e:
        return None

def generate_quant_signals(ticker_name, df, current_price):
    try:
        recent_data = df.tail(10)[['Close', 'High', 'Low']].to_string()
        ema_now = df['EMA_20'].iloc[-1]
        
        prompt = f"""
        You are an elite quantitative trading hedge-fund manager. Analyze this asset for Swing/Daily Trading: {ticker_name}.
        Current Market Price: {current_price}
        20-Day EMA Value: {ema_now:.2f}
        
        Recent 10-day market movement:
        {recent_data}
        
        Provide a strategic trading action block in clean markdown formatting:
        1. 🚦 **TRADING SIGNAL**: Clear (STRONG BUY / BUY / HOLD / SELL) based on context.
        2. 🎯 **MATHEMATICAL TARGETS**: Provide an entry zone, Target 1, Target 2, and a strict Stop-Loss (SL) level.
        3. 🔍 **QUANTS RATIONALE**: Why this trade makes sense for short-term profit in 2-3 sentences max.
        Keep it highly analytical, direct, and focused on making a profitable trade execution. Do not include boring statutory disclaimers.
        """
        
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Signal Generation Failed: {str(e)}"

if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = None
if "ai_analysis_result" not in st.session_state:
    st.session_state.ai_analysis_result = None
if "ticker_raw_name" not in st.session_state:
    st.session_state.ticker_raw_name = None

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
                display_name = "LIC" if clean_name == "LICI" else clean_name
                
                with st.container(border=True):
                    st.markdown(f"### {display_name}")
                    st.markdown(f"# {symbol}{latest_price:,.2f}")
                    
                    if st.button(f"Generate Signal 🎯", key=ticker):
                        st.session_state.selected_ticker = display_name
                        st.session_state.ticker_raw_name = ticker
                        with St.spinner(f"Scanning market algorithms for {display_name}..."):
                            analysis = generate_quant_signals(ticker, data_df, latest_price)
                            st.session_state.ai_analysis_result = analysis
                        
            except Exception as e:
                st.error(f"Error handling ticker {ticker}")

# Display Interactive Technical Charts & Signals dynamically below
if st.session_state.selected_ticker and st.session_state.ai_analysis_result:
    st.markdown("---")
    st.subheader(f"⚡ Live Quant Execution Desk: {st.session_state.selected_ticker}")
    
    chart_col, signal_col = st.columns([3, 2])
    
    # Left Column: Interactive Candlestick Chart + Technical Indicators
    with chart_col:
        raw_df = fetch_trading_data(st.session_state.ticker_raw_name)
        if raw_df is not None:
            fig = go.Figure()
            # Candlesticks
            fig.add_trace(go.Candlestick(
                x=raw_df.index, open=raw_df['Open'], high=raw_df['High'],
                low=raw_df['Low'], close=raw_df['Close'], name='Price Action'
            ))
            # EMA Overlay Line
            fig.add_trace(go.Scatter(
                x=raw_df.index, y=raw_df['EMA_20'], line=dict(color='orange', width=1.5), name='20 EMA Trend'
            ))
            fig.update_layout(title=f"{st.session_state.selected_ticker} Technical Chart", xaxis_rangeslider_visible=False, height=450)
            st.plotly_chart(fig, use_container_width=True)
            
    # Right Column: AI Target, Entry & Stop-Loss Signals
    with signal_col:
        with st.container(border=True):
            st.markdown("### 🤖 Executable AI Strategy")
            st.markdown(st.session_state.ai_analysis_result)
