from flask import Flask, request
import requests
import os
import re

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OWNER_CHAT_ID = os.environ.get("OWNER_CHAT_ID")
API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def send_message(chat_id, text):
    requests.post(
        f"{API_URL}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": True
        }
    )

# ===== נושאים + מילות מפתח =====
TOPICS = [
    {
        "keywords": ["מה זה", "חשבון", "פרופיל", "איך זה עובד", "account"],
        "answer": (
            "🎮 משחק דיגיטלי כחשבון / פרופיל\n\n"
            "אתם מקבלים חשבון PSN עם המשחק או החבילה שרכשתם.\n"
            "✔ משחקים מהחשבון הפרטי שלכם\n"
            "✔ גביעים, אונליין ועדכונים כרגיל\n\n"
            "⚠️ אין לשנות אימייל או סיסמה.\n"
            "כל עוד הפרטים נשמרים – אתם מכוסים באחריות מלאה."
        )
    },
    {
        "keywords": ["התקנה", "מתקין", "להתקין", "download"],
        "answer": (
            "📥 התקנת משחקים PS4 / PS5\n\n"
            "1️⃣ מוסיפים משתמש חדש בקונסולה\n"
            "2️⃣ נכנסים עם הפרטים שקיבלתם במייל\n"
            "3️⃣ מורידים את המשחק מהספריה\n"
            "4️⃣ חוזרים למשתמש הפרטי ומשחקים 🎮\n\n"
            "מדריכים מלאים לפי קונסולה זמינים באתר."
        )
    },
    {
        "keywords": ["אחריות", "בעיה", "לא עובד", "תקלה"],
        "answer": (
            "🛡️ אחריות ותקלות\n\n"
            "יש אחריות מלאה על תקינות החשבון.\n"
            "❗ שינוי אימייל או סיסמה מבטל אחריות.\n\n"
            "לפני פנייה:\n"
            "• כיבוי והדלקה של הקונסולה\n"
            "• בדיקת אינטרנט\n"
            "• Restore Licenses"
        )
    },
    {
        "keywords": ["לא קיבלתי", "לא הגיע", "אימייל", "משלוח"],
        "answer": (
            "📧 לא קיבלתם את החשבון?\n\n"
            "אספקה רגילה: עד 24 שעות\n"
            "בעומסים: עד 72 שעות\n\n"
            "בדקו ספאם / קידומי מכירות.\n"
            "אם עדיין לא הגיע – צוות התמיכה כאן."
        )
    },
    {
        "keywords": ["תשלום", "איך משלמים", "מחיר", "pay"],
        "answer": (
            "💳 אמצעי תשלום\n\n"
            "✅ ביט\n"
            "✅ העברה בנקאית\n"
            "✅ PayPal\n"
            "✅ BTC\n"
            "✅ שליח עד הבית (בתוספת תשלום)"
        )
    },
    {
        "keywords": ["התקנה אישית", "מישהו שיתקין", "עזרה בהתקנה"],
        "answer": (
            "👨‍🔧 התקנה אישית ללקוח\n\n"
            "איסוף הקונסולה → התקנה → החזרה עם המשחקים מותקנים.\n"
            "השירות בתשלום נוסף."
        )
    }
]

TRIGGER_WORDS = [
    "לקנות", "רכישה", "להזמין", "קנייה",
    "buy", "order", "purchase"
]

WELCOME_MESSAGE = (
    "שלום 👋\n"
    "ברוכים הבאים ל־PSNGAME 🎮\n\n"
    "אפשר לשאול אותי על:\n"
    "• איך זה עובד\n"
    "• התקנה PS4 / PS5\n"
    "• אחריות ותקלות\n"
    "• אמצעי תשלום\n\n"
    "כשתרצו לרכוש – אני מחבר לנציג.\n\n"
    "🌐 https://psngame.com"
)

@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    if not data or "message" not in data:
        return "ok"

    msg = data["message"]
    chat_id = msg["chat"]["id"]

    raw_text = msg.get("text", "")
    text = re.sub(r"[^\w\s]", "", raw_text.lower())

    # מעבר לנציג
    if any(word in text for word in TRIGGER_WORDS):
        send_message(
            OWNER_CHAT_ID,
            f"📥 פנייה חדשה\n👤 @{msg['from'].get('username')}\n💬 {raw_text}"
        )
        send_message(chat_id, "מעביר אותך לנציג מכירות 👤")
        return "ok"

    # תשובות לפי נושא
    for topic in TOPICS:
        if any(k in text for k in topic["keywords"]):
            send_message(chat_id, topic["answer"] + "\n\n🌐 https://psngame.com")
            return "ok"

    # ברירת מחדל
    send_message(chat_id, WELCOME_MESSAGE)
    return "ok"

@app.route("/", methods=["GET"])
def index():
    return "Bot is running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
