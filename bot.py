import sqlite3
import random
import time
import asyncio
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask
import threading

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
            "💳 TRC20 Adres: `{TRC20_WALLET}`\n"
        ),
        "vip_text": (
            "👑 **VIP Paketləri**\n\n"
            "Ödəniş üçün TRC20 (USDT) adresi:\n`{TRC20_WALLET}`\n\n"
            "Ödəniş etdikdən sonra çeki {ADMIN_USERNAME} ünvanına göndərin."
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

def main_menu_keyboard(lang):
    t = TEXTS.get(lang, TEXTS['az'])
    keyboard = [
        [InlineKeyboardButton(t["spin_btn"], callback_data="spin_menu"), InlineKeyboardButton(t["points_btn"], callback_data="my_points")],
        [InlineKeyboardButton(t["ref_btn"], callback_data="referral"), InlineKeyboardButton(t["task_btn"], callback_data="tasks")],
        [InlineKeyboardButton(t["vip_btn"], callback_data="vip_menu"), InlineKeyboardButton(t["withdraw_btn"], callback_data="withdraw")],
        [InlineKeyboardButton(t["info_btn"], callback_data="info")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not get_user(user_id):
        create_user(user_id)
    await update.message.reply_text("👋 Salam! Əsas Menyu:", reply_markup=main_menu_keyboard('az'))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data
    user = get_user(user_id)

    if data == "main_menu":
        await query.edit_message_text("Əsas Menyu:", reply_markup=main_menu_keyboard('az'))
    elif data == "spin_menu":
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🌀 Çarxı Fırlat", callback_data="do_spin"), InlineKeyboardButton("🔙 Geri", callback_data="main_menu")]])
        await query.edit_message_text("🎰 Şans Çarxı", reply_markup=kb)
    elif data == "do_spin":
        res_val = random.choice([15, 25, 35, 45, 55])
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (res_val, user_id))
        conn.commit()
        conn.close()
        await query.message.reply_text(f"🎉 {res_val} Xal qazandınız!")
    elif data == "my_points":
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Geri", callback_data="main_menu")]])
        await query.edit_message_text(f"💰 Xalınız: {user['points']}", reply_markup=kb)
    elif data == "referral":
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Geri", callback_data="main_menu")]])
        await query.edit_message_text("👥 Referal linkiniz aktivdir.", reply_markup=kb)
    elif data == "tasks":
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Geri", callback_data="main_menu")]])
        await query.edit_message_text("📢 Tapşırıqlar siyahısı", reply_markup=kb)
    elif data == "vip_menu":
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Geri", callback_data="main_menu")]])
        await query.edit_message_text("👑 VIP Paketlər", reply_markup=kb)
    elif data == "withdraw":
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Geri", callback_data="main_menu")]])
        await query.edit_message_text("💸 Çıxarış bölməsi", reply_markup=kb)
    elif data == "info":
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Geri", callback_data="main_menu")]])
        await query.edit_message_text("ℹ️ Məlumat bölməsi", reply_markup=kb)

def main():
    web_thread = threading.Thread(target=run_web)
    web_thread.daemon = True
    web_thread.start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print("Bot işə düşdü...")
    app.run_polling()

if __name__ == "__main__":
    main()
