import yfinance as yf
import requests
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# AI Setup
analyzer = SentimentIntensityAnalyzer()

# Secrets from GitHub
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def get_report():
    stocks = ["TSLA", "AAPL", "NVDA", "BTC-USD"]
    msg = "🚀 *MarketMind AI Report* 🚀\n\n"
    
    for s in stocks:
        try:
            t = yf.Ticker(s)
            price = round(t.history(period="1d")['Close'].iloc[-1], 2)
            
            score = 0
            if t.news:
                score = analyzer.polarity_scores(t.news[0].get('title', ''))['compound']
            
            decision = "✅ BUY/PROFIT" if score > 0.05 else "❌ SELL/LOSS" if score < -0.05 else "🔍 HOLD"
            msg += f"*{s}*: ${price}\nAI View: {decision}\n\n"
        except:
            msg += f"*{s}*: Service Down ⚠️\n\n"
    return msg

def send_msg(text):
    if not TOKEN or not CHAT_ID:
        print("CRITICAL ERROR: Token or Chat ID is missing in GitHub Secrets!")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    
    response = requests.post(url, json=data)
    
    # Ye line check karegi ki message kyun nahi gaya
    if response.status_code == 200:
        print("SUCCESS: Message sent to Telegram!")
    else:
        print(f"FAILED: Telegram says -> {response.text}")

if __name__ == "__main__":
    report_text = get_report()
    send_msg(report_text)
