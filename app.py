import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai
import plotly.graph_objects as go

# ⚡ Page Configuration
st.set_page_config(page_title="TradeSignal — Live Dashboard", layout="wide", initial_sidebar_state="expanded")

# 🔐 Streamlit Secrets Verification
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.sidebar.warning("⚠️ Please configure GEMINI_API_KEY in Streamlit Secrets.")

# INITIALIZE SESSION STATES
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {}
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = "RELIANCE"
if "ticker_raw_name" not in st.session_state:
    st.session_state.ticker_raw_name = "RELIANCE.NS"
if "ai_analysis_result" not in st.session_state:
    st.session_state.ai_analysis_result = "Click 'Scan 🎯' on any asset below to trigger the Gemini AI Visual Quant engine."
if "live_prices" not in st.session_state:
    st.session_state.live_prices = {}

# Premium Stock List matching your new design
if "custom_tickers" not in st.session_state:
    st.session_state.custom_tickers = [
        "RELIANCE.NS", "INFY.NS", "TCS.NS", "HDFCBANK.NS", 
        "WIPRO.NS", "ICICIBANK.NS", "BAJFINANCE.NS", "TATAMOTORS.NS"
    ]

# 🎨 PREMIUM NEON DARK MODE STYLE INJECTION
st.markdown("""
<style>
    /* Global Styles */
    .stApp { background-color: #0b0f19 !important; color: #f1f5f9 !important; }
    h1, h2, h3, p, span, label, div { color: #f1f5f9 !important; font-family: 'Inter', sans-serif; }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 1px solid #1e293b; }
    
    /* Top Market Ticker Banner */
    .market-ticker-banner {
        background: #111827; border: 1px solid #1e293b; border-radius: 8px;
        padding: 10px 20px; display: flex; justify-content: space-between; margin-bottom: 25px;
    }
    .ticker-item { font-size: 0.9rem; font-weight: bold; }
    .text-green { color: #10b981 !important; }
    .text-red { color: #ef4444 !important; }
    
    /* Glowing Asset Cards Layout */
    .crypto-card {
        background: #131c2e !important; border-radius: 12px !important;
        padding: 20px !important; margin-bottom: 15px; transition: all 0.3s ease;
    }
    .card-buy { border: 1px solid rgba(16, 185, 129, 0.4) !important; box-shadow: 0 0 15px rgba(16, 185, 129, 0.1) !important; }
    .card-sell { border: 1px solid rgba(239, 68, 68, 0.4) !important; box-shadow: 0 0 15px rgba(239, 68, 68, 0.1) !important; }
    .card-hold { border: 1px solid rgba(245, 158, 11, 0.4) !important; box-shadow: 0 0 15px rgba(245, 158, 11, 0.1) !important; }
    
    .stock-badge {
        float: right; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: bold;
    }
    .badge-buy { background: rgba(16, 185, 129, 0.2); color: #10b981; }
    .badge-sell { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
    .badge-hold { background: rgba(245, 158, 11, 0.2); color: #2563eb; }
    
    .price-large { font-size: 1.7rem !important; font-weight: 800 !important; font-family: 'JetBrains Mono', monospace; margin: 8px 0; }
</style>
""", unsafe_allow_html=True)

# 🧭 SIDEBAR NAVIGATION
with st.sidebar:
    st.markdown("### ⚡ TradeSignal `v2.0`")
    page = st.radio("NAVIGATION", [" Live Overview", " My Portfolio Simulation"])
    st.markdown("---")
    st.markdown("### 📊 WATCHLIST")
    for t in st.session_state.custom_tickers:
        st.markdown(f"• **{t.replace('.NS','')}**")

# TOP MARKET MARQUEE DATA FETCH
@st.cache_data(ttl=60)
def get_market_indices():
    return {"SENSEX": "72,066 (+0.4%)", "NIFTY 50": "22,104 (+0.3%)", "BANK NIFTY": "46,982 (-0.2%)", "USD/INR": "83.42"}

