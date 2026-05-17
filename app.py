import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(layout="wide")

# 1. Ticker list jisme LIC (LICI.NS) ko add kar diya hai
tickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "LICI.NS", "BTC-USD", "ETH-USD"]

st.title("🚀 MarketMind AI Terminal")
st.subheader("Market Overview")

# 2. Data fetching function with caching
@st.cache_data(ttl=60)
def fetch_market_data(ticker_list):
    # auto_adjust=True se exact adjusted close price milta hai
    df = yf.download(ticker_list, period="5d", interval="1d", auto_adjust=True)
    return df

try:
    data_df = fetch_market_data(tickers)
    
    # 3. Responsive Grid Layout (4 Columns)
    cols = st.columns(4)
    
    for i, ticker in enumerate(tickers):
        with cols[i % 4]:
            try:
                # MultiIndex DataFrame se safely specific ticker ka close price nikalna
                if isinstance(data_df['Close'], pd.DataFrame):
                    ticker_data = data_df['Close'][ticker].dropna()
                else:
                    ticker_data = data_df['Close'].dropna()
                
                # Latest close price extraction
                latest_price = float(ticker_data.iloc[-1])
                
                # Currency check (INR for Indian stocks, USD for Crypto)
                symbol = "$" if "USD" in ticker else "₹"
                clean_name = ticker.replace(".NS", "")
                
                # Beautiful Bordered UI Card
                with st.container(border=True):
                    st.markdown(f"### {clean_name}")
                    st.markdown(f"# {symbol}{latest_price:,.2f}")
                    
                    # Interactivity Button for Gemini AI
                    if st.button(f"Analyze {clean_name}", key=ticker):
                        st.session_state.selected_ticker = ticker
                        st.success(f"Analyzing {clean_name} with Gemini AI...")
                        
            except Exception as e:
                st.error(f"Error parsing {ticker}")

except Exception as e:
    st.error(f"Data fetch fail ho gaya: {e}")
