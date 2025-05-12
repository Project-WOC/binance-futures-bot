import os
from binance.client import Client
from binance.enums import *

# Ortam değişkenlerinden API anahtarlarını al
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

# Anahtarlar eksikse hata ver
if not api_key or not api_secret:
    raise ValueError("API key or secret not set!")

# Binance istemcisini oluştur
client = Client(api_key, api_secret)

# Test amaçlı küçük bir işlem aç (futures market)
try:
    order = client.futures_create_order(
        symbol='BTCUSDT',
        side=SIDE_BUY,
        type=ORDER_TYPE_MARKET,
        quantity=0.001
    )
    print("Order placed:", order)
except Exception as e:
    print("Order Error:", e)
