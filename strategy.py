class Strategy:
    def __init__(self, binance_handler):
        self.binance = binance_handler

    def execute_trade(self, signal):
        self.binance.set_leverage()
        balance = self.binance.get_balance()
        price = self.binance.get_price()
        margin = balance * self.binance.margin_ratio
        quantity = round((margin * self.binance.leverage) / price, 3)
        side = "BUY" if signal == "LONG" else "SELL"
        return self.binance.open_position(side=side, quantity=quantity)