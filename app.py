#!/usr/bin/env python3
from flask import Flask, Response, abort
import re
from db import init_db, get_regions

app = Flask(__name__)
UUID_RE = re.compile(r"^[a-f0-9-]{36}$", re.I)

# создаём БД при старте, если её нет
init_db()

@app.route("/subscribe/<uuid>")
def subscribe(uuid):
    if not UUID_RE.match(uuid):
        return abort(404)
    regions = get_regions()
    if not regions:
        return abort(500, "no regions")
    lines = []
    for r in regions:
        url = (
            f"vless://{uuid}@{r['domain']}:{r['port']}?"
            f"encryption=none&security=tls"
            f"&type={r['type']}"
            f"&host={r['domain']}"
            f"&path={r['path']}"
            f"#{r['code']}-VPN"
        )
        lines.append(url)
    body = "\n".join(lines)
    return Response(body, mimetype="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
