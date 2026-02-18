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
DEFAULT_DATA = {"users": {}}

# --------- أذكار تصاعدية (تسبيح) ---------
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

# --------- أذكار ثابتة (تنازلية تلقائية) ---------
AZKAR_FIXED = {
    "sabah": {
        "title": "🌅 أذكار الصباح",
        "list": [
            {"text": "اللّهُ لاَ إِلَـهَ إِلاَّ هُوَ الْحَيُّ الْقَيُّومُ لاَ تَأْخُذُهُ سِنَةٌ وَلاَ نَوْمٌ لَّهُ مَا فِي السَّمَاوَاتِ وَمَا فِي الأَرْضِ مَن ذَا الَّذِي يَشْفَعُ عِنْدَهُ إِلاَّ بِإِذْنِهِ يَعْلَمُ مَا بَيْنَ أَيْدِيهِمْ وَمَا خَلْفَهُمْ وَلاَ يُحِيطُونَ بِشَيْءٍ مِّنْ عِلْمِهِ إِلاَّ بِمَا شَاء وَسِعَ كُرْسِيُّهُ السَّمَاوَاتِ وَالأَرْضَ وَلاَ يَؤُودُهُ حِفْظُهُمَا وَهُوَ الْعَلِيُّ الْعَظِيمُ. [آية الكرسى - البقرة 255]. ", "count": 1},
            {"text": "قُلْ هُوَ ٱللَّهُ أَحَدٌ، ٱللَّهُ ٱلصَّمَدُ، لَمْ يَلِدْ وَلَمْ يُولَدْ، وَلَمْ يَكُن لَّهُۥ كُفُوًا أَحَدٌۢ. ", "count": 3},
            {"text": "قُلْ أَعُوذُ بِرَبِّ ٱلْفَلَقِ، مِن شَرِّ مَا خَلَقَ، وَمِن شَرِّ غَاسِقٍ إِذَا وَقَبَ، وَمِن شَرِّ ٱلنَّفَّٰثَٰتِ فِى ٱلْعُقَدِ، وَمِن شَرِّ حَاسِدٍ إِذَا حَسَدَ. ", "count": 3},
            {"text": "قُلْ أَعُوذُ بِرَبِّ ٱلنَّاسِ، مَلِكِ ٱلنَّاسِ، إِلَٰهِ ٱلنَّاسِ، مِن شَرِّ ٱلْوَسْوَاسِ ٱلْخَنَّاسِ، ٱلَّذِى يُوَسْوِسُ فِى صُدُورِ ٱلنَّاسِ، مِنَ ٱلْجِنَّةِ وَٱلنَّاسِ. ", "count": 3}
            {"text": "أَصْـبَحْنا وَأَصْـبَحَ المُـلْكُ لله وَالحَمدُ لله ، لا إلهَ إلاّ اللّهُ وَحدَهُ لا شَريكَ لهُ، لهُ المُـلكُ ولهُ الحَمْـد، وهُوَ على كلّ شَيءٍ قدير ، رَبِّ أسْـأَلُـكَ خَـيرَ ما في هـذا اليوم وَخَـيرَ ما بَعْـدَه ، وَأَعـوذُ بِكَ مِنْ شَـرِّ ما في هـذا اليوم وَشَرِّ ما بَعْـدَه، رَبِّ أَعـوذُبِكَ مِنَ الْكَسَـلِ وَسـوءِ الْكِـبَر ، رَبِّ أَعـوذُ بِكَ مِنْ عَـذابٍ في النّـارِ وَعَـذابٍ في القَـبْر. ", "count": 1}
            {"text": "اللّهـمَّ أَنْتَ رَبِّـي لا إلهَ إلاّ أَنْتَ ، خَلَقْتَنـي وَأَنا عَبْـدُك ، وَأَنا عَلـى عَهْـدِكَ وَوَعْـدِكَ ما اسْتَـطَعْـت ، أَعـوذُبِكَ مِنْ شَـرِّ ما صَنَـعْت ، أَبـوءُ لَـكَ بِنِعْـمَتِـكَ عَلَـيَّ وَأَبـوءُ بِذَنْـبي فَاغْفـِرْ لي فَإِنَّـهُ لا يَغْـفِرُ الذُّنـوبَ إِلاّ أَنْتَ . ", "count": 1}
            {"text": "رَضيـتُ بِاللهِ رَبَّـاً وَبِالإسْلامِ ديـناً وَبِمُحَـمَّدٍ صلى الله عليه وسلم نَبِيّـاً. ", "count": 3}
            {"text": "اللّهُـمَّ إِنِّـي أَصْبَـحْتُ أُشْـهِدُك ، وَأُشْـهِدُ حَمَلَـةَ عَـرْشِـك ، وَمَلَائِكَتَكَ ، وَجَمـيعَ خَلْـقِك ، أَنَّـكَ أَنْـتَ اللهُ لا إلهَ إلاّ أَنْـتَ وَحْـدَكَ لا شَريكَ لَـك ، وَأَنَّ ُ مُحَمّـداً عَبْـدُكَ وَرَسـولُـك. ", "count": 4}
            {"text": "اللّهُـمَّ ما أَصْبَـَحَ بي مِـنْ نِعْـمَةٍ أَو بِأَحَـدٍ مِـنْ خَلْـقِك ، فَمِـنْكَ وَحْـدَكَ لا شريكَ لَـك ، فَلَـكَ الْحَمْـدُ وَلَـكَ الشُّكْـر. ", "count": 1}
            {"text": "حَسْبِـيَ اللّهُ لا إلهَ إلاّ هُوَ عَلَـيهِ تَوَكَّـلتُ وَهُوَ رَبُّ العَرْشِ العَظـيم. ", "count": 7}
            {"text": "بِسـمِ اللهِ الذي لا يَضُـرُّ مَعَ اسمِـهِ شَيءٌ في الأرْضِ وَلا في السّمـاءِ وَهـوَ السّمـيعُ العَلـيم. ", "count": 3}
            {"text": "اللّهُـمَّ بِكَ أَصْـبَحْنا وَبِكَ أَمْسَـينا ، وَبِكَ نَحْـيا وَبِكَ نَمُـوتُ وَإِلَـيْكَ النُّـشُور. ", "count": 1}
            {"text": "أَصْبَـحْـنا عَلَى فِطْرَةِ الإسْلاَمِ، وَعَلَى كَلِمَةِ الإِخْلاَصِ، وَعَلَى دِينِ نَبِيِّنَا مُحَمَّدٍ صَلَّى اللهُ عَلَيْهِ وَسَلَّمَ، وَعَلَى مِلَّةِ أَبِينَا إبْرَاهِيمَ حَنِيفاً مُسْلِماً وَمَا كَانَ مِنَ المُشْرِكِينَ. ", "count": 1}
            {"text": "سُبْحـانَ اللهِ وَبِحَمْـدِهِ عَدَدَ خَلْـقِه ، وَرِضـا نَفْسِـه ، وَزِنَـةَ عَـرْشِـه ، وَمِـدادَ كَلِمـاتِـه. ", "count": 3}
            {"text": "اللّهُـمَّ عافِـني في بَدَنـي ، اللّهُـمَّ عافِـني في سَمْـعي ، اللّهُـمَّ عافِـني في بَصَـري ، لا إلهَ إلاّ أَنْـتَ. ", "count": 3}
            {"text": "اللّهُـمَّ إِنّـي أَعـوذُ بِكَ مِنَ الْكُـفر ، وَالفَـقْر ، وَأَعـوذُ بِكَ مِنْ عَذابِ القَـبْر ، لا إلهَ إلاّ أَنْـتَ. ", "count": 3}
            {"text": "اللّهُـمَّ إِنِّـي أسْـأَلُـكَ العَـفْوَ وَالعـافِـيةَ في الدُّنْـيا وَالآخِـرَة ، اللّهُـمَّ إِنِّـي أسْـأَلُـكَ العَـفْوَ وَالعـافِـيةَ في ديني وَدُنْـيايَ وَأهْـلي وَمالـي ، اللّهُـمَّ اسْتُـرْ عـوْراتي وَآمِـنْ رَوْعاتـي ، اللّهُـمَّ احْفَظْـني مِن بَـينِ يَدَيَّ وَمِن خَلْفـي وَعَن يَمـيني وَعَن شِمـالي ، وَمِن فَوْقـي ، وَأَعـوذُ بِعَظَمَـتِكَ أَن أُغْـتالَ مِن تَحْتـي. ", "count": 1}
{"text": "يَا حَيُّ يَا قيُّومُ بِرَحْمَتِكَ أسْتَغِيثُ أصْلِحْ لِي شَأنِي كُلَّهُ وَلاَ تَكِلْنِي إلَى نَفْسِي طَـرْفَةَ عَيْنٍ. ", "count": 3}
{"text": "أَصْبَـحْـنا وَأَصْبَـحْ المُـلكُ للهِ رَبِّ العـالَمـين ، اللّهُـمَّ إِنِّـي أسْـأَلُـكَ خَـيْرَ هـذا الـيَوْم ، فَـتْحَهُ ، وَنَصْـرَهُ ، وَنـورَهُ وَبَـرَكَتَـهُ ، وَهُـداهُ ، وَأَعـوذُ بِـكَ مِـنْ شَـرِّ ما فـيهِ وَشَـرِّ ما بَعْـدَه. ", "count": 1}
{"text": "اللّهُـمَّ عالِـمَ الغَـيْبِ وَالشّـهادَةِ فاطِـرَ السّماواتِ وَالأرْضِ رَبَّ كـلِّ شَـيءٍ وَمَليـكَه ، أَشْهَـدُ أَنْ لا إِلـهَ إِلاّ أَنْت ، أَعـوذُ بِكَ مِن شَـرِّ نَفْسـي وَمِن شَـرِّ الشَّيْـطانِ وَشِرْكِهِ ، وَأَنْ أَقْتَـرِفَ عَلـى نَفْسـي سوءاً أَوْ أَجُـرَّهُ إِلـى مُسْـلِم. ", "count": 1}
{"text": "أَعـوذُ بِكَلِمـاتِ اللّهِ التّـامّـاتِ مِنْ شَـرِّ ما خَلَـق. ", "count": 3}
{"text": "اللَّهُمَّ صَلِّ وَسَلِّمْ وَبَارِكْ على نَبِيِّنَا مُحمَّد. ", "count": 10}
{"text": "اللَّهُمَّ إِنَّا نَعُوذُ بِكَ مِنْ أَنْ نُشْرِكَ بِكَ شَيْئًا نَعْلَمُهُ ، وَنَسْتَغْفِرُكَ لِمَا لَا نَعْلَمُهُ. ", "count": 3}
{"text": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنْ الْهَمِّ وَالْحَزَنِ، وَأَعُوذُ بِكَ مِنْ الْعَجْزِ وَالْكَسَلِ، وَأَعُوذُ بِكَ مِنْ الْجُبْنِ وَالْبُخْلِ، وَأَعُوذُ بِكَ مِنْ غَلَبَةِ الدَّيْنِ، وَقَهْرِ الرِّجَالِ. ", "count": 3}
{"text": "أسْتَغْفِرُ اللهَ العَظِيمَ الَّذِي لاَ إلَهَ إلاَّ هُوَ، الحَيُّ القَيُّومُ، وَأتُوبُ إلَيهِ. ", "count": 3}
{"text": "يَا رَبِّ , لَكَ الْحَمْدُ كَمَا يَنْبَغِي لِجَلَالِ وَجْهِكَ , وَلِعَظِيمِ سُلْطَانِكَ. ", "count": 3}
{"text": "اللَّهُمَّ إِنِّي أَسْأَلُكَ عِلْمًا نَافِعًا، وَرِزْقًا طَيِّبًا، وَعَمَلًا مُتَقَبَّلًا. ", "count": 1}
{"text": "اللَّهُمَّ أَنْتَ رَبِّي لا إِلَهَ إِلا أَنْتَ ، عَلَيْكَ تَوَكَّلْتُ ، وَأَنْتَ رَبُّ الْعَرْشِ الْعَظِيمِ , مَا شَاءَ اللَّهُ كَانَ ، وَمَا لَمْ يَشَأْ لَمْ يَكُنْ ، وَلا حَوْلَ وَلا قُوَّةَ إِلا بِاللَّهِ الْعَلِيِّ الْعَظِيمِ , أَعْلَمُ أَنَّ اللَّهَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ ، وَأَنَّ اللَّهَ قَدْ أَحَاطَ بِكُلِّ شَيْءٍ عِلْمًا , اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنْ شَرِّ نَفْسِي ، وَمِنْ شَرِّ كُلِّ دَابَّةٍ أَنْتَ آخِذٌ بِنَاصِيَتِهَا ، إِنَّ رَبِّي عَلَى صِرَاطٍ مُسْتَقِيمٍ. ", "count": 1}
{"text": "لَا إلَه إلّا اللهُ وَحْدَهُ لَا شَرِيكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ وَهُوَ عَلَى كُلِّ شَيْءِ قَدِيرِ. ", "count": 100}
{"text": "سُبْحـانَ اللهِ وَبِحَمْـدِهِ. ", "count": 100}
{"text": "أسْتَغْفِرُ اللهَ وَأتُوبُ إلَيْهِ ", "count": 100}
        ]
    },
    "masaa": {
        "title": "🌙 أذكار المساء",
        "list": [
            {"text": "أمسينا وأمسى الملك لله", "count": 1},
            {"text": "اللهم بك أمسينا وبك أصبحنا", "count": 1},
            {"text": "سبحان الله وبحمده", "count": 100},
            {"text": "أعوذ بكلمات الله التامات من شر ما خلق", "count": 3}
        ]
    },
    "sleep": {
        "title": "😴 أذكار النوم",
        "list": [
            {"text": "باسمك ربي وضعت جنبي", "count": 1},
            {"text": "آية الكرسي", "count": 1},
            {"text": "سبحان الله", "count": 33},
            {"text": "الحمد لله", "count": 33},
            {"text": "الله أكبر", "count": 34}
        ]
    },
    "after_salat": {
        "title": "🕌 أذكار بعد الصلاة",
        "list": [
            {"text": "أستغفر الله", "count": 3},
            {"text": "اللهم أنت السلام ومنك السلام", "count": 1},
            {"text": "سبحان الله", "count": 33},
            {"text": "الحمد لله", "count": 33},
            {"text": "الله أكبر", "count": 34}
        ]
    }
}

# ===================== STORAGE =====================
def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_DATA, f, ensure_ascii=False, indent=2)
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
            "counts": {k: 0 for k in AZKAR_TASBEEH.keys()},
            "total": 0,
            "fixed_progress": {}
        }
        save_data(DATA)
    return DATA["users"][uid]

