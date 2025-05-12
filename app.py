from flask import Flask, request, jsonify
from binance_handler import BinanceHandler
from strategy import Strategy
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

binance = BinanceHandler()
strategy = Strategy(binance)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    signal = data.get('signal')
    print(f"[Webhook] Gelen sinyal: {signal}")
    if signal in ['LONG', 'SHORT']:
        result = strategy.execute_trade(signal)
        return jsonify({'status': 'ok', 'detail': result})
    return jsonify({'status': 'error', 'message': 'Invalid signal'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)