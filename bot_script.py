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
    # 🔥 TOP 20 INDIAN STOCKS (NSE) + 1 CRYPTO
    stocks = [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS",
        "BHARTIARTL.NS", "SBI-N.NS", "LICI.NS", "ITC.NS", "HINDUNILVR.NS",
        "LT.NS", "BAJFINANCE.NS", "TATAMOTORS.NS", "M&M.NS", "ADANIENT.NS",
        "SUNPHARMA.NS", "ASIANPAINT.NS", "TITAN.NS", "ZOMATO.NS", "NTPC.NS",
        "BTC-USD"
    ]
    
    msg = "🇮🇳 *MarketMind AI: Top 20 Indian Stocks* 🇮🇳\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for s in stocks:
        try:
            t = yf.Ticker(s)
            hist = t.history(period="1d")
            if hist.empty: continue
            
            price = round(hist['Close'].iloc[-1], 2)
            
            # AI News Sentiment
            score = 0
            if t.news:
                title = t.news[0].get('title', '')
                score = analyzer.polarity_scores(title)['compound']
            
            # Emoji & Verdict logic
            if score > 0.05:
                verdict = "✅ BULLISH"
            elif score < -0.05:
                verdict = "❌ BEARISH"
            else:
                verdict = "🔍 NEUTRAL"
                
            currency = "$" if "USD" in s else "₹"
            name = s.replace(".NS", "").replace("-N", "")
            
            msg += f"*{name}*: {currency}{price}\nView: {verdict}\n"
            msg += "┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n"
        except:
            msg += f"*{s}*: Data Error ⚠️\n"
            
    msg += "\n🤖 *AI Analysis Complete*"
    return msg

def send_msg(text):
    if not TOKEN or not CHAT_ID:
        print("Error: Secrets missing!")
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        print("✅ Top 20 Report Sent!")
    else:
        print(f"❌ Failed: {response.text}")

if __name__ == "__main__":
    report_text = get_report()
    send_msg(report_text)
