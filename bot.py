import os
import random
import time
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask
import threading

# Render port tələbi üçün Flask serveri
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "USDT Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

BOT_TOKEN = "8982385389:AAESNUF2bHc8kOqKPBGph7_369O4UPbZDyQ"
BOT_USERNAME = "USDT_Qazan_bot"
ADMIN_USERNAME = "@usdtqazanadmin"
TRC20_WALLET = "TKf5cMmCqjR76gN62Vim9BaP3G5XL4a7kp"
CHANNELS = {
    "1": {"name": "Craft Betting", "url": "https://t.me/craftbetting"},
    "2": {"name": "Merc ve Kuponlar", "url": "https://t.me/mercvekuponlarr"},
    "3": {"name": "Qizil Analiz", "url": "https://t.me/qizilanaliz"},
    "4": {"name": "Resmi Kanal", "url": "https://t.me/+ZMvnUmwWkJ0wZDI0"}
}

TEXTS = {
    "az": {
        "welcome": "👋 Salam! Zəhmət olmasa dil seçin:",
        "rate_info": "💳 **Məzənnə:**\n• Adi üzv: 1000 xal = 0.05$\n• VIP üzv: 1000 xal = 0.08$",
        "main_menu": "Əsas Menyu:",
        "spin": "🎰 Çarx", "balance": "💰 Balans", "ref": "👥 Referal",
        "tasks": "📢 Tapşırıqlar", "vip": "👑 VIP", "withdraw": "💸 Çıxarış",
        "info": "ℹ️ Məlumat", "lang": "🌐 Dil dəyiş", "channel": "📢 Rəsmi kanal", "notify": "🔔 Bot bildirişləri",
        "back": "🔙 Geri"
    },
    "tr": {
        "welcome": "👋 Merhaba! Lütfen dil seçin:",
        "rate_info": "💳 **Kur:**\n• Normal üye: 1000 puan = 0.05$\n• VIP üye: 1000 puan = 0.08$",
        "main_menu": "Ana Menü:",
        "spin": "🎰 Çark", "balance": "💰 Bakiye", "ref": "👥 Referans",
        "tasks": "📢 Görevler", "vip": "👑 VIP", "withdraw": "💸 Çekim",
        "info": "ℹ️ Bilgi", "lang": "🌐 Dil değiştir", "channel": "📢 Resmi kanal", "notify": "🔔 Bildirimler",
        "back": "🔙 Geri"
    },
    "ru": {
        "welcome": "👋 Здравствуйте! Пожалуйста, выберите язык:",
        "rate_info": "💳 **Курс:**\n• Обычный: 1000 очков = 0.05$\n• VIP: 1000 очков = 0.08$",
        "main_menu": "Главное меню:",
        "spin": "🎰 Колесо", "balance": "💰 Баланс", "ref": "👥 Рефералы",
        "tasks": "📢 Задания", "vip": "👑 VIP", "withdraw": "💸 Вывод",
        "info": "ℹ️ Информация", "lang": "🌐 Сменить язык", "channel": "📢 Официальный канал", "notify": "🔔 Уведомления",
        "back": "🔙 Назад"
    },
    "en": {
        "welcome": "👋 Hello! Please select language:",
        "rate_info": "💳 **Rate:**\n• Regular: 1000 pts = 0.05$\n• VIP: 1000 pts = 0.08$",
        "main_menu": "Main Menu:",
        "spin": "🎰 Wheel", "balance": "💰 Balance", "ref": "👥 Referrals",
        "tasks": "📢 Tasks", "vip": "👑 VIP", "withdraw": "💸 Withdraw",
        "info": "ℹ️ Info", "lang": "🌐 Change Lang", "channel": "📢 Official Channel", "notify": "🔔 Notifications",
        "back": "🔙 Back"
    }
}

def get_db():
    conn = sqlite3_connect("usdt_bot.db") if 'sqlite3_connect' in globals() else sqlite3.connect("usdt_bot.db")
    conn.row_factory = sqlite3.Row
    return conn

