import os
import re
import sqlite3
import zipfile
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
  created_at TEXT NOT NULL
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
  created_at TEXT NOT NULL
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
            "request_no": o["request_no"],
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
    f.save(os.path.join(UPLOAD_DIR, stored))
    con = get_db()
    cur = con.execute(
        "INSERT INTO docs(order_id,uploader,type,orig_name,stored_name,size,comment,status,created_at)"
        " VALUES(?,?,?,?,?,?,?, 'review', ?)",
        (order_id, u["name"], dtype, orig, stored, f.content_length or 0, comment, now_str()),
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
    cur = con.execute(
        "INSERT INTO exports(order_id,request_no,filename,stored_name,size,doc_count,created_by,created_at)"
        " VALUES(?,?,?,?,?,?,?,?)",
        (order_id, o["request_no"], zip_name, stored, size, len(used), u["name"], now_str()),
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
