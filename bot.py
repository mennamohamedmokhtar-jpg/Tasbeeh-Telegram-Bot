# -*- coding: utf-8 -*-
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os, time, json

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
DATA_FILE = "data.json"
ADMIN_ID = 5123695463

DEFAULT_DATA = {"users": {}}
AZKAR_TASBEEH = {
    "tasbeeh": {"name": "سبحان الله", "emoji": "🟢"},
    "tahmeed": {"name": "الحمد لله", "emoji": "🔵"},
    "takbeer": {"name": "الله أكبر", "emoji": "🟣"},
    "tahleel": {"name": "لا إله إلا الله", "emoji": "🟠"},
    "istighfar": {"name": "أستغفر الله", "emoji": "🟡"},
    "salat": {"name": "اللهم صلِّ على محمد ﷺ", "emoji": "🤍"},
    "hawqala": {"name": "لا حول ولا قوة إلا بالله", "emoji": "🟤"},
    "hirz": {"name": "بسم الله الذي لا يضر مع اسمه شيء في الأرض ولا في السماء وهو السميع العليم", "emoji": "🛡️"}
}
AZKAR_FIXED = {
    "sabah": {"title":"🌅 أذكار الصباح","list":[{"text":"أصبحنا وأصبح الملك لله","count":1},{"text":"اللهم بك أصبحنا وبك أمسينا","count":1},{"text":"سبحان الله وبحمده","count":100},{"text":"لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير","count":10}]},
    "masaa": {"title":"🌙 أذكار المساء","list":[{"text":"أمسينا وأمسى الملك لله","count":1},{"text":"اللهم بك أمسينا وبك أصبحنا","count":1},{"text":"سبحان الله وبحمده","count":100},{"text":"أعوذ بكلمات الله التامات من شر ما خلق","count":3}]},
    "sleep": {"title":"😴 أذكار النوم","list":[{"text":"باسمك ربي وضعت جنبي","count":1},{"text":"آية الكرسي","count":1},{"text":"سبحان الله","count":33},{"text":"الحمد لله","count":33},{"text":"الله أكبر","count":34}]},
    "after_salat": {"title":"🕌 أذكار بعد الصلاة","list":[{"text":"أستغفر الله","count":3},{"text":"اللهم أنت السلام ومنك السلام","count":1},{"text":"سبحان الله","count":33},{"text":"الحمد لله","count":33},{"text":"الله أكبر","count":34}]}
}

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE,"w",encoding="utf-8") as f:
            json.dump(DEFAULT_DATA,f,ensure_ascii=False,indent=2)
    try:
        with open(DATA_FILE,"r",encoding="utf-8") as f:
            return json.load(f)
    except:
        return DEFAULT_DATA.copy()

def save_data(data):
    with open(DATA_FILE,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)

DATA = load_data()

def get_user(uid):
    uid=str(uid)
    if uid not in DATA["users"]:
        DATA["users"][uid]={"counts":{k:0 for k in AZKAR_TASBEEH.keys()},"total":0,"fixed_progress":{}}
        save_data(DATA)
    return DATA["users"][uid]

def digital_counter(num):
    digits={"0":"𝟬","1":"𝟭","2":"𝟮","3":"𝟯","4":"𝟰","5":"𝟱","6":"𝟲","7":"𝟳","8":"𝟴","9":"𝟵"}
    return "".join(digits[d] for d in str(max(0,num)))

def main_menu():
    kb=InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("📿 تسبيح",callback_data="menu_tasbeeh"))
    kb.add(InlineKeyboardButton("🌿 أذكار ثابتة",callback_data="menu_fixed"))
    kb.add(InlineKeyboardButton("📊 إحصائياتي",callback_data="menu_stats"))
    if ADMIN_ID:
        kb.add(InlineKeyboardButton("📊 الإحصائيات العامة",callback_data="menu_global"))
    return kb

def tasbeeh_menu():
    kb=InlineKeyboardMarkup(row_width=2)
    for k,v in AZKAR_TASBEEH.items():
        kb.add(InlineKeyboardButton(f"{v['emoji']} {v['name']}",callback_data=f"zikr|{k}"))
    kb.add(InlineKeyboardButton("⬅️ القائمة الرئيسية",callback_data="back_main"))
    return kb

def fixed_menu():
    kb=InlineKeyboardMarkup(row_width=1)
    for k,v in AZKAR_FIXED.items():
        kb.add(InlineKeyboardButton(v["title"],callback_data=f"fixed|{k}"))
    kb.add(InlineKeyboardButton("⬅️ القائمة الرئيسية",callback_data="back_main"))
    return kb

def tasbeeh_counter_menu(key):
    kb=InlineKeyboardMarkup(row_width=3)
    kb.add(InlineKeyboardButton("➕",callback_data=f"add|{key}"),InlineKeyboardButton("➖",callback_data=f"sub|{key}"),InlineKeyboardButton("🔄",callback_data=f"reset|{key}"))
    kb.add(InlineKeyboardButton("⬅️ القائمة الرئيسية",callback_data="back_main"))
    return kb

def fixed_counter_menu(key):
    kb=InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("✔️ تم",callback_data=f"fixed_add|{key}"))
    kb.add(InlineKeyboardButton("⬅️ القائمة الرئيسية",callback_data="back_main"))
    return kb

def format_stats(user):
    lines=["<b>📊 إحصائياتك:</b>\n"]
    for k,v in AZKAR_TASBEEH.items():
        lines.append(f"{v['emoji']} {v['name']} : <b>{user['counts'][k]:,}</b>")
    lines.append(f"\n✨ المجموع الكلي: <b>{user['total']:,}</b>")
    return "\n".join(lines)

