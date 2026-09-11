import sqlite3
import random
import time
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "8982385389:AAESNUF2bHc8kOqKPBGph7_369O4UPbZDyQ"
BOT_USERNAME = "USDT_Qazan_bot"
ADMIN_USERNAME = "@kullanc234"
TRC20_WALLET = "TKf5cMmCqjR76gN62Vim9BaP3G5XL4a7kp"
CHANNELS = ["@qizilanaliz", "@mercvekuponlarr", "@craftbetting"]

# Admin ID qeyd edildi
ADMIN_IDS = [5878410437]

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
            "• **Adi üzvlər üçün 200 000 xal - 25$ çıxarış** (10 adi referal yoxlanıldıqdan sonra)\n"
            "• **Adi üzvlər üçün 200 000 xal - 30$ çıxarış** (10 adi referal və 1 VIP referal yoxlanıldıqdan sonra)\n"
            "• **VIP üzvlər üçün 150 000 xal - 20$ çıxarış** (5 adi referal və 2 VIP referal yoxlanıldıqdan sonra)\n"
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
        "info_text": (
            "ℹ️ **Информация и Правила**\n\n"
            "🎰 **Призы в колесе:**\n"
            "• Очки: 15, 25, 35, 45, 55 очков\n"
            "• Призы: 2 Бесплатных вращения / 40 очков\n"
            "• Пустой сектор\n\n"
            "👑 **Цены VIP:**\n"
            "• VIP на 7 дней: 3 $\n"
            "• VIP на 15 дней: 5 $\n\n"
            "💸 **Условия вывода:**\n"
            "• **Для обычных (25$):** 200 000 очков (после проверки 10 рефералов)\n"
            "• **Для обычных (30$):** 200 000 очков (после проверки 10 реф. и 1 VIP)\n"
            "• **Для VIP (20$):** 150 000 очков (после проверки 5 реф. и 2 VIP)\n"
        ),
        "vip_text": (
            "👑 **VIP Пакеты**\n\n"
            "1️⃣ **VIP на 7 дней:** 3 $\n"
            "2️⃣ **VIP на 15 дней:** 5 $\n\n"
            "TRC20 USDT адрес:\n`{TRC20_WALLET}`\n\n"
            "После оплаты отправьте чек {ADMIN_USERNAME}."
        )
    },
    "en": {
        "welcome": "👋 Hello! Please select your language:",
        "main_menu": "Main Menu:",
        "spin_btn": "🎰 Wheel", "points_btn": "💰 Balance", "ref_btn": "👥 Referrals",
        "task_btn": "📢 Tasks", "vip_btn": "👑 VIP", "withdraw_btn": "💸 Withdraw",
        "info_btn": "ℹ️ Info", "lang_btn": "🌐 Change Language", "back": "🔙 Back",
        "info_text": (
            "ℹ️ **System Information & Rules**\n\n"
            "🎰 **Wheel Rewards:**\n"
            "• Points: 15, 25, 35, 45, 55 pts\n"
            "• Rewards: 2 Free Spins / 40 points\n"
            "• Empty Spin\n\n"
            "👑 **VIP Prices:**\n"
            "• 7-Day VIP: $3\n"
            "• 15-Day VIP: $5\n\n"
            "💸 **Withdrawal Rules:**\n"
            "• **Regular ($25):** 200,000 pts (after 10 refs check)\n"
            "• **Regular ($30):** 200,000 pts (after 10 refs & 1 VIP check)\n"
            "• **VIP ($20):** 150,000 pts (after 5 refs & 2 VIP check)\n"
        ),
        "vip_text": (
            "👑 **VIP Membership**\n\n"
            "1️⃣ **7-Day VIP:** $3\n"
            "2️⃣ **15-Day VIP:** $5\n\n"
            "TRC20 USDT Wallet:\n`{TRC20_WALLET}`\n\n"
            "Send receipt to {ADMIN_USERNAME} after payment."
        )
    },
    "tr": {
        "welcome": "👋 Merhaba! Lütfen bir dil seçin:",
        "main_menu": "Ana Menü:",
        "spin_btn": "🎰 Çark", "points_btn": "💰 Bakiye", "ref_btn": "👥 Referans",
        "task_btn": "📢 Görevler", "vip_btn": "👑 VIP", "withdraw_btn": "💸 Çekim",
        "info_btn": "ℹ️ Bilgi", "lang_btn": "🌐 Dil Değiştir", "back": "🔙 Geri",
        "info_text": (
            "ℹ️ **Bilgi ve Kurallar**\n\n"
            "🎰 **Çark Ödülleri:**\n"
            "• Puanlar: 15, 25, 35, 45, 55 puan\n"
            "• Hediyeler: 2 Ücretsiz Çevirme / 40 Puan\n"
            "• Boş Çark\n\n"
            "👑 **VIP Fiyatları:**\n"
            "• 7 Günlük VIP: 3 $\n"
            "• 15 Günlük VIP: 5 $\n\n"
            "💸 **Çekim Şartları:**\n"
            "• **Normal üyeler 25$:** 200.000 puan (10 normal ref kontrolü sonrası)\n"
            "• **Normal üyeler 30$:** 200.000 puan (10 normal ve 1 VIP ref kontrolü sonrası)\n"
            "• **VIP üyeler 20$:** 150.000 puan (5 normal ve 2 VIP ref kontrolü sonrası)\n"
        ),
        "vip_text": (
            "👑 **VIP Paketleri**\n\n"
            "1️⃣ **7 Günlük VIP:** 3 $\n"
            "2️⃣ **15 Günlük VIP:** 5 $\n\n"
            "TRC20 USDT adresi:\n`{TRC20_WALLET}`\n\n"
            "Ödeme yaptıktan sonra dekontu {ADMIN_USERNAME} hesabına gönderin."
        )
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
        user_dict = dict(user)
        lang = user_dict.get('lang')
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

async def notify_user_job(context: ContextTypes.DEFAULT_TYPE):
    user_id = context.job.user_id
    user = get_user(user_id)
    if user and user['notify_enabled']:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="🔔 **Xəbərdarlıq!** Çarx fırlatma vaxtınız çatdı! Yenidən 50 fırlatma haqqınız aktivdir! 🎰"
            )
        except Exception:
            pass

