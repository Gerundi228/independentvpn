from dotenv import load_dotenv
import os

load_dotenv()   # если используете .env для BOT_TOKEN

BOT_TOKEN = os.getenv("BOT_TOKEN", "<ВАШ_ТОКЕН>")

# Endpoints Flask API на VPN-серверах
API_ENDPOINTS = {
    "RU": "http://194.87.74.91:8080/add_user",
    "US": "http://185.106.95.235:8080/add_user"
}

# Доменная часть для линков
DOMAINS = {
    "RU": "vpn.independentvpn.ru",
    "US": "us.independentvpn.ru"
}
