import os
import requests

# Mengambil ID dan Token dari GitHub Secrets
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def tes_kirim():
    pesan = "🔥 *HALLO! TES NOTIFIKASI SCREENER BERHASIL!*\n\nSistem GitHub Actions & Bot Telegram kamu sudah 100% terhubung dan siap memburu saham IHSG hari Senin!"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": pesan, "parse_mode": "Markdown"}

    response = requests.post(url, json=payload)
    print("Status Code:", response.status_code)
    print("Response Telegram:", response.text)


if __name__ == "__main__":
    tes_kirim()
