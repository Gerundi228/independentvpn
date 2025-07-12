import os
import qrcode
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters, CallbackContext
)
from config import BOT_TOKEN, DOMAINS, PORT
from vpn_api import add_user_to_vpn
from db import init_db, add_user_record, get_user_record

# Инициализируем базу
init_db()

# Создаём бота
updater = Updater(BOT_TOKEN)
dp = updater.dispatcher

# /start — клавиатура выбора
def cmd_start(update: Update, ctx: CallbackContext):
    kb = ReplyKeyboardMarkup([["🇷🇺 Россия", "🇺🇸 США"]], resize_keyboard=True)
    update.message.reply_text("Привет! Выберите сервер:", reply_markup=kb)

# Обработка выбора региона
def handle_region(update: Update, ctx: CallbackContext):
    text = update.message.text
    user_id = update.message.from_user.id
    region = "RU" if text == "🇷🇺 Россия" else "US"

    # Проверить, есть ли запись в БД
    rec = get_user_record(user_id)
    if rec and rec[1] == region:
        user_uuid = rec[0]
    else:
        # Запрос к Flask-API
        try:
            user_uuid = add_user_to_vpn(region, user_id)
        except Exception as e:
            update.message.reply_text(f"❌ Ошибка API: {e}")
            return
        add_user_record(user_id, user_uuid, region)

    domain = DOMAINS[region]
    # Формируем VLESS-ссылку
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

    # Отправляем ссылку и фото
    update.message.reply_text(f"🔗 Ваша ссылка:\n`{link}`", parse_mode="Markdown")
    update.message.reply_photo(photo=open(path, "rb"))
    os.remove(path)

# /status — текущий UUID и срок
def cmd_status(update: Update, ctx: CallbackContext):
    rec = get_user_record(update.message.from_user.id)
    if rec:
        update.message.reply_text(
            f"Ваш UUID: `{rec[0]}`\n"
            f"Регион: {rec[1]}\n"
            f"Доступ до: {rec[2]}",
            parse_mode="Markdown"
        )
    else:
        update.message.reply_text("У вас пока нет доступа. Нажмите /start")

# Регистрируем хендлеры
dp.add_handler(CommandHandler("start", cmd_start))
dp.add_handler(MessageHandler(Filters.regex("🇷🇺 Россия|🇺🇸 США"), handle_region))
dp.add_handler(CommandHandler("status", cmd_status))

# Запуск
if __name__ == "__main__":
    updater.start_polling()
    updater.idle()
