import os
import re
import json
import sqlite3
import zipfile
import hashlib
import secrets
import urllib.request
import urllib.parse
from datetime import datetime

from flask import Flask, jsonify, request, session, send_from_directory, abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ON_AMVERA = "AMVERA" in os.environ
DATA_DIR = "/data" if ON_AMVERA else BASE_DIR
DB_PATH = os.path.join(DATA_DIR, "translog.db")
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
EXPORTS_DIR = os.path.join(DATA_DIR, "exports")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production")
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # 25 МБ

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  login TEXT UNIQUE NOT NULL,
  pass_hash TEXT NOT NULL,
  name TEXT NOT NULL,
  role TEXT NOT NULL CHECK(role IN ('driver','dispatcher')),
  order_id TEXT
);
CREATE TABLE IF NOT EXISTS orders (
  id TEXT PRIMARY KEY,
  driver_name TEXT NOT NULL,
  route TEXT NOT NULL,
  cargo TEXT NOT NULL,
  plate TEXT NOT NULL,
  status TEXT NOT NULL,
  request_no TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS exports (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id TEXT NOT NULL,
  request_no TEXT DEFAULT '',
  filename TEXT NOT NULL,
  stored_name TEXT NOT NULL,
  size INTEGER NOT NULL DEFAULT 0,
  doc_count INTEGER NOT NULL DEFAULT 0,
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL,
  mega_url TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS docs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id TEXT NOT NULL,
  uploader TEXT NOT NULL,
  type TEXT NOT NULL,
  orig_name TEXT NOT NULL,
  stored_name TEXT NOT NULL,
  size INTEGER NOT NULL DEFAULT 0,
  comment TEXT DEFAULT '',
  status TEXT NOT NULL DEFAULT 'review' CHECK(status IN ('review','approved','rejected')),
  created_at TEXT NOT NULL,
  mega_url TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS msgs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id TEXT NOT NULL,
  who TEXT NOT NULL,
  text TEXT DEFAULT '',
  doc_id INTEGER,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS last_read (
  login TEXT NOT NULL,
  order_id TEXT NOT NULL,
  last_id INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (login, order_id)
);
CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL DEFAULT ''
);
"""


def get_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def fmt_size(n):
    if n is None or n <= 0:
        return "—"
    if n < 1024 * 1024:
        return f"{n / 1024:.0f} КБ"
    return f"{n / 1024 / 1024:.1f} МБ".replace(".", ",")


def fmt_time(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
    except Exception:
        return s


def seed(con):
    users = [
        ("dispatcher", "dispatcher123", "Алексей Смирнов", "dispatcher", None),
        ("ivan", "driver123", "Иван Петров", "driver", "ORD-1042"),
        ("maria", "driver123", "Мария Сидорова", "driver", "ORD-1043"),
        ("oleg", "driver123", "Олег Козлов", "driver", "ORD-1044"),
        ("dmitry", "driver123", "Дмитрий Волков", "driver", "ORD-1045"),
    ]
    for login, pw, name, role, oid in users:
        con.execute(
            "INSERT INTO users(login,pass_hash,name,role,order_id) VALUES(?,?,?,?,?)",
            (login, generate_password_hash(pw), name, role, oid),
        )
    orders = [
        ("ORD-1042", "Иван Петров", "Москва → Казань", "Стройматериалы, 20 т", "А123БВ77", "enroute", "З-778"),
        ("ORD-1043", "Мария Сидорова", "Санкт-Петербург → Новосибирск", "Бытовая техника, 12 т", "К456МН98", "loading", "З-779"),
        ("ORD-1044", "Олег Козлов", "Казань → Самара", "Продукты, 8 т", "М789ОР116", "problem", "З-780"),
        ("ORD-1045", "Дмитрий Волков", "Москва → Нижний Новгород", "Мебель, 6 т", "Р012СТ77", "done", "З-781"),
    ]
    for o in orders:
        con.execute(
            "INSERT INTO orders(id,driver_name,route,cargo,plate,status,request_no) VALUES(?,?,?,?,?,?,?)", o
        )
    demo = [
        ("ORD-1042", "dispatcher", "Добрый день, Иван! Пришлите CMR сразу после разгрузки.", "2026-09-30 10:01:00"),
        ("ORD-1042", "driver", "Добрый! Разгрузка до 13:00, сразу отправлю.", "2026-09-30 10:05:00"),
        ("ORD-1043", "dispatcher", "Мария, путевой лист вернулся — нет подписи экспедитора. Переснимите страницу.", "2026-09-30 09:20:00"),
        ("ORD-1043", "driver", "Поняла, сделаю на посту через час.", "2026-09-30 09:24:00"),
        ("ORD-1044", "driver", "Диспетчер, стою в пробке на М-5, около 15 км.", "2026-09-30 11:30:00"),
        ("ORD-1044", "dispatcher", "Принял, предупрежу клиента. Доверенность уже готова?", "2026-09-30 11:33:00"),
    ]
    for oid, who, text, ts in demo:
        con.execute(
            "INSERT INTO msgs(order_id,who,text,doc_id,created_at) VALUES(?,?,?,NULL,?)",
            (oid, who, text, ts),
        )
    con.commit()


def migrate(con):
    cols = [r[1] for r in con.execute("PRAGMA table_info(orders)").fetchall()]
    if "request_no" not in cols:
        con.execute("ALTER TABLE orders ADD COLUMN request_no TEXT DEFAULT ''")
    if "tt_order_id" not in cols:
        con.execute("ALTER TABLE orders ADD COLUMN tt_order_id TEXT DEFAULT ''")
    dcols = [r[1] for r in con.execute("PRAGMA table_info(docs)").fetchall()]
    if "mega_url" not in dcols:
        con.execute("ALTER TABLE docs ADD COLUMN mega_url TEXT DEFAULT ''")
    ecols = [r[1] for r in con.execute("PRAGMA table_info(exports)").fetchall()]
    if "mega_url" not in ecols:
        con.execute("ALTER TABLE exports ADD COLUMN mega_url TEXT DEFAULT ''")
    for row in con.execute("SELECT id FROM orders WHERE request_no='' OR request_no IS NULL").fetchall():
        m = re.search(r"(\d+)", row["id"])
        num = int(m.group(1)) - 264 if m else 600
        con.execute("UPDATE orders SET request_no=? WHERE id=?", (f"З-{num}", row["id"]))


def init_db():
    con = get_db()
    con.executescript(SCHEMA)
    migrate(con)
    if con.execute("SELECT COUNT(*) c FROM users").fetchone()["c"] == 0:
        seed(con)
    con.commit()
    con.close()


init_db()


# ---------- helpers ----------

def current_user():
    login = session.get("login")
    if not login:
        return None
    con = get_db()
    u = con.execute("SELECT * FROM users WHERE login=?", (login,)).fetchone()
    con.close()
    return u


def require_auth():
    u = current_user()
    if not u:
        abort(401)
    return u


def require_order_access(u, order_id):
    if u["role"] == "driver" and u["order_id"] != order_id:
        abort(403)


def doc_json(d):
    return {
        "id": d["id"],
        "order_id": d["order_id"],
        "type": d["type"],
        "name": d["orig_name"],
        "size": fmt_size(d["size"]),
        "status": d["status"],
        "comment": d["comment"],
        "time": fmt_time(d["created_at"]),
        "uploader": d["uploader"],
        "mega_url": d["mega_url"] if "mega_url" in d.keys() else "",
    }


def msg_json(con, m):
    d = None
    if m["doc_id"]:
        row = con.execute("SELECT * FROM docs WHERE id=?", (m["doc_id"],)).fetchone()
        if row:
            d = doc_json(row)
    return {
        "id": m["id"],
        "who": m["who"],
        "text": m["text"],
        "doc": d,
        "time": fmt_time(m["created_at"]),
    }


def add_sys_msg(con, order_id, text):
    con.execute(
        "INSERT INTO msgs(order_id,who,text,doc_id,created_at) VALUES(?,?,?,NULL,?)",
        (order_id, "sys", text, now_str()),
    )


# ---------- auth ----------

@app.post("/api/login")
def login():
    data = request.get_json(force=True, silent=True) or {}
    login_v = (data.get("login") or "").strip()
    password = data.get("password") or ""
    con = get_db()
    u = con.execute("SELECT * FROM users WHERE login=?", (login_v,)).fetchone()
    con.close()
    if not u or not check_password_hash(u["pass_hash"], password):
        return jsonify({"error": "Неверный логин или пароль"}), 401
    session["login"] = u["login"]
    return jsonify({"login": u["login"], "name": u["name"], "role": u["role"], "order_id": u["order_id"]})


@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"ok": True})


@app.get("/api/me")
def me():
    u = require_auth()
    return jsonify({"login": u["login"], "name": u["name"], "role": u["role"], "order_id": u["order_id"]})


# ---------- orders ----------

@app.get("/api/orders")
def orders():
    u = require_auth()
    con = get_db()
    if u["role"] == "driver":
        rows = con.execute(
            "SELECT * FROM orders WHERE id=?", (u["order_id"],)
        ).fetchall()
    else:
        rows = con.execute("SELECT * FROM orders").fetchall()
    result = []
    for o in rows:
        review = con.execute(
            "SELECT COUNT(*) c FROM docs WHERE order_id=? AND status='review'", (o["id"],)
        ).fetchone()["c"]
        lr = con.execute(
            "SELECT last_id FROM last_read WHERE login=? AND order_id=?", (u["login"], o["id"])
        ).fetchone()
        last_id = lr["last_id"] if lr else 0
        unread = con.execute(
            "SELECT COUNT(*) c FROM msgs WHERE order_id=? AND who!=? AND id>? AND who!='sys'",
            (o["id"], u["role"], last_id),
        ).fetchone()["c"]
        result.append({
            "id": o["id"], "driver": o["driver_name"], "route": o["route"],
            "cargo": o["cargo"], "plate": o["plate"], "status": o["status"],
            "request_no": o["request_no"], "tt_order_id": o["tt_order_id"],
            "review_count": review, "unread": unread,
        })
    con.close()
    return jsonify(result)


# ---------- documents ----------

@app.get("/api/docs")
def docs():
    u = require_auth()
    con = get_db()
    q = request.args.get("q", "").strip().lower()
    status = request.args.get("status", "all")
    order_id = request.args.get("order_id", "").strip()
    sql = "SELECT * FROM docs WHERE 1=1"
    params = []
    if u["role"] == "driver":
        sql += " AND order_id=?"
        params.append(u["order_id"])
    elif order_id:
        sql += " AND order_id=?"
        params.append(order_id)
    if status in ("review", "approved", "rejected"):
        sql += " AND status=?"
        params.append(status)
    sql += " ORDER BY id DESC"
    rows = con.execute(sql, params).fetchall()
    con.close()
    out = [doc_json(r) for r in rows]
    if q:
        out = [d for d in out if q in d["name"].lower() or q in d["type"].lower()]
    return jsonify(out)


@app.post("/api/docs")
def upload_doc():
    u = require_auth()
    order_id = (request.form.get("order_id") or "").strip()
    dtype = (request.form.get("type") or "Документ").strip()
    comment = (request.form.get("comment") or "").strip()
    f = request.files.get("file")
    if not order_id:
        return jsonify({"error": "Не указан рейс"}), 400
    require_order_access(u, order_id)
    if not f or not f.filename:
        return jsonify({"error": "Выберите файл"}), 400
    orig = f.filename
    stored = f"{int(datetime.now().timestamp() * 1000)}_{secure_filename(orig)}"
    local_path = os.path.join(UPLOAD_DIR, stored)
    f.save(local_path)
    mega_url = mega_upload(local_path) if mega_configured() else ""
    con = get_db()
    cur = con.execute(
        "INSERT INTO docs(order_id,uploader,type,orig_name,stored_name,size,comment,status,created_at,mega_url)"
        " VALUES(?,?,?,?,?,?,?, 'review', ?, ?)",
        (order_id, u["name"], dtype, orig, stored, f.content_length or 0, comment, now_str(), mega_url),
    )
    add_sys_msg(con, order_id, f"Документ {orig} отправлен на проверку")
    con.commit()
    d = con.execute("SELECT * FROM docs WHERE id=?", (cur.lastrowid,)).fetchone()
    con.close()
    return jsonify(doc_json(d)), 201


def change_doc_status(doc_id, new_status, sys_text):
    con = get_db()
    d = con.execute("SELECT * FROM docs WHERE id=?", (doc_id,)).fetchone()
    if not d:
        con.close()
        abort(404)
    con.execute("UPDATE docs SET status=? WHERE id=?", (new_status, doc_id))
    add_sys_msg(con, d["order_id"], sys_text)
    con.commit()
    d = con.execute("SELECT * FROM docs WHERE id=?", (doc_id,)).fetchone()
    con.close()
    return doc_json(d)


@app.post("/api/docs/<int:doc_id>/approve")
def approve(doc_id):
    u = require_auth()
    if u["role"] != "dispatcher":
        abort(403)
    return jsonify(change_doc_status(doc_id, "approved", "Документ одобрен"))


@app.post("/api/docs/<int:doc_id>/reject")
def reject(doc_id):
    u = require_auth()
    if u["role"] != "dispatcher":
        abort(403)
    return jsonify(change_doc_status(doc_id, "rejected", "Документ отклонён: требуется повторная отправка"))


@app.post("/api/docs/<int:doc_id>/resend")
def resend(doc_id):
    u = require_auth()
    con = get_db()
    d = con.execute("SELECT * FROM docs WHERE id=?", (doc_id,)).fetchone()
    if not d:
        con.close()
        abort(404)
    require_order_access(u, d["order_id"])
    con.execute("UPDATE docs SET status='review', created_at=? WHERE id=?", (now_str(), doc_id))
    add_sys_msg(con, d["order_id"], f"Документ {d['orig_name']} отправлен повторно")
    con.commit()
    d = con.execute("SELECT * FROM docs WHERE id=?", (doc_id,)).fetchone()
    con.close()
    return jsonify(doc_json(d))


@app.get("/api/docs/<int:doc_id>/download")
def download(doc_id):
    u = require_auth()
    con = get_db()
    d = con.execute("SELECT * FROM docs WHERE id=?", (doc_id,)).fetchone()
    con.close()
    if not d:
        abort(404)
    require_order_access(u, d["order_id"])
    return send_from_directory(UPLOAD_DIR, d["stored_name"], as_attachment=True, download_name=d["orig_name"])


# ---------- exports (ZIP-архивы по рейсу) ----------

def safe_zip_name(s):
    s = re.sub(r"[\\/:*?\"<>|\s]+", "_", str(s))
    return s.strip("_") or "archive"


def export_json(e):
    return {
        "id": e["id"],
        "order_id": e["order_id"],
        "request_no": e["request_no"],
        "filename": e["filename"],
        "size": fmt_size(e["size"]),
        "doc_count": e["doc_count"],
        "created_by": e["created_by"],
        "time": fmt_time(e["created_at"]),
        "mega_url": e["mega_url"] if "mega_url" in e.keys() else "",
    }


@app.post("/api/orders/<order_id>/export")
def export_order(order_id):
    u = require_auth()
    require_order_access(u, order_id)
    con = get_db()
    o = con.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    if not o:
        con.close()
        abort(404)
    rows = con.execute(
        "SELECT * FROM docs WHERE order_id=? ORDER BY id", (order_id,)
    ).fetchall()
    if not rows:
        con.close()
        return jsonify({"error": "По этому рейсу пока нет документов"}), 400
    zip_name = safe_zip_name(f"{order_id}_{o['request_no']}") + ".zip"
    stored = f"{int(datetime.now().timestamp() * 1000)}_{zip_name}"
    zip_path = os.path.join(EXPORTS_DIR, stored)
    used = set()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for d in rows:
            src = os.path.join(UPLOAD_DIR, d["stored_name"])
            if not os.path.exists(src):
                continue
            arc = d["orig_name"]
            if arc in used:
                arc = f"{d['id']}_{arc}"
            used.add(arc)
            z.write(src, arc)
    if not used:
        os.remove(zip_path)
        con.close()
        return jsonify({"error": "Файлы документов не найдены на сервере"}), 400
    size = os.path.getsize(zip_path)
    mega_url = mega_upload(zip_path) if mega_configured() else ""
    cur = con.execute(
        "INSERT INTO exports(order_id,request_no,filename,stored_name,size,doc_count,created_by,created_at,mega_url)"
        " VALUES(?,?,?,?,?,?,?,?,?)",
        (order_id, o["request_no"], zip_name, stored, size, len(used), u["name"], now_str(), mega_url),
    )
    add_sys_msg(con, order_id, f"Сформирован архив документов {zip_name} ({len(used)} файлов)")
    con.commit()
    e = con.execute("SELECT * FROM exports WHERE id=?", (cur.lastrowid,)).fetchone()
    con.close()
    return jsonify(export_json(e)), 201


@app.get("/api/exports")
def exports_list():
    u = require_auth()
    con = get_db()
    if u["role"] == "driver":
        rows = con.execute(
            "SELECT * FROM exports WHERE order_id=? ORDER BY id DESC", (u["order_id"],)
        ).fetchall()
    else:
        rows = con.execute("SELECT * FROM exports ORDER BY id DESC").fetchall()
    con.close()
    return jsonify([export_json(e) for e in rows])


@app.get("/api/exports/<int:export_id>/download")
def export_download(export_id):
    u = require_auth()
    con = get_db()
    e = con.execute("SELECT * FROM exports WHERE id=?", (export_id,)).fetchone()
    con.close()
    if not e:
        abort(404)
    require_order_access(u, e["order_id"])
    return send_from_directory(EXPORTS_DIR, e["stored_name"], as_attachment=True, download_name=e["filename"])


# ---------- MEGA storage ----------

_MEGA_CLIENT = None
_MEGA_BROKEN = False


def mega_reset():
    global _MEGA_CLIENT, _MEGA_BROKEN
    _MEGA_CLIENT = None
    _MEGA_BROKEN = False


def mega_configured():
    return bool(get_setting("mega_email") and get_setting("mega_password"))


def mega_client():
    global _MEGA_CLIENT, _MEGA_BROKEN
    if _MEGA_CLIENT is not None:
        return _MEGA_CLIENT
    if _MEGA_BROKEN or not mega_configured():
        return None
    try:
        from mega import Mega
        _MEGA_CLIENT = Mega().login(get_setting("mega_email"), get_setting("mega_password"))
        return _MEGA_CLIENT
    except Exception:
        _MEGA_BROKEN = True
        return None


def mega_upload(path):
    """Загружает файл в MEGA, возвращает публичную ссылку или ''."""
    m = mega_client()
    if not m:
        return ""
    try:
        node = m.upload(path)
        return m.get_upload_link(node) or ""
    except Exception:
        return ""


@app.get("/api/settings/mega")
def mega_settings_get():
    u = require_auth()
    if u["role"] != "dispatcher":
        abort(403)
    return jsonify({
        "email": get_setting("mega_email"),
        "has_password": bool(get_setting("mega_password")),
    })


@app.post("/api/settings/mega")
def mega_settings_save():
    u = require_auth()
    if u["role"] != "dispatcher":
        abort(403)
    data = request.get_json(force=True, silent=True) or {}
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""
    if email:
        if "@" not in email:
            return jsonify({"error": "Некорректный email"}), 400
        set_setting("mega_email", email)
    if password:
        set_setting("mega_password", password)
    mega_reset()
    return jsonify({"ok": True, "configured": mega_configured()})


@app.post("/api/mega/test")
def mega_test():
    u = require_auth()
    if u["role"] != "dispatcher":
        abort(403)
    if not mega_configured():
        return jsonify({"error": "MEGA не настроен: укажите email и пароль"}), 400
    mega_reset()
    m = mega_client()
    if not m:
        return jsonify({"ok": False, "error": "Не удалось войти в MEGA — проверьте email/пароль (2FA должна быть выключена)"}), 502
    try:
        quota = m.get_quota() or 0
        used = m.get_storage_space().get("used", 0) if hasattr(m, "get_storage_space") else 0
        gb = quota / 1024 / 1024 if quota else 0
        return jsonify({"ok": True, "detail": f"Вход выполнен. Хранилище: {gb:.0f} ГБ."})
    except Exception as e:
        return jsonify({"ok": True, "detail": "Вход выполнен."})


# ---------- TransTrade API (tt-ok.ru) ----------

def get_setting(key):
    con = get_db()
    row = con.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    con.close()
    return row["value"] if row else ""


def set_setting(key, value):
    con = get_db()
    con.execute(
        "INSERT INTO settings(key,value) VALUES(?,?)"
        " ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )
    con.commit()
    con.close()


def tt_configured():
    return bool(get_setting("tt_api_url") and get_setting("tt_api_key") and get_setting("tt_api_user_id"))


def tt_request(method, data):
    """Подписанный запрос к TransTrade API. Возвращает (ok, result_dict)."""
    url = get_setting("tt_api_url")
    key = get_setting("tt_api_key")
    data.setdefault("api_user_id", int(get_setting("tt_api_user_id") or 0))
    data_str = json.dumps(data, ensure_ascii=False)
    rnd = secrets.token_hex(8)
    sign = hashlib.md5(
        (key + "###" + data_str + "###" + method + "###" + rnd + "###" + key).encode("utf-8")
    ).hexdigest()
    body = urllib.parse.urlencode(
        {"data": data_str, "method": method, "random": rnd, "signature": sign}
    ).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return False, {"error": f"Ошибка соединения с API: {e}"}
    if payload.get("error_code"):
        return False, {"error": payload.get("error_text") or "Ошибка API"}
    return True, payload


@app.get("/api/settings/tt")
def tt_settings_get():
    u = require_auth()
    if u["role"] != "dispatcher":
        abort(403)
    key = get_setting("tt_api_key")
    return jsonify({
        "url": get_setting("tt_api_url"),
        "api_user_id": get_setting("tt_api_user_id"),
        "has_key": bool(key),
        "api_key_masked": (key[:4] + "…" + key[-4:]) if len(key) > 8 else "",
    })


@app.post("/api/settings/tt")
def tt_settings_save():
    u = require_auth()
    if u["role"] != "dispatcher":
        abort(403)
    data = request.get_json(force=True, silent=True) or {}
    url = (data.get("url") or "").strip()
    key = (data.get("api_key") or "").strip()
    uid = str(data.get("api_user_id") or "").strip()
    if url:
        if not re.match(r"^https?://", url):
            return jsonify({"error": "URL должен начинаться с http:// или https://"}), 400
        set_setting("tt_api_url", url.rstrip("/"))
    if key:
        set_setting("tt_api_key", key)
    if uid:
        if not uid.isdigit():
            return jsonify({"error": "api_user_id — целое положительное число"}), 400
        set_setting("tt_api_user_id", uid)
    return jsonify({"ok": True, "configured": tt_configured()})


@app.post("/api/tt/test")
def tt_test():
    u = require_auth()
    if u["role"] != "dispatcher":
        abort(403)
    if not tt_configured():
        return jsonify({"error": "API не настроен: заполните URL, KEY и api_user_id"}), 400
    ok, res = tt_request("GetDrivers", {})
    if not ok:
        return jsonify({"ok": False, "error": res["error"]}), 502
    drivers = res.get("data") or []
    names = [d.get("Driver", "") for d in drivers[:3] if isinstance(d, dict)]
    return jsonify({
        "ok": True,
        "detail": f"Связь установлена. Водителей в TransTrade: {len(drivers)}"
                  + (": " + ", ".join(names) if names else ""),
    })


@app.post("/api/orders/<order_id>/push_tt")
def push_order_tt(order_id):
    u = require_auth()
    if u["role"] != "dispatcher":
        abort(403)
    if not tt_configured():
        return jsonify({"error": "TransTrade API не настроен (Настройки → TransTrade API)"}), 400
    con = get_db()
    o = con.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    if not o:
        con.close()
        abort(404)
    parts = [p.strip() for p in o["route"].split("→")]
    load = parts[0] if parts else ""
    unload = parts[1] if len(parts) > 1 else ""
    data = {
        "Client": o["driver_name"],
        "ContactFace": o["driver_name"],
        "AutoType": "-",
        "Load": load,
        "Unload": unload,
        "User": u["name"],
        "Cargo": o["cargo"],
        "Comment": f"Рейс {o['id']} (заявка {o['request_no']}) из TransLog",
        "Firm": "-",
        "Transport": o["plate"],
        "Driver": o["driver_name"],
        "OrderNum": o["id"],
        "ClientOrderNum": o["request_no"],
    }
    if o["tt_order_id"] and str(o["tt_order_id"]).isdigit():
        method, data = "EditOrder", dict(data, OrderId=int(o["tt_order_id"]))
    else:
        method = "CreateOrder"
    ok, res = tt_request(method, data)
    if not ok:
        con.close()
        return jsonify({"error": res["error"]}), 502
    tt_id = str((res.get("data") or {}).get("order_id") or o["tt_order_id"] or "")
    if tt_id:
        con.execute("UPDATE orders SET tt_order_id=? WHERE id=?", (tt_id, order_id))
    verb = "обновлён" if method == "EditOrder" else "создан"
    add_sys_msg(con, order_id, f"Заказ {verb} в TransTrade" + (f" (ID {tt_id})" if tt_id else ""))
    con.commit()
    con.close()
    return jsonify({"ok": True, "method": method, "tt_order_id": tt_id})


# ---------- chat ----------

@app.get("/api/msgs")
def msgs():
    u = require_auth()
    order_id = request.args.get("order_id", "").strip()
    after_id = int(request.args.get("after_id", 0))
    if not order_id:
        return jsonify([])
    require_order_access(u, order_id)
    con = get_db()
    rows = con.execute(
        "SELECT * FROM msgs WHERE order_id=? AND id>? ORDER BY id",
        (order_id, after_id),
    ).fetchall()
    out = [msg_json(con, m) for m in rows]
    if rows:
        max_id = rows[-1]["id"]
        con.execute(
            "INSERT INTO last_read(login,order_id,last_id) VALUES(?,?,?)"
            " ON CONFLICT(login,order_id) DO UPDATE SET last_id=excluded.last_id",
            (u["login"], order_id, max_id),
        )
        con.commit()
    con.close()
    return jsonify(out)


@app.post("/api/msgs")
def send_msg():
    u = require_auth()
    data = request.get_json(force=True, silent=True) or {}
    order_id = (data.get("order_id") or "").strip()
    text = (data.get("text") or "").strip()
    doc_id = data.get("doc_id")
    if not order_id or (not text and not doc_id):
        return jsonify({"error": "Пустое сообщение"}), 400
    require_order_access(u, order_id)
    con = get_db()
    cur = con.execute(
        "INSERT INTO msgs(order_id,who,text,doc_id,created_at) VALUES(?,?,?,?,?)",
        (order_id, u["role"], text, doc_id, now_str()),
    )
    m = con.execute("SELECT * FROM msgs WHERE id=?", (cur.lastrowid,)).fetchone()
    out = msg_json(con, m)
    con.commit()
    con.close()
    return jsonify(out), 201


@app.get("/")
def index():
    return send_from_directory("static", "index.html")


@app.get("/healthz")
def healthz():
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
