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
    cur.execute(
        "SELECT count FROM zikr WHERE user_id=? AND zikr_key=?",
        (uid, key)
    )
    row = cur.fetchone()

    if row:
        cur.execute(
            "UPDATE zikr SET count = count + 1 WHERE user_id=? AND zikr_key=?",
            (uid, key)
        )
    else:
        cur.execute(
            "INSERT INTO zikr (user_id, zikr_key, zikr_name, count) VALUES (?, ?, ?, 1)",
            (uid, key, name)
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
def pretty_count(n):
    return f"✨ <b>{n:,}</b> ✨"

# ================= KEYBOARDS =================
def main_menu():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📿 الأذكار", callback_data="menu_zikr"),
        InlineKeyboardButton("📊 الإحصائيات", callback_data="menu_stats")
    )
    return kb

def zikr_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    for k, v in ZIKR.items():
        kb.add(InlineKeyboardButton(v, callback_data=f"zikr:{k}"))
    kb.add(InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_main"))
    return kb

def counter_menu(key):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("➕ تسبيحة", callback_data=f"add:{key}"),
        InlineKeyboardButton("📿 باقي الأذكار", callback_data="menu_zikr")
    )
    return kb

def stats_menu():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_main"))
    return kb

# ================= HANDLERS =================
@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(
        msg.chat.id,
        "📿 <b>سبحتك الإلكترونية</b>\n\nاختر من القوائم:",
        reply_markup=main_menu()
    )

@bot.callback_query_handler(func=lambda c: True)
def callbacks(c):
    uid = c.from_user.id
    data = c.data

    # ---------- MENUS ----------
    if data == "menu_zikr":
        bot.send_message(
            c.message.chat.id,
            "📿 اختر الذكر:",
            reply_markup=zikr_menu()
        )

    elif data == "menu_stats":
        stats = get_stats(uid)
        if not stats:
            text = "📭 <b>لا توجد أذكار بعد</b>"
        else:
            text = "📊 <b>إحصائياتك منذ البداية</b>\n\n"
            for name, count in stats:
                text += f"{name}\n{pretty_count(count)}\n\n"

        bot.send_message(
            c.message.chat.id,
            text,
            reply_markup=stats_menu()
        )

    elif data == "back_main":
        bot.send_message(
            c.message.chat.id,
            "🔙 القائمة الرئيسية:",
            reply_markup=main_menu()
        )

    # ---------- SELECT ZIKR ----------
    elif data.startswith("zikr:"):
        key = data.split(":")[1]
        name = ZIKR[key]
        count = get_count(uid, key)

        bot.send_message(
            c.message.chat.id,
            f"{name}\n\n🧮 العداد الحالي\n{pretty_count(count)}",
            reply_markup=counter_menu(key)
        )

    # ---------- ADD COUNT ----------
    elif data.startswith("add:"):
        key = data.split(":")[1]
        name = ZIKR[key]

        add_count(uid, key, name)
        count = get_count(uid, key)

        bot.send_message(
            c.message.chat.id,
            f"{name}\n\n🧮 العداد الحالي\n{pretty_count(count)}",
            reply_markup=counter_menu(key)
        )

# ================= RUN =================
print("📿 Tasbeeh Bot is running...")
bot.infinity_polling(skip_pending=True)
