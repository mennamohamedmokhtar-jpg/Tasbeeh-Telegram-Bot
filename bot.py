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

# ===================== DATA =====================
DEFAULT_DATA = {
    "users": {}
}

AZKAR = {
    "tasbeeh": {
        "name": "سبحان الله",
        "emoji": "🟢"
    },
    "tahmeed": {
        "name": "الحمد لله",
        "emoji": "🔵"
    },
    "takbeer": {
        "name": "الله أكبر",
        "emoji": "🟣"
    },
    "tahleel": {
        "name": "لا إله إلا الله",
        "emoji": "🟠"
    },
    "istighfar": {
        "name": "أستغفر الله",
        "emoji": "🟡"
    }
}

# ===================== STORAGE =====================
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
            "counts": {k: 0 for k in AZKAR.keys()},
            "total": 0,
            "created": int(time.time())
        }
        save_data(DATA)
    return DATA["users"][uid]

# ===================== UI =====================
def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📿 الأذكار", callback_data="menu_azkar"),
        InlineKeyboardButton("📊 الإحصائيات", callback_data="menu_stats")
    )
    return kb

def azkar_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    for k, v in AZKAR.items():
        kb.add(
            InlineKeyboardButton(
                f"{v['emoji']} {v['name']}",
                callback_data=f"zikr|{k}"
            )
        )
    kb.add(
        InlineKeyboardButton("⬅️ رجوع", callback_data="back_main")
    )
    return kb

def zikr_counter_menu(zikr_key, user):
    kb = InlineKeyboardMarkup(row_width=3)
    kb.add(
        InlineKeyboardButton("➕ تسبيحة", callback_data=f"add|{zikr_key}"),
        InlineKeyboardButton("➖ إنقاص", callback_data=f"sub|{zikr_key}"),
        InlineKeyboardButton("🔄 تصفير", callback_data=f"reset|{zikr_key}")
    )
    kb.add(
        InlineKeyboardButton("⬅️ رجوع للأذكار", callback_data="menu_azkar"),
        InlineKeyboardButton("🏠 الرئيسية", callback_data="back_main")
    )
    return kb

def stats_menu(user):
    lines = ["<b>📊 إحصائياتك:</b>\n"]
    for k, v in AZKAR.items():
        count = user["counts"][k]
        lines.append(f"{v['emoji']} {v['name']} : <b>{count:,}</b>")
    lines.append(f"\n✨ المجموع الكلي: <b>{user['total']:,}</b>")
    text = "\n".join(lines)

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("⬅️ رجوع", callback_data="back_main")
    )
    return text, kb

# ===================== HELPERS =====================
def format_zikr_text(zikr_key, user):
    z = AZKAR[zikr_key]
    count = user["counts"][zikr_key]
    total = user["total"]
    return (
        f"{z['emoji']} <b>{z['name']}</b>\n\n"
        f"🔢 عدد هذا الذكر: <b>{count:,}</b>\n"
        f"✨ إجمالي أذكارك: <b>{total:,}</b>"
    )

# ===================== HANDLERS =====================
@bot.message_handler(commands=["start"])
def start(m):
    get_user(m.from_user.id)
    bot.send_message(
        m.chat.id,
        "📿 مرحباً بك في بوت الأذكار\n\nاختر من القائمة:",
        reply_markup=main_menu()
    )

@bot.callback_query_handler(func=lambda c: True)
def callbacks(c):
    uid = c.from_user.id
    user = get_user(uid)
    data = c.data

    if data == "menu_azkar":
        bot.edit_message_text(
            "📿 اختر الذكر:",
            c.message.chat.id,
            c.message.message_id,
            reply_markup=azkar_menu()
        )

    elif data == "menu_stats":
        text, kb = stats_menu(user)
        bot.edit_message_text(
            text,
            c.message.chat.id,
            c.message.message_id,
            reply_markup=kb
        )

    elif data == "back_main":
        bot.edit_message_text(
            "🏠 القائمة الرئيسية:",
            c.message.chat.id,
            c.message.message_id,
            reply_markup=main_menu()
        )

    elif data.startswith("zikr|"):
        zikr_key = data.split("|")[1]
        bot.edit_message_text(
            format_zikr_text(zikr_key, user),
            c.message.chat.id,
            c.message.message_id,
            reply_markup=zikr_counter_menu(zikr_key, user)
        )

    elif data.startswith("add|"):
        zikr_key = data.split("|")[1]
        user["counts"][zikr_key] += 1
        user["total"] += 1
        save_data(DATA)
        bot.edit_message_text(
            format_zikr_text(zikr_key, user),
            c.message.chat.id,
            c.message.message_id,
            reply_markup=zikr_counter_menu(zikr_key, user)
        )

    elif data.startswith("sub|"):
        zikr_key = data.split("|")[1]
        if user["counts"][zikr_key] > 0:
            user["counts"][zikr_key] -= 1
            user["total"] -= 1
        save_data(DATA)
        bot.edit_message_text(
            format_zikr_text(zikr_key, user),
            c.message.chat.id,
            c.message.message_id,
            reply_markup=zikr_counter_menu(zikr_key, user)
        )

    elif data.startswith("reset|"):
        zikr_key = data.split("|")[1]
        user["total"] -= user["counts"][zikr_key]
        user["counts"][zikr_key] = 0
        save_data(DATA)
        bot.edit_message_text(
            format_zikr_text(zikr_key, user),
            c.message.chat.id,
            c.message.message_id,
            reply_markup=zikr_counter_menu(zikr_key, user)
        )

    bot.answer_callback_query(c.id)

# ===================== RUN =====================
print("📿 Zikr Bot is running...")
bot.infinity_polling(skip_pending=True)
