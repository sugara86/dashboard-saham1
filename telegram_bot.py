import xml.etree.ElementTree as ET
import os
import requests
import yfinance as yf

# Token & Chat ID dari GitHub Secrets
TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

# Daftar Ticker Global, Komoditas & Mata Uang
GLOBAL_MARKETS = {
    "S&P 500 (US)": "^GSPC",
    "Nasdaq (US)": "^IXIC",
    "Nikkei 225 (Jepang)": "^N225",
    "Hang Seng (Cina/HK)": "^HSI",
    "Minyak Mentah (WTI)": "CL=F",
    "Emas Dunia": "GC=F",
    "USD / IDR": "IDR=X",
}

# Daftar Saham Likuid IHSG
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


def send_telegram(message):
    token = TOKEN.replace(" ", "")
    if token.startswith("bot"):
        token = token[3:]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error Send Telegram: {e}")


def get_global_data():
    """Mengambil Pergerakan Bursa AS, Asia, Komoditas & Kurs"""
    results = []
    for name, ticker in GLOBAL_MARKETS.items():
        try:
            data = yf.Ticker(ticker).history(period="2d")
            if len(data) >= 2:
                close_now = data["Close"].iloc[-1]
                close_prev = data["Close"].iloc[-2]
                change_pct = ((close_now - close_prev) / close_prev) * 100
                icon = "🟢" if change_pct >= 0 else "🔴"
                results.append(f"{icon} *{name}*: {change_pct:+.2f}%")
        except Exception:
            pass
    return "\n".join(results) if results else "Data global tidak tersedia."


def get_market_news():
    """Mengambil Headline Berita Saham IHSG Terbaru via Google News RSS"""
    url = "https://news.google.com/rss/search?q=saham+IHSG+ekonomi+indonesia&hl=id&gl=ID&ceid=ID:id"
    news_items = []
    try:
        res = requests.get(url, timeout=10)
        root = ET.fromstring(res.content)
        for item in root.findall("./channel/item")[:3]:
            title = item.find("title").text
            news_items.append(f"📰 • {title}")
    except Exception:
        news_items.append("📰 Tidak dapat mengambil berita terbaru saat ini.")
    return "\n".join(news_items)


def run_full_screener():
    print("Memproses Analisa Pasar Global & IHSG...")

    # 1. Analisa Pasar Global
    global_text = get_global_data()

    # 2. Berita Ter-update
    news_text = get_market_news()

    # 3. Screener Saham IHSG
    saham_lolos = []
    for ticker in SAHAM_IHSG:
        try:
            df = yf.Ticker(ticker).history(period="1m")
            if len(df) < 5:
                continue

            close_now = df["Close"].iloc[-1]
            close_prev = df["Close"].iloc[-2]
            volume_now = df["Volume"].iloc[-1]
            volume_avg = df["Volume"].tail(20).mean()
            ma5 = df["Close"].tail(5).mean()

            price_change = ((close_now - close_prev) / close_prev) * 100
            vol_ratio = volume_now / volume_avg if volume_avg > 0 else 0

            # Kriteria: Kenaikan >= 1.5%, Volume Spike >= 1.2x, di atas MA5
            if price_change >= 1.5 and vol_ratio >= 1.2 and close_now > ma5:
                kode = ticker.replace(".JK", "")
                saham_lolos.append(
                    f"🚀 *{kode}* | Rp{int(close_now):,} | *+{price_change:.2f}%* | Vol: *{vol_ratio:.2f}x*"
                )
        except Exception:
            pass

    ihsg_text = (
        "\n".join(saham_lolos)
        if saham_lolos
        else "⚠️ Belum ada saham lokal yang memenuhi syarat (Pasar sepi/tutup)."
    )

    # 4. Merakit Laporan Akhir
    report = (
        "🌐 *DASHBOARD PASAR GLOBAL & REGIONAL*\n"
        "------------------------------------\n"
        f"{global_text}\n\n"
        "📰 *BERITA & SENTIMEN TERBARU*\n"
        "------------------------------------\n"
        f"{news_text}\n\n"
        "📊 *SCREENER MOMENTUM SAHAM IHSG*\n"
        "------------------------------------\n"
        f"{ihsg_text}\n\n"
        "💡 _Analisa otomatis dikirim via GitHub Actions._"
    )

    print(report)
    send_telegram(report)


if __name__ == "__main__":
    run_full_screener()
