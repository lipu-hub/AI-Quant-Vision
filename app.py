import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai
import plotly.graph_objects as go
from datetime import datetime  # 📅 Time stamp engine import kiya

# ⚡ Page Configuration
st.set_page_config(page_title="MarketMind AI Terminal", layout="wide", initial_sidebar_state="expanded")

# 🔐 Streamlit Secrets Verification
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.sidebar.warning("⚠️ Please configure GEMINI_API_KEY in Streamlit Secrets.")

# INITIALIZE SESSION STATES
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {}
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = "IFCI"
if "ticker_raw_name" not in st.session_state:
    st.session_state.ticker_raw_name = "IFCI.NS"
if "ai_analysis_result" not in st.session_state:
    st.session_state.ai_analysis_result = None
if "live_prices" not in st.session_state:
    st.session_state.live_prices = {}
if "custom_tickers" not in st.session_state:
    st.session_state.custom_tickers = [
        "SUZLON.NS", "RVNL.NS", "NBCC.NS", "GAIL.NS", "IRFC.NS", 
        "IDEA.NS", "TATAPOWER.NS", "HUDCO.NS", "IFCI.NS", "YESBANK.NS", 
        "NHPC.NS", "IOC.NS", "BTC-USD", "PNB.NS", "JPPOWER.NS", 
        "SJVN.NS", "SAIL.NS", "ETH-USD"
    ]

# ⚙️ CORE ADMIN CONSOLE IN SIDEBAR
with st.sidebar:
    st.markdown("## ⚙️ Core Admin Console")
    admin_pin = st.text_input("Enter Admin Master Pin:", type="password")
    if admin_pin == "777":
        st.success("🔓 Admin Access Granted!")
        new_ticker = st.text_input("Add Ticker Name (e.g., RELIANCE.NS):").upper().strip()
        if st.button("➕ Inject Asset"):
            if new_ticker and new_ticker not in st.session_state.custom_tickers:
                st.session_state.custom_tickers.append(new_ticker)
                st.rerun()
    st.markdown("---")

# 🎛️ INJECTING ORIGINAL PREMIUM LIGHT STYLE BLOCK
bg_color = "#f8fafc"
text_color = "#0f172a"
card_bg = "#ffffff"
border_color = "rgba(234, 88, 12, 0.4)"
price_color = "#ea580c"
title_color = "#475569"

st.markdown(f"""
<style>
.stApp {{ background-color: {bg_color} !important; color: {text_color} !important; }}
h1, h2, h3, p, span, label {{ color: {text_color} !important; font-weight: 600; }}
div[data-testid="stVComponentBlock"] > div[style*="border"] {{
    border: 1px solid {border_color} !important;
    border-radius: 12px !important;
    background: {card_bg} !important;
    padding: 16px !important;
    box-shadow: 0 4px 12px rgba(234, 88, 12, 0.05) !important;
}}
.card-header-flex {{ display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }}
.company-logo-avatar {{ 
    width: 40px; 
    height: 40px; 
    border-radius: 8px; 
    display: flex; 
    align-items: center; 
    justify-content: center; 
    font-size: 1.5rem; 
    font-weight: bold; 
    color: white;
}}
.price-text {{ font-family: 'Courier New', Courier, monospace; font-size: 1.7rem !important; font-weight: bold; color: {price_color} !important; margin: 2px 0px; }}
.stock-title {{ font-size: 1.1rem; font-weight: bold; color: {title_color} !important; }}
.indicator-text {{ font-size: 0.85rem; font-weight: 600; margin-top: 4px; }}

.alert-box {{
    padding: 14px 20px;
    border-radius: 10px;
    font-size: 2rem !important;
    font-weight: 900 !important;
    text-align: center;
    margin-bottom: 15px;
    letter-spacing: 2px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}}
.alert-buy {{ background-color: #10b981 !important; color: white !important; }}
.alert-sell {{ background-color: #ef4444 !important; color: white !important; }}
.alert-hold {{ background-color: #f59e0b !important; color: white !important; }}
</style>
""", unsafe_allow_html=True)