# ===================== DIGITAL COUNTER =====================
def digital_counter(num):
    digits = {"0":"𝟬","1":"𝟭","2":"𝟮","3":"𝟯","4":"𝟰","5":"𝟱","6":"𝟲","7":"𝟳","8":"𝟴","9":"𝟵"}
    return "".join(digits[d] for d in str(max(0, num)))

# ===================== UI =====================
def main_menu():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📿 تسبيح", callback_data="menu_tasbeeh"),
        InlineKeyboardButton("🌿 أذكار ثابتة", callback_data="menu_fixed"),
        InlineKeyboardButton("📊 الإحصائيات", callback_data="menu_stats")
    )
    return kb

def tasbeeh_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    for k,v in AZKAR_TASBEEH.items():
        kb.add(InlineKeyboardButton(f"{v['emoji']} {v['name']}", callback_data=f"zikr|{k}"))
    kb.add(InlineKeyboardButton("⬅️ رجوع", callback_data="back_main"))
    return kb

def fixed_menu():
    kb = InlineKeyboardMarkup(row_width=1)
    for k,v in AZKAR_FIXED.items():
        kb.add(InlineKeyboardButton(v["title"], callback_data=f"fixed|{k}"))
    kb.add(InlineKeyboardButton("⬅️ رجوع", callback_data="back_main"))
    return kb

