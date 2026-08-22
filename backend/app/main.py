"""
SwasthiQ EOD Billing & Analytics Agent — FastAPI entrypoint.

Run locally with:
    uvicorn app.main:app --reload
"""
from dotenv import load_dotenv
load_dotenv()
from app.narrative import generate_narrative
from datetime import date

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.analytics import compute_analytics
from app.models import BillingLog
from app.reconciliation import compute_reconciliation
from app.storage import get_log, get_log_by_clinic_date, list_logs, save_log

app = FastAPI(
    title="SwasthiQ EOD Billing & Analytics Agent",
    description="Ingests a clinic's daily billing log and produces a "
    "reconciliation report, analytics, and an LLM-grounded narrative summary.",
    version="0.1.0",
)

# Allow the React frontend (running on a different port/domain) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your deployed frontend URL before submission
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "swasthiq-eod-agent"}


@app.post("/billing-log/upload", status_code=201)
def upload_billing_log(log: BillingLog):
    """
    Ingest a clinic's daily billing log.

    Pydantic validates the request body against BillingLog automatically.
    Any malformed row (missing field, wrong type, refund-sign mismatch,
    multiple clinics in one file) results in a 422 response listing the
    exact field and reason — not a generic 500.
    """
    log_id = save_log(log)
    return {
        "log_id": log_id,
        "visit_count": len(log.records),
        "clinic_id": log.records[0].clinic_id if log.records else None,
    }


@app.get("/billing-logs")
def get_billing_logs():
    """List uploaded logs — used to populate a date picker in the frontend."""
    return {"logs": list_logs()}


def _resolve_log(log_id: str | None, clinic_id: str | None, log_date: date | None) -> BillingLog:
    if log_id:
        log = get_log(log_id)
    elif clinic_id and log_date:
        log = get_log_by_clinic_date(clinic_id, log_date)
    else:
        raise HTTPException(
            status_code=400,
            detail="Provide either log_id, or both clinic_id and date as query params.",
        )

    if log is None:
        raise HTTPException(status_code=404, detail="No billing log found for that reference.")
    return log


@app.get("/reconciliation")
def get_reconciliation(
    log_id: str | None = None, clinic_id: str | None = None, log_date: date | None = None
):
    log = _resolve_log(log_id, clinic_id, log_date)
    return compute_reconciliation(log)


@app.get("/analytics")
def get_analytics(
    log_id: str | None = None, clinic_id: str | None = None, log_date: date | None = None
):
    log = _resolve_log(log_id, clinic_id, log_date)
    return compute_analytics(log)

@app.get("/narrative")
def get_narrative(
    log_id: str | None = None, clinic_id: str | None = None, log_date: date | None = None
):
    log = _resolve_log(log_id, clinic_id, log_date)
    reconciliation = compute_reconciliation(log)
    analytics = compute_analytics(log)
    combined_report = {**reconciliation, **analytics}
    return generate_narrative(combined_report)