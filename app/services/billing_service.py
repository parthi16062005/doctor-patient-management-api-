from datetime import datetime
from sqlalchemy.orm import Session

from app.models.billing import Billing
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.appointment import Appointment


VALID_PAYMENT_STATUS = {
    "pending",
    "paid",
    "cancelled"
}

VALID_PAYMENT_MODES = {
    "cash",
    "card",
    "upi"
}


# ==================================================
# CREATE BILLING
# ==================================================

def create_billing(
    db: Session,
    patient_id: int,
    doctor_id: int,
    appointment_id: int | None,
    consultation_fee,
    additional_charges,
    payment_status: str,
    payment_mode: str | None
):

    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    if not patient:
        raise ValueError("Patient not found")

    doctor = (
        db.query(Doctor)
        .filter(Doctor.id == doctor_id)
        .first()
    )

    if not doctor:
        raise ValueError("Doctor not found")

    if not doctor.is_active:
        raise ValueError("Doctor is inactive")

    if payment_status not in VALID_PAYMENT_STATUS:
        raise ValueError("Invalid payment status")

    if payment_mode is not None:
        if payment_mode not in VALID_PAYMENT_MODES:
            raise ValueError("Invalid payment mode")

    appointment = None

    if appointment_id is not None:

        appointment = (
            db.query(Appointment)
            .filter(Appointment.id == appointment_id)
            .first()
        )

        if not appointment:
            raise ValueError("Appointment not found")

        if appointment.doctor_id != doctor_id:
            raise ValueError(
                "Appointment does not belong to this doctor"
            )

        if appointment.patient_id != patient_id:
            raise ValueError(
                "Appointment does not belong to this patient"
            )

        if appointment.status == "cancelled":
            raise ValueError(
                "Cannot create billing for a cancelled appointment"
            )

        existing_billing = (
            db.query(Billing)
            .filter(
                Billing.appointment_id == appointment_id
            )
            .first()
        )

        if existing_billing:
            raise ValueError(
                "Billing already exists for this appointment"
            )

    total_amount = (
        consultation_fee +
        additional_charges
    )

    billing = Billing(
        patient_id=patient_id,
        doctor_id=doctor_id,
        appointment_id=appointment_id,
        consultation_fee=consultation_fee,
        additional_charges=additional_charges,
        total_amount=total_amount,
        payment_status=payment_status,
        payment_mode=payment_mode,
        is_active=True
    )

    db.add(billing)

    if appointment is not None:
        appointment.status = "completed"

    try:
        db.commit()

    except Exception:
        db.rollback()
        raise

    db.refresh(billing)

    return billing


# ==================================================
# GET BILLING BY ID
# ==================================================

def get_billing_by_id(
    db: Session,
    billing_id: int
):

    return (
        db.query(Billing)
        .filter(Billing.id == billing_id)
        .first()
    )


# ==================================================
# GET BILLINGS BY FILTERS + PAGINATION
# ==================================================

def get_billings(
    db: Session,
    payment_status: str | None = None,
    doctor_id: int | None = None,
    patient_id: int | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    page: int = 1,
    limit: int = 10
):

    query = (
        db.query(Billing)
        .filter(Billing.is_active == True)
    )

    # Payment status filter
    if payment_status is not None:
        query = query.filter(
            Billing.payment_status == payment_status
        )

    # Doctor filter
    if doctor_id is not None:
        query = query.filter(
            Billing.doctor_id == doctor_id
        )

    # Patient filter
    if patient_id is not None:
        query = query.filter(
            Billing.patient_id == patient_id
        )

    # From date filter
    if from_date is not None:
        query = query.filter(
            Billing.created_at >= from_date
        )

    # To date filter
    if to_date is not None:
        query = query.filter(
            Billing.created_at <= to_date
        )

    # Total records before pagination
    total = query.count()

    # Pagination
    offset = (page - 1) * limit

    billings = (
        query
        .order_by(Billing.id)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return total, billings


# ==================================================
# GET BILLINGS BY PATIENT
# ==================================================

def get_billings_by_patient(
    db: Session,
    patient_id: int
):

    return (
        db.query(Billing)
        .filter(
            Billing.patient_id == patient_id,
            Billing.is_active == True
        )
        .all()
    )


# ==================================================
# GET BILLINGS BY DOCTOR
# ==================================================

def get_billings_by_doctor(
    db: Session,
    doctor_id: int
):

    return (
        db.query(Billing)
        .filter(
            Billing.doctor_id == doctor_id,
            Billing.is_active == True
        )
        .all()
    )


# ==================================================
# UPDATE BILLING
# ==================================================

def update_billing(
    db: Session,
    billing: Billing,
    patient_id: int,
    doctor_id: int,
    appointment_id: int | None,
    consultation_fee,
    additional_charges,
    payment_status: str,
    payment_mode: str | None,
    is_active: bool | None = None
):

    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    if not patient:
        raise ValueError("Patient not found")

    doctor = (
        db.query(Doctor)
        .filter(Doctor.id == doctor_id)
        .first()
    )

    if not doctor:
        raise ValueError("Doctor not found")

    if not doctor.is_active:
        raise ValueError("Doctor is inactive")

    if payment_status not in VALID_PAYMENT_STATUS:
        raise ValueError("Invalid payment status")

    if payment_mode is not None:
        if payment_mode not in VALID_PAYMENT_MODES:
            raise ValueError("Invalid payment mode")

    appointment = None

    if appointment_id is not None:

        appointment = (
            db.query(Appointment)
            .filter(Appointment.id == appointment_id)
            .first()
        )

        if not appointment:
            raise ValueError("Appointment not found")

        if appointment.doctor_id != doctor_id:
            raise ValueError(
                "Appointment does not belong to this doctor"
            )

        if appointment.patient_id != patient_id:
            raise ValueError(
                "Appointment does not belong to this patient"
            )

        if appointment.status == "cancelled":
            raise ValueError(
                "Cannot bill a cancelled appointment"
            )

        existing_billing = (
            db.query(Billing)
            .filter(
                Billing.appointment_id == appointment_id,
                Billing.id != billing.id
            )
            .first()
        )

        if existing_billing:
            raise ValueError(
                "Billing already exists for this appointment"
            )

    total_amount = (
        consultation_fee +
        additional_charges
    )

    billing.patient_id = patient_id
    billing.doctor_id = doctor_id
    billing.appointment_id = appointment_id
    billing.consultation_fee = consultation_fee
    billing.additional_charges = additional_charges
    billing.total_amount = total_amount
    billing.payment_status = payment_status
    billing.payment_mode = payment_mode

    if is_active is not None:
        billing.is_active = is_active

    billing.updated_at = datetime.utcnow()

    try:
        db.commit()

    except Exception:
        db.rollback()
        raise

    db.refresh(billing)

    return billing


# ==================================================
# DELETE BILLING - SOFT DELETE
# ==================================================

def delete_billing(
    db: Session,
    billing: Billing
):

    billing.is_active = False
    billing.updated_at = datetime.utcnow()

    try:
        db.commit()

    except Exception:
        db.rollback()
        raise

    db.refresh(billing)

    return billing