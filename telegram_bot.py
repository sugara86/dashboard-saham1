
import io
import os
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import requests
import ta
import yfinance as yf

# ==========================================
# 1. KONFIGURASI TELEGRAM (DARI GITHUB SECRETS)
# ==========================================
TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

# ==========================================
# 2. DAFTAR PORTOFOLIO SAHAM YANG ANDA PEGANG
# Ubah harga beli, stop loss, & target jual sesuai kepemilikan Anda
# ==========================================
MY_PORTFOLIO = {
    "ANTM.JK": {
        "buy_price": 1500,  # Harga rata-rata beli Anda
        "stop_loss_pct": -2.0,  # Alert jika rugi >= -2%
        "target_price": 1600,  # Target harga jual (Take Profit)
    },
    "MEDC.JK": {
        "buy_price": 1300,
        "stop_loss_pct": -2.0,
        "target_price": 1400,
    },
}

# ==========================================
# 3. DAFTAR SAHAM UNTUK SCREENER DAN GLOBAL
# ==========================================
GLOBAL_MARKETS = {
    "S&P 500 (US)": "^GSPC",
    "Nasdaq (US)": "^IXIC",
    "Nikkei 225 (Jepang)": "^N225",
    "Hang Seng (HK/Cina)": "^HSI",
    "Minyak Mentah (WTI)": "CL=F",
    "Emas Dunia": "GC=F",
    "USD / IDR": "IDR=X",
}

SAHAM_IHSG = [
    "BBCA.JK",
    "BBRI.JK",
    "BMRI.JK",
    "BBNI.JK",
    "TLKM.JK",
    "ASII.JK",
    "ANTM.JK",
    "PGAS.JK",
    "UNTR.JK",
    "AMRT.JK",
    "GOTO.JK",
    "ADRO.JK",
    "PTBA.JK",
    "MEDC.JK",
    "BRIS.JK",
    "MDKA.JK",
    "INKP.JK",
    "CPIN.JK",
    "ICBP.JK",
    "KLBF.JK",
]


# ==========================================
# 4. FUNGSI PENGIRIMAN TELEGRAM
# ==========================================
def clean_token():
    t = TOKEN.replace(" ", "")
    return t[3:] if t.startswith("bot") else t


def send_telegram_text(text):
    url = f"https://api.telegram.org/bot{clean_token()}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Gagal kirim pesan teks: {e}")


def send_telegram_photo(photo_bytes, caption):
    url = f"https://api.telegram.org/bot{clean_token()}/sendPhoto"
    files = {"photo": ("chart.png", photo_bytes, "image/png")}
    data = {"chat_id": CHAT_ID, "caption": caption, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=data, files=files)
    except Exception as e:
        print(f"Gagal kirim foto: {e}")


# ==========================================
# 5. FUNGSI MEMBUAT GRAFIK/CHART TEKNIS
# ==========================================
def generate_chart(df, ticker):
    plt.figure(figsize=(8, 5))

    # Subplot 1: Price & MA5
    plt.subplot(2, 1, 1)
    plt.plot(df.index[-20:], df["Close"].tail(20), label="Close", color="blue")
    plt.plot(df.index[-20:], df["MA5"].tail(20), label="MA5", color="orange")
    plt.title(f"Chart Teknis {ticker.replace('.JK', '')}")
    plt.legend(loc="upper left")
    plt.grid(True)

    # Subplot 2: RSI
    plt.subplot(2, 1, 2)
    plt.plot(df.index[-20:], df["RSI"].tail(20), label="RSI(14)", color="purple")
    plt.axhline(70, linestyle="--", color="red", alpha=0.5)  # Overbought
    plt.axhline(30, linestyle="--", color="green", alpha=0.5)  # Oversold
    plt.legend(loc="upper left")
    plt.grid(True)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()
    return buf


# ==========================================
# 6. FUNGSI PEMANTAUAN PORTOFOLIO (CUT LOSS & TAKE PROFIT)
# ==========================================
def check_portfolio():
    print("Memeriksa status portofolio saham yang dipegang...")
    for ticker, info in MY_PORTFOLIO.items():
        try:
            df = yf.Ticker(ticker).history(period="2d")
            if df.empty:
                continue

            current_price = df["Close"].iloc[-1]
            buy_price = info["buy_price"]
            target_price = info["target_price"]
            pnl_pct = ((current_price - buy_price) / buy_price) * 100
            kode = ticker.replace(".JK", "")

            # Alert Cut Loss
            if pnl_pct <= info["stop_loss_pct"]:
                msg = (
                    f"🛑 *ALERT CUT LOSS: {kode}*\n"
                    f"• Harga Beli Anda: Rp{buy_price:,}\n"
                    f"• Harga Sekarang: Rp{int(current_price):,}\n"
                    f"• Posisi Rugi: *{pnl_pct:.2f}%*\n\n"
                    f"⚠️ *SARAN:* Pertimbangkan JUAL / CUT LOSS untuk amankan modal!"
                )
                send_telegram_text(msg)

            # Alert Take Profit
            elif current_price >= target_price:
                msg = (
                    f"🎯 *ALERT TAKE PROFIT: {kode}*\n"
                    f"• Harga Beli Anda: Rp{buy_price:,}\n"
                    f"• Harga Sekarang: Rp{int(current_price):,}\n"
                    f"• Keuntungan: *+{pnl_pct:.2f}%*\n\n"
                    f"💰 *SARAN:* Target harga Rp{target_price:,} tercapai. Siap-siap JUAL untuk amankan CUAN!"
                )
                send_telegram_text(msg)
        except Exception as e:
            print(f"Error portfolio {ticker}: {e}")


