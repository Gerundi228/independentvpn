import os
from dotenv import load_dotenv

load_dotenv()   # подтягиваем BOT_TOKEN из .env

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Endpoints Flask API на VPN-серверах
API_ENDPOINTS = {
    "RU": "http://194.87.74.91:8080/add_user",
    "US": "http://185.106.95.235:8080/add_user"
}

# Домены для формирования VLESS-ссылки
DOMAINS = {
    "RU": "vpn.independentvpn.ru",
    "US": "us.independentvpn.ru"
}

# Порт, который вы используете (443 или 8443 и т.п.)
PORT = 443
