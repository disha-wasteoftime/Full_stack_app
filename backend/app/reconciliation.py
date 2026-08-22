"""
Deterministic reconciliation engine.

This module NEVER calls an LLM. It is the ground truth that the narrative
layer (Step 5) will later be checked against.
"""

from collections import defaultdict

from app.models import BillingLog, PaymentMode


def _empty_mode_breakdown() -> dict[str, int]:
    return {mode.value: 0 for mode in PaymentMode}


def compute_reconciliation(log: BillingLog) -> dict:
    """
    Compute total billed, total collected, outstanding, and refunds,
    each split by payment mode. All amounts in integer paise.
    """
    billed_by_mode = _empty_mode_breakdown()
    collected_by_mode = _empty_mode_breakdown()
    outstanding_by_mode = _empty_mode_breakdown()
    refunds_by_mode = _empty_mode_breakdown()

    total_visits = 0
    refund_visits = 0
    outstanding_visits = 0

    for record in log.records:
        mode = record.payment_mode.value
        total_visits += 1

        if record.is_refund:
            refund_visits += 1
            refunds_by_mode[mode] += abs(record.amount_paid_paise)
            continue

        billed = record.billed_amount_paise
        collected = record.amount_paid_paise
        outstanding = billed - collected

        billed_by_mode[mode] += billed
        collected_by_mode[mode] += collected

        if outstanding > 0:
            outstanding_visits += 1
            outstanding_by_mode[mode] += outstanding

    total_billed = sum(billed_by_mode.values())
    total_collected = sum(collected_by_mode.values())
    total_outstanding = sum(outstanding_by_mode.values())
    total_refunds = sum(refunds_by_mode.values())

    return {
        "total_visits": total_visits,
        "total_billed_paise": total_billed,
        "total_collected_paise": total_collected,
        "total_outstanding_paise": total_outstanding,
        "total_refunds_paise": total_refunds,
        "outstanding_visit_count": outstanding_visits,
        "refund_visit_count": refund_visits,
        "collected_pct_of_billed": (
            round(100 * total_collected / total_billed, 1) if total_billed > 0 else 0.0
        ),
        "by_payment_mode": {
            mode.value: {
                "billed_paise": billed_by_mode[mode.value],
                "collected_paise": collected_by_mode[mode.value],
                "outstanding_paise": outstanding_by_mode[mode.value],
                "refunds_paise": refunds_by_mode[mode.value],
            }
            for mode in PaymentMode
        },
    }