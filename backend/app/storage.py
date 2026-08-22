"""
In-memory storage for uploaded billing logs.

Kept as a simple, isolated module so swapping this for SQLite later
only requires changing this file — nothing in reconciliation.py,
analytics.py, or the API routes needs to change.
"""

import uuid
from datetime import date

from app.models import BillingLog

# log_id -> BillingLog
_logs: dict[str, BillingLog] = {}
# (clinic_id, date) -> log_id, for lookup by day
_by_clinic_date: dict[tuple[str, date], str] = {}


def save_log(log: BillingLog) -> str:
    log_id = str(uuid.uuid4())
    _logs[log_id] = log

    if log.records:
        clinic_id = log.records[0].clinic_id
        log_date = log.records[0].timestamp.date()
        _by_clinic_date[(clinic_id, log_date)] = log_id

    return log_id


def get_log(log_id: str) -> BillingLog | None:
    return _logs.get(log_id)


def get_log_by_clinic_date(clinic_id: str, log_date: date) -> BillingLog | None:
    log_id = _by_clinic_date.get((clinic_id, log_date))
    return _logs.get(log_id) if log_id else None


def list_logs() -> list[dict]:
    """Summary list for populating a date-picker/sidebar in the frontend."""
    result = []
    for log_id, log in _logs.items():
        if not log.records:
            result.append({"log_id": log_id, "clinic_id": None, "date": None, "visit_count": 0})
            continue
        result.append(
            {
                "log_id": log_id,
                "clinic_id": log.records[0].clinic_id,
                "date": log.records[0].timestamp.date().isoformat(),
                "visit_count": len(log.records),
            }
        )
    return result