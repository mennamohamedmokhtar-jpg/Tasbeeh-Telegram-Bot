# -*- coding: utf-8 -*-

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import os

# ================= BOT INIT =================
TOKEN = os.getenv("BOT_TOKEN")
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

def add_zikr(uid, key, name):
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

def get_count(uid, key):
    cur.execute(
        "SELECT count FROM zikr WHERE user_id=? AND zikr_key=?",
        (uid, key)
    )
    row = cur.fetchone()
    return row[0] if row else 0

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
        kb.add(InlineKeyboardButton(v, callback_data=f"zikr|{k}"))
    kb.add(InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
    return kb

def zikr_counter_kb(key):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("➕ تسبيحة", callback_data=f"add|{key}"),
        InlineKeyboardButton("🔙 رجوع", callback_data="menu_zikr")
    )
    return kb

def stats_menu():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
    return kb

# ================= HANDLERS =================
@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(
        msg.chat.id,
        "📿 سبحتك الإلكترونية\n\nاختار من القائمة:",
        reply_markup=main_menu()
    )

@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    uid = c.from_user.id
    data = c.data.split("|")

    # ---------- MAIN MENUS ----------
    if c.data == "menu_zikr":
        bot.send_message(c.message.chat.id, "📿 اختر الذكر:", reply_markup=zikr_menu())

    elif c.data == "menu_stats":
        stats = get_stats(uid)
        if not stats:
            text = "📭 لا توجد أذكار بعد"
        else:
            text = "📊 إحصائياتك منذ بداية الاستخدام:\n\n"
            for name, count in stats:
                text += f"{name} : <b>{count}</b>\n"

        bot.send_message(c.message.chat.id, text, reply_markup=stats_menu())

    elif c.data == "back_main":
        bot.send_message(c.message.chat.id, "🔙 القائمة الرئيسية:", reply_markup=main_menu())

    # ---------- ZIKR SELECT ----------
    elif data[0] == "zikr":
        key = data[1]
        name = ZIKR[key]
        count = get_count(uid, key)

        bot.send_message(
            c.message.chat.id,
            f"{name}\n\n🧮 العدد الحالي: <b>{count}</b>",
            reply_markup=zikr_counter_kb(key)
        )

    # ---------- ADD COUNT ----------
    elif data[0] == "add":
        key = data[1]
        name = ZIKR[key]

        add_zikr(uid, key, name)
        count = get_count(uid, key)

        bot.edit_message_text(
            chat_id=c.message.chat.id,
            message_id=c.message.message_id,
            text=f"{name}\n\n🧮 العدد الحالي: <b>{count}</b>",
            reply_markup=zikr_counter_kb(key)
        )

# ================= RUN =================
print("📿 Tasbeeh Bot running...")
bot.infinity_polling(skip_pending=True)
