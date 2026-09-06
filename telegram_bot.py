
import os
import requests

# Mengambil variabel dari GitHub Secrets
raw_token = os.environ.get("TELEGRAM_TOKEN", "").strip()
chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

# Membersihkan token dari spasi atau awalan/akhiran yang salah
token = raw_token.replace(" ", "")
if token.startswith("bot"):
    token = token[3:]


def test_telegram():
    # Memastikan format URL benar
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": "🔥 *TES NOTIFIKASI TELEGRAM BERHASIL!*\n\nScript Python kamu sudah 100% terhubung dengan Bot Telegram!",
        "parse_mode": "Markdown",
    }

    print("Sending request to Telegram...")
    response = requests.post(url, json=payload)

    print(f"Status Code: {response.status_code}")
    print(f"Response Telegram: {response.text}")


if __name__ == "__main__":
    test_telegram()
