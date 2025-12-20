from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OWNER_CHAT_ID = os.environ.get("OWNER_CHAT_ID")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def send_message(chat_id, text):
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={"chat_id": chat_id, "text": text}
    )

@app.route("/", methods=["POST"])
def webhook():
    data = request.json

    if not data or "message" not in data:
        return "ok"

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    trigger_words = [
        "לקנות", "להזמין", "רכישה",
        "לא עובד", "תקלה", "בעיה",
        "buy", "order", "not working", "issue"
    ]

    if any(word in text.lower() for word in trigger_words):
        summary = (
            "📥 פנייה חדשה\n"
            f"👤 משתמש: @{message['from'].get('username')}\n"
            f"💬 הודעה: {text}"
        )
        send_message(OWNER_CHAT_ID, summary)
        send_message(chat_id, "מעביר אותך לנציג, הוא ימשיך איתך עכשיו 👤")
        return "ok"

    reply = (
        "שלום 👋\n"
        "ברוכים הבאים ל-PSNGAME!\n\n"
        "אפשר לשאול אותי על:\n"
        "🎮 משחקים\n"
        "🔥 מבצעים וחבילות\n"
        "❓ עזרה בתקלות\n\n"
        "כשתרצה להזמין – אני מחבר אותך לנציג."
    )

    send_message(chat_id, reply)
    return "ok"

@app.route("/", methods=["GET"])
def index():
    return "Bot is running"

if __name__ == "__main__":
    app.run()
