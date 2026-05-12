import json
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

# Supported languages. First is primary (fallback).
LANGS = ["en", "cs", "sk", "de", "es", "fr", "it", "pl", "tr", "pt", "nl", "hu"]
PRIMARY = "en"

app = FastAPI(title="linuxcmd")
_conn: sqlite3.Connection | None = None


def strip_diacritics(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)
    ).lower()


def get_lang_field(entry: dict, field: str, lang: str) -> str | list:
    """Get field for given lang, fallback to primary lang, then any available."""
    val = entry.get(field, {})
    if isinstance(val, dict):
        if lang in val and val[lang]:
            return val[lang]
        if PRIMARY in val and val[PRIMARY]:
            return val[PRIMARY]
        for k in LANGS:
            if k in val and val[k]:
                return val[k]
        return "" if field != "tags" else []
    # Legacy flat string (shouldn't happen after migration)
    return val or ("" if field != "tags" else [])


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
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    search_cols = ", ".join(f"search_{l}" for l in LANGS)
    conn.execute(f"""
        CREATE VIRTUAL TABLE cmd USING fts5(
            id UNINDEXED,
            category UNINDEXED,
            {search_cols},
            payload UNINDEXED,
            tokenize = "unicode61 remove_diacritics 2"
        )
    """)
    items = load_data()

    for it in items:
        search_per_lang = {}
        for lang in LANGS:
            title = get_lang_field(it, "title", lang)
            tags = get_lang_field(it, "tags", lang) or []
            if isinstance(tags, list):
                tags_text = " ".join(tags)
            else:
                tags_text = str(tags)
            cmds_text = " ".join(
                (c.get("cmd", "") + " " + get_lang_field(c, "desc", lang))
                for c in it.get("commands", [])
            )
            search_per_lang[lang] = f"{title} {tags_text} {cmds_text}"

        cols = ", ".join(["id", "category"] + [f"search_{l}" for l in LANGS] + ["payload"])
        placeholders = ", ".join(["?"] * (3 + len(LANGS)))
        values = (
            it.get("id", ""),
            it.get("_category", ""),
            *[search_per_lang[l] for l in LANGS],
            json.dumps(it, ensure_ascii=False),
        )
        conn.execute(f"INSERT INTO cmd ({cols}) VALUES ({placeholders})", values)
    conn.commit()
    return conn


@app.on_event("startup")
def startup():
    global _conn
    _conn = build_db()


def localize_entry(entry: dict, lang: str) -> dict:
    """Return entry with localized title/desc/tags for the chosen lang."""
    out = {
        "id": entry.get("id", ""),
        "category": entry.get("category", entry.get("_category", "")),
        "title": get_lang_field(entry, "title", lang),
        "tags": get_lang_field(entry, "tags", lang) or [],
        "commands": [],
    }
    for c in entry.get("commands", []):
        out["commands"].append({
            "cmd": c.get("cmd", ""),
            "desc": get_lang_field(c, "desc", lang),
        })
    return out


@app.get("/api/search")
def search(q: str = Query(default=""), lang: str = Query(default=PRIMARY), limit: int = 30):
    assert _conn is not None
    if lang not in LANGS:
        lang = PRIMARY
    q = q.strip()
    if not q:
        rows = _conn.execute(
            "SELECT payload, category FROM cmd ORDER BY rowid LIMIT ?", (limit,)
        ).fetchall()
    else:
        terms = [strip_diacritics(t) for t in q.split() if t]
        fts_q = " ".join(f'"{t}"*' for t in terms)
        col = f"search_{lang}"
        try:
            rows = _conn.execute(
                f"SELECT payload, category FROM cmd WHERE {col} MATCH ? ORDER BY bm25(cmd) LIMIT ?",
                (fts_q, limit),
            ).fetchall()
        except sqlite3.OperationalError:
            rows = []
    results = []
    for payload, category in rows:
        entry = json.loads(payload)
        entry["category"] = category
        results.append(localize_entry(entry, lang))
    return JSONResponse({"results": results, "count": len(results), "lang": lang})


@app.get("/api/languages")
def languages():
    return {"languages": LANGS, "primary": PRIMARY}


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
