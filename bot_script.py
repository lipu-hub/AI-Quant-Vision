import yfinance as yf
import requests
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# AI Setup
analyzer = SentimentIntensityAnalyzer()

# Telegram Details
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def get_market_update():
    stocks = ["TSLA", "AAPL", "NVDA", "BTC-USD", "MSFT"]
    message = "🤖 *MarketMind AI Daily Report* 🤖\n\n"
    
    for s in stocks:
        try:
            ticker = yf.Ticker(s)
            # Price nikalna
            hist = ticker.history(period="1d")
            price = round(hist['Close'].iloc[-1], 2)
            
            # Safe News fetching
            sentiment_score = 0
            if hasattr(ticker, 'news') and ticker.news:
                # Sirf pehli news check karo safety ke saath
                title = ticker.news[0].get('title', 'No News')
                sentiment_score = analyzer.polarity_scores(title)['compound']
            
            # Decision Logic
            emoji = "✅ PROFIT" if sentiment_score > 0.05 else "❌ LOSS" if sentiment_score < -0.05 else "🔍 NEUTRAL"
            
            message += f"*{s}*: ${price}\n"
            message += f"AI Forecast: {emoji}\n"
            message += "-------------------\n"
        except Exception as e:
            message += f"*{s}*: Data unavailable ⚠️\n"
    
    return message

def send_telegram_msg(text):
    if not TOKEN or not CHAT_ID:
        print("Error: Secrets missing!")
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

if __name__ == "__main__":
    report = get_market_update()
    send_telegram_msg(report)
