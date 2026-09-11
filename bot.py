import sqlite3
import random
import time
import asyncio
import os
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask
import threading

# Render üçün mini veb-server (Port xətası verməməsi üçün)
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

BOT_TOKEN = "8982385389:AAESNUF2bHc8kOqKPBGph7_369O4UPbZDyQ"
BOT_USERNAME = "USDT_Qazan_bot"
ADMIN_USERNAME = "@kullanc234"
TRC20_WALLET = "TKf5cMmCqjR76gN62Vim9BaP3G5XL4a7kp"
CHANNELS = ["@qizilanaliz", "@mercvekuponlarr", "@craftbetting"]

TEXTS = {
    "az": {
        "welcome": "👋 Salam! Zəhmət olmasa dil seçin:",
        "main_menu": "Əsas Menyu:",
        "spin_btn": "🎰 Çarx", "points_btn": "💰 Balans", "ref_btn": "👥 Referal",
        "task_btn": "📢 Tapşırıqlar", "vip_btn": "👑 VIP", "withdraw_btn": "💸 Çıxarış",
        "info_btn": "ℹ️ Məlumat", "lang_btn": "🌐 Dil Dəyiş", "back": "🔙 Geri",
        "info_text": (
            "ℹ️ **Sistem Məlumatı və Qaydalar**\n\n"
            "🎰 **Çarx Mükafatları:**\n"
            "• Xallar: 15, 25, 35, 45, 55 xal\n"
            "• Hədiyyələr: 2 Pulsuz fırlatma / 40 xal\n"
            "• Boş Çarx (xal yoxdur)\n\n"
            "👑 **VIP Üzvlük Qiymətləri:**\n"
            "• 7 Günlük VIP: 3 $\n"
            "• 15 Günlük VIP: 5 $\n"
            "💳 TRC20 Adres: `{TRC20_WALLET}`\n\n"
            "💸 **Çıxarış Qaydaları:**\n"
            "• **Adi üzvlər üçün 200 000 xal - 25$ çıxarış**\n"
            "• **VIP üzvlər üçün 150 000 xal - 20$ çıxarış**\n"
        ),
        "vip_text": (
            "👑 **VIP Paketləri**\n\n"
            "1️⃣ **7 Günlük VIP:** 3 $\n"
            "2️⃣ **15 Günlük VIP:** 5 $\n\n"
            "Ödəniş üçün TRC20 (USDT) adresi:\n`{TRC20_WALLET}`\n\n"
            "Ödəniş etdikdən sonra çeki {ADMIN_USERNAME} ünvanına göndərin."
        )
    },
    "ru": {
        "welcome": "👋 Здравствуйте! Пожалуйста, выберите язык:",
        "main_menu": "Главное меню:",
        "spin_btn": "🎰 Колесо", "points_btn": "💰 Баланс", "ref_btn": "👥 Рефералы",
        "task_btn": "📢 Задания", "vip_btn": "👑 VIP", "withdraw_btn": "💸 Вывод",
        "info_btn": "ℹ️ Информация", "lang_btn": "🌐 Сменить язык", "back": "🔙 Назад",
        "info_text": "ℹ️ **Информация и Правила**\n\n🎰 **Колесо:** Очки и призы.\n👑 **VIP:** 7 дней - 3$, 15 дней - 5$.",
        "vip_text": "👑 **VIP Пакеты**\n\nTRC20 USDT адрес:\n`{TRC20_WALLET}`\n\nОтправьте чек {ADMIN_USERNAME}."
    },
    "en": {
        "welcome": "👋 Hello! Please select your language:",
        "main_menu": "Main Menu:",
        "spin_btn": "🎰 Wheel", "points_btn": "💰 Balance", "ref_btn": "👥 Referrals",
        "task_btn": "📢 Tasks", "vip_btn": "👑 VIP", "withdraw_btn": "💸 Withdraw",
        "info_btn": "ℹ️ Info", "lang_btn": "🌐 Change Language", "back": "🔙 Back",
        "info_text": "ℹ️ **System Information**\n\n🎰 **Wheel Rewards**\n👑 **VIP Prices:** 7-Day ($3), 15-Day ($5)",
        "vip_text": "👑 **VIP Membership**\n\nTRC20 USDT Wallet:\n`{TRC20_WALLET}`\n\nSend receipt to {ADMIN_USERNAME}."
    },
    "tr": {
        "welcome": "👋 Merhaba! Lütfen bir dil seçin:",
        "main_menu": "Ana Menü:",
        "spin_btn": "🎰 Çark", "points_btn": "💰 Bakiye", "ref_btn": "👥 Referans",
        "task_btn": "📢 Görevler", "vip_btn": "👑 VIP", "withdraw_btn": "💸 Çekim",
        "info_btn": "ℹ️ Bilgi", "lang_btn": "🌐 Dil Değiştir", "back": "🔙 Geri",
        "info_text": "ℹ️ **Bilgi ve Kurallar**\n\n🎰 **Çark Ödülleri**\n👑 **VIP:** 7 Gün (3$), 15 Gün (5$)",
        "vip_text": "👑 **VIP Paketleri**\n\nTRC20 USDT adresi:\n`{TRC20_WALLET}`\n\nDekontu {ADMIN_USERNAME} hesabına gönderin."
    }
}

