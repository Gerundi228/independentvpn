import uuid
import os
import qrcode
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InputFile

from config import BOT_TOKEN, API_ENDPOINTS, DOMAINS
from vpn_api import add_user_to_vpn
from db import init_db, add_user_record, get_user_record

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

init_db()

@dp.message_handler(commands=["start"])
async def cmd_start(msg: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🇷🇺 Россия", "🇺🇸 США")
    await msg.reply("Выберите сервер:", reply_markup=kb)

@dp.message_handler(lambda msg: msg.text in ["🇷🇺 Россия", "🇺🇸 США"])
async def region_selected(msg: types.Message):
    user_id = msg.from_user.id
    region = "RU" if msg.text.startswith("🇷🇺") else "US"

    # Проверим, не создавали ли мы ранее
    existing = get_user_record(user_id)
    if existing and existing[1] == region:
        uuid_str = existing[0]
    else:
        # создаём в VPN через API
        uuid_str = add_user_to_vpn(region, user_id)
        add_user_record(user_id, uuid_str, region)

    domain = DOMAINS[region]
    link = (f"vless://{uuid_str}@{domain}:443"
            f"?encryption=none&security=tls&type=grpc&serviceName=vpn&sni={domain}"
            f"#{region}-VPN")

    # QR-код
    img = qrcode.make(link)
    path = f"/tmp/{user_id}_{region}.png"
    img.save(path)

    await msg.reply(f"🔗 Ваша ссылка:\n`{link}`", parse_mode="Markdown")
    await bot.send_photo(msg.chat.id, InputFile(path))
    os.remove(path)

@dp.message_handler(commands=["status"])
async def cmd_status(msg: types.Message):
    rec = get_user_record(msg.from_user.id)
    if rec:
        await msg.reply(f"Ваш UUID: `{rec[0]}`\nРегион: {rec[1]}\nДоступ до: {rec[2]}", parse_mode="Markdown")
    else:
        await msg.reply("У вас пока нет выданного доступа. /start")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
