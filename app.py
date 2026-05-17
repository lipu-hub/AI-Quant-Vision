import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai

st.set_page_config(layout="wide")

# 🔐 Streamlit Secrets se Gemini API configure karna
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.sidebar.warning("⚠️ Please configure GEMINI_API_KEY in Streamlit Secrets.")

# 1. Tickers List
tickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "LICI.NS", "BTC-USD", "ETH-USD"]

st.title("🚀 MarketMind AI Terminal")
st.subheader("Market Overview")

# 2. Single Ticker Fetching Function
@st.cache_data(ttl=60)
def fetch_single_ticker(ticker_name):
    try:
        df = yf.download(ticker_name, period="1mo", interval="1d", auto_adjust=True, progress=False)
        return df
    except Exception as e:
        return None

# 🧠 Gemini AI Analysis Logic
def generate_ai_analysis(ticker_name, df, current_price):
    try:
        recent_data = df.tail(5)[['Close', 'High', 'Low']].to_string()
        
        prompt = f"""
        You are an elite quantitative trading assistant. Analyze the market data for {ticker_name}.
        Current Closing Price: {current_price}
        
        Recent 5-day OHLC snippet:
        {recent_data}
        
        Provide a concise, professional technical analysis markdown report:
        1. **Market Sentiment**: Bullish/Bearish/Neutral with brief reasoning.
        2. **Key Levels**: Crucial Support and Resistance zones based on recent data.
        3. **Actionable Insight**: One line takeaway for short term traders.
        Keep it direct, professional, and do not include financial advice disclaimers.
        """
        
        # 🛠️ FIX: Using the production-ready alias name that bypasses v1beta 404 errors
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Generation Failed: {str(e)}"

# Session State Initialize
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = None
if "ai_analysis_result" not in st.session_state:
    st.session_state.ai_analysis_result = None

# 3. Grid Layout (4 Columns)
cols = st.columns(4)

for i, ticker in enumerate(tickers):
    with cols[i % 4]:
        data_df = fetch_single_ticker(ticker)
        
        if data_df is not None and not data_df.empty:
            try:
                close_series = data_df['Close'].squeeze()
                latest_price = float(close_series.iloc[-1])
                
                symbol = "$" if "USD" in ticker else "₹"
                clean_name = ticker.replace(".NS", "")
                display_name = "LIC" if clean_name == "LICI" else clean_name
                
                # UI Card Design
                with st.container(border=True):
                    st.markdown(f"### {display_name}")
                    st.markdown(f"# {symbol}{latest_price:,.2f}")
                    
                    # Gemini AI Trigger Button
                    if st.button(f"Analyze {display_name}", key=ticker):
                        st.session_state.selected_ticker = display_name
                        with st.spinner(f"AI is calculating patterns for {display_name}..."):
                            analysis = generate_ai_analysis(ticker, data_df, latest_price)
                            st.session_state.ai_analysis_result = analysis
                        
            except Exception as e:
                st.error(f"Error parsing price for {ticker}")
        else:
            st.error(f"Data not available for {ticker}")

# 4. Display AI insights below the grid dashboard
if st.session_state.selected_ticker and st.session_state.ai_analysis_result:
    st.markdown("---")
    st.subheader(f"🧠 Deep Quant Insights: {st.session_state.selected_ticker}")
    with st.container(border=True):
        st.markdown(st.session_state.ai_analysis_result)
