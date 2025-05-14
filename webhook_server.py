from flask import Flask, request
import subprocess
import json
import time

app = Flask(__name__)

# Bellekte tutulan son sinyaller
last_15m_signal = None
last_15m_time = 0
pending_hourly_signal = None
pending_hourly_time = 0

@app.route('/webhook', methods=['POST'])
def webhook():
    global last_15m_signal, last_15m_time
    global pending_hourly_signal, pending_hourly_time

    data = request.json
    print("🚀 Webhook verisi alındı:", data)

    symbol = data.get('symbol')
    signal = data.get('signal')  # 'long' veya 'short'
    interval = data.get('interval')  # '1h' veya '15m'

    if not all([symbol, signal, interval]):
        return '❗ Geçersiz veri', 400

    current_time = time.time()

    if interval == "15m":
        last_15m_signal = signal
        last_15m_time = current_time
        print(f"⏱ 15dk sinyali güncellendi: {signal.upper()}")

        # Bekleyen bir saatlik sinyal varsa ve yönler eşleşiyorsa işleme geç
        if pending_hourly_signal and pending_hourly_signal == signal:
            print(f"✅ 1h ve 15m eşleşti: {signal.upper()} işlemi başlatılıyor...")
            subprocess.Popen(["python3", "autotrader.py", symbol, signal])
            pending_hourly_signal = None  # Temizle
            return '✅ Gecikmeli işlem açıldı', 200
        else:
            return 'ℹ️ 15m sinyali kaydedildi', 200

    elif interval == "1h":
        # 1h geldiğinde önceki 15m sinyali uyumluysa anında işlem aç
        if last_15m_signal == signal and (current_time - last_15m_time) < 3600:
            print(f"⚡ Uyumlu 15m bulundu → {signal.upper()} işlemi başlatılıyor...")
            subprocess.Popen(["python3", "autotrader.py", symbol, signal])
            return '✅ Hızlı işlem açıldı', 200
        else:
            # Eşleşme yok → beklemeye al
            pending_hourly_signal = signal
            pending_hourly_time = current_time
            print(f"⏳ Saatlik sinyal beklemeye alındı: {signal.upper()}")
            return '🕒 Beklemeye alındı, 15m sinyali beklenecek', 200

    return '❌ Tanımsız işlem', 400

if __name__ == '__main__':
    app.run(port=5000)
