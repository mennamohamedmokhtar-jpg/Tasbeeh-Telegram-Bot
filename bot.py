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

# ===================== AZKAR =====================

# تسبيح (تصاعدي)
AZKAR_INC = {
    "tasbeeh": {"name": "سبحان الله", "emoji": "🟢"},
    "tahmeed": {"name": "الحمد لله", "emoji": "🔵"},
    "takbeer": {"name": "الله أكبر", "emoji": "🟣"},
    "tahleel": {"name": "لا إله إلا الله", "emoji": "🟠"},
    "istighfar": {"name": "أستغفر الله", "emoji": "🟡"},
    "salat": {"name": "اللهم صلِّ على محمد ﷺ", "emoji": "🤍"}
}

# أذكار ثابتة (متسلسلة)
AZKAR_SEQUENCES = {

    "morning": {
        "name": "أذكار الصباح",
        "emoji": "🌅",
        "items": [
            {"text": "آية الكرسي", "count": 1},
            {"text": "سورة الإخلاص", "count": 3},
            {"text": "سورة الفلق", "count": 3},
            {"text": "سورة الناس", "count": 3},
            {"text": "أصبحنا وأصبح الملك لله", "count": 1},
            {"text": "اللهم بك أصبحنا", "count": 1},
            {"text": "سبحان الله وبحمده", "count": 100}
        ]
    },

    "evening": {
        "name": "أذكار المساء",
        "emoji": "🌇",
        "items": [
            {"text": "آية الكرسي", "count": 1},
            {"text": "سورة الإخلاص", "count": 3},
            {"text": "سورة الفلق", "count": 3},
            {"text": "سورة الناس", "count": 3},
            {"text": "أمسينا وأمسى الملك لله", "count": 1},
            {"text": "اللهم بك أمسينا", "count": 1},
            {"text": "سبحان الله وبحمده", "count": 100}
        ]
    },

    "after_prayer": {
        "name": "أذكار بعد الصلاة",
        "emoji": "🕌",
        "items": [
            {"text": "أستغفر الله", "count": 3},
            {"text": "اللهم أنت السلام", "count": 1},
            {"text": "سبحان الله", "count": 33},
            {"text": "الحمد لله", "count": 33},
            {"text": "الله أكبر", "count": 34}
        ]
    },

    "sleep": {
        "name": "أذكار النوم",
        "emoji": "🌙",
        "items": [
            {"text": "آية الكرسي", "count": 1},
            {"text": "باسمك ربي وضعت جنبي", "count": 1},
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
            "counts_inc": {k: 0 for k in AZKAR_INC.keys()},
            "total_inc": 0,
            "sequence_progress": {},
            "created": int(time.time())
        }
        save_data(DATA)
    return DATA["users"][uid]

# ===================== DIGITAL =====================

DIGITS = {
    "0": "𝟎", "1": "𝟏", "2": "𝟐", "3": "𝟑", "4": "𝟒",
    "5": "𝟓", "6": "𝟔", "7": "𝟕", "8": "𝟖", "9": "𝟗"
}

def digital(n):
    return "".join(DIGITS.get(d, d) for d in str(n))

# ===================== UI =====================

def main_menu():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📿 تسبيح", callback_data="menu_inc"),
        InlineKeyboardButton("📖 أذكار ثابتة", callback_data="menu_seq"),
        InlineKeyboardButton("📊 الإحصائيات", callback_data="menu_stats")
    )
    return kb

def inc_menu(key):
    kb = InlineKeyboardMarkup(row_width=3)
    kb.add(
        InlineKeyboardButton("➕", callback_data=f"inc_add|{key}"),
        InlineKeyboardButton("➖", callback_data=f"inc_sub|{key}"),
        InlineKeyboardButton("🔄", callback_data=f"inc_reset|{key}")
    )
    kb.add(InlineKeyboardButton("🏠 الرئيسية", callback_data="back_main"))
    return kb

def seq_menu(key):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("➖ إنقاص", callback_data=f"seq_sub|{key}"))
    kb.add(InlineKeyboardButton("🏠 الرئيسية", callback_data="back_main"))
    return kb

# ===================== FORMAT =====================

def format_inc_text(key, user):
    z = AZKAR_INC[key]
    count = user["counts_inc"][key]
    total = user["total_inc"]
    return (
        f"{z['emoji']} <b>{z['name']}</b>\n\n"
        f"╔══════════╗\n"
        f"   {digital(count)}\n"
        f"╚══════════╝\n\n"
        f"✨ الإجمالي: {digital(total)}"
    )

def format_sequence_text(key, user):
    seq = AZKAR_SEQUENCES[key]
    progress = user["sequence_progress"].get(key, {"index": 0, "remaining": seq["items"][0]["count"]})
    index = progress["index"]

    if index >= len(seq["items"]):
        return "✅ <b>تمت الأذكار كاملة</b>\n\nبارك الله لك وجعله في ميزان حسناتك 🤍"

    item = seq["items"][index]
    return (
        f"{seq['emoji']} <b>{seq['name']}</b>\n\n"
        f"<b>{item['text']}</b>\n\n"
        f"╔══════════╗\n"
        f"   {digital(progress['remaining'])}\n"
        f"╚══════════╝"
    )