def get_brand_avatar(ticker):
    brands = {
        "SUZLON": {"bg": "#0284c7", "txt": "SZ"}, "RVNL": {"bg": "#b91c1c", "txt": "RV"},
        "NBCC": {"bg": "#0f766e", "txt": "NB"}, "GAIL": {"bg": "#15803d", "txt": "GL"},
        "IRFC": {"bg": "#1e3a8a", "txt": "IF"}, "IDEA": {"bg": "#e11d48", "txt": "VI"},
        "TATAPOWER": {"bg": "#0369a1", "txt": "TP"}, "HUDCO": {"bg": "#4d7c0f", "txt": "HD"},
        "IFCI": {"bg": "#6d28d9", "txt": "IF"}, "YESBANK": {"bg": "#2563eb", "txt": "YB"},
        "NHPC": {"bg": "#0369a1", "txt": "NH"}, "IOC": {"bg": "#ea580c", "txt": "IO"},
        "PNB": {"bg": "#991b1b", "txt": "PB"}, "JPPOWER": {"bg": "#d97706", "txt": "JP"},
        "SJVN": {"bg": "#475569", "txt": "SJ"}, "SAIL": {"bg": "#1e40af", "txt": "SL"},
        "BTC-USD": {"bg": "#f59e0b", "txt": "₿"}, "ETH-USD": {"bg": "#6366f1", "txt": "Ξ"}
    }
    return brands.get(ticker, {"bg": "#475569", "txt": "ST"})

tickers = st.session_state.custom_tickers
st.title("🚀 MarketMind AI Trading Terminal")
st.subheader("Live Budget Scanner with Real-Time Risk & News Sentiment Tracker")

@st.cache_data(ttl=30)
def fetch_trading_data(ticker_name):
    try:
        df = yf.download(ticker_name, period="1mo", interval="15m", auto_adjust=True, progress=False)
        if df.empty:
            df = yf.download(ticker_name, period="1mo", interval="1d", auto_adjust=True, progress=False)
        
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            close_prices = df['Close'].squeeze()
            df['EMA_20'] = close_prices.ewm(span=20, adjust=False).mean()
            
            delta = close_prices.diff()
            gain = (delta.where(delta > 0, 0)).ewm(alpha=1/14, adjust=False).mean()
            loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
            rs = gain / (loss + 1e-10)
            df['RSI'] = 100 - (100 / (1 + rs))
            
            exp1 = close_prices.ewm(span=12, adjust=False).mean()
            exp2 = close_prices.ewm(span=26, adjust=False).mean()
            df['MACD'] = exp1 - exp2
            df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
            return df
    except:
        return None
    return None

# 🚨 REAL-TIME LIVE TRADING ALERT TRACE ENGINE WITH TIMESTAMP
critical_alerts = []
for tick in tickers:
    t_df = fetch_trading_data(tick)
    if t_df is not None and not t_df.empty:
        r_val = float(t_df['RSI'].iloc[-1]) if 'RSI' in t_df.columns else 50.0
        c_price = float(t_df['Close'].iloc[-1])
        c_name = tick.replace(".NS", "")
        current_time = datetime.now().strftime("%H:%M:%S")  # 🕐 Real-time clock formatted
        
        if r_val <= 23:
            critical_alerts.append(f"⏰ **[{current_time}]** 🔥 **{c_name}** is Super OVERSOLD (RSI: {r_val:.1f}) at ₹{c_price:,.2f}! Strong setup for sudden BUY bounce.")
        elif r_val >= 70:
            critical_alerts.append(f"⏰ **[{current_time}]** 💥 **{c_name}** is Super OVERBOUGHT (RSI: {r_val:.1f}) at ₹{c_price:,.2f}! High risk zone, look for SELL/SHORT setup.")

@st.fragment(run_every=15)
def live_alert_scanner(alerts_list):
    st.markdown("### 🚦 Immediate AI Whistleblower (Live Alerts)")
    if alerts_list:
        for alert in alerts_list:
            st.error(alert)
            if "OVERSOLD" in alert:
                st.toast(f"🎯 Buy Opportunity detected!", icon="🔥")
            else:
                st.toast(f"⚠️ Profit Booking zone reached!", icon="💥")
    else:
        st.info("🔄 Scanner active. Real-time Quant risk tracking enabled. Monitoring market entries...")

live_alert_scanner(critical_alerts)
st.markdown("---")

