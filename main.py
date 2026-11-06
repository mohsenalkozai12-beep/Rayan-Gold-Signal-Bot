import os
import yfinance as yf
import pandas as pd
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    }, timeout=20)

def analyze_gold():
    data = yf.download(
        "GC=F",
        period="2d",
        interval="5m",
        progress=False
    )

    if data.empty or len(data) < 60:
        print("Not enough market data")
        return

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    close = data["Close"].dropna()

    ema20 = close.ewm(span=20, adjust=False).mean()
    ema50 = close.ewm(span=50, adjust=False).mean()

    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1/14, adjust=False
    ).mean()

    avg_loss = loss.ewm(
        alpha=1/14, adjust=False
    ).mean()

    rs = avg_gain / avg_loss.replace(0, float("nan"))
    rsi = 100 - (100 / (1 + rs))

    current = float(close.iloc[-2])
    e20 = float(ema20.iloc[-2])
    e50 = float(ema50.iloc[-2])
    previous_e20 = float(ema20.iloc[-3])
    previous_e50 = float(ema50.iloc[-3])
    current_rsi = float(rsi.iloc[-2])

    if pd.isna(current_rsi):
        return

    signal = None

    if (previous_e20 <= previous_e50
        and e20 > e50 and current_rsi > 50):
        signal = "BUY 🟢"

    elif (previous_e20 >= previous_e50
          and e20 < e50 and current_rsi < 50):
        signal = "SELL 🔴"

    if signal:
        message = (
            "RAYAN GOLD SIGNAL BOT\n\n"
            f"Gold Futures: {signal}\n"
            "Timeframe: M5\n"
            f"Entry reference: {current:.2f}\n"
            f"RSI: {current_rsi:.2f}\n\n"
            "Signal for analysis only.\n"
            "Not a guaranteed trading recommendation."
        )
        send_message(message)
        print(message)
    else:
        print("No new signal")

if __name__ == "__main__":
    send_message("RAYAN GOLD SIGNAL BOT is working! ✅")
    analyze_gold()