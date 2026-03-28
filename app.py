import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import requests

# 1. Page Configuration
st.set_page_config(page_title="MarketMind AI - Pro Terminal", layout="wide")

# 2. Auto-Refresh (Updates every 60 seconds)
st_autorefresh(interval=60 * 1000, key="datarefresh")

# 3. Telegram Config (Replace with your real details)
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN_HERE"
CHAT_ID = "YOUR_CHAT_ID_HERE"

def send_telegram_msg(message):
    if TELEGRAM_TOKEN != "YOUR_BOT_TOKEN_HERE":
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
        try:
            requests.get(url)
        except:
            pass

# 4. Premium CSS Styling
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .compact-card {
        background: #1e2130;
        padding: 12px;
        border-radius: 10px;
        border-top: 3px solid #444;
        margin-bottom: 5px;
    }
    .stock-symbol { font-size: 0.9rem; font-weight: bold; color: #aaa; margin-bottom: 2px; }
    .price-text { font-size: 1.1rem; font-weight: bold; margin: 2px 0; }
    .pnl-text { font-size: 0.75rem; font-weight: bold; margin-top: 5px; }
    [data-testid="stSidebar"] { background-color: #161925; }
</style>
""", unsafe_allow_html=True)

# 5. Sidebar Navigation & Portfolio
st.sidebar.title("🚀 Terminal Menu")
page = st.sidebar.radio("Navigate", ["🏠 Market Overview", "🏆 Top Movers"])

st.sidebar.markdown("---")
st.sidebar.subheader("💰 My Holdings")
stocks_list = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", 
    "BHARTIARTL.NS", "SBIN.NS", "LICI.NS", "ITC.NS", "HINDUNILVR.NS",
    "LT.NS", "BAJFINANCE.NS", "TATAMOTORS.NS", "M&M.NS", "ADANIENT.NS",
    "SUNPHARMA.NS", "ASIANPAINT.NS", "TITAN.NS", "ZOMATO.NS", "NTPC.NS",
    "KOTAKBANK.NS", "AXISBANK.NS", "BTC-USD", "ETH-USD"
]
my_stock = st.sidebar.selectbox("Select Stock", stocks_list)
buy_price = st.sidebar.number_input("Buying Price", value=0.0, step=0.1)

# 6. Data Fetching Logic (Cached for 10 mins)
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
                data_list.append({
                    'Symbol': s, 
                    'Price': round(curr, 2), 
                    'Change %': round(p_chg, 2), 
                    'History': df
                })
        except: continue
    return data_list

market_data = get_market_data(stocks_list)

# Alert Logic (Runs every refresh)
for item in market_data:
    if abs(item['Change %']) >= 3.0: # 3% movement alert
        alert_key = f"alert_sent_{item['Symbol']}_{datetime.now().strftime('%Y%m%d')}"
        if alert_key not in st.session_state:
            send_telegram_msg(f"🚨 ALERT: {item['Symbol']} move detected! \nPrice: {item['Price']} \nChange: {item['Change %']}%")
            st.session_state[alert_key] = True

# --- PAGE 1: MARKET OVERVIEW ---
if page == "🏠 Market Overview":
    st.title("📊 Live Market Terminal")
    st.caption(f"Tracking {len(stocks_list)} assets | Last Sync: {datetime.now().strftime('%H:%M:%S')} IST")
    
    for i in range(0, len(market_data), 5):
        cols = st.columns(5)
        for j in range(5):
            if i + j < len(market_data):
                item = market_data[i + j]
                color = "#00ff88" if item['Change %'] >= 0 else "#ff4b4b"
                
                with cols[j]:
                    pnl_html = ""
                    if item['Symbol'] == my_stock and buy_price > 0:
                        diff = round(item['Price'] - buy_price, 2)
                        p_color = "#00ff88" if diff >= 0 else "#ff4b4b"
                        pnl_html = f'<div class="pnl-text" style="color:{p_color};">P&L: {diff}</div>'

                    st.markdown(f"""
                    <div class="compact-card" style="border-top-color: {color};">
                        <div class="stock-symbol">{item['Symbol'].replace('.NS','')}</div>
                        <div class="price-text">{item['Price']} <span style="font-size:0.75rem; color:{color};">({item['Change %']}%)</span></div>
                        {pnl_html}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    fig = go.Figure(go.Scatter(x=item['History'].index, y=item['History']['Close'], mode='lines', line=dict(color=color, width=1.5), fill='tozeroy', fillcolor=f"rgba({ '0,255,136,0.05' if item['Change %'] >= 0 else '255,75,75,0.05' })"))
                    fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=45, xaxis=dict(visible=False), yaxis=dict(visible=False), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# --- PAGE 2: TOP MOVERS ---
elif page == "🏆 Top Movers":
    st.title("🏆 Market Leaders & Laggards")
    df_movers = pd.DataFrame(market_data).sort_values(by='Change %', ascending=False)
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🚀 Top 5 Gainers")
        for _, row in df_movers.head(5).iterrows():
            st.success(f"**{row['Symbol'].replace('.NS','')}** | {row['Price']} | **+{row['Change %']}%**")
    with c2:
        st.subheader("📉 Top 5 Losers")
        for _, row in df_movers.tail(5).sort_values(by='Change %').iterrows():
            st.error(f"**{row['Symbol'].replace('.NS','')}** | {row['Price']} | **{row['Change %']}%**")
