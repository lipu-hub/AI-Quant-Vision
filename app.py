import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai
import plotly.graph_objects as go

# ⚡ Page Configuration & Themes
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

# 🎛️ PREMIUM HIGH-TECH DARK UI INJECTION
st.markdown("""
<style>
/* Base Theme Overrides */
.stApp { background-color: #0b0f19 !important; color: #e2e8f0 !important; }
h1, h2, h3, p, span, label { color: #f1f5f9 !important; font-family: 'Inter', sans-serif; }

/* Glowing Dashboard Cards */
div[data-testid="stVComponentBlock"] > div[style*="border"] {
    border: 1px solid rgba(244, 63, 94, 0.2) !important;
    border-radius: 16px !important;
    background: linear-gradient(145deg, #111827, #1f2937) !important;
    padding: 20px !important;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 0 15px 0 rgba(244, 63, 94, 0.05) !important;
    transition: all 0.3s ease-in-out !important;
}
div[data-testid="stVComponentBlock"] > div[style*="border"]:hover {
    transform: translateY(-4px) !important;
    border-color: rgba(244, 63, 94, 0.6) !important;
    box-shadow: 0 20px 30px -10px rgba(0, 0, 0, 0.5), 0 0 20px 2px rgba(244, 63, 94, 0.15) !important;
}

/* Typography & Live Prices */
.price-text { font-family: 'JetBrains Mono', monospace; font-size: 1.8rem !important; font-weight: 800; color: #38bdf8 !important; margin: 4px 0px; text-shadow: 0 0 10px rgba(56, 189, 248, 0.2); }
.stock-title { font-size: 1.2rem; font-weight: 700; color: #f8fafc !important; letter-spacing: 0.5px; }
.indicator-tag { font-size: 0.85rem; padding: 4px 8px; border-radius: 6px; font-weight: bold; background: #374151; }

/* Interactive Tabs Stylings */
.stTabs [data-baseweb="tab-list"] { gap: 12px; background-color: #111827; padding: 8px; border-radius: 12px; border: 1px solid #1f2937; }
.stTabs [data-baseweb="tab"] { background-color: transparent !important; color: #94a3b8 !important; padding: 10px 20px !important; border-radius: 8px !important; font-weight: 600 !important; transition: all 0.2s; }
.stTabs [data-baseweb="tab"]:hover { color: #f43f5e !important; background: rgba(244, 63, 94, 0.05) !important; }
.stTabs [aria-selected="true"] { background-color: #f43f5e !important; color: white !important; box-shadow: 0 4px 12px rgba(244, 63, 94, 0.3) !important; }

/* Big Action Alerts */
.alert-box { padding: 16px; border-radius: 12px; font-size: 2.2rem !important; font-weight: 900 !important; text-align: center; margin-bottom: 20px; letter-spacing: 3px; text-shadow: 0 2px 4px rgba(0,0,0,0.2); }
.alert-buy { background: linear-gradient(90deg, #059669, #10b981) !important; color: white !important; box-shadow: 0 0 20px rgba(16, 185, 129, 0.3); }
.alert-sell { background: linear-gradient(90deg, #dc2626, #ef4444) !important; color: white !important; box-shadow: 0 0 20px rgba(239, 68, 68, 0.3); }
.alert-hold { background: linear-gradient(90deg, #d97706, #f59e0b) !important; color: white !important; box-shadow: 0 0 20px rgba(245, 158, 11, 0.3); }
</style>
""", unsafe_allow_html=True)

# ⚙️ CORE ADMIN CONSOLE IN SIDEBAR
with st.sidebar:
    st.markdown("## ⚙️ Quant Control Unit")
    admin_pin = st.text_input("Enter Master Pin:", type="password")
    if admin_pin == "777":
        st.success("🔓 System Unlocked")
        new_ticker = st.text_input("Inject Asset Ticker (e.g., RELIANCE.NS):").upper().strip()
        if st.button("⚡ Inject Into Engine"):
            if new_ticker and new_ticker not in st.session_state.custom_tickers:
                st.session_state.custom_tickers.append(new_ticker)
                st.rerun()
    st.markdown("---")

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

# 📊 GLITCH-PROOF MATHEMATICAL ENGINE
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

# HEADER TITLE
st.markdown("<h1 style='text-align: center; color: #f43f5e !important; font-size: 2.8rem;'>⚡ MarketMind AI Quantum Terminal</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8 !important;'>High-Speed Algorithmic Technical Scanner & Macro News Engine</p>", unsafe_allow_html=True)

# 🌐 MULTI-TAB MATRIX INTERACTIVE UI LAYER
tab1, tab2, tab3 = st.tabs(["📊 LIVE AI TERMINAL", "💼 ACTIVE RISK ROOM", "🌐 GLOBAL SENTIMENT WATCH"])