def format_stats(user):
    lines = ["<b>📊 إحصائياتك الإجمالية:</b>\n"]
    lines.append("<b>📿 التسبيح:</b>")
    for k, v in AZKAR_INC.items():
        lines.append(f"{v['emoji']} {v['name']} : <b>{digital(user['counts_inc'][k])}</b>")
    lines.append(f"\n✨ مجموع التسبيح: <b>{digital(user['total_inc'])}</b>\n")
    lines.append("<b>📖 الأذكار الثابتة (المنجزة حالياً):</b>")
    for k, v in AZKAR_SEQUENCES.items():
        progress = user["sequence_progress"].get(k)
        if progress:
            done = sum(item["count"] for item in AZKAR_SEQUENCES[k]["items"][:progress["index"]])
            done += (AZKAR_SEQUENCES[k]["items"][progress["index"]]["count"] - progress["remaining"]) if progress["index"] < len(AZKAR_SEQUENCES[k]["items"]) else 0
        else:
            done = 0
        lines.append(f"{v['emoji']} {v['name']} : <b>{digital(done)}</b>")
    return "\n".join(lines)

# ===================== HANDLERS =====================

@bot.message_handler(commands=["start"])
def start(m):
    get_user(m.from_user.id)
    bot.send_message(m.chat.id, "📿 <b>القائمة الرئيسية</b>", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda c: True)
def callbacks(c):
    uid = c.from_user.id
    user = get_user(uid)
    data = c.data

    if data == "menu_inc":
        kb = InlineKeyboardMarkup(row_width=2)
        for k, v in AZKAR_INC.items():
            kb.add(InlineKeyboardButton(f"{v['emoji']} {v['name']}", callback_data=f"inc|{k}"))
        kb.add(InlineKeyboardButton("🏠 الرئيسية", callback_data="back_main"))
        bot.send_message(c.message.chat.id, "📿 <b>التسبيح</b>", reply_markup=kb)

    elif data.startswith("inc|"):
        key = data.split("|")[1]
        bot.send_message(c.message.chat.id, format_inc_text(key, user), reply_markup=inc_menu(key))

    elif data.startswith("inc_add|"):
        key = data.split("|")[1]
        user["counts_inc"][key] += 1
        user["total_inc"] += 1
        save_data(DATA)
        bot.edit_message_text(format_inc_text(key, user),
                              c.message.chat.id, c.message.message_id,
                              reply_markup=inc_menu(key))

    elif data.startswith("inc_sub|"):
        key = data.split("|")[1]
        if user["counts_inc"][key] > 0:
            user["counts_inc"][key] -= 1
            user["total_inc"] -= 1
        save_data(DATA)
        bot.edit_message_text(format_inc_text(key, user),
                              c.message.chat.id, c.message.message_id,
                              reply_markup=inc_menu(key))

    elif data.startswith("inc_reset|"):
        key = data.split("|")[1]
        user["total_inc"] -= user["counts_inc"][key]
        user["counts_inc"][key] = 0
        save_data(DATA)
        bot.edit_message_text(format_inc_text(key, user),
                              c.message.chat.id, c.message.message_id,
                              reply_markup=inc_menu(key))

    elif data == "menu_seq":
        kb = InlineKeyboardMarkup(row_width=2)
        for k, v in AZKAR_SEQUENCES.items():
            kb.add(InlineKeyboardButton(f"{v['emoji']} {v['name']}", callback_data=f"seq|{k}"))
        kb.add(InlineKeyboardButton("🏠 الرئيسية", callback_data="back_main"))
        bot.send_message(c.message.chat.id, "📖 <b>الأذكار الثابتة</b>", reply_markup=kb)

    elif data.startswith("seq|"):
        key = data.split("|")[1]
        first_item = AZKAR_SEQUENCES[key]["items"][0]
        user["sequence_progress"][key] = {"index": 0, "remaining": first_item["count"]}
        save_data(DATA)
        bot.send_message(c.message.chat.id, format_sequence_text(key, user), reply_markup=seq_menu(key))

    elif data.startswith("seq_sub|"):
        key = data.split("|")[1]
        seq = AZKAR_SEQUENCES[key]
        progress = user["sequence_progress"].get(key)

        if not progress:
            return

        if progress["remaining"] > 0:
            progress["remaining"] -= 1

        if progress["remaining"] == 0:
            progress["index"] += 1
            if progress["index"] < len(seq["items"]):
                next_item = seq["items"][progress["index"]]
                progress["remaining"] = next_item["count"]
            else:
                user["sequence_progress"][key] = progress
                save_data(DATA)
                bot.edit_message_text(
                    "✅ <b>تمت الأذكار كاملة</b>\n\nبارك الله لك وجعله في ميزان حسناتك 🤍",
                    c.message.chat.id,
                    c.message.message_id
                )
                return

        user["sequence_progress"][key] = progress
        save_data(DATA)
        bot.edit_message_text(format_sequence_text(key, user),
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=seq_menu(key))

    elif data == "menu_stats":
        bot.send_message(c.message.chat.id, format_stats(user), reply_markup=main_menu())

    elif data == "back_main":
        bot.send_message(c.message.chat.id, "📿 <b>القائمة الرئيسية</b>", reply_markup=main_menu())

    bot.answer_callback_query(c.id)

# ===================== RUN =====================
print("📿 Zikr Bot running...")
bot.infinity_polling(skip_pending=True)
