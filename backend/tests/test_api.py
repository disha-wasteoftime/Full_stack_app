import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
DATA_DIR = Path(__file__).parent.parent / "data"


def _load_raw(filename: str) -> list:
    with open(DATA_DIR / filename) as f:
        return json.load(f)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_upload_and_fetch_reconciliation():
    raw = _load_raw("sample_day1.json")
    upload_resp = client.post("/billing-log/upload", json={"records": raw})
    assert upload_resp.status_code == 201
    log_id = upload_resp.json()["log_id"]

    recon_resp = client.get(f"/reconciliation?log_id={log_id}")
    assert recon_resp.status_code == 200
    assert recon_resp.json()["total_refunds_paise"] == 49000


def test_upload_malformed_row_returns_422_not_500():
    raw = _load_raw("sample_day3.json")
    resp = client.post("/billing-log/upload", json={"records": raw})
    assert resp.status_code == 422
    assert "payment_mode" in str(resp.json())


def test_reconciliation_without_log_id_returns_400():
    resp = client.get("/reconciliation")
    assert resp.status_code == 400