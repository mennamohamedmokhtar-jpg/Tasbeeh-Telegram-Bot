import json
import os
from datetime import datetime, date
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

BOT_TOKEN = "PUT_YOUR_TOKEN_HERE"
DATA_FILE = "data.json"

ADHKAR = {
    "tasbeeh": "سبحان الله",
    "tahmeed": "الحمد لله",
    "takbeer": "الله أكبر",
    "istighfar": "أستغفر الله",
    "salat": "اللهم صلِّ على محمد",
    "hawqala": "لا حول ولا قوة إلا بالله"
}

# ----------------- DATA -----------------

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user(data, user_id):
    today = str(date.today())
    if str(user_id) not in data:
        data[str(user_id)] = {
            "counts": {k: 0 for k in ADHKAR},
            "daily": {today: {k: 0 for k in ADHKAR}},
            "session": {k: 0 for k in ADHKAR},
            "achievements": [],
            "custom": {},
            "silent": False,
            "night": False
        }
    return data[str(user_id)]

# ----------------- UI -----------------

def adhkar_menu():
    buttons = [
        [InlineKeyboardButton(ADHKAR[k], callback_data=f"zikr_{k}")]
        for k in ADHKAR
    ]
    buttons.append([
        InlineKeyboardButton("📊 الإحصائيات", callback_data="stats"),
        InlineKeyboardButton("🕊 وضع الخشوع", callback_data="khushoo")
    ])
    buttons.append([
        InlineKeyboardButton("➕ ذكر مخصص", callback_data="custom"),
        InlineKeyboardButton("⚙️ الإعدادات", callback_data="settings")
    ])
    return InlineKeyboardMarkup(buttons)

def zikr_keyboard(key):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ سبح", callback_data=f"count_{key}"),
            InlineKeyboardButton("🔙 رجوع", callback_data="back")
        ]
    ])

# ----------------- HANDLERS -----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤍 مرحبًا بك في سبحتك الرقمية\nاختر الذكر وابدأ الطمأنينة",
        reply_markup=adhkar_menu()
    )

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = load_data()
    user = get_user(data, query.from_user.id)

    if query.data.startswith("zikr_"):
        key = query.data.split("_")[1]
        await query.edit_message_text(
            f"📿 {ADHKAR[key]}\n\n"
            f"🔢 الجلسة: {user['session'][key]}\n"
            f"📊 الإجمالي: {user['counts'][key]}",
            reply_markup=zikr_keyboard(key)
        )

    elif query.data.startswith("count_"):
        key = query.data.split("_")[1]
        today = str(date.today())

        user["counts"][key] += 1
        user["session"][key] += 1
        user["daily"].setdefault(today, {k: 0 for k in ADHKAR})
        user["daily"][today][key] += 1

        # Achievement
        if user["counts"][key] in [1000, 10000, 100000]:
            user["achievements"].append(f"{ADHKAR[key]} x {user['counts'][key]}")

        save_data(data)

        await query.edit_message_text(
            f"📿 {ADHKAR[key]}\n\n"
            f"✨ الجلسة: {user['session'][key]}\n"
            f"📊 الإجمالي: {user['counts'][key]}",
            reply_markup=zikr_keyboard(key)
        )

    elif query.data == "stats":
        text = "📊 إحصائياتك:\n\n"
        for k, v in user["counts"].items():
            text += f"{ADHKAR[k]}: {v}\n"

        if user["achievements"]:
            text += "\n🏆 إنجازات:\n"
            for a in user["achievements"]:
                text += f"• {a}\n"

        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
        ]))

    elif query.data == "khushoo":
        await query.edit_message_text(
            "🕊 وضع الخشوع\nاضغط فقط واذكر الله",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ ذكر", callback_data="count_tasbeeh")],
                [InlineKeyboardButton("🔙 خروج", callback_data="back")]
            ])
        )

    elif query.data == "settings":
        await query.edit_message_text(
            "⚙️ الإعدادات",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔒 وضع السرية", callback_data="silent")],
                [InlineKeyboardButton("🌙 الوضع الليلي", callback_data="night")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
            ])
        )

    elif query.data == "back":
        await query.edit_message_text(
            "📿 اختر الذكر:",
            reply_markup=adhkar_menu()
        )

    save_data(data)

# ----------------- MAIN -----------------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_handler))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
