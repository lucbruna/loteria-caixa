import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json

from app import app


def test_index_returns_html():
    with app.test_client() as c:
        resp = c.get("/")
    assert resp.status_code == 200
    assert resp.content_type.startswith("text/html")


def test_mobile_returns_html():
    with app.test_client() as c:
        resp = c.get("/mobile")
    assert resp.status_code == 200


def test_lottery_not_found_404():
    with app.test_client() as c:
        resp = c.get("/api/analise/loteria_invalida")
    assert resp.status_code == 404
    data = json.loads(resp.data)
    assert "erro" in data


def test_security_headers_present():
    with app.test_client() as c:
        resp = c.get("/")
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert resp.headers.get("X-Frame-Options") == "DENY"
    assert resp.headers.get("Content-Security-Policy") is not None
