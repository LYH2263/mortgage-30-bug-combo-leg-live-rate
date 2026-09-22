import json
import sqlite3
from app.modules.combo_loan import LEG_KEYS

def _shape(row):
    d = dict(row)
    raw = d.pop("legs_json", None)
    d["legs"] = json.loads(raw) if raw else None
    return d

def list_all(conn): return [_shape(r) for r in conn.execute("SELECT * FROM loans ORDER BY id").fetchall()]
def get(conn, lid):
    row = conn.execute("SELECT * FROM loans WHERE id=?", (lid,)).fetchone()
    return _shape(row) if row else None
def update_legs(conn, lid, legs):
    principal = sum(float(legs[k]["principal"]) for k in LEG_KEYS)
    months = max(int(legs[k]["months"]) for k in LEG_KEYS)
    conn.execute("UPDATE loans SET legs_json=?, principal=?, months=? WHERE id=?",
        (json.dumps(legs, ensure_ascii=False), principal, months, lid))
    conn.commit()
