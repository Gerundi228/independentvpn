import os
from dotenv import load_dotenv

BOT_TOKEN = "7971301798:AAErmSXi-WVr7YLJGlMrmo2g1w_Cb56p0Iw"
API_URL   = "http://ru.independentvpn.ru:8080/subscribe" 
# Endpoints Flask API на VPN-серверах
API_ENDPOINTS = {
    "RU": "http://194.87.74.91:8080/add_user",
    "US": "http://185.106.95.235:8080/add_user",
    "KZ": "http://45.144.175.11:8080/add_user",
    "FIN": "http://64.188.73.65:8080/add_user"
}

# Домены для формирования VLESS-ссылки
DOMAINS = {
    "RU": "ru.independentvpn.ru",
    "US": "us.independentvpn.ru",
    "KZ": "kz.independentvpn.ru",
    "FIN": "fin.independentvpn.ru"
}

# Порт, который вы используете (443 или 8443 и т.п.)
PORT = 443
