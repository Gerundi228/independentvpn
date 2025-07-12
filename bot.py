# bot.py

import os
import qrcode
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from config import BOT_TOKEN, API_ENDPOINTS, DOMAINS, PORT
from vpn_api import add_user_to_vpn
from db import init_db, add_user_record, get_user_record

# Инициализируем базу при старте
init_db()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = ReplyKeyboardMarkup(
        [["🇷🇺 Россия", "🇺🇸 США"]],
        resize_keyboard=True
    )
    await update.message.reply_text("Привет! Выберите сервер:", reply_markup=kb)

async def handle_region(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id
    region = "RU" if text == "🇷🇺 Россия" else "US"

    # Проверяем, не выдавали ли уже доступ для этого региона
    rec = get_user_record(user_id)
    if rec and rec[1] == region:
        user_uuid = rec[0]
    else:
        try:
            user_uuid = add_user_to_vpn(region, user_id)
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка API: {e}")
            return
        add_user_record(user_id, user_uuid, region)

    domain = DOMAINS[region]
    link = (
        f"vless://{user_uuid}@{domain}:{PORT}"
        f"?encryption=none&security=tls"
        f"&type=grpc&serviceName=vpn&sni={domain}"
        f"#{region}-VPN"
    )

    # Генерация QR
    img = qrcode.make(link)
    path = f"/tmp/{user_id}_{region}.png"
    img.save(path)

    # Отправляем ссылку и QR
    await update.message.reply_text(f"🔗 Ваша ссылка:\n`{link}`", parse_mode="Markdown")
    await update.message.reply_photo(photo=open(path, "rb"))
    os.remove(path)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rec = get_user_record(update.message.from_user.id)
    if rec:
        await update.message.reply_text(
            f"Ваш UUID: `{rec[0]}`\n"
            f"Регион: {rec[1]}\n"
            f"Доступ до: {rec[2]}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("У вас пока нет доступа. Нажмите /start")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("🇷🇺 Россия|🇺🇸 США"), handle_region))
    app.add_handler(CommandHandler("status", status))

    app.run_polling()

if __name__ == "__main__":
    main()
