# tracker_v2.py
import time
import os
from binance.client import Client
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
client = Client(API_KEY, API_SECRET)

symbol = None  # Otomatik belirlenecek
leverage = 20
sl_triggered = False

# TP seviyeleri ve SL güncellemeleri
tp_levels = [
    {"roi": 5, "close_ratio": 0.20, "new_sl": -5},
    {"roi": 10, "close_ratio": 0.20, "new_sl": 0},
    {"roi": 15, "close_ratio": 0.20, "new_sl": 0},
    {"roi": 20, "close_ratio": 0.20, "new_sl": 5},
    {"roi": 25, "close_ratio": "ALL", "new_sl": 10},
]
tp_hit_flags = [False] * len(tp_levels)
sl_roi = -5  # Başlangıçta ROI -%5'te SL var

position_open = False
entry_price = None
entry_time = None
position_side = None
position_qty = 0

def get_open_position():
    positions = client.futures_position_information()
    for p in positions:
        amt = float(p['positionAmt'])
        if amt != 0:
            sym = p['symbol']
            entry = float(p['entryPrice'])
            qty = abs(amt)
            side = "LONG" if amt > 0 else "SHORT"
            current_price = float(client.futures_mark_price(symbol=sym)['markPrice'])
            price_diff = (current_price - entry) if side == "LONG" else (entry - current_price)
            roi = (price_diff / entry) * leverage * 100
            return sym, entry, qty, round(roi, 2), side, current_price
    return None, None, None, None, None, None

def close_partial(ratio, qty, side):
    qty_to_close = qty if ratio == "ALL" else round(qty * ratio, 3)
    order_side = "SELL" if side == "LONG" else "BUY"

    client.futures_create_order(
        symbol=symbol,
        side=order_side,
        positionSide=side,
        type="MARKET",
        quantity=qty_to_close
    )
    print(f"✅ Pozisyonun %{round(100 if ratio == 'ALL' else ratio*100)}'i kapatıldı: {qty_to_close} {order_side}")

while True:
    symbol, entry, qty, roi, side, current_price = get_open_position()

    if symbol:
        entry_price = entry
        position_qty = qty
        position_side = side
        position_open = True
        if entry_time is None:
            entry_time = int(time.time())

        print(f"📈 {symbol} | Fiyat: {current_price}, Giriş: {entry_price}, ROI: %{roi} ({position_side}), SL Aktif: %{sl_roi}")

        if sl_roi > -100 and roi <= sl_roi and not sl_triggered:
            close_partial("ALL", position_qty, position_side)
            sl_triggered = True
            print("🛑 Stop loss tetiklendi, kalan pozisyon kapatıldı.")
        else:
            for i, level in enumerate(tp_levels):
                if not tp_hit_flags[i] and roi >= level["roi"]:
                    close_partial(level["close_ratio"], position_qty, position_side)
                    tp_hit_flags[i] = True
                    if level["close_ratio"] != "ALL":
                        sl_roi = level["new_sl"]
                        print(f"🎯 TP{i+1} gerçekleşti, SL şimdi %{sl_roi}")
                    else:
                        print(f"🎯 TP{i+1} gerçekleşti, tüm pozisyon kapandı.")
                        sl_triggered = True
                    break

    elif position_open:
        print("📄 Pozisyon kapanmış görünüyor, tüm veriler sıfırlanıyor...")
        position_open = False
        entry_price = None
        entry_time = None
        position_side = None
        position_qty = 0
        sl_triggered = False
        sl_roi = -5
        tp_hit_flags = [False] * len(tp_levels)

    else:
        print("⏳ Açık pozisyon bekleniyor...")

    time.sleep(0.25)
