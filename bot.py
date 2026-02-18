import sqlite3
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ================== TOKEN ==================
TOKEN = os.getenv("8500926319:AAGTRh-neXMwUrBOrzUFkOOEEclXKXSLg8c")

# ================== DATABASE ==================
conn = sqlite3.connect("tasbeeh.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS zikr (
    user_id INTEGER,
    zikr TEXT,
    count INTEGER,
    PRIMARY KEY (user_id, zikr)
)
""")
conn.commit()

def add_zikr(user_id, zikr):
    cursor.execute(
        "SELECT count FROM zikr WHERE user_id=? AND zikr=?",
        (user_id, zikr)
    )
    row = cursor.fetchone()

    if row:
        cursor.execute(
            "UPDATE zikr SET count = count + 1 WHERE user_id=? AND zikr=?",
            (user_id, zikr)
        )
    else:
        cursor.execute(
            "INSERT INTO zikr (user_id, zikr, count) VALUES (?, ?, 1)",
            (user_id, zikr)
        )
    conn.commit()

def get_stats(user_id):
    cursor.execute(
        "SELECT zikr, count FROM zikr WHERE user_id=?",
        (user_id,)
    )
    return cursor.fetchall()

# ================== BOT UI ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🤍 الصلاة على النبي", callback_data="salat")],
        [InlineKeyboardButton("🌿 استغفار", callback_data="istighfar")],
        [InlineKeyboardButton("📿 تسبيح", callback_data="tasbeeh")],
        [InlineKeyboardButton("✨ حوقلة", callback_data="hawqala")],
        [InlineKeyboardButton("📊 الإحصائيات", callback_data="stats")]
    ]

    await update.message.reply_text(
        "📿 اختر الذكر:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    zikr_names = {
        "salat": "الصلاة على النبي ﷺ",
        "istighfar": "الاستغفار",
        "tasbeeh": "التسبيح",
        "hawqala": "لا حول ولا قوة إلا بالله"
    }

    if data == "stats":
        stats = get_stats(user_id)
        if not stats:
            text = "📭 لم تقم بأي ذكر بعد"
        else:
            text = "📊 إحصائياتك:\n\n"
            for z, c in stats:
                text += f"🔹 {z} : {c}\n"

        await query.edit_message_text(text)
        return

    if data == "back":
        await start(update, context)
        return

    # زيادة العداد
    add_zikr(user_id, zikr_names[data])

    keyboard = [
        [InlineKeyboardButton("➕ تسبيحة", callback_data=data)],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
    ]

    await query.edit_message_text(
        f"🧮 {zikr_names[data]}\nاضغط للعدّ",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== RUN ==================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
