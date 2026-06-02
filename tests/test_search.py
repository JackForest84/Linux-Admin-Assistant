"""Unit tests for linuxcmd search backend.

Run from the repo root:
    pip install -r app/requirements.txt -r requirements-dev.txt
    pytest
"""
from fastapi.testclient import TestClient

from app.main import (
    MAX_LIMIT,
    build_db,
    get_lang_field,
    strip_diacritics,
    app,
)


def test_strip_diacritics():
    assert strip_diacritics("MÍSTO") == "misto"
    assert strip_diacritics("Voľné") == "volne"
    # Combining diacritics are stripped; ß has no NFKD decomposition so it stays.
    assert strip_diacritics("Größe") == "große"
    assert strip_diacritics("ücretsiz") == "ucretsiz"
    assert strip_diacritics("Zürich") == "zurich"


def test_get_lang_field_direct_and_fallback():
    entry = {"title": {"en": "Free space", "cs": "Volné místo"}}
    assert get_lang_field(entry, "title", "cs") == "Volné místo"
    assert get_lang_field(entry, "title", "en") == "Free space"
    # Missing language falls back to primary (en).
    assert get_lang_field(entry, "title", "tr") == "Free space"
    # Missing field returns empty string, tags returns empty list.
    assert get_lang_field(entry, "title", "xx") == "Free space"
    assert get_lang_field({}, "tags", "en") == []


def test_build_db_has_rows():
    conn = build_db()
    try:
        count = conn.execute("SELECT COUNT(*) FROM cmd").fetchone()[0]
        assert count > 100  # we ship 150+ entries
    finally:
        conn.close()


def test_search_returns_results_per_language():
    with TestClient(app) as client:
        for lang in ("en", "cs", "de", "tr"):
            r = client.get("/api/search", params={"q": "disk", "lang": lang})
            assert r.status_code == 200
            data = r.json()
            assert data["lang"] == lang
            assert data["count"] > 0
            assert data["results"][0]["title"]


def test_unknown_language_falls_back_to_en():
    with TestClient(app) as client:
        r = client.get("/api/search", params={"q": "disk", "lang": "zz"})
        assert r.status_code == 200
        assert r.json()["lang"] == "en"


def test_limit_is_clamped():
    with TestClient(app) as client:
        r = client.get("/api/search", params={"q": "", "limit": 999999})
        assert r.status_code == 200
        assert r.json()["count"] <= MAX_LIMIT


def test_empty_query_lists_entries():
    with TestClient(app) as client:
        r = client.get("/api/search", params={"q": "", "limit": 5})
        assert r.status_code == 200
        assert r.json()["count"] == 5


def test_categories_endpoint():
    with TestClient(app) as client:
        r = client.get("/api/categories")
        assert r.status_code == 200
        cats = r.json()["categories"]
        assert len(cats) == 36
