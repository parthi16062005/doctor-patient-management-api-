from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String,
    ForeignKey,
    Numeric,
    Boolean,
    CheckConstraint,
    UniqueConstraint
)

from app.database import Base


class Billing(Base):

    __tablename__ = "billings"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    patient_id = Column(
        Integer,
        ForeignKey("patients.id"),
        nullable=False,
        index=True
    )

    doctor_id = Column(
        Integer,
        ForeignKey("doctors.id"),
        nullable=False,
        index=True
    )

    appointment_id = Column(
        Integer,
        ForeignKey("appointments.id"),
        nullable=True,
        unique=True,
        index=True
    )

    consultation_fee = Column(
        Numeric(10, 2),
        nullable=False
    )

    additional_charges = Column(
        Numeric(10, 2),
        nullable=False,
        default=0
    )

    total_amount = Column(
        Numeric(10, 2),
        nullable=False
    )

    payment_status = Column(
        String,
        nullable=False,
        default="pending"
    )

    payment_mode = Column(
        String,
        nullable=True
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    __table_args__ = (

        CheckConstraint(
            "consultation_fee >= 0",
            name="ck_billings_consultation_fee_non_negative"
        ),

        CheckConstraint(
            "additional_charges >= 0",
            name="ck_billings_additional_charges_non_negative"
        ),

        CheckConstraint(
            "total_amount >= 0",
            name="ck_billings_total_amount_non_negative"
        ),

        CheckConstraint(
            "payment_status IN ('pending', 'paid', 'cancelled')",
            name="ck_billings_payment_status"
        ),

        CheckConstraint(
            "payment_mode IS NULL OR payment_mode IN ('cash', 'card', 'upi')",
            name="ck_billings_payment_mode"
        ),

        UniqueConstraint(
            "appointment_id",
            name="uq_billings_appointment_id"
        )
    )