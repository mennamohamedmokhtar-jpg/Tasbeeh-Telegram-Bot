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
CREATE TABLE IF NOT EXISTS tasbeeh (
    user_id INTEGER,
    zikr TEXT,
    count INTEGER,
    PRIMARY KEY (user_id, zikr)
)
""")
db.commit()

def add_zikr(uid, zikr):
    cur.execute(
        "SELECT count FROM tasbeeh WHERE user_id=? AND zikr=?",
        (uid, zikr)
    )
    row = cur.fetchone()

    if row:
        cur.execute(
            "UPDATE tasbeeh SET count = count + 1 WHERE user_id=? AND zikr=?",
            (uid, zikr)
        )
    else:
        cur.execute(
            "INSERT INTO tasbeeh (user_id, zikr, count) VALUES (?, ?, 1)",
            (uid, zikr)
        )
    db.commit()

def get_stats(uid):
    cur.execute(
        "SELECT zikr, count FROM tasbeeh WHERE user_id=?",
        (uid,)
    )
    return cur.fetchall()

# ================= ZIKR DATA =================
ZIKR = {
    "salat": "🤍 الصلاة على النبي ﷺ",
    "istighfar": "🌿 الاستغفار",
    "tasbeeh": "📿 التسبيح",
    "hawqala": "✨ لا حول ولا قوة إلا بالله"
}

# ================= KEYBOARDS =================
def main_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    for k, v in ZIKR.items():
        kb.add(InlineKeyboardButton(v, callback_data=f"zikr|{k}"))
    kb.add(InlineKeyboardButton("📊 الإحصائيات", callback_data="stats"))
    return kb

def zikr_kb(z):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("➕ تسبيحة", callback_data=f"add|{z}"),
        InlineKeyboardButton("🔙 رجوع", callback_data="back")
    )
    return kb

# ================= HANDLERS =================
@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(
        msg.chat.id,
        "📿 سبحتك الإلكترونية\n\nاختار الذكر:",
        reply_markup=main_kb()
    )

@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    uid = c.from_user.id
    data = c.data.split("|")

    # اختيار ذكر
    if data[0] == "zikr":
        z = data[1]
        bot.send_message(
            c.message.chat.id,
            f"{ZIKR[z]}\n\nاضغط للعدّ 👇",
            reply_markup=zikr_kb(z)
        )

    # زيادة العداد
    elif data[0] == "add":
        z = data[1]
        add_zikr(uid, ZIKR[z])
        bot.answer_callback_query(c.id, "✔️ تم العد")

    # إحصائيات
    elif data[0] == "stats":
        stats = get_stats(uid)
        if not stats:
            text = "📭 لا توجد أذكار بعد"
        else:
            text = "📊 إحصائياتك:\n\n"
            for z, c_ in stats:
                text += f"{z} : <b>{c_}</b>\n"

        bot.send_message(c.message.chat.id, text)

    # رجوع
    elif data[0] == "back":
        bot.send_message(
            c.message.chat.id,
            "📿 اختار الذكر:",
            reply_markup=main_kb()
        )

# ================= RUN =================
print("📿 Tasbeeh Bot is running...")
bot.infinity_polling(skip_pending=True)