indices = get_market_indices()
st.markdown(f"""
<div class="market-ticker-banner">
    <div class="ticker-item">SENSEX: <span class="text-green">{indices['SENSEX']}</span></div>
    <div class="ticker-item">NIFTY 50: <span class="text-green">{indices['NIFTY 50']}</span></div>
    <div class="ticker-item">BANK NIFTY: <span class="text-red">{indices['BANK NIFTY']}</span></div>
    <div class="ticker-item">USD/INR: <span>{indices['USD/INR']}</span></div>
</div>
""", unsafe_allow_html=True)

@st.cache_data(ttl=20)
def fetch_trading_data(ticker_name):
    try:
        df = yf.download(ticker_name, period="1mo", interval="15m", auto_adjust=True, progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
        return df
    except:
        return None

# ==========================================
# PAGE 1: LIVE OVERVIEW (WHISTLEBLOWER GRID)
# ==========================================
if page == " Live Overview":
    st.title("⚡ Live Overview")
    st.caption("On-Demand AI Smart Trading Signals Desk")
    
    # 📢 LIVE BREAKOUT ALERTS BLOCK (YFINANCE FREE REFRESH ENGINE)
    @st.fragment(run_every=15)
    def live_data_scrip_scanner():
        st.markdown("### 🔔 Active Whistleblower Feed")
        alert_triggered = False
        
        for ticker in st.session_state.custom_tickers:
            df = yf.download(ticker, period="1d", interval="1m", auto_adjust=True, progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                close_series = df['Close'].squeeze()
                current_price = float(close_series.iloc[-1])
                prev_price = float(close_series.iloc[-2]) if len(close_series) > 1 else current_price
                price_change = ((current_price - prev_price) / prev_price) * 100
                clean_name = ticker.replace(".NS", "")
                
                # Determine status rules visually
                status = "HOLD"
                if price_change > 0.05: status = "BUY"
                elif price_change < -0.05: status = "SELL"
                
                st.session_state.live_prices[ticker] = {"price": current_price, "change": price_change, "status": status}
                
                if price_change > 0.12:
                    st.success(f"🚀 **{clean_name} — BUY ALERT:** Surge detected (+{price_change:.2f}%) at ₹{current_price:,.2f}")
                    alert_triggered = True
                elif price_change < -0.12:
                    st.error(f"📉 **{clean_name} — EXIT ALERT:** Drop detected ({price_change:.2f}%) at ₹{current_price:,.2f}")
                    alert_triggered = True
                    
        if not alert_triggered:
            st.info("🔄 Free yfinance engine monitoring live ticks... Everything stable in neutral corridors.")

    live_data_scrip_scanner()
    st.markdown("---")

    # 🎛️ SMART NEON ASSET GRID
    st.markdown("### 💎 Intelligent Asset Grid")
    cols = st.columns(4)
    
    for i, ticker in enumerate(st.session_state.custom_tickers):
        clean_name = ticker.replace(".NS", "")
        live_info = st.session_state.live_prices.get(ticker, {"price": 0.0, "change": 0.0, "status": "HOLD"})
        
        # Color mapping logic based on your custom UI choice
        card_class = "card-hold"
        badge_class = "badge-hold"
        if live_info["status"] == "BUY":
            card_class = "card-buy"
            badge_class = "badge-buy"
        elif live_info["status"] == "SELL":
            card_class = "card-sell"
            badge_class = "badge-sell"
            
        with cols[i % 4]:
            st.markdown(f"""
            <div class="crypto-card {card_class}">
                <span class="stock-badge {badge_class}">{live_info['status']}</span>
                <div style="font-size:1.1rem; font-weight:bold; color:#94a3b8;">{clean_name}</div>
                <div class="price-large">₹{live_info['price']:,.2f}</div>
                <div style="font-size:0.85rem; color:{'#10b981' if live_info['change'] >= 0 else '#ef4444'}">
                    {'+' if live_info['change'] >= 0 else ''}{live_info['change']:.2f}% today
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            b1, b2 = st.columns(2)
            with b1:
                if st.button(f"Scan 🎯", key=f"sc_{ticker}", use_container_width=True):
                    st.session_state.selected_ticker = clean_name
                    st.session_state.ticker_raw_name = ticker
                    with st.spinner("Gemini AI computing..."):
                        data_df = fetch_trading_data(ticker)
                        if data_df is not None and not data_df.empty:
                            recent_str = data_df.tail(10)[['Close', 'High', 'Low']].to_string()
                            prompt = f"Act as a simplified trading meter.
