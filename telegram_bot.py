import os
import requests

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def send_test_message():
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": "🔔 *TES NOTIFIKASI SCREENER SUCCESS!*\n\nBot Telegram kamu sudah terhubung sempurna dengan GitHub Actions! Siap memantau pasar saham Senin esok.",
        "parse_mode": "Markdown",
    }
    response = requests.post(url, json=payload)
    print("Response Status:", response.status_code)
    print("Response Body:", response.text)


if __name__ == "__main__":
    send_test_message()
