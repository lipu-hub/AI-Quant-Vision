import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="MarketMind AI - Pro", layout="wide")

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["🏠 Market Overview", "🏆 Top Movers"])

# Common Stock List
stocks_list = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", 
    "BHARTIARTL.NS", "SBIN.NS", "LICI.NS", "ITC.NS", "HINDUNILVR.NS",
    "LT.NS", "BAJFINANCE.NS", "TATAMOTORS.NS", "M&M.NS", "ADANIENT.NS",
    "SUNPHARMA.NS", "ASIANPAINT.NS", "TITAN.NS", "ZOMATO.NS", "NTPC.NS",
    "KOTAKBANK.NS", "AXISBANK.NS", "BTC-USD", "ETH-USD"
]

# Function to get data (cached for speed)
@st.cache_data(ttl=600)
def get_market_data(stocks):
    data_list = []
    for s in stocks:
        try:
            t = yf.Ticker(s)
            df = t.history(period="7d")
            if not df.empty:
                curr = df['Close'].iloc[-1]
                prev = df['Close'].iloc[-2]
                p_chg = ((curr - prev) / prev) * 100
                data_list.append({'Symbol': s, 'Price': round(curr, 2), 'Change %': round(p_chg, 2), 'History': df})
        except: continue
    return data_list

market_data = get_market_data(stocks_list)

# --- PAGE 1: MARKET OVERVIEW ---
if page == "🏠 Market Overview":
    st.title("📊 Market Overview")
    st.markdown("""<style>.compact-card { background: #1e2130; padding: 10px; border-radius: 10px; border-top: 3px solid #444; margin-bottom: 2px; } .price-text { font-size: 1.1rem; font-weight: bold; }</style>""", unsafe_allow_html=True)
    
    for i in range(0, len(market_data), 5):
        cols = st.columns(5)
        for j in range(5):
            if i + j < len(market_data):
                item = market_data[i + j]
                color = "#00ff88" if item['Change %'] >= 0 else "#ff4b4b"
                with cols[j]:
                    st.markdown(f"""<div class="compact-card" style="border-top-color: {color};">
                        <div style="color:#aaa; font-weight:bold;">{item['Symbol'].replace('.NS','')}</div>
                        <div class="price-text">{item['Price']} <span style="font-size:0.7rem; color:{color};">({item['Change %']}%)</span></div>
                    </div>""", unsafe_allow_html=True)
                    # Small Graph
                    fig = go.Figure(go.Scatter(x=item['History'].index, y=item['History']['Close'], mode='lines', line=dict(color=color, width=1.5)))
                    fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=40, xaxis=dict(visible=False), yaxis=dict(visible=False), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# --- PAGE 2: TOP MOVERS ---
elif page == "🏆 Top Movers":
    st.title("🏆 Today's Top Movers")
    
    # Sort data for gainers and losers
    df_movers = pd.DataFrame(market_data).sort_values(by='Change %', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚀 Top Gainers")
        for _, row in df_movers.head(5).iterrows():
            st.success(f"**{row['Symbol'].replace('.NS','')}**: {row['Price']} (+{row['Change %']}%)")
            
    with col2:
        st.subheader("📉 Top Losers")
        for _, row in df_movers.tail(5).sort_values(by='Change %').iterrows():
            st.error(f"**{row['Symbol'].replace('.NS','')}**: {row['Price']} ({row['Change %']}%)")

    st.info("Signals are updated every 10 minutes based on NSE live data.")
