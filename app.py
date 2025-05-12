
from flask import Flask, request, jsonify
import os
from binance.um_futures import UMFutures
from dotenv import load_dotenv
import logging

load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
client = UMFutures(key=API_KEY, secret=API_SECRET)

symbol = "TAOUSDT"
leverage = 20
quantity_fraction = 0.99

active_position = None

def get_position():
    positions = client.get_position_risk(symbol=symbol)
    for p in positions:
        if float(p["positionAmt"]) != 0.0:
            return p
    return None

def close_position(position):
    side = "SELL" if float(position["positionAmt"]) > 0 else "BUY"
    quantity = abs(float(position["positionAmt"]))
    client.new_order(symbol=symbol, side=side, type="MARKET", quantity=quantity)
    logging.info(f"[Kapatıldı] Pozisyon kapatıldı: {side} {quantity}")

@app.route("/webhook", methods=["POST"])
def webhook():
    global active_position
    data = request.json
    signal = data.get("signal", "").upper()

    logging.info(f"[Webhook] Sinyal alındı: {signal}")

    if signal not in ["LONG", "SHORT"]:
        return jsonify({"error": "Geçersiz sinyal"}), 400

    current_position = get_position()
    if current_position:
        pos_amt = float(current_position["positionAmt"])
        if (signal == "LONG" and pos_amt > 0) or (signal == "SHORT" and pos_amt < 0):
            logging.info("[Durum] Aynı yönde pozisyon zaten açık.")
            return jsonify({"message": "Pozisyon zaten açık"}), 200
        else:
            close_position(current_position)

    balance_info = client.balance()
    usdt_balance = float([x for x in balance_info if x["asset"] == "USDT"][0]["balance"])
    price = float(client.ticker_price(symbol=symbol)["price"])
    order_side = "BUY" if signal == "LONG" else "SELL"
    order_qty = round((usdt_balance * quantity_fraction * leverage) / price, 3)

    client.change_leverage(symbol=symbol, leverage=leverage)
    client.new_order(symbol=symbol, side=order_side, type="MARKET", quantity=order_qty)
    logging.info(f"[Açıldı] Yeni pozisyon: {order_side} {order_qty}")

    return jsonify({"message": "İşlem alındı"}), 200
