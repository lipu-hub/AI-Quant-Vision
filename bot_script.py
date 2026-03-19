import yfinance as yf
import requests
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

# Secrets ko fetch karna
TOKEN = os.getenv('TELEGRAM_TOKEN', '').strip()
CHAT_ID = os.getenv('CHAT_ID', '').strip()

def get_report():
    stocks = ["TSLA", "NVDA", "BTC-USD"]
    msg = "🚀 *MarketMind AI Live Report* 🚀\n\n"
    for s in stocks:
        try:
            t = yf.Ticker(s)
            price = round(t.history(period="1d")['Close'].iloc[-1], 2)
            msg += f"*{s}*: ${price}\n"
        except:
            msg += f"*{s}*: Data Error\n"
    return msg

def send_msg(text):
    # Direct URL check
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    print(f"DEBUG: Trying to send message via bot token starting with: {TOKEN[:5]}...")
    
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        print("✅ SUCCESS: Message reached Telegram!")
    else:
        print(f"❌ FAILED: Error {response.status_code}")
        print(f"Response Body: {response.text}")

if __name__ == "__main__":
    report_text = get_report()
    send_msg(report_text)