def global_stats():
    total_users=len(DATA["users"])
    total_all=sum(u.get("total",0) for u in DATA["users"].values())
    global_counts={k:sum(u.get("counts",{}).get(k,0) for u in DATA["users"].values()) for k in AZKAR_TASBEEH.keys()}
    most_used=max(global_counts,key=global_counts.get) if global_counts else None
    most_used_name=AZKAR_TASBEEH[most_used]["name"] if most_used else "لا يوجد"
    most_used_count=global_counts[most_used] if most_used else 0
    return f"📊 <b>الإحصائيات العامة للبوت</b>\n\n👥 عدد المستخدمين: <b>{total_users}</b>\n📿 إجمالي التسبيحات: <b>{total_all:,}</b>\n🔥 أكثر ذكر استخداماً: <b>{most_used_name}</b> ({most_used_count:,} مرة)"

@bot.message_handler(commands=["start"])
def start(m):
    get_user(m.from_user.id)
    bot.send_message(m.chat.id,"📿 مرحباً بك في بوت الأذكار",reply_markup=main_menu())

@bot.callback_query_handler(func=lambda c: True)
def callbacks(c):
    try:
        uid=c.from_user.id
        user=get_user(uid)
        data=c.data

        if data=="menu_tasbeeh":
            bot.send_message(uid,"📿 اختر ذكر:",reply_markup=tasbeeh_menu())
        elif data=="menu_fixed":
            bot.send_message(uid,"🌿 اختر نوع الأذكار:",reply_markup=fixed_menu())
        elif data=="back_main":
            bot.send_message(uid,"📿 القائمة الرئيسية",reply_markup=main_menu())
        elif data=="menu_stats":
            kb=InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("⬅️ القائمة الرئيسية",callback_data="back_main"))
            bot.send_message(uid,format_stats(user),reply_markup=kb)
        elif data=="menu_global" and uid==ADMIN_ID:
            kb=InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("⬅️ القائمة الرئيسية",callback_data="back_main"))
            bot.send_message(uid,global_stats(),reply_markup=kb)
        elif data.startswith("zikr|"):
            key=data.split("|")[1]
            z=AZKAR_TASBEEH[key]
            text=f"{z['emoji']} <b>{z['name']}</b>\n\n🔢 {digital_counter(user['counts'][key])}"
            bot.send_message(uid,text,reply_markup=tasbeeh_counter_menu(key))
        elif data.startswith("add|"):
            key=data.split("|")[1]
            user["counts"][key]+=1
            user["total"]+=1
            save_data(DATA)
            z=AZKAR_TASBEEH[key]
            text=f"{z['emoji']} <b>{z['name']}</b>\n\n🔢 {digital_counter(user['counts'][key])}"
            bot.send_message(uid,text,reply_markup=tasbeeh_counter_menu(key))
        elif data.startswith("sub|"):
            key=data.split("|")[1]
            if user["counts"][key]>0:
                user["counts"][key]-=1
                user["total"]-=1
            save_data(DATA)
            z=AZKAR_TASBEEH[key]
            text=f"{z['emoji']} <b>{z['name']}</b>\n\n🔢 {digital_counter(user['counts'][key])}"
            bot.send_message(uid,text,reply_markup=tasbeeh_counter_menu(key))
        elif data.startswith("reset|"):
            key=data.split("|")[1]
            user["total"]-=user["counts"][key]
            user["counts"][key]=0
            save_data(DATA)
            z=AZKAR_TASBEEH[key]
            text=f"{z['emoji']} <b>{z['name']}</b>\n\n🔢 {digital_counter(0)}"
            bot.send_message(uid,text,reply_markup=tasbeeh_counter_menu(key))
        elif data.startswith("fixed|"):
            key=data.split("|")[1]
            user["fixed_progress"][key]={"index":0,"remaining":AZKAR_FIXED[key]["list"][0]["count"]}
            save_data(DATA)
            item=AZKAR_FIXED[key]["list"][0]
            text=f"{AZKAR_FIXED[key]['title']}\n\n{item['text']}\n\n🔢 {digital_counter(item['count'])}"
            bot.send_message(uid,text,reply_markup=fixed_counter_menu(key))
        elif data.startswith("fixed_add|"):
            key=data.split("|")[1]
            if key not in user["fixed_progress"]:
                bot.answer_callback_query(c.id)
                return
            prog=user["fixed_progress"][key]
            prog["remaining"]-=1
            if prog["remaining"]<=0:
                prog["index"]+=1
                if prog["index"]>=len(AZKAR_FIXED[key]["list"]):
                    user["fixed_progress"].pop(key,None)
                    save_data(DATA)
                    bot.send_message(uid,"🌸 بارك الله لك وجعله في ميزان حسناتك",reply_markup=main_menu())
                    bot.answer_callback_query(c.id)
                    return
                next_item=AZKAR_FIXED[key]["list"][prog["index"]]
                prog["remaining"]=next_item["count"]
            save_data(DATA)
            item=AZKAR_FIXED[key]["list"][prog["index"]]
            text=f"{AZKAR_FIXED[key]['title']}\n\n{item['text']}\n\n🔢 {digital_counter(prog['remaining'])}"
            bot.send_message(uid,text,reply_markup=fixed_counter_menu(key))

        bot.answer_callback_query(c.id)
    except Exception as e:
        print("ERROR:",e)
        bot.answer_callback_query(c.id,"حدث خطأ ❌",show_alert=False)

print("📿 Zikr Bot running...")
bot.infinity_polling(skip_pending=True)
