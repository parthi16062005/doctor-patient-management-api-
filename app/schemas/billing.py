from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BillingCreate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_id: int | None = None

    consultation_fee: Decimal = Field(
        ge=0,
        max_digits=10,
        decimal_places=2
    )

    additional_charges: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        max_digits=10,
        decimal_places=2
    )

    payment_status: str = "pending"
    payment_mode: str | None = None


class BillingUpdate(BaseModel):
    patient_id: int | None = None
    doctor_id: int | None = None
    appointment_id: int | None = None

    consultation_fee: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=10,
        decimal_places=2
    )

    additional_charges: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=10,
        decimal_places=2
    )

    payment_status: str | None = None
    payment_mode: str | None = None
    is_active: bool | None = None


class BillingResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_id: int | None

    consultation_fee: Decimal
    additional_charges: Decimal
    total_amount: Decimal

    payment_status: str
    payment_mode: str | None

    is_active: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )