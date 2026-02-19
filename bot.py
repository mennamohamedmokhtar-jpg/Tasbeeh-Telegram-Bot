# -*- coding: utf-8 -*-
# ===================== IMPORTS =====================
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os, time, json

# ===================== CONFIG =====================
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
DATA_FILE = "data.json"
ADMIN_ID = 5123695463  # ضع هنا رقمك من @userinfobot

# ===================== DATA =====================
DEFAULT_DATA = {"users": {}}

# --------- أذكار تصاعدية (تسبيح) ---------
AZKAR_TASBEEH = {
    "tasbeeh": {"name": "سبحان الله", "emoji": "🟢"},
    "tahmeed": {"name": "الحمد لله", "emoji": "🔵"},
    "takbeer": {"name": "الله أكبر", "emoji": "🟣"},
    "tahleel": {"name": "لا إله إلا الله", "emoji": "🟠"},
    "istighfar": {"name": "أستغفر الله", "emoji": "🟡"},
    "salat": {"name": "اللهم صلِّ على محمد ﷺ", "emoji": "🤍"},
    "hawqala": {"name": "لا حول ولا قوة إلا بالله", "emoji": "🟤"},
    "hirz": {"name": "بسم الله الذي لا يضر مع اسمه شيء في الأرض ولا في السماء وهو السميع العليم", "emoji": "🛡️"}
}

# --------- أذكار ثابتة (تنازلية تلقائية) ---------
AZKAR_FIXED = {
    "sabah": {
        "title": "🌅 أذكار الصباح",
        "list": [
            {"text": "أصبحنا وأصبح الملك لله", "count": 1},
            {"text": "اللهم بك أصبحنا وبك أمسينا", "count": 1},
            {"text": "سبحان الله وبحمده", "count": 100},
            {"text": "لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير", "count": 10}
        ]
    },
    "masaa": {
        "title": "🌙 أذكار المساء",
        "list": [
            {"text": "أمسينا وأمسى الملك لله", "count": 1},
            {"text": "اللهم بك أمسينا وبك أصبحنا", "count": 1},
            {"text": "سبحان الله وبحمده", "count": 100},
            {"text": "أعوذ بكلمات الله التامات من شر ما خلق", "count": 3}
        ]
    },
    "sleep": {
        "title": "😴 أذكار النوم",
        "list": [
            {"text": "باسمك ربي وضعت جنبي", "count": 1},
            {"text": "آية الكرسي", "count": 1},
            {"text": "سبحان الله", "count": 33},
            {"text": "الحمد لله", "count": 33},
            {"text": "الله أكبر", "count": 34}
        ]
    },
    "after_salat": {
        "title": "🕌 أذكار بعد الصلاة",
        "list": [
            {"text": "أستغفر الله", "count": 3},
            {"text": "اللهم أنت السلام ومنك السلام", "count": 1},
            {"text": "سبحان الله", "count": 33},
            {"text": "الحمد لله", "count": 33},
            {"text": "الله أكبر", "count": 34}
        ]
    }
}

# ===================== STORAGE =====================
def load_data():
    if not os.path.exists(DATA_FILE):
        save_data(DEFAULT_DATA)
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return DEFAULT_DATA.copy()

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

DATA = load_data()

def get_user(uid):
    uid = str(uid)
    if uid not in DATA["users"]:
        DATA["users"][uid] = {
            "counts": {k: 0 for k in AZKAR_TASBEEH.keys()},
            "total": 0,
            "fixed_progress": {},
            "daily_goal": 0,
            "today_count": 0,
            "last_day": ""
        }
        save_data(DATA)
    return DATA["users"][uid]

# ===================== DIGITAL COUNTER =====================
def digital_counter(num):
    digits = {"0":"𝟬","1":"𝟭","2":"𝟮","3":"𝟯","4":"𝟰","5":"𝟱","6":"𝟲","7":"𝟳","8":"𝟴","9":"𝟵"}
    return "".join(digits[d] for d in str(max(0,num)))

# ===================== NEW FEATURES =====================
def check_new_day(user):
    today = time.strftime("%Y-%m-%d")
    if user["last_day"] != today:
        user["last_day"] = today
        user["today_count"] = 0

def progress_bar(current, goal):
    if goal == 0:
        return ""
    percent = int((current / goal) * 100)
    filled = int(percent / 10)
    bar = "█" * filled + "░" * (10 - filled)
    return f"\n🎯 {current}/{goal}\n{bar} {percent}%"

def get_level(total):
    if total < 100:
        return "🌱 مبتدئ"
    elif total < 1000:
        return "💪 مجتهد"
    elif total < 10000:
        return "🌟 ذاكر"
    elif total < 100000:
        return "🔥 ثابت"
    else:
        return "👑 سابق بالخيرات"

# تعديل الإحصائيات بدون حذف أي سطر
def format_stats(user):
    lines = ["<b>📊 إحصائياتك:</b>\n"]
    for k,v in AZKAR_TASBEEH.items():
        lines.append(f"{v['emoji']} {v['name']} : <b>{user['counts'][k]:,}</b>")
    lines.append(f"\n🏆 مستواك: <b>{get_level(user['total'])}</b>")
    lines.append(f"🎯 هدفك اليومي: <b>{user['daily_goal']}</b>")
    lines.append(f"📿 إنجاز اليوم: <b>{user['today_count']}</b>")
    lines.append(f"\n✨ المجموع الكلي: <b>{user['total']:,}</b>")
    return "\n".join(lines)

# ===================== RUN =====================
print("📿 Zikr Bot running...")
bot.infinity_polling(skip_pending=True)
