import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="MarketMind AI - Classic", layout="wide")

# Custom CSS for Clean Cards
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .compact-card {
        background: #1e2130;
        padding: 15px;
        border-radius: 12px;
        border-top: 4px solid #444;
        margin-bottom: 5px;
    }
    .stock-symbol { font-size: 1.1rem; font-weight: bold; color: #aaa; }
    .price-text { font-size: 1.4rem; font-weight: bold; margin: 5px 0; }
    .pnl-text { font-size: 0.85rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("💰 Portfolio Settings")
stocks_list = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "TATAMOTORS.NS", "ZOMATO.NS", "BTC-USD", "ETH-USD"]
my_stock = st.sidebar.selectbox("Track My Stock", stocks_list)
buy_price = st.sidebar.number_input("Buying Price", value=0.0)

st.title("📈 MarketMind AI: Classic Dashboard")
st.caption(f"Live 7-Day Trend Charts | {datetime.now().strftime('%H:%M:%S')} IST")

# Grid Logic
for i in range(0, len(stocks_list), 4):
    cols = st.columns(4)
    for j in range(4):
        if i + j < len(stocks_list):
            s = stocks_list[i + j]
            try:
                t = yf.Ticker(s)
                df = t.history(period="7d")
                if df.empty:
                    continue
                
                curr = round(df['Close'].iloc[-1], 2)
                prev = round(df['Close'].iloc[-2], 2)
                p_change = round(((curr - prev) / prev) * 100, 2)
                color = "#00ff88" if p_change >= 0 else "#ff4b4b"
                
                with cols[j]:
                    # Portfolio Logic - Fixed Indentation
                    pnl_str = ""
                    if s == my_stock and buy_price > 0:
                        diff = round(curr - buy_price, 2)
                        p_color = "#00ff88" if diff >= 0 else "#ff4b4b"
                        pnl_str = f'<div class="pnl-text" style="color:{p_color};">P&L: {diff}</div>'

                    # Rendering Info Card
                    st.markdown(f"""
                    <div class="compact-card" style="border-top-color: {color};">
                        <div class="stock-symbol">{s.replace('.NS','')}</div>
                        <div class="price-text">{curr} <span style="font-size:0.8rem; color:{color};">({p_change}%)</span></div>
                        {pnl_str}
                    </div>
                    """, unsafe_allow_html=True)

                    # Plotly Sparkline (The Graph)
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df.index, y=df['Close'], 
                        mode='lines', 
                        line=dict(color=color, width=2), 
                        fill='tozeroy', 
                        fillcolor=f"rgba({ '0,255,136,0.1' if p_change >= 0 else '255,75,75,0.1' })"
                    ))
                    fig.update_layout(
                        margin=dict(l=0,r=0,t=0,b=0), 
                        height=60, 
                        xaxis=dict(visible=False), 
                        yaxis=dict(visible=False), 
                        paper_bgcolor='rgba(0,0,0,0)', 
                        plot_bgcolor='rgba(0,0,0,0)', 
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            except:
                continue
