import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(layout="wide")

# 1. Tickers List (LIC Included)
tickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "LICI.NS", "BTC-USD", "ETH-USD"]

st.title("🚀 MarketMind AI Terminal")
st.subheader("Market Overview")

# 2. Single Ticker Fetching Function
@st.cache_data(ttl=60)
def fetch_single_ticker(ticker_name):
    try:
        # 1mo data for AI and Forecasting consistency
        df = yf.download(ticker_name, period="1mo", interval="1d", auto_adjust=True, progress=False)
        return df
    except Exception as e:
        return None

# 3. Responsive Grid Layout (4 Columns)
cols = st.columns(4)

for i, ticker in enumerate(tickers):
    with cols[i % 4]:
        data_df = fetch_single_ticker(ticker)
        
        if data_df is not None and not data_df.empty:
            try:
                # 🛠️ FIX: Safely extracting the exact last price as a single number
                close_series = data_df['Close'].squeeze()
                latest_price = float(close_series.iloc[-1])
                
                # Currency check
                symbol = "$" if "USD" in ticker else "₹"
                clean_name = ticker.replace(".NS", "")
                
                # UI Card Design
                with st.container(border=True):
                    st.markdown(f"### {clean_name}")
                    st.markdown(f"# {symbol}{latest_price:,.2f}")
                    
                    # Gemini AI Trigger Button
                    if st.button(f"Analyze {clean_name}", key=ticker):
                        st.session_state.selected_ticker = ticker
                        st.success(f"Analyzing {clean_name} with Gemini AI...")
                        
            except Exception as e:
                st.error(f"Error parsing price for {ticker}")
        else:
            st.error(f"Data not available for {ticker}")
