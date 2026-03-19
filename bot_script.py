import yfinance as yf
import requests
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# AI Setup
analyzer = SentimentIntensityAnalyzer()

# Telegram Details (Ye GitHub Secrets se aayenge)
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def get_market_update():
    stocks = ["TSLA", "AAPL", "NVDA", "BTC-USD"]
    message = "🤖 *MarketMind AI Daily Report* 🤖\n\n"
    
    for s in stocks:
        ticker = yf.Ticker(s)
        price = ticker.history(period="1d")['Close'].iloc[-1]
        
        # Intelligence: News Sentiment
        news = ticker.news[:1]
        score = 0
        if news:
            score = analyzer.polarity_scores(news[0]['title'])['compound']
        
        # Decision Logic
        emoji = "✅ PROFIT" if score > 0.05 else "❌ LOSS" if score < -0.05 else "🔍 NEUTRAL"
        
        message += f"*{s}*: ${round(price, 2)}\n"
        message += f"AI Forecast: {emoji}\n"
        message += "-------------------\n"
    
    return message

def send_telegram_msg(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

# Run the system
if __name__ == "__main__":
    report = get_market_update()
    send_telegram_msg(report)
