# Binance Futures Trading Bot

## Kurulum
1. `.env` dosyasını oluştur ve API bilgilerini gir.
2. Render'da yeni Web Service aç, bu dosyaları yükle.
3. TradingView alarm webhook'unu şu şekilde ayarla:
   - URL: `https://<render-app-name>.onrender.com/webhook`
   - Mesaj: `{ "signal": "LONG" }` veya `{ "signal": "SHORT" }`

## Not
Bu temel versiyon sadece işlem açar. TP/SL ve takip mekanikleri bir sonraki aşamada eklenecektir.