from binance.um_futures import UMFutures
import os

class BinanceHandler:
    def __init__(self):
        self.client = UMFutures(
            key=os.getenv("BINANCE_API_KEY"),
            secret=os.getenv("BINANCE_API_SECRET")
        )
        self.symbol = os.getenv("SYMBOL", "TAOUSDT")
        self.leverage = int(os.getenv("LEVERAGE", "20"))
        self.margin_ratio = float(os.getenv("MARGIN_USAGE", "0.99"))

    def get_balance(self):
        balance = self.client.balance()
        usdt = next((b for b in balance if b['asset'] == 'USDT'), None)
        return float(usdt['balance']) if usdt else 0

    def set_leverage(self):
        self.client.change_leverage(symbol=self.symbol, leverage=self.leverage)

    def open_position(self, side, quantity):
        return self.client.new_order(
            symbol=self.symbol,
            side=side,
            type="MARKET",
            quantity=quantity
        )

    def close_position(self, side, quantity):
        return self.client.new_order(
            symbol=self.symbol,
            side=side,
            type="MARKET",
            quantity=quantity
        )

    def get_price(self):
        return float(self.client.ticker_price(symbol=self.symbol)['price'])