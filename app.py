from flask import Flask, request
import requests
import os

app = Flask(__name__)

# טוקן הבוט וצ'אט של המנהל
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OWNER_CHAT_ID = os.environ.get("OWNER_CHAT_ID")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# מילון שאלות ותשובות
qna = {
    "מה זה משחק פלייסטיישן שמגיע כחשבון/פרופיל": "משתמש טעון בחבילה או המשחק שבחרתם. שחקו מהפרופיל הפרטי שלכם. הרוויחו גביעים, שחקו ברשת, קבלו עדכונים...",
    "איך מתקינים משחק פלייסטיישן 4/5 מתוך חשבון": "להסבר על התקנת המשחקים אנא כנסו ללשונית מדריכים באתר PSNGAME.COM, שם תמצאו מדריכי התקנה ל-2 הקונסולות.",
    "האם יש לי אחריות על תקינות החשבון": "יש אחריות מלאה לתקינות החשבון. אין לשנות את פרטי הכניסה (דוא\"ל+סיסמה) של חשבון PSN.",
    "לא קיבלתי את חשבון לאחר הרכישה": "משלוח של חשבון יכול לקחת עד 24 שעות, לפעמים עד 72 שעות במייל הפרטי. בדקו ספאם. אם לא קיבלתם - פנו לצוות התמיכה.",
    "כיצד ניתן לשלם": "✅ ביט, ✅ העברה בנקאית, ✅ PayPal, ✅ BTC, ✅ שליח עד הבית (תוספת תשלום).",
    "האם אפשר לשלוח מישהו שיעזור לי להתקין את המשחקים": "ניתן לתאם התקנה אישית ללקוח, כולל תשלום נוסף."
}

# פונקציה לשליחת הודעות לטלגרם
def send_message(chat_id, text):
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={"chat_id": chat_id, "text": text}
    )

# Webhook לטלגרם
@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    if not data or "message" not in data:
        return "ok"

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "").lower()

    # מילת טריגר לפנייה אל מנהל
    trigger_words = ["לקנות", "להזמין", "רכישה", "buy", "order"]
    
    if any(word in text for word in trigger_words):
        summary = (
            "📥 פנייה חדשה\n"
            f"👤 משתמש: @{message['from'].get('username')}\n"
            f"💬 הודעה: {text}"
        )
        send_message(OWNER_CHAT_ID, summary)
        send_message(chat_id, "מעביר אותך לנציג, הוא ימשיך איתך עכשיו 👤")
        return "ok"

    # בדיקה במילון שאלות ותשובות
    for question, answer in qna.items():
        if question.lower() in text:
            send_message(chat_id, answer)
            return "ok"

    # הודעה פתיחה למי שלא מזוהה
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

# בדיקה ב־GET
@app.route("/", methods=["GET"])
def index():
    return "Bot is running"

# הפעלה נכונה ל־Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