# --- ADMIN ƏMRLƏRİ ---
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    conn.close()
    await update.message.reply_text(f"📊 **Bot Statistikası:**\n\n👥 Toplam istifadəçi sayı: **{total_users}**")

async def user_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if not context.args:
        await update.message.reply_text("İstifadə üçün: `/user <user_id>`")
        return
    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("İstifadəçi ID rəqəm olmalıdır.")
        return

    user = get_user(target_id)
    if not user:
        await update.message.reply_text("Bu ID ilə istifadəçi tapılmadı.")
        return

    reg_r, vip_r = get_ref_counts(target_id)
    vip_st = is_vip(target_id)
    await update.message.reply_text(
        f"👤 **İstifadəçi Məlumatı:**\n\n"
        f"🆔 ID: `{target_id}`\n"
        f"🎯 Xal: **{user['points']}**\n"
        f"🎁 Bonus Fırlatma: **{user['bonus_spins']}**\n"
        f"👥 Referallar: **{reg_r} Adi / {vip_r} VIP**\n"
        f"👑 VIP Status: **{'Aktiv' if vip_st else 'Deaktiv'}**",
        parse_mode="Markdown"
    )

async def make_vip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if len(context.args) < 2:
        await update.message.reply_text("İstifadə üçün: `/vip <user_id> <gün>` (Məsələn: `/vip 123456789 7`)")
        return
    try:
        target_id = int(context.args[0])
        days = int(context.args[1])
    except ValueError:
        await update.message.reply_text("ID və gün rəqəm olmalıdır.")
        return

    vip_until = (datetime.now() + timedelta(days=days)).isoformat()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET vip_until = ? WHERE user_id = ?", (vip_until, target_id))
    conn.commit()
    conn.close()

    await update.message.reply_text(f"✅ Uğurlu! `{target_id}` nömrəli istifadəçi **{days} günlük** VIP edildi.", parse_mode="Markdown")
    try:
        await context.bot.send_message(chat_id=target_id, text=f"👑 Təbriklər! Hesabınız admin tərəfindən **{days} günlük** VIP statusuna yüksəldildi!")
    except Exception:
        pass

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
        notify_st = "✅ Aktiv" if user['notify_enabled'] else "❌ Deaktiv"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🌀 Çarxı Fırlat", callback_data="do_spin")],
            [InlineKeyboardButton(f"🔔 Bildiriş: {notify_st}", callback_data="toggle_notify")],
            [InlineKeyboardButton(t["back"], callback_data="main_menu")]
        ])

        limit_txt = "12 saatda 50 ədəd" if vip_st else "24 saatda 50 ədəd"
        await query.edit_message_text(
            f"🎰 **Şans Çarxı**\n\n"
            f"Sizin limitiniz: **{limit_txt}**\n"
            f"Qalan fırlatma sayınız: **{50 - user['daily_spin_count']}**\n\n"
            f"Vaxtınız bitdikdə bildiriş almaq üçün aşağıdakı düymədən tənzimləyə bilərsiniz.",
            reply_markup=kb
        )

    elif data == "toggle_notify":
        new_val = 0 if user['notify_enabled'] else 1
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET notify_enabled = ? WHERE user_id = ?", (new_val, user_id))
        conn.commit()
        conn.close()

        user = get_user(user_id)
        notify_st = "✅ Aktiv" if user['notify_enabled'] else "❌ Deaktiv"
        vip_st = is_vip(user_id)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🌀 Çarxı Fırlat", callback_data="do_spin")],
            [InlineKeyboardButton(f"🔔 Bildiriş: {notify_st}", callback_data="toggle_notify")],
            [InlineKeyboardButton(t["back"], callback_data="main_menu")]
        ])
        limit_txt = "12 saatda 50 ədəd" if vip_st else "24 saatda 50 ədəd"
        await query.edit_message_text(
            f"🎰 **Şans Çarxı**\n\n"
            f"Sizin limitiniz: **{limit_txt}**\n"
            f"Qalan fırlatma sayınız: **{50 - user['daily_spin_count']}**\n\n"
            f"Vaxtınız bitdikdə bildiriş almaq üçün aşağıdakı düymədən tənzimləyə bilərsiniz.",
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
            last_reset = now
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
            await query.message.reply_text(
                f"🚫 **Günlük limitiniz (50/50) bitmişdir!**\n\n"
                f"Yenidən fırlatmaq üçün gözləməli olduğunuz vaxt:\n"
                f"⏳ **{hours} saat {minutes} dəqiqə**",
                reply_markup=kb
            )
            return

        await query.message.reply_dice(emoji="🎰")

        if vip_st:
            outcomes = [
                ("points", 25), ("points", 25),
                ("points", 35), ("points", 35),
                ("points", 55), ("points", 55),
                ("points", 100), ("points", 100),
                ("gift", 0),
                ("empty", 0)
            ]
        else:
            outcomes = [
                ("points", 15), ("points", 15),
                ("points", 25), ("points", 25),
                ("points", 35), ("points", 35),
                ("points", 45),
                ("points", 55),
                ("gift", 0),
                ("empty", 0), ("empty", 0), ("empty", 0)
            ]

        res_type, res_val = random.choice(outcomes)

        if res_type == "gift":
            sub_outcome = random.choice([("spins", 2), ("points", 40)])
            res_type, res_val = sub_outcome

        await asyncio.sleep(2.5)

        conn = get_db()
        cursor = conn.cursor()
        new_spin_count = spin_count + 1

        if res_type == "points":
            cursor.execute("UPDATE users SET points = points + ?, daily_spin_count = ? WHERE user_id = ?", (res_val, new_spin_count, user_id))
            msg_out = f"🎉 **Təbriklər!** Siz **{res_val} Xal** qazandınız!"

            if user['referrer_id'] and res_val > 0:
                ref_bonus = max(1, int(res_val * 0.05))
                cursor.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (ref_bonus, user['referrer_id']))

        elif res_type == "spins":
            cursor.execute("UPDATE users SET bonus_spins = bonus_spins + ?, daily_spin_count = ? WHERE user_id = ?", (res_val, new_spin_count, user_id))
            msg_out = f"🎁 **HƏDİYYƏ!** Siz **{res_val} Pulsuz Fırlatma** qazandınız!"
        else:
            cursor.execute("UPDATE users SET daily_spin_count = ? WHERE user_id = ?", (new_spin_count, user_id))
            msg_out = "❌ **Təəssüf!** Çarx boş çıxdı."

        conn.commit()
        conn.close()

        if new_spin_count == 50 and user['notify_enabled']:
            if context.job_queue:
                context.job_queue.run_once(notify_user_job, cooldown, user_id=user_id, name=str(user_id))

        updated = get_user(user_id)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🌀 Yenidən Fırlat", callback_data="do_spin")],
            [InlineKeyboardButton(t["back"], callback_data="spin_menu")]
        ])
        await query.message.reply_text(
            f"{msg_out}\n\n"
            f"💰 Balans: **{updated['points']} Xal**\n"
            f"🔢 Günlük fırlatma: **{new_spin_count}/50**",
            parse_mode="Markdown",
            reply_markup=kb
        )

    elif data == "referral":
        ref_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
        reg_r, vip_r = get_ref_counts(user_id)
        text = (
            f"👥 **Referal Sistemi**\n\n"
            f"Linkiniz:\n`{ref_link}`\n\n"
            f"• Sizin Referallarınız: **{reg_r} Adi / {vip_r} VIP**"
        )
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(t["back"], callback_data="main_menu")]])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "withdraw":
        reg_r, vip_r = get_ref_counts(user_id)
        vip_st = is_vip(user_id)

        text = (
            f"💸 **Çıxarış Bölməsi**\n\n"
            f"Statusunuz: **{'👑 VIP' if vip_st else 'Adi Üzv'}**\n"
            f"Sizin referallarınız: **{reg_r} Adi / {vip_r} VIP**\n\n"
            f"Çıxarış üçün müraciəti {ADMIN_USERNAME} ünvanına göndərin."
        )
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(t["back"], callback_data="main_menu")]])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    elif data == "tasks":
        kb = []
        for ch in CHANNELS:
            kb.append([InlineKeyboardButton(f"📢 {ch}", url=f"https://t.me/{ch.replace('@','')}")])
        kb.append([InlineKeyboardButton(t["back"], callback_data="main_menu")])
        await query.edit_message_text("📢 **Tapşırıqlar**\n\nKanallara abunə olun:", reply_markup=InlineKeyboardMarkup(kb))

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("user", user_info_command))
    app.add_handler(CommandHandler("vip", make_vip_command))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print("Bot aktivdir...")
    app.run_polling()

if __name__ == "__main__":
    main()
