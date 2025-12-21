from flask import Flask, request
import requests, os, re

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN")
OWNER_CHAT_ID = os.environ.get("OWNER_CHAT_ID")
API_URL = f"https://api.telegram.org/bot{TOKEN}"

# זיכרון זמני למשתמשים
user_state = {}

def send(chat_id, text):
    requests.post(
        f"{API_URL}/sendMessage",
        json={"chat_id": chat_id, "text": text}
    )

WELCOME = (
    "שלום 👋\n"
    "ברוכים הבאים ל־PSNGAME 🎮\n\n"
    "אפשר לעזור ב:\n"
    "• איך זה עובד\n"
    "• התקנה PS4 / PS5\n"
    "• תקלות ועזרה\n"
    "• תשלום והזמנה\n\n"
    "פשוט כתבו מה אתם צריכים 🙂"
)

ASK_ISSUE_TYPE = (
    "אשמח לעזור 👌\n"
    "איזו תקלה יש לך?\n\n"
    "אפשר לכתוב למשל:\n"
    "• המשחק לא עובד\n"
    "• המשחק ננעל\n"
    "• מבקש רישיון\n"
    "• בעיית התקנה"
)

ASK_CONSOLE = (
    "על איזו קונסולה מדובר?\n"
    "כתוב:\n"
    "• PS4\n"
    "• PS5"
)

FIX_RESTORE = (
    "🛠️ פתרון – Restore Licenses\n\n"
    "1️⃣ היכנס להגדרות\n"
    "2️⃣ Account Management\n"
    "3️⃣ Restore Licenses\n"
    "4️⃣ אשר וחכה לסיום\n\n"
    "לאחר מכן הפעל מחדש את הקונסולה."
)

FIX_PS4_PRIMARY = (
    "🔓 הפעלת Primary PS4\n\n"
    "1️⃣ היכנס לחשבון שקיבלת\n"
    "2️⃣ Settings → Account Management\n"
    "3️⃣ Activate as your Primary PS4\n"
    "4️⃣ Activate\n"
    "5️⃣ Restore Licenses\n\n"
    "לאחר מכן חזור למשתמש הראשי."
)

FIX_PS5_PRIMARY = (
    "🔓 הפעלת Console Sharing – PS5\n\n"
    "1️⃣ Settings → Users and Accounts\n"
    "2️⃣ Other → Console Sharing\n"
    "3️⃣ Enable\n\n"
    "כבה והדלק את הקונסולה בסיום."
)

HOW_TO_ORDER = (
    "🛒 איך מזמינים?\n\n"
    "אפשר להזמין עצמאית באתר:\n"
    "https://psngame.com\n\n"
    "או אם תרצו נציג שילווה אתכם – כתבו:\n"
    "רוצה נציג"
)

BUY_TRIGGER = ["רוצה נציג", "דבר עם נציג", "אני רוצה לקנות"]

@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    if not data or "message" not in data:
        return "ok"

    msg = data["message"]
    chat_id = msg["chat"]["id"]
    raw = msg.get("text", "")
    text = re.sub(r"[^\w\s]", "", raw.lower())

    # מעבר לנציג
    if any(x in text for x in BUY_TRIGGER):
        send(OWNER_CHAT_ID, f"📥 לקוח צריך נציג\n👤 @{msg['from'].get('username')}\n💬 {raw}")
        send(chat_id, "מעביר אותך לנציג 👤")
        user_state.pop(chat_id, None)
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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