def tasbeeh_counter_menu(key):
    kb = InlineKeyboardMarkup(row_width=3)
    kb.add(
        InlineKeyboardButton("➕", callback_data=f"add|{key}"),
        InlineKeyboardButton("➖", callback_data=f"sub|{key}"),
        InlineKeyboardButton("🔄", callback_data=f"reset|{key}")
    )
    kb.add(InlineKeyboardButton("⬅️ رجوع", callback_data="menu_tasbeeh"))
    return kb

def fixed_counter_menu(key):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("✔️ تم", callback_data=f"fixed_add|{key}"))
    kb.add(InlineKeyboardButton("⬅️ رجوع", callback_data="menu_fixed"))
    return kb

# ===================== HELPERS =====================
def format_stats(user):
    lines = ["<b>📊 إحصائياتك:</b>\n"]
    for k,v in AZKAR_TASBEEH.items():
        lines.append(f"{v['emoji']} {v['name']} : <b>{user['counts'][k]:,}</b>")
    lines.append(f"\n✨ المجموع الكلي: <b>{user['total']:,}</b>")
    return "\n".join(lines)

# ===================== HANDLERS =====================
@bot.message_handler(commands=["start"])
def start(m):
    get_user(m.from_user.id)
    bot.send_message(m.chat.id,"📿 مرحباً بك في بوت الأذكار",reply_markup=main_menu())

