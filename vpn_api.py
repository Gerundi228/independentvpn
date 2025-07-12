import requests

def add_user_to_vpn(region, user_id, email=None):
    url = API_ENDPOINTS[region]
    payload = {"user_id": user_id, "email": email}
    r = requests.post(url, json=payload, timeout=10)
    r.raise_for_status()
    data = r.json()
    if data.get("status") == "ok":
        return data["uuid"]
    else:
        raise RuntimeError(f"API error: {data}")
