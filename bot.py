import os
import logging
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

# ─── Настройка логирования ──────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# ─── ErrorHandler для всех необработанных исключений ────────────────────────────
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    # печатаем полный traceback (уже есть)
    logger.error("Exception while handling an update:", exc_info=context.error)
    
    # теперь явно логируем текст ошибки
    err = context.error
    logger.error(">>> CONTEXT.ERROR: %s", err)
    
    if hasattr(update, "message") and update.message:
        try:
            await update.message.reply_text(
                "❌ Упс! Внутренняя ошибка, администратор уже смотрит логи."
            )
        except Exception:
            logger.exception("Failed to send error message to user")

# ─── Инициализируем БД ──────────────────────────────────────────────────────────
init_db()

# ─── Хэндлеры ───────────────────────────────────────────────────────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug(f"/start from {update.effective_user.id}")
    kb = ReplyKeyboardMarkup(
        [["🇷🇺 Россия", "🇺🇸 США"]],
        resize_keyboard=True
    )
    await update.message.reply_text("Привет! Выберите сервер:", reply_markup=kb)

async def handle_region(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    region  = "RU" if update.message.text.startswith("🇷🇺") else "US"

    # 1) Запросим у API всегда новый UUID
    try:
        user_uuid = add_user_to_vpn(region, user_id)
        add_user_record(user_id, user_uuid, region)
        logger.info(f"Generated new UUID {user_uuid} for user {user_id} ({region})")
    except Exception as e:
        logger.exception("API error in handle_region")
        return await update.message.reply_text(f"❌ Ошибка API: {e}")

    # 2) Формируем ссылку и QR
    domain = DOMAINS[region]
    link = (
        f"vless://{user_uuid}@{domain}:443"
        f"?encryption=none&security=tls"
        f"&type=ws"
        f"&host={domain}"
        f"&path=%2Fvpn"
        f"#{region}-VPN"
    )

    img = qrcode.make(link)
    qr_path = f"/tmp/{user_id}_{region}.png"
    img.save(qr_path)

    # 3) Отправляем
    await update.message.reply_text(f"🔗 Ваша ссылка:\n`{link}`", parse_mode="Markdown")
    with open(qr_path, "rb") as photo:
        await update.message.reply_photo(photo=photo)
    os.remove(qr_path)


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    rec = get_user_record(user_id)
    logger.debug(f"/status for {user_id}: {rec}")
    if rec:
        await update.message.reply_text(
            f"Ваш UUID: `{rec[0]}`\n"
            f"Регион: {rec[1]}\n"
            f"Доступ до: {rec[2]}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("У вас пока нет доступа. Нажмите /start")

# ─── Запуск бота ────────────────────────────────────────────────────────────────
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Удаляем web-hook (если когда-то включали), чтобы не было конфликта
    app.bot.delete_webhook(drop_pending_updates=True)

    # Регистрируем ErrorHandler
    app.add_error_handler(error_handler)

    # Регистрируем хэндлеры
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(MessageHandler(filters.Regex("🇷🇺 Россия|🇺🇸 США"), handle_region))
    app.add_handler(CommandHandler("status", cmd_status))

    logger.info("Bot is starting with drop_pending_updates=True...")
    # Сбрасываем все pending updates и стартуем
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
