"""
Pydantic models for the billing log schema.

These models are the single source of truth for validation. FastAPI will
automatically reject any malformed request with a clear 422 error listing
exactly which field failed and why — no generic 500s.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator


class PaymentMode(str, Enum):
    CASH = "cash"
    CARD = "card"
    UPI = "upi"


class LineItem(BaseModel):
    drug_name: str = Field(..., min_length=1)
    qty: int = Field(..., gt=0, description="Quantity must be a positive integer")
    unit_price_paise: int = Field(..., ge=0, description="Price in integer paise, must be >= 0")

    @field_validator("drug_name")
    @classmethod
    def normalize_drug_name(cls, v: str) -> str:
        # Normalize casing so "Paracetamol" and "PARACETAMOL" are treated
        # as the same drug in analytics rankings.
        return v.strip().upper()


class BillingRecord(BaseModel):
    clinic_id: str = Field(..., min_length=1)
    visit_id: str = Field(..., min_length=1)
    timestamp: datetime
    doctor_id: str = Field(..., min_length=1)
    line_items: list[LineItem] = Field(..., min_length=1)
    payment_mode: PaymentMode
    amount_paid_paise: int
    discount_paise: int = Field(default=0, ge=0)
    is_refund: bool

    @model_validator(mode="after")
    def check_refund_sign_consistency(self) -> "BillingRecord":
        """
        Business rule from the spec: if is_refund is true, amount_paid_paise
        must be a negative adjustment. If false, it must not be negative.
        Catching this here gives a specific, actionable error instead of
        silently producing wrong reconciliation numbers downstream.
        """
        if self.is_refund and self.amount_paid_paise >= 0:
            raise ValueError(
                f"visit_id={self.visit_id}: is_refund is true but "
                f"amount_paid_paise ({self.amount_paid_paise}) is not negative"
            )
        if not self.is_refund and self.amount_paid_paise < 0:
            raise ValueError(
                f"visit_id={self.visit_id}: is_refund is false but "
                f"amount_paid_paise ({self.amount_paid_paise}) is negative"
            )
        return self

    @property
    def billed_amount_paise(self) -> int:
        """
        Gross billed amount for this visit: sum(qty * unit_price) - discount.
        Confirmed against the sample data (e.g. visit V-20260725-001:
        2 * 12000 - 0 = 24000, matching the refunded amount exactly).
        """
        gross = sum(item.qty * item.unit_price_paise for item in self.line_items)
        return gross - self.discount_paise


class BillingLog(BaseModel):
    """A full day's billing log: a list of records for a single clinic."""
    records: list[BillingRecord]

    @model_validator(mode="after")
    def check_single_clinic(self) -> "BillingLog":
        clinic_ids = {r.clinic_id for r in self.records}
        if len(clinic_ids) > 1:
            raise ValueError(
                f"Billing log must contain a single clinic per file, found: {clinic_ids}"
            )
        return self