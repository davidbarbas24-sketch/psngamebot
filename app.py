from flask import Flask, request
import requests, os, re

app = Flask(__name__)

# Telegram
TOKEN = os.environ.get("TELEGRAM_TOKEN")
OWNER_CHAT_ID = os.environ.get("OWNER_CHAT_ID")
API_URL = f"https://api.telegram.org/bot{TOKEN}"

# WooCommerce
WC_URL = os.environ.get("WC_URL")
WC_KEY = os.environ.get("WC_KEY")
WC_SECRET = os.environ.get("WC_SECRET")

# זיכרון זמני למשתמשים
user_state = {}

def send(chat_id, text):
    requests.post(
        f"{API_URL}/sendMessage",
        json={"chat_id": chat_id, "text": text}
    )

# הודעות קבועות
WELCOME = "שלום 👋\nברוכים הבאים ל־PSNGAME 🎮\n..."
ASK_ISSUE_TYPE = "אשמח לעזור 👌\nאיזו תקלה יש לך?\n..."
ASK_CONSOLE = "על איזו קונסולה מדובר?\n..."
FIX_RESTORE = "🛠️ פתרון – Restore Licenses\n..."
FIX_PS4_PRIMARY = "🔓 הפעלת Primary PS4\n..."
FIX_PS5_PRIMARY = "🔓 הפעלת Console Sharing – PS5\n..."
HOW_TO_ORDER = "🛒 איך מזמינים?\n..."

BUY_TRIGGER = ["רוצה נציג", "דבר עם נציג", "אני רוצה לקנות"]

# פונקציה להבאת מחירים מהאתר
def get_prices():
    try:
        r = requests.get(f"{WC_URL}products", auth=(WC_KEY, WC_SECRET), timeout=5)
        r.raise_for_status()
        data = r.json()
        if not data:
            return "⚠️ לא נמצאו מוצרים באתר"
        msg = "💰 מחירים:\n\n"
        for product in data:
            name = product.get("name", "לא ידוע")
            price = product.get("price", "לא זמין")
            msg += f"{name}: {price}₪\n"
        return msg
    except Exception as e:
        print("WC API Error:", e)
        return f"⚠️ לא הצלחתי להביא מחירים: {e}"

@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    if not data or "message" not in data:
        return "ok"

    msg = data["message"]
    chat_id = msg["chat"]["id"]
    raw = msg.get("text", "")
    text = re.sub(r"[^\w\s]", "", raw.lower())

    # בדיקה אם הלקוח רוצה נציג
    if any(x in text for x in BUY_TRIGGER):
        send(OWNER_CHAT_ID, f"📥 לקוח צריך נציג\n👤 @{msg['from'].get('username')}\n💬 {raw}")
        send(chat_id, "מעביר אותך לנציג 👤")
        user_state.pop(chat_id, None)
        return "ok"

    # בדיקה אם המשתמש שואל על מחיר
    if "מחיר" in text or "כמה עולה" in text:
        send(chat_id, get_prices())
        return "ok"

    # התחלת תהליך תקלה
    if "תקלה" in text or "לא עובד" in text or "בעיה" in text:
        user_state[chat_id] = {"step": "issue_type"}
        send(chat_id, ASK_ISSUE_TYPE)
        return "ok"

    # שלב 1 – סוג תקלה
    if chat_id in user_state and user_state[chat_id]["step"] == "issue_type":
        user_state[chat_id]["issue"] = text
        user_state[chat_id]["step"] = "console"
        send(chat_id, ASK_CONSOLE)
        return "ok"

    # שלב 2 – קונסולה
    if chat_id in user_state and user_state[chat_id]["step"] == "console":
        issue = user_state[chat_id]["issue"]
        user_state.pop(chat_id)

        if "ps4" in text:
            send(chat_id, FIX_RESTORE + "\n\n" + FIX_PS4_PRIMARY)
        elif "ps5" in text:
            send(chat_id, FIX_RESTORE + "\n\n" + FIX_PS5_PRIMARY)
        else:
            send(chat_id, "לא זיהיתי קונסולה, נסה לכתוב PS4 או PS5")

        send(chat_id, "\nאם זה לא פתר את הבעיה – כתבו: רוצה נציג")
        return "ok"

    if "איך מזמינים" in text or "הזמנה" in text:
        send(chat_id, HOW_TO_ORDER)
        return "ok"

    send(chat_id, WELCOME)
    return "ok"

@app.route("/", methods=["GET"])
def index():
    return "Bot is running"

if __name__ == "__main__":
    # תיקון PORT
    port = os.environ.get("PORT")
    if not port:
        port = 5000
    else:
        port = int(port)

    app.run(host="0.0.0.0", port=port)
