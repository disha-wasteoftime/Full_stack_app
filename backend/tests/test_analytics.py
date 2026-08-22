from app.analytics import compute_analytics
from tests.test_reconciliation import load_log


def test_all_refunds_day_has_no_revenue():
    """On a day with only refunds, there's no actual revenue or medicine
    sales — peak_hour should be None, not a misleading default."""
    log = load_log("sample_day1.json")
    result = compute_analytics(log)

    assert result["peak_hour"] is None
    assert all(h["revenue_paise"] == 0 for h in result["revenue_by_hour"])
    assert result["top_medicines_by_quantity"] == []
    assert result["top_medicines_by_revenue"] == []

def test_empty_day_has_no_analytics():
    log = load_log("sample_day2.json")
    result = compute_analytics(log)

    assert result["peak_hour"] is None
    assert all(h["revenue_paise"] == 0 for h in result["revenue_by_hour"])
    assert result["top_medicines_by_quantity"] == []