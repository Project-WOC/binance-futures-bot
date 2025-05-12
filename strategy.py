import time

class Strategy:
    def __init__(self, binance_handler):
        self.binance = binance_handler
        self.active_position = None

    def execute_trade(self, signal):
        self.binance.set_leverage()
        balance = self.binance.get_balance()
        entry_price = self.binance.get_price()
        margin = balance * self.binance.margin_ratio
        qty = round((margin * self.binance.leverage) / entry_price, 3)

        print(f"Balance: {balance}, Entry Price: {entry_price}, Margin: {margin}, Quantity: {qty}")

        side = "BUY" if signal == "LONG" else "SELL"
        response = self.binance.open_position(side, qty)

        print(f"Opening {side} position with response: {response}")

        self.active_position = {
            "entry": entry_price,
            "qty": qty,
            "side": side,
            "step": 0
        }

        self.monitor_position(signal)  # Pass the signal for monitoring

        return response

    def monitor_position(self, signal):
        if not self.active_position:
            return

        entry = self.active_position["entry"]
        qty = self.active_position["qty"]
        side = self.active_position["side"]
        step = self.active_position["step"]

        sl_base = entry * (0.90 if side == "BUY" else 1.10)
        tp_levels = [1.05, 1.10, 1.15, 1.20] if side == "BUY" else [0.95, 0.90, 0.85, 0.80]
        sl_levels = [entry, entry * tp_levels[0], entry * tp_levels[1]]

        current_price = self.binance.get_price()

        # Stop loss kontrolü
        if (side == "BUY" and current_price <= sl_base) or (side == "SELL" and current_price >= sl_base):
            print(f"Stop loss triggered, closing {side} position.")
            self.binance.close_position("SELL" if side == "BUY" else "BUY", qty)
            self.active_position = None
            return

        # Kademeli TP
        if step < 4:
            target_price = entry * tp_levels[step]
            if (side == "BUY" and current_price >= target_price) or                (side == "SELL" and current_price <= target_price):
                portion = round(qty * 0.5, 3)
                print(f"Closing {portion} of the {side} position at {target_price}")
                self.binance.close_position("SELL" if side == "BUY" else "BUY", portion)
                self.active_position["qty"] -= portion
                self.active_position["step"] += 1

        # Ters sinyal geldiyse mevcut pozisyonu kapat ve yeni pozisyon aç
        if (signal == "SHORT" and side == "BUY") or (signal == "LONG" and side == "SELL"):
            print(f"Ters sinyal geldi! Closing {side} position and opening {signal} position.")
            self.binance.close_position(side, qty)
            self.execute_trade(signal)  # Yeni sinyal için işlem aç