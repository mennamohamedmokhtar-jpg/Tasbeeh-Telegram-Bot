```python
# -*- coding: utf-8 -*-
# ===================== IMPORTS =====================
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import time
import json

# ===================== CONFIG =====================
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

DATA_FILE = "data.json"

# ===================== AZKAR CONFIG =====================

# عداد تصاعدي (مثل الكود الأصلي)
AZKAR_INCREMENT = {
    "tasbeeh": {"name": "سبحان الله", "emoji": "🟢"},
    "tahmeed": {"name": "الحمد لله", "emoji": "🔵"},
    "takbeer": {"name": "الله أكبر", "emoji": "🟣"},
    "tahleel": {"name": "لا إله إلا الله", "emoji": "🟠"},
    "istighfar": {"name": "أستغفر الله", "emoji": "🟡"},
    "salat": {"name": "اللهم صلِّ على محمد ﷺ", "emoji": "🤍"}
}

# عداد تنازلي (أذكار بعدد محدد)
AZKAR_DECREMENT = {
    "morning": {"name": "أذكار الصباح", "emoji": "🌅", "max": 33},
    "evening": {"name": "أذكار المساء", "emoji": "🌇", "max": 33},
    "prayer": {"name": "أذكار بعد الصلاة", "emoji": "🕌", "max": 33},
    "sleep": {"name": "أذكار النوم", "emoji": "🌙", "max": 33}
}

# ===================== STORAGE =====================
DEFAULT_DATA = {"users": {}}

def load_data():
    if not os.path.exists(DATA_FILE):
        save_data(DEFAULT_DATA)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

DATA = load_data()

def get_user(uid):
    uid = str(uid)
    if uid not in DATA["users"]:
        DATA["users"][uid] = {
            "inc_counts": {k: 0 for k in AZKAR_INCREMENT.keys()},
            "dec_counts": {k: v["max"] for k, v in AZKAR_DECREMENT.items()},
            "total_inc": 0,
            "created": int(time.time())
        }
        save_data(DATA)
    return DATA["users"][uid]

# ===================== UI =====================

def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)

    for k, v in AZKAR_INCREMENT.items():
        kb.add(InlineKeyboardButton(f"{v['emoji']} {v['name']}", callback_data=f"inc|{k}"))

    for k, v in AZKAR_DECREMENT.items():
        kb.add(InlineKeyboardButton(f"{v['emoji']} {v['name']}", callback_data=f"dec|{k}"))

    kb.add(InlineKeyboardButton("📊 الإحصائيات", callback_data="menu_stats"))
    return kb

def inc_menu(key):
    kb = InlineKeyboardMarkup(row_width=3)
    kb.add(
        InlineKeyboardButton("➕ تسبيحة", callback_data=f"inc_add|{key}"),
        InlineKeyboardButton("➖ إنقاص", callback_data=f"inc_sub|{key}"),
        InlineKeyboardButton("🔄 تصفير", callback_data=f"inc_reset|{key}")
    )
    kb.add(InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="back_main"))
    return kb

def dec_menu(key):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✅ تم", callback_data=f"dec_done|{key}"),
        InlineKeyboardButton("🔄 إعادة", callback_data=f"dec_reset|{key}")
    )
    kb.add(InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="back_main"))
    return kb

# ===================== FORMATTERS =====================

def format_inc_text(key, user):
    z = AZKAR_INCREMENT[key]
    count = user["inc_counts"][key]
    total = user["total_inc"]
    return (
        f"{z['emoji']} <b>{z['name']}</b>\n\n"
        f"🔢 عدد هذا الذكر: <b>{count:,}</b>\n"
        f"✨ إجمالي أذكارك: <b>{total:,}</b>"
    )

def format_dec_text(key, user):
    z = AZKAR_DECREMENT[key]
    remaining = user["dec_counts"][key]
    max_count = z["max"]
    done = max_count - remaining
    return (
        f"{z['emoji']} <b>{z['name']}</b>\n\n"
        f"📿 المتبقي: <b>{remaining}</b>\n"
        f"✅ المنجز: <b>{done}</b> من <b>{max_count}</b>"
    )

def format_stats(user):
    lines = ["<b>📊 إحصائياتك:</b>\n"]

    lines.append("<b>🔹 الأذكار التصاعدية:</b>")
    for k, v in AZKAR_INCREMENT.items():
        lines.append(f"{v['emoji']} {v['name']} : <b>{user['inc_counts'][k]:,}</b>")

    lines.append(f"\n✨ المجموع الكلي التصاعدي: <b>{user['total_inc']:,}</b>\n")

    lines.append("<b>🔹 الأذكار التنازلية (الحالية):</b>")
    for k, v in AZKAR_DECREMENT.items():
        remaining = user["dec_counts"][k]
        lines.append(f"{v['emoji']} {v['name']} : المتبقي <b>{remaining}</b>")

    return "\n".join(lines)

# ===================== HANDLERS =====================

@bot.message_handler(commands=["start"])
def start(m):
    get_user(m.from_user.id)
    bot.send_message(
        m.chat.id,
        "📿 مرحباً بك في بوت الأذكار\nاختر من القائمة أدناه:",
        reply_markup=main_menu()
    )

@bot.callback_query_handler(func=lambda c: True)
def callbacks(c):
    uid = c.from_user.id
    user = get_user(uid)
    data = c.data

    # ====== عرض التصاعدي ======
    if data.startswith("inc|"):
        key = data.split("|")[1]
        bot.edit_message_text(
            format_inc_text(key, user),
            c.message.chat.id,
            c.message.message_id,
            reply_markup=inc_menu(key)
        )

    elif data.startswith("inc_add|"):
        key = data.split("|")[1]
        user["inc_counts"][key] += 1
        user["total_inc"] += 1
        save_data(DATA)
        bot.edit_message_text(
            format_inc_text(key, user),
            c.message.chat.id,
            c.message.message_id,
            reply_markup=inc_menu(key)
        )

    elif data.startswith("inc_sub|"):
        key = data.split("|")[1]
        if user["inc_counts"][key] > 0:
            user["inc_counts"][key] -= 1
            user["total_inc"] -= 1
        save_data(DATA)
        bot.edit_message_text(
            format_inc_text(key, user),
            c.message.chat.id,
            c.message.message_id,
            reply_markup=inc_menu(key)
        )

    elif data.startswith("inc_reset|"):
        key = data.split("|")[1]
        user["total_inc"] -= user["inc_counts"][key]
        user["inc_counts"][key] = 0
        save_data(DATA)
        bot.edit_message_text(
            format_inc_text(key, user),
            c.message.chat.id,
            c.message.message_id,
            reply_markup=inc_menu(key)
        )

    # ====== عرض التنازلي ======
    elif data.startswith("dec|"):
        key = data.split("|")[1]
        bot.edit_message_text(
            format_dec_text(key, user),
            c.message.chat.id,
            c.message.message_id,
            reply_markup=dec_menu(key)
        )

    elif data.startswith("dec_done|"):
        key = data.split("|")[1]
        if user["dec_counts"][key] > 0:
            user["dec_counts"][key] -= 1
        save_data(DATA)
        bot.edit_message_text(
            format_dec_text(key, user),
            c.message.chat.id,
            c.message.message_id,
            reply_markup=dec_menu(key)
        )

    elif data.startswith("dec_reset|"):
        key = data.split("|")[1]
        user["dec_counts"][key] = AZKAR_DECREMENT[key]["max"]
        save_data(DATA)
        bot.edit_message_text(
            format_dec_text(key, user),
            c.message.chat.id,
            c.message.message_id,
            reply_markup=dec_menu(key)
        )

    elif data == "menu_stats":
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="back_main"))
        bot.edit_message_text(
            format_stats(user),
            c.message.chat.id,
            c.message.message_id,
            reply_markup=kb
        )

    elif data == "back_main":
        bot.edit_message_text(
            "📿 القائمة الرئيسية:",
            c.message.chat.id,
            c.message.message_id,
            reply_markup=main_menu()
        )

    bot.answer_callback_query(c.id)

# ===================== RUN =====================
print("📿 Advanced Zikr Bot running...")
bot.infinity_polling(skip_pending=True)
```
