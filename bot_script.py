import yfinance as yf
import requests
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# AI Sentiment Setup
analyzer = SentimentIntensityAnalyzer()

# Secrets from GitHub
TOKEN = os.getenv('TELEGRAM_TOKEN', '').strip()
CHAT_ID = os.getenv('CHAT_ID', '').strip()

def get_report():
    # Indian Stocks (.NS) aur Crypto
    stocks = ["RELIANCE.NS", "TATAMOTORS.NS", "ZOMATO.NS", "HDFCBANK.NS", "BTC-USD"]
    msg = "🚀 *MarketMind AI: Indian Market Report* 🚀\n\n"
    
    for s in stocks:
        try:
            t = yf.Ticker(s)
            # Latest price fetch
            hist = t.history(period="1d")
            if hist.empty: continue
            
            price = round(hist['Close'].iloc[-1], 2)
            
            # AI News Sentiment logic
            score = 0
            if t.news:
                title = t.news[0].get('title', '')
                score = analyzer.polarity_scores(title)['compound']
            
            # Decision & Emoji
            verdict = "✅ BUY/PROFIT" if score > 0.05 else "❌ SELL/LOSS" if score < -0.05 else "🔍 HOLD"
            symbol = "₹" if ".NS" in s else "$"
            name = s.replace(".NS", "")
            
            msg += f"*{name}*: {symbol}{price}\nAI View: {verdict}\n"
            msg += "-------------------\n"
        except Exception as e:
            msg += f"*{s}*: Data Error ⚠️\n"
            
    return msg

def send_msg(text):
    if not TOKEN or not CHAT_ID:
        print("Error: Secrets missing!")
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        print("✅ Message Sent Successfully!")
    else:
        print(f"❌ Failed: {response.text}")

if __name__ == "__main__":
    report_text = get_report()
    send_msg(report_text)