def get_db():
    conn = sqlite3.connect("wheel_bot.db")
    conn.row_factory = sqlite3.Row
    return conn

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
        notify_enabled INTEGER DEFAULT 1,
        lang TEXT DEFAULT 'az'
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
    cursor.execute("""
    INSERT OR IGNORE INTO users (user_id, points, bonus_spins, referrer_id, lang, last_spin_reset, daily_spin_count, notify_enabled)
    VALUES (?, 0, 0, ?, 'az', 0, 0, 1)
    """, (user_id, referrer_id))
    conn.commit()
    conn.close()

def get_user_lang(user):
    if user and isinstance(user, sqlite3.Row):
        lang = dict(user).get('lang')
        if lang in TEXTS:
            return lang
    return 'az'

def is_vip(user_id):
    user = get_user(user_id)
    if not user or not user['vip_until']:
        return False
    try:
        return datetime.now() < datetime.fromisoformat(user['vip_until'])
    except Exception:
        return False

def get_ref_counts(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, vip_until FROM users WHERE referrer_id = ?", (user_id,))
    refs = cursor.fetchall()
    conn.close()

    reg_count = 0
    vip_count = 0
    now = datetime.now()
    for r in refs:
        if r['vip_until']:
            try:
                if now < datetime.fromisoformat(r['vip_until']):
                    vip_count += 1
                else:
                    reg_count += 1
            except:
                reg_count += 1
        else:
            reg_count += 1
    return reg_count, vip_count

def main_menu_keyboard(lang):
    t = TEXTS.get(lang, TEXTS['az'])
    keyboard = [
        [InlineKeyboardButton(t["spin_btn"], callback_data="spin_menu"), InlineKeyboardButton(t["points_btn"], callback_data="my_points")],
        [InlineKeyboardButton(t["ref_btn"], callback_data="referral"), InlineKeyboardButton(t["task_btn"], callback_data="tasks")],
        [InlineKeyboardButton(t["vip_btn"], callback_data="vip_menu"), InlineKeyboardButton(t["withdraw_btn"], callback_data="withdraw")],
        [InlineKeyboardButton(t["info_btn"], callback_data="info"), InlineKeyboardButton(t["lang_btn"], callback_data="change_lang")]
    ]
    return InlineKeyboardMarkup(keyboard)

def language_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇦🇿 Azərbaycan", callback_data="set_lang_az"), InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en"), InlineKeyboardButton("🇹🇷 Türkçe", callback_data="set_lang_tr")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    referrer_id = int(args[0]) if args and args[0].isdigit() and int(args[0]) != user_id else None

    if not get_user(user_id):
        create_user(user_id, referrer_id)
        if referrer_id:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET points = points + 25 WHERE user_id = ?", (referrer_id,))
            conn.commit()
            conn.close()

    user = get_user(user_id)
    lang = get_user_lang(user)
    t = TEXTS.get(lang, TEXTS['az'])
    await update.message.reply_text(t["welcome"], reply_markup=language_keyboard())

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    user = get_user(user_id)
    if not user:
        create_user(user_id)
        user = get_user(user_id)

    lang = get_user_lang(user)
    t = TEXTS.get(lang, TEXTS['az'])

    if data.startswith("set_lang_"):
        new_lang = data.split("_")[2]
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET lang = ? WHERE user_id = ?", (new_lang, user_id))
        conn.commit()
        conn.close()
        new_t = TEXTS.get(new_lang, TEXTS['az'])
        await query.edit_message_text(new_t["main_menu"], reply_markup=main_menu_keyboard(new_lang))

    elif data == "change_lang":
        await query.edit_message_text(t["welcome"], reply_markup=language_keyboard())

    elif data == "main_menu":
        await query.edit_message_text(t["main_menu"], reply_markup=main_menu_keyboard(lang))

    elif data == "info":
        info = t["info_text"].format(TRC20_WALLET=TRC20_WALLET)
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(t["back"], callback_data="main_menu")]])
        await query.edit_message_text(info, parse_mode="Markdown", reply_markup=kb)

    elif data == "vip_menu":
        vip = t["vip_text"].format(TRC20_WALLET=TRC20_WALLET, ADMIN_USERNAME=ADMIN_USERNAME)
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(t["back"], callback_data="main_menu")]])
        await query.edit_message_text(vip, parse_mode="Markdown", reply_markup=kb)

    elif data == "my_points":
        reg_r, vip_r = get_ref_counts(user_id)
        vip_st = is_vip(user_id)
        text = (
            f"💰 **{t['points_btn']}**\n\n"
            f"🎯 Xal: **{user['points']}**\n"
            f"🎁 Pulsuz Fırlatmalar: **{user['bonus_spins']}**\n"
            f"👥 Referallar: **{reg_r} Adi / {vip_r} VIP**\n"
            f"👑 VIP Status: **{'Aktiv' if vip_st else 'Deaktiv'}**"
        )
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(t["back"], callback_data="main_menu")]])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "spin_menu":
        vip_st = is_vip(user_id)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🌀 Çarxı Fırlat", callback_data="do_spin")],
            [InlineKeyboardButton(t["back"], callback_data="main_menu")]
        ])
        limit_txt = "12 saatda 50 ədəd" if vip_st else "24 saatda 50 ədəd"
        await query.edit_message_text(
            f"🎰 **Şans Çarxı**\n\n"
            f"Sizin limitiniz: **{limit_txt}**\n"
            f"Qalan fırlatma sayınız: **{50 - user['daily_spin_count']}**",
            reply_markup=kb
        )

    elif data == "do_spin":
        vip_st = is_vip(user_id)
        cooldown = 12 * 3600 if vip_st else 24 * 3600
        now = int(time.time())

        last_reset = user['last_spin_reset'] or 0
        spin_count = user['daily_spin_count'] or 0

        if now - last_reset >= cooldown:
            spin_count = 0
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET daily_spin_count = 0, last_spin_reset = ? WHERE user_id = ?", (now, user_id))
            conn.commit()
            conn.close()

        if spin_count >= 50:
            remaining = cooldown - (now - last_reset)
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            kb = InlineKeyboardMarkup([[InlineKeyboardButton(t["back"], callback_data="spin_menu")]])
            await query.message.reply_text(f"🚫 Limit bitib! Gözləyin: {hours} saat {minutes} dəqiqə", reply_markup=kb)
            return

        await query.message.reply_dice(emoji="🎰")

        res_val = random.choice([15, 25, 35, 45, 55])
        await asyncio.sleep(2.5)

        conn = get_db()
        cursor = conn.cursor()
        new_spin_count = spin_count + 1
        cursor.execute("UPDATE users SET points = points + ?, daily_spin_count = ? WHERE user_id = ?", (res_val, new_spin_count, user_id))
        conn.commit()
        conn.close()

        updated = get_user(user_id)
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🌀 Yenidən", callback_data="do_spin"), InlineKeyboardButton(t["back"], callback_data="spin_menu")]])
        await query.message.reply_text(f"🎉 **{res_val} Xal** qazandınız!\n💰 Balans: {updated['points']} Xal", parse_mode="Markdown", reply_markup=kb)

    elif data == "referral":
        ref_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
        reg_r, vip_r = get_ref_counts(user_id)
        text = f"👥 **Referal Sistemi**\n\nLinkiniz:\n`{ref_link}`\n\nReferallarınız: **{reg_r} Adi / {vip_r} VIP**"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(t["back"], callback_data="main_menu")]])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "withdraw":
        vip_st = is_vip(user_id)
        text = f"💸 **Çıxarış**\n\nStatus: **{'👑 VIP' if vip_st else 'Adi'}**\nMüraciət üçün: {ADMIN_USERNAME}"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(t["back"], callback_data="main_menu")]])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "tasks":
        kb = [[InlineKeyboardButton(f"📢 {ch}", url=f"https://t.me/{ch.replace('@','')}")] for ch in CHANNELS]
        kb.append([InlineKeyboardButton(t["back"], callback_data="main_menu")])
        await query.edit_message_text("📢 **Tapşırıqlar**", reply_markup=InlineKeyboardMarkup(kb))

def main():
    # Veb serveri arxa planda işə salırıq
    web_thread = threading.Thread(target=run_web)
    web_thread.daemon = True
    web_thread.start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print("Bot aktivdir...")
    app.run_polling()

if __name__ == "__main__":
    main()
