import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- UI CONFIGURATION ---
st.set_page_config(page_title="QuantVision AI", layout="wide")

# Glossy Dark Theme CSS
st.markdown("""
    <style>
    .stApp { background-color: #0a0e14; color: white; }
    div[data-testid="stMetricValue"] { color: #00ff88; font-family: 'Courier New'; }
    .card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- THE AUTO-BRAIN ---
@st.cache_data(ttl=3600)
def fetch_and_analyze():
    # It picks these stocks automatically
    tickers = ["NVDA", "TSLA", "AAPL", "BTC-USD", "GOOGL"]
    data_list = []
    
    for t in tickers:
        stock = yf.Ticker(t)
        df = stock.history(period="60d")
        current = df['Close'].iloc[-1]
        prev = df['Close'].iloc[-2]
        change = current - prev
        
        # Intelligence Logic: Simple Moving Average Cross
        sma_20 = df['Close'].rolling(window=20).mean().iloc[-1]
        # Prediction: If price is above SMA, it's a "Profit" trend
        prediction = "PROFIT" if current > sma_20 else "LOSS"
        confidence = "HIGH" if abs(current - sma_20) > (current * 0.02) else "LOW"
        
        data_list.append({
            "Symbol": t, "Price": current, "Change": change,
            "Forecast": prediction, "Confidence": confidence
        })
    return data_list, df

# --- RENDER WEBSITE ---
st.title("🚀 AI Autonomous Forecasting")
st.write