st.markdown("### 🔍 Intelligent Asset Filter")
cols = st.columns(4)
for i, ticker in enumerate(tickers):
    with cols[i % 4]:
        data_df = fetch_trading_data(ticker)
        if data_df is not None and not data_df.empty:
            close_series = data_df['Close'].squeeze()
            latest_price = float(close_series.iloc[-1])
            symbol = "$" if "USD" in ticker else "₹"
            clean_name = ticker.replace(".NS", "")
            meta = get_brand_avatar(clean_name)
            
            st.session_state.live_prices[ticker] = latest_price
            
            rsi_val = float(data_df['RSI'].iloc[-1]) if 'RSI' in data_df.columns else 50.0
            macd_val = float(data_df['MACD'].iloc[-1]) if 'MACD' in data_df.columns else 0.0
            sig_val = float(data_df['Signal_Line'].iloc[-1]) if 'Signal_Line' in data_df.columns else 0.0
            
            rsi_color = "#ef4444" if rsi_val >= 70 else ("#10b981" if rsi_val <= 30 else "#475569")
            rsi_status = "OVERBOUGHT" if rsi_val >= 70 else ("OVERSOLD" if rsi_val <= 30 else "NEUTRAL")
            macd_signal = "🟢 BULLISH" if macd_val > sig_val else "🔴 BEARISH"
            
            with st.container(border=True):
                st.markdown(f"""
                <div class="card-header-flex">
                    <div class="company-logo-avatar" style="background-color: {meta['bg']};">{meta['txt']}</div>
                    <div class="stock-title">{clean_name}</div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"<div class='price-text'>{symbol}{latest_price:,.2f}</div>", unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="indicator-text">RSI (14): <span style="color:{rsi_color}; font-weight:bold;">{rsi_val:.1f} ({rsi_status})</span></div>
                <div class="indicator-text">MACD Cross: <span style="font-weight:bold;">{macd_signal}</span></div>
                <div style="margin-bottom: 12px;"></div>
                """, unsafe_allow_html=True)
                
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button(f"Scan 🎯", key=f"scan_{ticker}", use_container_width=True):
                        st.session_state.selected_ticker = clean_name
                        st.session_state.ticker_raw_name = ticker
                        with st.spinner("AI analyzing Global News & Quants..."):
                            try:
                                recent_data = data_df.tail(10)[['Close', 'High', 'Low']].to_string()
                                ema_now = float(data_df['EMA_20'].iloc[-1])
                                
                                ticker_obj = yf.Ticker(ticker)
                                news_list = ticker_obj.news[:3]
                                news_text = ""
                                if news_list:
                                    for n in news_list:
                                        news_text += f"- Title: {n.get('title')} | Summary: {n.get('summary', 'N/A')}\n"
                                else:
                                    news_text = "No recent headlines. Evaluate based on general macroeconomic context."

                                prompt = (
                                    f"Analyze {clean_name}.\n"
                                    f"TECHNICAL DATA:\nPrice: {latest_price}, EMA_20: {ema_now:.2f}, RSI: {rsi_val:.2f}, MACD: {macd_signal}.\n"
                                    f"Recent Prices:\n{recent_data}\n\n"
                                    f"LATEST 3 STOCK NEWS HEADLINES:\n{news_text}\n\n"
                                    f"STRICT FORMAT RULES:\n"
                                    f"1. Your first line must be exactly 'ACTION: BUY', 'ACTION: SELL', or 'ACTION: HOLD'.\n"
                                    f"2. Your second line must provide exact target and stop-loss like this: '**🎯 Target: X | 🛑 Stop-Loss: Y**'.\n"
                                    f"3. In the breakdown below, combine the technical indicators AND the latest news sentiments to justify the move for an intraday player."
                                )
                                model = genai.GenerativeModel('models/gemini-2.5-flash')
                                st.session_state.ai_analysis_result = model.generate_content(prompt).text
                            except Exception as e:
                                calc_action = 'BUY' if rsi_val <= 30 else ('SELL' if rsi_val >= 70 else 'HOLD')
                                target_p = latest_price * 1.025 if calc_action == 'BUY' else latest_price * 0.975
                                sl_p = latest_price * 0.99 if calc_action == 'BUY' else latest_price * 1.01
                                st.session_state.ai_analysis_result = f"ACTION: {calc_action}\n**🎯 Target: {symbol}{target_p:,.2f} | 🛑 Stop-Loss: {symbol}{sl_p:,.2f}**\n\n[🤖 Terminal Engine Backup Output] Gemini core limit reached. Fallback triggered at {datetime.now().strftime('%H:%M:%S')}. RSI is {rsi_val:.1f} with active {macd_signal} setup."
                with btn_col2:
                    if st.button(f"Sim Buy 🛍️", key=f"sim_{ticker}", use_container_width=True):
                        st.session_state.portfolio[ticker] = {
                            "buy_price": latest_price, 
                            "qty": 100,
                            "symbol": symbol
                        }
                        st.toast(f"Bought 100 shares of {clean_name}!", icon="🛍️")

# Execution desk render logic
if st.session_state.selected_ticker and st.session_state.ai_analysis_result:
    st.markdown
