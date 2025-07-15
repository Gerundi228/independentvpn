#!/usr/bin/env python3
import json
import uuid
import traceback
import re
from flask import Flask, request, jsonify, Response, abort
import paramiko
from db import init_db, get_regions
from config import REGION_SERVERS

app = Flask(__name__)
UUID_RE = re.compile(r"^[a-f0-9-]{36}$", re.I)

init_db()

def add_user_via_ssh(region: str, tg_id: int) -> str:
    srv = REGION_SERVERS[region]
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        hostname=srv["host"],
        port=srv["ssh_port"],
        username=srv["ssh_user"],
        key_filename=srv["ssh_key"],
        timeout=10
    )
    sftp = ssh.open_sftp()
    # читаем конфиг
    with sftp.file(srv["config_path"], "r") as f:
        cfg = json.load(f)
    # генерим UUID и добавляем клиента
    new_uuid = str(uuid.uuid4())
    cfg["inbounds"][0]["settings"]["clients"].append({
        "id":    new_uuid,
        "level": 0,
        "email": f"{tg_id}@vpn"
    })
    # пишем обратно
    with sftp.file(srv["config_path"], "w") as f:
        f.write(json.dumps(cfg, indent=2))
    sftp.close()
    # перезапускаем сервис Xray
    stdin, stdout, stderr = ssh.exec_command(f"systemctl restart {srv['service']}")
    err = stderr.read().decode().strip()
    ssh.close()
    if err:
        raise RuntimeError(f"Failed to restart {srv['service']}: {err}")
    return new_uuid

@app.route("/add_user", methods=["POST"])
def api_add_user():
    data = request.get_json(force=True)
    region = data.get("region")
    tg_id   = data.get("user_id")
    if region not in REGION_SERVERS:
        return jsonify({"status":"error","message":"Unknown region"}), 400
    try:
        new_uuid = add_user_via_ssh(region, tg_id)
        return jsonify({"status":"ok","uuid": new_uuid})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status":"error","message": str(e)}), 500

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
    return Response("\n".join(lines), mimetype="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
