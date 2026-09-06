import os
import requests
import yfinance as yf

# Mengambil token dan chat ID dari GitHub Secrets
TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

# Daftar Saham IHSG Populer & Likuid untuk Dipindai (bisa ditambah/dikurangi)
DAFTAR_SAHAM = [
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


def send_telegram_message(message):
    """Fungsi untuk mengirimkan pesan teks ke Telegram"""
    token = TOKEN.replace(" ", "")
    if token.startswith("bot"):
        token = token[3:]

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}

    try:
        res = requests.post(url, json=payload)
        print(f"Status Kirim Telegram: {res.status_code}")
    except Exception as e:
        print(f"Gagal mengirim pesan: {e}")


def run_screener():
    """Fungsi utama memindai saham IHSG"""
    print("Mulai memindai saham IHSG...")
    saham_lolos = []

    for ticker in DAFTAR_SAHAM:
        try:
            # Mengambil data harga harian 1 bulan terakhir
            stock = yf.Ticker(ticker)
            df = stock.history(period="1m")

            if len(df) < 5:
                continue

            # Menghitung Indikator
            close_now = df["Close"].iloc[-1]
            close_prev = df["Close"].iloc[-2]
            volume_now = df["Volume"].iloc[-1]
            volume_avg = df["Volume"].tail(20).mean()  # Rata-rata Volume 20 Hari
            ma5 = df["Close"].tail(5).mean()  # Moving Average 5 Hari

            # Perhitungan Persentase Perubahan Harga & Ratio Volume
            price_change_pct = ((close_now - close_prev) / close_prev) * 100
            volume_ratio = (
                volume_now / volume_avg if volume_avg > 0 else 0
            )

            # --- KRITERIA SCREENER DAY TRADING ---
            # 1. Kenaikan harga > 1.5%
            # 2. Volume Ratio > 1.2x (Ada lonjakan volume)
            # 3. Harga berada di atas MA5 (Tren Naik)
            if (
                price_change_pct >= 1.5
                and volume_ratio >= 1.2
                and close_now > ma5
            ):
                kode_saham = ticker.replace(".JK", "")
                saham_lolos.append(
                    f"🚀 *{kode_saham}*\n"
                    f"• Harga: Rp{int(close_now):,}\n"
                    f"• Kenaikan: *+{price_change_pct:.2f}%*\n"
                    f"• Vol Ratio: *{volume_ratio:.2f}x*\n"
                    f"• Posisi: Di atas MA5 (Rp{int(ma5):,})\n"
                )
        except Exception as e:
            print(f"Error scan {ticker}: {e}")

    # --- MEMBENTUK PESAN LAPORAN ---
    if saham_lolos:
        pesan_akhir = (
            "📊 *HASIL SCREENER SAHAM IHSG HARIAN*\n"
            "------------------------------------\n"
            + "\n".join(saham_lolos)
            + "\n💡 _Selalu cek Chart Intraday & Orderbook sebelum entry!_"
        )
    else:
        pesan_akhir = (
            "📢 *LAPORAN SCREENER SAHAM*\n\n"
            "Tidak ditemukan saham yang memenuhi kriteria (Screener Sepi / Pasar Tutup)."
        )

    print(pesan_akhir)
    send_telegram_message(pesan_akhir)


if __name__ == "__main__":
    run_screener()
