import requests
from config import API_ENDPOINTS

def add_user_to_vpn(region: str, user_id: int, email: str = None) -> str:
  
    url = API_ENDPOINTS[region]
    payload = {"user_id": user_id, "email": email}
    r = requests.post(url, json=payload, timeout=(5, 30))
    r.raise_for_status()
    data = r.json()
    if data.get("status") == "ok" and "uuid" in data:
        return data["uuid"]
    else:
        raise RuntimeError(f"API error: {data}")