# ==========================================
# 7. FUNGSI PASAR GLOBAL & BERITA
# ==========================================
def get_global_data():
    results = []
    for name, ticker in GLOBAL_MARKETS.items():
        try:
            data = yf.Ticker(ticker).history(period="2d")
            if len(data) >= 2:
                c_now = data["Close"].iloc[-1]
                c_prev = data["Close"].iloc[-2]
                chg = ((c_now - c_prev) / c_prev) * 100
                icon = "🟢" if chg >= 0 else "🔴"
                results.append(f"{icon} *{name}*: {chg:+.2f}%")
        except Exception:
            pass
    return "\n".join(results) if results else "Data global tidak tersedia."


def get_market_news():
    url = "https://news.google.com/rss/search?q=saham+IHSG+ekonomi+indonesia&hl=id&gl=ID&ceid=ID:id"
    items = []
    try:
        res = requests.get(url, timeout=10)
        root = ET.fromstring(res.content)
        for item in root.findall("./channel/item")[:3]:
            title = item.find("title").text
            items.append(f"📰 • {title}")
    except Exception:
        items.append("📰 Tidak dapat mengambil berita terbaru.")
    return "\n".join(items)


# ==========================================
# 8. FUNGSI UTAMA (MAIN RUNNER)
# ==========================================
def main():
    print("Memulai analisa komprehensif...")

    # 1. Kirim Laporan Global & Berita Lebih Dulu
    global_text = get_global_data()
    news_text = get_market_news()

    header_report = (
        "🌐 *DASHBOARD PASAR GLOBAL & REGIONAL*\n"
        "------------------------------------\n"
        f"{global_text}\n\n"
        "📰 *BERITA & SENTIMEN TERBARU*\n"
        "------------------------------------\n"
        f"{news_text}"
    )
    send_telegram_text(header_report)

    # 2. Cek Kesehatan Portofolio Pribadi
    check_portfolio()

    # 3. Jalankan Screener Saham & Kirim Chart jika Lolos
    print("Memulai pemindaian saham IHSG...")
    for ticker in SAHAM_IHSG:
        try:
            df = yf.Ticker(ticker).history(period="2m")
            if len(df) < 20:
                continue

            df["MA5"] = df["Close"].rolling(window=5).mean()
            df["RSI"] = ta.momentum.rsi(df["Close"], window=14)

            close_now = df["Close"].iloc[-1]
            close_prev = df["Close"].iloc[-2]
            volume_now = df["Volume"].iloc[-1]
            volume_avg = df["Volume"].tail(20).mean()
            ma5_now = df["MA5"].iloc[-1]
            rsi_now = df["RSI"].iloc[-1]

            price_change = ((close_now - close_prev) / close_prev) * 100
            vol_ratio = volume_now / volume_avg if volume_avg > 0 else 0

            # Kriteria: Price >= 1.5%, Vol Ratio >= 1.2x, Price > MA5, RSI < 70
            if (
                price_change >= 1.5
                and vol_ratio >= 1.2
                and close_now > ma5_now
                and rsi_now < 70
            ):
                kode = ticker.replace(".JK", "")
                chart_img = generate_chart(df, ticker)

                caption = (
                    f"🚀 *MOMENTUM SIGNAL: {kode}*\n"
                    f"• Harga: Rp{int(close_now):,}\n"
                    f"• Kenaikan: *+{price_change:.2f}%*\n"
                    f"• Vol Ratio: *{vol_ratio:.2f}x*\n"
                    f"• RSI (14): *{rsi_now:.1f}* (Zona Aman < 70)\n"
                    f"• Posisi: Di atas MA5\n\n"
                    f"💡 _Cek Bid/Offer & VWAP di aplikasi sekuritas sebelum entry!_"
                )
                send_telegram_photo(chart_img, caption)
                print(f"Sinyal + Chart terkirim untuk {kode}")
        except Exception as e:
            print(f"Error {ticker}: {e}")


if __name__ == "__main__":
    main()
