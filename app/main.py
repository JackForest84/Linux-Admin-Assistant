import sqlite3
import unicodedata
from pathlib import Path

import yaml
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

BASE = Path(__file__).resolve().parent.parent
DATA_DIR = BASE / "data"
STATIC_DIR = BASE / "static"
DB_PATH = ":memory:"

app = FastAPI(title="linuxcmd")
_conn: sqlite3.Connection | None = None


def strip_diacritics(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)
    ).lower()


def load_data() -> list[dict]:
    items = []
    for f in sorted(DATA_DIR.glob("*.yaml")):
        with open(f) as fp:
            doc = yaml.safe_load(fp) or []
        for entry in doc:
            entry["_category"] = f.stem
            items.append(entry)
    return items


def build_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""
        CREATE VIRTUAL TABLE cmd USING fts5(
            id UNINDEXED,
            category UNINDEXED,
            title_cs, title_en,
            tags_cs, tags_en,
            search_cs, search_en,
            payload UNINDEXED,
            tokenize = "unicode61 remove_diacritics 2"
        )
    """)
    items = load_data()
    import json

    for it in items:
        title_cs = it.get("title_cs", "")
        title_en = it.get("title_en", "")
        tags_cs = " ".join(it.get("tags_cs", []) or [])
        tags_en = " ".join(it.get("tags_en", []) or [])
        cmds_text = " ".join(
            (c.get("cmd", "") + " " + c.get("desc_cs", "") + " " + c.get("desc_en", ""))
            for c in it.get("commands", [])
        )
        search_cs = f"{title_cs} {tags_cs} {cmds_text}"
        search_en = f"{title_en} {tags_en} {cmds_text}"
        conn.execute(
            "INSERT INTO cmd VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                it.get("id", ""),
                it.get("_category", ""),
                title_cs,
                title_en,
                tags_cs,
                tags_en,
                search_cs,
                search_en,
                json.dumps(it, ensure_ascii=False),
            ),
        )
    conn.commit()
    return conn


@app.on_event("startup")
def startup():
    global _conn
    _conn = build_db()


@app.get("/api/search")
def search(q: str = Query(default=""), lang: str = Query(default="cs"), limit: int = 30):
    import json

    assert _conn is not None
    q = q.strip()
    if not q:
        rows = _conn.execute(
            "SELECT payload, category FROM cmd ORDER BY rowid LIMIT ?", (limit,)
        ).fetchall()
    else:
        terms = [strip_diacritics(t) for t in q.split() if t]
        fts_q = " ".join(f'"{t}"*' for t in terms)
        col = "search_cs" if lang == "cs" else "search_en"
        try:
            rows = _conn.execute(
                f"SELECT payload, category FROM cmd WHERE {col} MATCH ? ORDER BY bm25(cmd) LIMIT ?",
                (fts_q, limit),
            ).fetchall()
        except sqlite3.OperationalError:
            rows = []
    results = []
    for payload, category in rows:
        item = json.loads(payload)
        item["category"] = category
        results.append(item)
    return JSONResponse({"results": results, "count": len(results)})


@app.get("/api/categories")
def categories():
    assert _conn is not None
    rows = _conn.execute(
        "SELECT category, COUNT(*) FROM cmd GROUP BY category ORDER BY category"
    ).fetchall()
    return {"categories": [{"name": c, "count": n} for c, n in rows]}


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")
