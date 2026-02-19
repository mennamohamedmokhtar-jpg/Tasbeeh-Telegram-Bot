# -*- coding: utf-8 -*-
# ===================== IMPORTS =====================
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os, time, json
from datetime import datetime

# ===================== CONFIG =====================
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
DATA_FILE = "data.json"
ADMIN_ID = 123456789

# ===================== DATA =====================
DEFAULT_DATA = {"users": {}}

AZKAR_TASBEEH = {
    "tasbeeh": {"name": "سبحان الله", "emoji": "🟢"},
    "tahmeed": {"name": "الحمد لله", "emoji": "🔵"},
    "takbeer": {"name": "الله أكبر", "emoji": "🟣"},
    "tahleel": {"name": "لا إله إلا الله", "emoji": "🟠"},
    "istighfar": {"name": "أستغفر الله", "emoji": "🟡"},
    "salat": {"name": "اللهم صلِّ على محمد ﷺ", "emoji": "🤍"},
    "hawqala": {"name": "لا حول ولا قوة إلا بالله", "emoji": "🟤"},
    "hirz": {"name": "بسم الله الذي لا يضر مع اسمه شيء", "emoji": "🛡️"}
}

AZKAR_FIXED = {
    "sabah": {"title": "🌅 أذكار الصباح", "list": [{"text": "أصبحنا وأصبح الملك لله", "count": 1}]}
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
    today = datetime.utcnow().date().isoformat()

    if uid not in DATA["users"]:
        DATA["users"][uid] = {
            "counts": {k: 0 for k in AZKAR_TASBEEH.keys()},
            "total": 0,
            "fixed_progress": {},
            "daily_count": 0,
            "daily_goal": 100,
            "last_day": today,
            "achievements": []
        }

    user = DATA["users"][uid]

    if user.get("last_day") != today:
        user["daily_count"] = 0
        user["last_day"] = today

    save_data(DATA)
    return user

# ===================== DIGITAL COUNTER =====================
def digital_counter(num):
    digits = {"0":"𝟬","1":"𝟭","2":"𝟮","3":"𝟯","4":"𝟰","5":"𝟱","6":"𝟲","7":"𝟳","8":"𝟴","9":"𝟵"}
    return "".join(digits[d] for d in str(max(0,num)))

# ===================== ACHIEVEMENTS =====================
ACHIEVEMENTS = [
    (1, "🎉 أول تسبيحة"),
    (100, "💯 100 تسبيحة"),
    (1000, "🔥 1000 تسبيحة"),
    (10000, "🚀 10,000 تسبيحة")
]

def check_achievements(uid, user):
    new_achievements = []
    for value, title in ACHIEVEMENTS:
        if user["total"] >= value and title not in user["achievements"]:
            user["achievements"].append(title)
            new_achievements.append(title)

    if new_achievements:
        save_data(DATA)
        bot.send_message(uid, "🏆 <b>إنجاز جديد!</b>\n\n" + "\n".join(new_achievements))

# ===================== UI =====================
def main_menu():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📿 تسبيح", callback_data="menu_tasbeeh"),
        InlineKeyboardButton("🎯 الهدف اليومي", callback_data="menu_daily"),
        InlineKeyboardButton("🏆 إنجازاتي", callback_data="menu_achievements"),
        InlineKeyboardButton("📊 إحصائياتي", callback_data="menu_stats")
    )
    return kb

def tasbeeh_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    for k,v in AZKAR_TASBEEH.items():
        kb.add(InlineKeyboardButton(f"{v['emoji']} {v['name']}", callback_data=f"zikr|{k}"))
    kb.add(InlineKeyboardButton("⬅️ القائمة الرئيسية", callback_data="back_main"))
    return kb

