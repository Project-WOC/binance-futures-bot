import os
from binance.um_futures import UMFutures

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

client = UMFutures(key=api_key, secret=api_secret)

def place_test_order():
    try:
        response = client.new_order(
            symbol="TAOUSDT",
            side="BUY",
            type="MARKET",
            quantity=1
        )
        print("Order Response:", response)
    except Exception as e:
        print("Order Error:", str(e))

if __name__ == "__main__":
    place_test_order()