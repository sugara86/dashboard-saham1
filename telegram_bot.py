import os
import requests
import yfinance as yf

# Token & Chat ID dari Telegram
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Universe Saham Aktif IHSG
ihsg_universe = {
    "TINS.JK": "Timah / Tembaga",
    "MEDC.JK": "Minyak Mentah",
    "MDKA.JK": "Emas & Tembaga",
    "ANTM.JK": "Emas & Nikel",
    "PTBA.JK": "Batu Bara",
    "ADRO.JK": "Batu Bara",
    "GGRM.JK": "Rokok / Consumer",
    "FILM.JK": "Hiburan / Media",
    "GOTO.JK": "Teknologi",
    "BBCA.JK": "Bank Perbankan",
    "BBRI.JK": "Bank Perbankan",
    "BRIS.JK": "Bank Syariah",
}


def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
    }
    requests.post(url, json=payload)


def scan_market():
    alerts = []
    for symbol, sektor in ihsg_universe.items():
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="10d")
            if len(df) >= 5:
                last_price = df["Close"].iloc[-1]
                prev_price = df["Close"].iloc[-2]
                change_pct = ((last_price - prev_price) / prev_price) * 100

                today_vol = df["Volume"].iloc[-1]
                avg_vol = df["Volume"].iloc[-5:-1].mean()
                vol_spike = (today_vol / avg_vol) if avg_vol > 0 else 1.0

                # Kriteria Alert Telegram (Naik > 2% DAN Volume Ratio > 1.2x)
                if change_pct >= 2.0 and vol_spike >= 1.2:
                    kode = symbol.replace(".JK", "")
                    alerts.append(
                        f"🚀 *ALERTI DAY TRADE: {kode}*\n"
                        f"• Harga: Rp {int(last_price)} ({round(change_pct, 2)}%)\n"
                        f"• Rasio Volume: {round(vol_spike, 1)}x (Spike!)\n"
                        f"• Sektor: {sektor}\n"
                    )
        except Exception:
            pass

    if alerts:
        msg = (
            "🔔 *SIGNAL SCREENER BELI PAGI (IHSG)*\n\n"
            + "\n---\n".join(alerts)
        )
        send_telegram_msg(msg)


if __name__ == "__main__":
    scan_market()