def tasbeeh_counter_menu(key):
    kb = InlineKeyboardMarkup(row_width=3)
    kb.add(
        InlineKeyboardButton("➕", callback_data=f"add|{key}"),
        InlineKeyboardButton("➖", callback_data=f"sub|{key}"),
        InlineKeyboardButton("🔄", callback_data=f"reset|{key}")
    )
    kb.add(InlineKeyboardButton("⬅️ القائمة الرئيسية", callback_data="back_main"))
    return kb

# ===================== HELPERS =====================
def format_stats(user):
    return f"""
<b>📊 إحصائياتك</b>

✨ المجموع الكلي: <b>{user['total']:,}</b>
🎯 اليوم: <b>{user['daily_count']:,}</b> / {user['daily_goal']}
"""

# ===================== HANDLERS =====================
@bot.message_handler(commands=["start"])
def start(m):
    get_user(m.from_user.id)
    bot.send_message(m.chat.id,"📿 مرحباً بك",reply_markup=main_menu())

@bot.callback_query_handler(func=lambda c: True)
def callbacks(c):
    try:
        uid = c.from_user.id
        user = get_user(uid)
        data = c.data

        if data == "menu_tasbeeh":
            bot.send_message(uid, "📿 اختر ذكر:", reply_markup=tasbeeh_menu())

        elif data == "menu_stats":
            bot.send_message(uid, format_stats(user), reply_markup=main_menu())

        elif data == "menu_daily":
            bot.send_message(uid,
                f"🎯 هدفك اليومي الحالي: <b>{user['daily_goal']}</b>\n"
                f"📿 أنجزت اليوم: <b>{user['daily_count']}</b>")

        elif data == "menu_achievements":
            text = "<b>🏆 إنجازاتك:</b>\n\n"
            text += "\n".join(user["achievements"]) if user["achievements"] else "لا يوجد بعد"
            bot.send_message(uid, text)

        elif data.startswith("zikr|"):
            key = data.split("|")[1]
            z = AZKAR_TASBEEH[key]
            text = f"{z['emoji']} <b>{z['name']}</b>\n\n🔢 {digital_counter(user['counts'][key])}"
            bot.send_message(uid, text, reply_markup=tasbeeh_counter_menu(key))

        elif data.startswith("add|"):
            key = data.split("|")[1]
            user["counts"][key] += 1
            user["total"] += 1
            user["daily_count"] += 1
            save_data(DATA)

            check_achievements(uid, user)

            z = AZKAR_TASBEEH[key]
            text = f"{z['emoji']} <b>{z['name']}</b>\n\n🔢 {digital_counter(user['counts'][key])}"
            bot.edit_message_text(text, uid, c.message.message_id, reply_markup=tasbeeh_counter_menu(key))

        elif data.startswith("sub|"):
            key = data.split("|")[1]
            if user["counts"][key] > 0:
                user["counts"][key] -= 1
                user["total"] -= 1
                user["daily_count"] -= 1
            save_data(DATA)

            z = AZKAR_TASBEEH[key]
            text = f"{z['emoji']} <b>{z['name']}</b>\n\n🔢 {digital_counter(user['counts'][key])}"
            bot.edit_message_text(text, uid, c.message.message_id, reply_markup=tasbeeh_counter_menu(key))

        elif data.startswith("reset|"):
            key = data.split("|")[1]
            user["total"] -= user["counts"][key]
            user["daily_count"] -= user["counts"][key]
            user["counts"][key] = 0
            save_data(DATA)

            z = AZKAR_TASBEEH[key]
            text = f"{z['emoji']} <b>{z['name']}</b>\n\n🔢 {digital_counter(0)}"
            bot.edit_message_text(text, uid, c.message.message_id, reply_markup=tasbeeh_counter_menu(key))

        bot.answer_callback_query(c.id)

    except Exception as e:
        print("ERROR:", e)
        bot.answer_callback_query(c.id, "حدث خطأ ❌", show_alert=False)

# ===================== RUN =====================
print("📿 Zikr Bot running...")
bot.infinity_polling(skip_pending=True)