import sqlite3

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        points INTEGER DEFAULT 0,
        bonus_spins INTEGER DEFAULT 0,
        vip_until TEXT,
        referrer_id INTEGER,
        last_spin_reset INTEGER DEFAULT 0,
        daily_spin_count INTEGER DEFAULT 0,
        lang TEXT DEFAULT 'az',
        last_active INTEGER DEFAULT 0,
        tasks_completed TEXT DEFAULT '',
        notify_status INTEGER DEFAULT 1
    )
    """)
    conn.commit()
    conn.close()

init_db()

def get_user(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user(user_id, referrer_id=None):
    conn = get_db()
    cursor = conn.cursor()
    now = int(time.time())
    cursor.execute("""
    INSERT OR IGNORE INTO users (user_id, points, bonus_spins, referrer_id, lang, last_active)
    VALUES (?, 0, 0, ?, 'az', ?)
    """, (user_id, referrer_id, now))
    conn.commit()
    conn.close()

def get_lang(user):
    if user and 'lang' in user and user['lang'] in TEXTS:
        return user['lang']
    return 'az'

def is_vip(user_id):
    user = get_user(user_id)
    if not user or not user['vip_until']:
        return False
    try:
        return datetime.now() < datetime.fromisoformat(user['vip_until'])
    except:
        return False

def main_menu_keyboard(lang):
    t = TEXTS.get(lang, TEXTS['az'])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t["spin"], callback_data="spin_menu"), InlineKeyboardButton(t["balance"], callback_data="my_balance")],
        [InlineKeyboardButton(t["ref"], callback_data="referral"), InlineKeyboardButton(t["tasks"], callback_data="tasks")],
        [InlineKeyboardButton(t["vip"], callback_data="vip_menu"), InlineKeyboardButton(t["withdraw"], callback_data="withdraw_menu")],
        [InlineKeyboardButton(t["info"], callback_data="info"), InlineKeyboardButton(t["lang"], callback_data="change_lang")],
        [InlineKeyboardButton(t["channel"], url=CHANNELS["4"]["url"]), InlineKeyboardButton(t["notify"], callback_data="toggle_notify")]
    ])

def lang_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇦🇿 Azərbaycan", callback_data="set_lang_az"), InlineKeyboardButton("🇹🇷 Türkçe", callback_data="set_lang_tr")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru"), InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    referrer_id = int(args[0]) if args and args[0].isdigit() and int(args[0]) != user_id else None

    if not get_user(user_id):
        create_user(user_id, referrer_id)

    user = get_user(user_id)
    lang = get_lang(user)
    t = TEXTS[lang]

    text = f"{t['welcome']}\n\n{t['rate_info']}"
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=lang_keyboard())

async def handle_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    user = get_user(user_id)
    if not user:
        create_user(user_id)
        user = get_user(user_id)

    lang = get_lang(user)
    t = TEXTS[lang]
    back_kb = InlineKeyboardMarkup([[InlineKeyboardButton(t["back"], callback_data="main_menu")]])

    if data.startswith("set_lang_"):
        new_lang = data.split("_")[2]
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET lang = ? WHERE user_id = ?", (new_lang, user_id))
        conn.commit()
        conn.close()
        new_t = TEXTS[new_lang]
        await query.edit_message_text(f"{new_t['main_menu']}\n\n{new_t['rate_info']}", parse_mode="Markdown", reply_markup=main_menu_keyboard(new_lang))

    elif data == "change_lang":
        await query.edit_message_text(t["welcome"], reply_markup=lang_keyboard())

    elif data == "main_menu":
        await query.edit_message_text(f"{t['main_menu']}\n\n{t['rate_info']}", parse_mode="Markdown", reply_markup=main_menu_keyboard(lang))

    elif data == "my_balance":
        vip_status = "👑 VIP" if is_vip(user_id) else "👤 Adi Üzv"
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE referrer_id = ?", (user_id,))
        total_refs = cursor.fetchone()[0]
        conn.close()

        text = (
            f"💰 Sizi USDT Bot-da görməkdən məmnunuq!\n\n"
            f"• Ümumi balans: **{user['points']} Xal**\n"
            f"• Referal sayı: **{total_refs} nəfər**\n"
            f"• Status: **{vip_status}**"
        )
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_kb)

    elif data == "spin_menu":
        limit_text = "Çarx gündəlik 50 ədətdir və yenilənmə 24 saat sonra olacaq. 50 çarxdan sonra 10 hədiyyə çarx tələb edə bilərsiniz."
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🌀 Çarxı Fırlat", callback_data="do_spin")],
            [InlineKeyboardButton(t["back"], callback_data="main_menu")]
        ])
        await query.edit_message_text(f"🎰 **Şans Çarxı**\n\n{limit_text}\n\nFırlatmaq üçün düyməyə basın:", parse_mode="Markdown", reply_markup=kb)

    elif data == "do_spin":
        vip_st = is_vip(user_id)
        now = int(time.time())
        last_reset = user['last_spin_reset'] or 0
        spin_count = user['daily_spin_count'] or 0

        if now - last_reset >= 86400:
            spin_count = 0
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET daily_spin_count = 0, last_spin_reset = ? WHERE user_id = ?", (now, user_id))
            conn.commit()
            conn.close()

        if spin_count >= 50 and user['bonus_spins'] <= 0:
            await query.message.reply_text("🚫 Günlük 50 fırlatma limitiniz bitdi!")
            return

        if spin_count >= 50:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET bonus_spins = bonus_spins - 1 WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
        else:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET daily_spin_count = daily_spin_count + 1 WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()

        await query.message.reply_dice(emoji="🎰")
        await asyncio.sleep(2.5)

        if not vip_st:
            roll_opt = random.choices([35, 45, 55, 65, 0, "gift"], weights=[20, 20, 20, 10, 20, 10])[0]
        else:
            roll_opt = random.choices([60, 80, 100, 120, 0, "gift"], weights=[20, 20, 20, 10, 20, 10])[0]

        conn = get_db()
        cursor = conn.cursor()
        msg_text = ""
        if roll_opt == "gift":
            gift_spin = random.choices([2, 3, 5], weights=[50, 30, 20])[0]
            cursor.execute("UPDATE users SET bonus_spins = bonus_spins + ? WHERE user_id = ?", (gift_spin, user_id))
            msg_text = f"🎁 Təbriklər! Hədiyyə çarxda **+{gift_spin} fırlatma** qazandınız!"
        elif roll_opt == 0:
            msg_text = "😢 Çox təəssüf, bu dəfə boş gəldi (0 Xal)."
        else:
            cursor.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (roll_opt, user_id))
            msg_text = f"🎉 Təbriklər! **{roll_opt} Xal** qazandınız!"

        conn.commit()
        conn.close()

        updated_user = get_user(user_id)
        spin_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🌀 Çarxı Yenidən Fırlat", callback_data="do_spin")],
            [InlineKeyboardButton(t["back"], callback_data="spin_menu")]
        ])
        await query.message.reply_text(f"{msg_text}\n💰 Cari balans: **{updated_user['points']} Xal**", parse_mode="Markdown", reply_markup=spin_kb)

    elif data == "referral":
        ref_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, points FROM users WHERE referrer_id = ?", (user_id,))
        refs = cursor.fetchall()
        conn.close()

        reg_count = len(refs)
        vip_count = sum(1 for r in refs if is_vip(r['user_id']))

        text = (
            f"👥 **Referal Sistemi**\n\n"
            f"Linkiniz:\n`{ref_link}`\n\n"
            f"• Adi referal sayı: {reg_count}\n"
            f"• VIP referal sayı: {vip_count}\n\n"
            f"Hər 1000 xalı olan referaldan sizə 20 xal qazandırılır!"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Referalları yoxla", callback_data="check_refs")],
            [InlineKeyboardButton(t["back"], callback_data="main_menu")]
        ])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "check_refs":
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, points FROM users WHERE referrer_id = ?", (user_id,))
        refs = cursor.fetchall()
        conn.close()

        ref_list_txt = "📋 **Referallarınız:**\n\n"
        for r in refs:
            ref_list_txt += f"🆔 ID: `{r['user_id']}` | Xal: {r['points']}\n"

        if not refs:
            ref_list_txt += "Hələ ki referalınız yoxdur."

        await query.edit_message_text(ref_list_txt, parse_mode="Markdown", reply_markup=back_kb)

    elif data == "tasks":
        kb = [
            [InlineKeyboardButton("📢 Craft Betting", url=CHANNELS["1"]["url"])],
            [InlineKeyboardButton("📢 Merc ve Kuponlar", url=CHANNELS["2"]["url"])],
            [InlineKeyboardButton("📢 Qizil Analiz", url=CHANNELS["3"]["url"])],
            [InlineKeyboardButton("📢 Resmi Kanal", url=CHANNELS["4"]["url"])],
            [InlineKeyboardButton("✅ Tapşırıqları Yoxla", callback_data="verify_tasks")],
            [InlineKeyboardButton(t["back"], callback_data="main_menu")]
        ]
        await query.edit_message_text("📢 **Tapşırıqlar**\n\nBütün kanallara qoşulun və yoxla düyməsini basın (Hədiyyə: 100 Xal).", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

    elif data == "verify_tasks":
        if "completed" not in (user['tasks_completed'] or ""):
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET points = points + 100, tasks_completed = 'completed' WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            await query.message.reply_text("🎉 Təbriklər! Tapşırıqlar tamamlandı və balansınıza **100 Xal** əlavə olundu!")
        else:
            await query.message.reply_text("Siz bu tapşırığı artıq tamamlamısınız.")

    elif data == "vip_menu":
        text = (
            "👑 **VIP Üstünlükləri**\n\n"
            "• Yüksək çarx xalları\n"
            "• Daha sərfəli çıxarış dərəcələri (1000 xal = 0.08$)\n\n"
            "💳 **VIP Qiymətləri:**\n"
            "• 7 günlük: **3$**\n"
            "• 15 günlük: **5$**\n\n"
            f"Ödəniş Ünvanı (TRC20):\n`{TRC20_WALLET}`\n\n"
            f"Ödəniş çeki və ID kodunu {ADMIN_USERNAME} ünvanına göndərin."
        )
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_kb)

    elif data == "withdraw_menu":
        text = (
            f"💸 **Çıxarış Mərkəzi**\n\n"
            f"Şərtləri ödədikdən sonra müraciət çeki və ID-nizi **{ADMIN_USERNAME}** ünvanına göndərin."
        )
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_kb)

    elif data == "info":
        text = (
            f"ℹ️ **Bot Məlumatı**\n\n"
            f"• Bot tamamilə pulsuzdur. Əsas şərt referal cəlb etməyinizdir.\n"
            f"• Şikayət üçün: **{ADMIN_USERNAME}**\n"
            f"• Bütün ödənişlər **TRC20** vasitəsilə həyata keçirilir."
        )
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_kb)

    elif data == "toggle_notify":
        conn = get_db()
        cursor = conn.cursor()
        new_status = 0 if user['notify_status'] == 1 else 1
        cursor.execute("UPDATE users SET notify_status = ? WHERE user_id = ?", (new_status, user_id))
        conn.commit()
        conn.close()
        st_text = "aktivləşdirildi" if new_status == 1 else "deaktiv edildi"
        await query.message.reply_text(f"🔔 Bot bildirişləri uğurla {st_text}!")

def main():
    web_thread = threading.Thread(target=run_web)
    web_thread.daemon = True
    web_thread.start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callbacks))
    print("Bot tam funksional işləyir...")
    app.run_polling()

if __name__ == "__main__":
    main()