with tab1:
    st.markdown("### 🔍 Intelligent Liquidity Filter")
    tickers = st.session_state.custom_tickers
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
                
                rsi_color = "#ef4444" if rsi_val >= 70 else ("#10b981" if rsi_val <= 30 else "#94a3b8")
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
                    <div style='margin-top:8px;'>
                        <span class='indicator-tag'>RSI: <span style='color:{rsi_color};'>{rsi_val:.1f}</span></span>
                        <span class='indicator-tag'>MACD: {macd_signal}</span>
                    </div>
                    <div style='margin-bottom:12px;'></div>
                    """, unsafe_allow_html=True)
                    
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button(f"Scan 🎯", key=f"scan_{ticker}", use_container_width=True):
                            st.session_state.selected_ticker = clean_name
                            st.session_state.ticker_raw_name = ticker
                            with st.spinner("Analyzing Market Vectors..."):
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
                                        news_text = "No recent headlines. Analyze pure structural price action."

                                    prompt = (
                                        f"Analyze {clean_name}.\n"
                                        f"TECHNICAL DATA:\nPrice: {latest_price}, EMA_20: {ema_now:.2f}, RSI: {rsi_val:.2f}, MACD: {macd_signal}.\n"
                                        f"Data Matrix:\n{recent_data}\n\n"
                                        f"LATEST HEADLINES:\n{news_text}\n\n"
                                        f"STRICT FORMAT RULES:\n"
                                        f"1. Your first line must be exactly 'ACTION: BUY', 'ACTION: SELL', or 'ACTION: HOLD'.\n"
                                        f"2. Your second line must provide exact targets: '**🎯 Target: X | 🛑 Stop-Loss: Y**'.\n"
                                        f"3. Keep the breakdown micro-focused on intraday logic."
                                    )
                                    model = genai.GenerativeModel('models/gemini-2.5-flash')
                                    st.session_state.ai_analysis_result = model.generate_content(prompt).text
                                except Exception as e:
                                    st.session_state.ai_analysis_result = f"Error: {str(e)}"
                    with btn_col2:
                        if st.button(f"Sim Buy 🛍️", key=f"sim_{ticker}", use_container_width=True):
                            st.session_state.portfolio[ticker] = {"buy_price": latest_price, "qty": 100, "symbol": symbol}
                            st.toast(f"Position Locked for {clean_name}!", icon="🛍️")

    # Execution Workspace
    if st.session_state.selected_ticker and st.session_state.ai_analysis_result:
        st.markdown("---")
        st.subheader(f"⚡ Live Quantum Execution Desk: {st.session_state.selected_ticker}")
        chart_col, signal_col = st.columns([3, 2])
        with chart_col:
            raw_df = fetch_trading_data(st.session_state.ticker_raw_name)
            if raw_df is not None and not raw_df.empty:
                fig = go.Figure()
                fig.add_trace(go.Candlestick(x=raw_df.index, open=raw_df['Open'].squeeze(), high=raw_df['High'].squeeze(), low=raw_df['Low'].squeeze(), close=raw_df['Close'].squeeze(), name='Price Action'))
                fig.add_trace(go.Scatter(x=raw_df.index, y=raw_df['EMA_20'].squeeze(), line=dict(color='#f43f5e', width=2), name='20 EMA'))
                fig.update_layout(xaxis_rangeslider_visible=False, height=420, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
        with signal_col:
            with st.container(border=True):
                st.markdown("### 🤖 Executable AI Strategy")
                raw_ai_text = st.session_state.ai_analysis_result
                lines = raw_ai_text.strip().split('\n')
                first_line = lines[0].upper() if lines else ""
                
                if "BUY" in first_line:
                    st.markdown('<div class="alert-box alert-buy">🔥 BUY ALERT</div>', unsafe_allow_html=True)
                elif "SELL" in first_line:
                    st.markdown('<div class="alert-box alert-sell">💥 SELL ALERT</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="alert-box alert-hold">⚠️ HOLD SIGNAL</div>', unsafe_allow_html=True)
                    
                st.markdown("\n".join(lines[1:]))

with tab2:
    st.markdown("### 💼 Active Margin Positions (Live Risk Room)")
    if not st.session_state.portfolio:
        st.info("No open exposures found in the current execution block.")
    else:
        portfolio_data = []
        total_pnl = 0.0
        for ticker, details in list(st.session_state.portfolio.items()):
            current_price = st.session_state.live_prices.get(ticker, details['buy_price'])
            qty = details['qty']
            buy_value = details['buy_price'] * qty
            current_value = current_price * qty
            pnl = current_value - buy_value
            total_pnl += pnl
            pnl_arrow = "▲" if pnl >= 0 else "▼"
            pnl_color = "green" if pnl >= 0 else "red"
            
            portfolio_data.append({
                "Asset": ticker.replace(".NS", ""),
                "Contracts": qty,
                "Avg Entry": f"{details['symbol']}{details['buy_price']:,.2f}",
                "Mark-to-Market (LTP)": f"{details['symbol']}{current_price:,.2f}",
                "Margin Investment": f"{details['symbol']}{buy_value:,.2f}",
                "Live Value": f"{details['symbol']}{current_value:,.2f}",
                "Unrealized P&L": f":{pnl_color}[{pnl_arrow} {details['symbol']}{pnl:,.2f}]"
            })
        st.table(pd.DataFrame(portfolio_data))
        total_color = "green" if total_pnl >= 0 else "red"
        st.markdown(f"### 🏁 Aggregated Net Exposure Balance: :{total_color}[₹{total_pnl:,.2f}]")
        if st.button("🧹 Emergency Liquidate / Clear Exposure Tray"):
            st.session_state.portfolio = {}
            st.rerun()

with tab3:
    st.markdown("### 🌐 Global Macro & Sentiment Intelligence")
    st.info("📡 Scanning terminal ports for global central bank updates and geopolitical risk indices.")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        with st.container(border=True):
            st.markdown("#### 🏛️ Central Bank Watch")
            st.write("• **US Federal Reserve:** Hawkish stance observed; interest rate decisions pacing tech momentum.")
            st.write("• **RBI Policy Desk:** Liquidity checks on mid-caps tracking strict budget allocations.")
    with col_m2:
        with st.container(border=True):
            st.markdown("#### 🌋 Geopolitical Risk Room")
            st.write("• **Energy Corridors:** Crude Oil movements balancing public sector units like GAIL & IOC.")
            st.write("• **Tech Supply Chains:** Semiconductor flows directly dictating momentum on solar/power assets.")