@bot.callback_query_handler(func=lambda c: True)
def callbacks(c):
    try:
        uid = c.from_user.id
        user = get_user(uid)
        data = c.data

        # -------- MAIN MENUS --------
        if data == "menu_tasbeeh":
            bot.edit_message_text("📿 اختر ذكر:", c.message.chat.id, c.message.message_id, reply_markup=tasbeeh_menu())

        elif data == "menu_fixed":
            bot.edit_message_text("🌿 اختر نوع الأذكار:", c.message.chat.id, c.message.message_id, reply_markup=fixed_menu())

        elif data == "back_main":
            bot.edit_message_text("📿 القائمة الرئيسية", c.message.chat.id, c.message.message_id, reply_markup=main_menu())

        # -------- TASBEEH --------
        elif data.startswith("zikr|"):
            key = data.split("|")[1]
            z = AZKAR_TASBEEH[key]
            text = f"{z['emoji']} <b>{z['name']}</b>\n\n🔢 {digital_counter(user['counts'][key])}"
            bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=tasbeeh_counter_menu(key))

        elif data.startswith("add|"):
            key = data.split("|")[1]
            user["counts"][key]+=1
            user["total"]+=1
            save_data(DATA)
            z = AZKAR_TASBEEH[key]
            text = f"{z['emoji']} <b>{z['name']}</b>\n\n🔢 {digital_counter(user['counts'][key])}"
            bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=tasbeeh_counter_menu(key))

        elif data.startswith("sub|"):
            key = data.split("|")[1]
            if user["counts"][key]>0:
                user["counts"][key]-=1
                user["total"]-=1
            save_data(DATA)
            z = AZKAR_TASBEEH[key]
            text = f"{z['emoji']} <b>{z['name']}</b>\n\n🔢 {digital_counter(user['counts'][key])}"
            bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=tasbeeh_counter_menu(key))

        elif data.startswith("reset|"):
            key = data.split("|")[1]
            user["total"]-=user["counts"][key]
            user["counts"][key]=0
            save_data(DATA)
            z = AZKAR_TASBEEH[key]
            text = f"{z['emoji']} <b>{z['name']}</b>\n\n🔢 {digital_counter(0)}"
            bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=tasbeeh_counter_menu(key))

        # -------- FIXED AZKAR --------
        elif data.startswith("fixed|"):
            key = data.split("|")[1]
            user["fixed_progress"][key]={"index":0,"remaining":AZKAR_FIXED[key]["list"][0]["count"]}
            save_data(DATA)
            item=AZKAR_FIXED[key]["list"][0]
            text=f"{AZKAR_FIXED[key]['title']}\n\n{item['text']}\n\n🔢 {digital_counter(item['count'])}"
            bot.edit_message_text(text,c.message.chat.id,c.message.message_id,reply_markup=fixed_counter_menu(key))

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
                    bot.edit_message_text("🌸 بارك الله لك وجعله في ميزان حسناتك",c.message.chat.id,c.message.message_id,reply_markup=main_menu())
                    bot.answer_callback_query(c.id)
                    return
                next_item=AZKAR_FIXED[key]["list"][prog["index"]]
                prog["remaining"]=next_item["count"]

            save_data(DATA)
            item=AZKAR_FIXED[key]["list"][prog["index"]]
            text=f"{AZKAR_FIXED[key]['title']}\n\n{item['text']}\n\n🔢 {digital_counter(prog['remaining'])}"
            bot.edit_message_text(text,c.message.chat.id,c.message.message_id,reply_markup=fixed_counter_menu(key))

        # -------- STATS --------
        elif data=="menu_stats":
            kb=InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("⬅️ رجوع",callback_data="back_main"))
            bot.edit_message_text(format_stats(user),c.message.chat.id,c.message.message_id,reply_markup=kb)

        bot.answer_callback_query(c.id)

    except Exception as e:
        print("ERROR:",e)
        bot.answer_callback_query(c.id,"حدث خطأ ❌",show_alert=False)

# ===================== RUN =====================
print("📿 Zikr Bot running...")
bot.infinity_polling(skip_pending=True)

