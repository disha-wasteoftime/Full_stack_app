import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.models import BillingLog
from app.reconciliation import compute_reconciliation

DATA_DIR = Path(__file__).parent.parent / "data"


def load_log(filename: str) -> BillingLog:
    with open(DATA_DIR / filename) as f:
        raw = json.load(f)
    return BillingLog(records=raw)


def test_all_refunds_day():
    """
    sample_day1.json is our non-happy-path day: every visit is a refund.
    Billed/collected should be zero; refunds should equal the sum of
    the three refunded amounts.
    """
    log = load_log("sample_day1.json")
    result = compute_reconciliation(log)

    assert result["total_visits"] == 3
    assert result["refund_visit_count"] == 3
    assert result["total_billed_paise"] == 0
    assert result["total_collected_paise"] == 0
    assert result["total_outstanding_paise"] == 0
    # 24000 + 22000 + 3000
    assert result["total_refunds_paise"] == 49000

    assert result["by_payment_mode"]["card"]["refunds_paise"] == 24000
    assert result["by_payment_mode"]["upi"]["refunds_paise"] == 25000  # 22000 + 3000
    assert result["by_payment_mode"]["cash"]["refunds_paise"] == 0

def test_empty_day_has_zero_everything():
    """sample_day2.json is an empty log (zero visits) — must not crash,
    should return clean zeros."""
    log = load_log("sample_day2.json")
    result = compute_reconciliation(log)

    assert result["total_visits"] == 0
    assert result["total_billed_paise"] == 0
    assert result["total_collected_paise"] == 0
    assert result["collected_pct_of_billed"] == 0.0


def test_malformed_row_is_rejected_with_specific_error():
    """sample_day3.json has one visit (V-20260727-019) missing
    payment_mode. The whole log should be rejected with an error that
    points at the specific field, not a generic crash."""
    with open(DATA_DIR / "sample_day3.json") as f:
        raw = json.load(f)

    with pytest.raises(ValidationError) as exc_info:
        BillingLog(records=raw)

    errors = exc_info.value.errors()
    assert any(
        "payment_mode" in str(e["loc"]) and e["type"] == "missing"
        for e in errors
    )