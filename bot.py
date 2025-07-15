import uuid as _uuid
import logging, os, requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from config import BOT_TOKEN, API_URL
from db import init_db, get_user, add_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализируем БД (создание таблиц/регионов)
init_db()

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    user = get_user(tg_id)
    if not user:
        # генерируем новый UUID v4
        new_uuid = str(_uuid.uuid4())
        add_user(tg_id, new_uuid)
    else:
        new_uuid = user["uuid"]

    # Кнопка «Получить подписку»
    btn = InlineKeyboardButton("🔑 Получить ключ доступа", callback_data=f"sub:{new_uuid}")
    markup = InlineKeyboardMarkup([[btn]])
    await update.message.reply_text("Ваш единый ключ доступа к VPN:", reply_markup=markup)

async def on_button(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data  # "sub:UUID"
    if data.startswith("sub:"):
        uuid = data.split(":",1)[1]
        link = f"{API_URL}/{uuid}"
        text = (
            "✨ Ваша подписка готова!\n\n"
            f"`{link}`\n\n"
            "Скопируйте эту ссылку в V2RayN/Clash/Shadowrocket\n"
            "— и в клиенте вы сможете выбрать нужный сервер (RU/US/KZ)."
        )
        await query.edit_message_text(text, parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(on_button))
    app.run_polling()

if __name__ == "__main__":
    main()
