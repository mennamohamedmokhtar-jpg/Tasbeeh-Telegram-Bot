# -*- coding: utf-8 -*-

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import os

# ================= BOT INIT =================
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise Exception("BOT_TOKEN is not set")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ================= DATABASE =================
db = sqlite3.connect("tasbeeh.db", check_same_thread=False)
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS zikr (
    user_id INTEGER,
    zikr_key TEXT,
    zikr_name TEXT,
    count INTEGER,
    PRIMARY KEY (user_id, zikr_key)
)
""")
db.commit()

# ================= DB FUNCTIONS =================
def get_count(uid, key):
    cur.execute(
        "SELECT count FROM zikr WHERE user_id=? AND zikr_key=?",
        (uid, key)
    )
    row = cur.fetchone()
    return row[0] if row else 0

def add_count(uid, key, name):
    if get_count(uid, key) == 0:
        cur.execute(
            "INSERT OR IGNORE INTO zikr VALUES (?, ?, ?, 0)",
            (uid, key, name)
        )

    cur.execute(
        "UPDATE zikr SET count = count + 1 WHERE user_id=? AND zikr_key=?",
        (uid, key)
    )
    db.commit()

def get_stats(uid):
    cur.execute(
        "SELECT zikr_name, count FROM zikr WHERE user_id=?",
        (uid,)
    )
    return cur.fetchall()

# ================= ZIKR DATA =================
ZIKR = {
    "salat": "🤍 الصلاة على النبي ﷺ",
    "istighfar": "🌿 الاستغفار",
    "tasbeeh": "📿 التسبيح",
    "hawqala": "✨ لا حول ولا قوة إلا بالله",
    "takbeer": "🕌 الله أكبر"
}

# ================= FORMAT =================
def pretty(n):
    return f"✨ <b>{n:,}</b> ✨"

# ================= KEYBOARDS =================
def main_menu():
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("📿 الأذكار", callback_data="menu_zikr"),
        InlineKeyboardButton("📊 الإحصائيات", callback_data="menu_stats")
    )
    return kb

def zikr_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    for k, v in ZIKR.items():
        kb.add(InlineKeyboardButton(v, callback_data=f"open:{k}"))
    kb.add(InlineKeyboardButton("🔙 الرئيسية", callback_data="menu_main"))
    return kb

def counter_kb(key):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("➕ تسبيحة", callback_data=f"add:{key}"),
        InlineKeyboardButton("📿 باقي الأذكار", callback_data="menu_zikr")
    )
    return kb

# ================= HANDLERS =================
@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(
        msg.chat.id,
        "📿 <b>سبحتك الإلكترونية</b>\nاختر:",
        reply_markup=main_menu()
    )

@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    uid = c.from_user.id
    data = c.data

    # -------- MENUS --------
    if data == "menu_main":
        bot.send_message(
            c.message.chat.id,
            "🏠 القائمة الرئيسية:",
            reply_markup=main_menu()
        )

    elif data == "menu_zikr":
        bot.send_message(
            c.message.chat.id,
            "📿 اختر الذكر:",
            reply_markup=zikr_menu()
        )

    elif data == "menu_stats":
        stats = get_stats(uid)
        if not stats:
            text = "📭 لا توجد أذكار بعد"
        else:
            text = "📊 <b>إحصائياتك</b>\n\n"
            for n, c_ in stats:
                text += f"{n}\n{pretty(c_)}\n\n"

        bot.send_message(c.message.chat.id, text)

    # -------- OPEN ZIKR --------
    elif data.startswith("open:"):
        key = data.split(":")[1]
        name = ZIKR[key]
        count = get_count(uid, key)

        bot.send_message(
            c.message.chat.id,
            f"{name}\n\n🧮 العداد الحالي\n{pretty(count)}",
            reply_markup=counter_kb(key)
        )

    # -------- ADD COUNT (EDIT SAME MESSAGE) --------
    elif data.startswith("add:"):
        key = data.split(":")[1]
        name = ZIKR[key]

        add_count(uid, key, name)
        count = get_count(uid, key)

        bot.edit_message_text(
            chat_id=c.message.chat.id,
            message_id=c.message.message_id,
            text=f"{name}\n\n🧮 العداد الحالي\n{pretty(count)}",
            reply_markup=counter_kb(key)
        )

# ================= RUN =================
print("📿 Smart Tasbeeh Bot running...")
bot.infinity_polling(skip_pending=True)
