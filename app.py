from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import pandas_ta as ta
from binance.client import Client

app = Flask(__name__)
CORS(app) # මේක ඕන වෙනවා උඹේ web page එකට ඩේටා ගන්න දෙන්න

API_KEY = 'cy1nLr9iLfimsfi89gYoue9JfmXblkdteueN1xWHV5y5W3HI6QUPlgC14mWF5QQz'
API_SECRET = 'E5iF8Lo3yZ58w8mi0k65cwuSRWQC37mYHLOgMHkAI3wB5X2wU3t13Hed5sS2VOOR'
client = Client(API_KEY, API_SECRET)

COINS = ['ETHUSDT', 'SOLUSDT', 'BTCUSDT', 'DOGEUSDT', 'XRPUSDT']

@app.route('/get-signals', methods=['GET'])
def get_signals():
    all_signals = []
    for symbol in COINS:
        try:
            candles = client.futures_klines(symbol=symbol, interval='15m', limit=100)
            df = pd.DataFrame(candles, columns=['time','open','high','low','close','vol','ct','qv','tr','tbb','tbq','ig'])
            df[['high','low','close']] = df[['high','low','close']].astype(float)
            
            adx = ta.adx(df['high'], df['low'], df['close'], length=14)['ADX_14'].iloc[-1]
            rsi = ta.rsi(df['close'], length=14).iloc[-1]
            ema9 = ta.ema(df['close'], length=9).iloc[-1]
            ema21 = ta.ema(df['close'], length=21).iloc[-1]
            price = df['close'].iloc[-1]

            signal = "None"
            if adx > 22:
                if ema9 > ema21 and rsi > 55: signal = "BUY"
                elif ema9 < ema21 and rsi < 45: signal = "SELL"

            if signal != "None":
                all_signals.append({
                    "symbol": symbol,
                    "signal": signal,
                    "price": round(price, 4),
                    "adx": round(adx, 2),
                    "rsi": round(rsi, 2)
                })
        except: continue
    
    return jsonify(all_signals)

if __name__ == "__main__":
    app.run(debug=True, port=5000)