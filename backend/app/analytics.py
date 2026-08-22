"""
Deterministic analytics engine.

Like reconciliation.py, this module NEVER calls an LLM — it's ground truth.
"""

from collections import defaultdict

from app.models import BillingLog


def compute_analytics(log: BillingLog) -> dict:
    """
    Compute revenue by hour-of-day, top medicines by quantity, and
    top medicines by revenue (as two distinct rankings).

    Refund visits are excluded from revenue/medicine analytics since they
    represent money going back out, not medicines actually sold that day.
    """
    revenue_by_hour: dict[int, int] = defaultdict(int)
    qty_by_drug: dict[str, int] = defaultdict(int)
    revenue_by_drug: dict[str, int] = defaultdict(int)

    for record in log.records:
        if record.is_refund:
            continue

        hour = record.timestamp.hour
        revenue_by_hour[hour] += record.billed_amount_paise

        for item in record.line_items:
            qty_by_drug[item.drug_name] += item.qty
            revenue_by_drug[item.drug_name] += item.qty * item.unit_price_paise

    # Build a full 0-23 hour series (0 for hours with no business) so the
    # frontend chart doesn't have gaps.
    hourly_series = [
        {"hour": h, "revenue_paise": revenue_by_hour.get(h, 0)} for h in range(24)
    ]

    peak_hour_entry = max(hourly_series, key=lambda x: x["revenue_paise"])
    peak_hour = (
        {"hour": peak_hour_entry["hour"], "revenue_paise": peak_hour_entry["revenue_paise"]}
        if peak_hour_entry["revenue_paise"] > 0
        else None
    )

    top_by_quantity = sorted(
        ({"drug_name": k, "qty": v} for k, v in qty_by_drug.items()),
        key=lambda x: x["qty"],
        reverse=True,
    )
    top_by_revenue = sorted(
        ({"drug_name": k, "revenue_paise": v} for k, v in revenue_by_drug.items()),
        key=lambda x: x["revenue_paise"],
        reverse=True,
    )

    return {
        "revenue_by_hour": hourly_series,
        "peak_hour": peak_hour,
        "top_medicines_by_quantity": top_by_quantity,
        "top_medicines_by_revenue": top_by_revenue,
    }