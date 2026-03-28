import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import requests

# 1. Page Configuration
st.set_page_config(page_title="MarketMind AI - Pro Terminal", layout="wide")

# 2. Auto-Refresh
st_autorefresh(interval=60 * 1000, key="datarefresh")

# 3. Session State for Navigation (Taki page switch ho sake)
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'grid'
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = None

# 4. Telegram Config
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN_HERE" 
CHAT_ID = "8546128135"

def send_telegram_msg(message):
    if TELEGRAM_TOKEN != "YOUR_BOT_TOKEN_HERE":
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
        try: requests.get(url)
        except: pass

# 5. Prediction Engine (Advanced Logic)
def get_prediction_logic(symbol):
    try:
        data = yf.Ticker(symbol).history(period="60d") # Needs more data for RSI
        if len(data) < 20: return None
        
        curr = data['Close'].iloc[-1]
        # RSI Logic
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean().iloc[-1]
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().iloc[-1]
        rs = gain / (loss if loss != 0 else 0.1)
        rsi = 100 - (100 / (1 + rs))
        
        # Volatility based Target/Stoploss
        volatility = (data['High'] - data['Low']).tail(10).mean()
        
        return {
            "rsi": round(rsi, 2),
            "target": round(curr + (volatility * 1.5), 2),
            "stoploss": round(curr - (volatility * 1.2), 2),
            "verdict": "STRONG BUY 🚀" if rsi < 35 else "STRONG SELL 📉" if rsi > 65 else "HOLD ⚖️",
            "color": "#00ff88" if rsi < 50 else "#ff4b4b"
        }
    except: return None

# 6. CSS Styling
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .compact-card {
        background: #1e2130; padding: 12px; border-radius: 10px;
        border-top: 3px solid #444; margin-bottom: 5px;
    }
    .stock-symbol { font-size: 0.9rem; font-weight: bold; color: #aaa; }
    .price-text { font-size: 1.1rem; font-weight: bold; margin: 2px 0; }
    [data-testid="stSidebar"] { background-color: #161925; }
</style>
""", unsafe_allow_html=True)

# 7. Sidebar
st.sidebar.title("🚀 Terminal Menu")
main_page = st.sidebar.radio("Navigate", ["🏠 Market Overview", "🏆 Top Movers"])

# Sidebar Portfolio
st.sidebar.markdown("---")
stocks_list = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "BHARTIARTL.NS", "SBIN.NS", "TATAMOTORS.NS", "ZOMATO.NS", "BTC-USD", "ETH-USD"]
my_stock = st.sidebar.selectbox("Select Stock", stocks_list)
buy_price = st.sidebar.number_input("Buying Price", value=0.0, step=0.1)

# 8. Data Fetching
@st.cache_data(ttl=600)
def get_market_data(stocks):
    data_list = []
    for s in stocks:
        try:
            df = yf.Ticker(s).history(period="7d")
            if not df.empty:
                curr, prev = df['Close'].iloc[-1], df['Close'].iloc[-2]
                data_list.append({'Symbol': s, 'Price': round(curr, 2), 'Change %': round(((curr-prev)/prev)*100, 2), 'History': df})
        except: continue
    return data_list

market_data = get_market_data(stocks_list)

# --- NAVIGATION ENGINE ---

# VIEW 1: PREDICTION PAGE (Deep Dive)
if st.session_state.current_view == 'predict' and st.session_state.selected_stock:
    s = st.session_state.selected_stock
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.current_view = 'grid'
        st.rerun()
    
    st.title(f"🔮 AI Forecast: {s}")
    df_long = yf.Ticker(s).history(period="1mo")
    analysis = get_prediction_logic(s)
    
    if analysis:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Verdict", analysis['verdict'])
        c2.metric("RSI (14D)", analysis['rsi'])
        c3.metric("Target", f"₹{analysis['target']}")
        c4.metric("Stop-Loss", f"₹{analysis['stoploss']}")
        
        # Big Chart
        fig = go.Figure(data=[go.Candlestick(x=df_long.index, open=df_long['Open'], high=df_long['High'], low=df_long['Low'], close=df_long['Close'])])
        fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Not enough data for this stock yet.")

# VIEW 2: ORIGINAL GRID VIEW
else:
    if main_page == "🏠 Market Overview":
        st.title("📊 Live Market Terminal")
        
        for i in range(0, len(market_data), 5):
            cols = st.columns(5)
            for j in range(5):
                if i + j < len(market_data):
                    item = market_data[i + j]
                    color = "#00ff88" if item['Change %'] >= 0 else "#ff4b4b"
                    with cols[j]:
                        # P&L Logic
                        pnl_html = ""
                        if item['Symbol'] == my_stock and buy_price > 0:
                            diff = round(item['Price'] - buy_price, 2)
                            pnl_html = f'<div style="color:{"#00ff88" if diff >= 0 else "#ff4b4b"}; font-size:12px;">P&L: {diff}</div>'

                        st.markdown(f"""
                        <div class="compact-card" style="border-top-color: {color};">
                            <div class="stock-symbol">{item['Symbol'].replace('.NS','')}</div>
                            <div class="price-text">{item['Price']} <span style="font-size:0.8rem; color:{color};">({item['Change %']}%)</span></div>
                            {pnl_html}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Clickable Predict Button
                        if st.button(f"Predict {item['Symbol'].split('.')[0]}", key=f"btn_{item['Symbol']}"):
                            st.session_state.selected_stock = item['Symbol']
                            st.session_state.current_view = 'predict'
                            st.rerun()

                        # Sparkline
                        fig = go.Figure(go.Scatter(x=item['History'].index, y=item['History']['Close'], mode='lines', line=dict(color=color, width=1.5), fill='tozeroy', fillcolor=f"rgba({ '0,255,136,0.05' if item['Change %'] >= 0 else '255,75,75,0.05' })"))
                        fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=45, xaxis=dict(visible=False), yaxis=dict(visible=False), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    elif main_page == "🏆 Top Movers":
        st.title("🏆 Market Leaders & Laggards")
        df_movers = pd.DataFrame(market_data).sort_values(by='Change %', ascending=False)
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🚀 Top 5 Gainers")
            for _, r in df_movers.head(5).iterrows(): st.success(f"**{r['Symbol']}** | {r['Price']} | +{r['Change %']}%")
        with c2:
            st.subheader("📉 Top 5 Losers")
            for _, r in df_movers.tail(5).iterrows(): st.error(f"**{r['Symbol']}** | {r['Price']} | {r['Change %']}%")
