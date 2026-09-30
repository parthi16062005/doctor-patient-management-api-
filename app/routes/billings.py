from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db

from app.models.billing import Billing
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.user import User

from app.schemas.billing import (
    BillingCreate,
    BillingUpdate,
    BillingResponse
)

from app.dependencies import (
    get_current_user,
    admin_required
)

from app.services.billing_service import (
    create_billing,
    get_billing_by_id,
    get_billings,
    update_billing,
    delete_billing
)


router = APIRouter(
    prefix="/billings",
    tags=["Billings"]
)


# ============================================================
# CREATE BILLING
# ============================================================

@router.post(
    "/",
    response_model=BillingResponse,
    status_code=201,
    summary="Create a billing record",
    description="""
Create a new billing record.

Only administrators can create billing records.

Rules:
- Patient must exist.
- Doctor must exist.
- Doctor must be active.
- If appointment is provided, it must belong to the same doctor and patient.
- Cancelled appointments cannot be billed.
- Only one billing record can exist for an appointment.
- total_amount is calculated automatically.

total_amount = consultation_fee + additional_charges

If an appointment is provided, its status is changed to completed
in the same database transaction.
""",
    responses={
        201: {
            "description": "Billing record created successfully"
        },
        400: {
            "description": "Invalid billing data"
        },
        403: {
            "description": "Admin access required"
        }
    }
)
def create_billing_api(
    billing: BillingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    try:
        return create_billing(
            db=db,
            patient_id=billing.patient_id,
            doctor_id=billing.doctor_id,
            appointment_id=billing.appointment_id,
            consultation_fee=billing.consultation_fee,
            additional_charges=billing.additional_charges,
            payment_status=billing.payment_status,
            payment_mode=billing.payment_mode
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Unable to create billing. Please check the provided data."
        )


# ============================================================
# GET ALL BILLINGS
# ============================================================

@router.get(
    "/",
    response_model=list[BillingResponse],
    summary="Get billings with filters and pagination",
    description="""
Retrieve active billing records.

Supported filters:
- payment_status
- doctor_id
- patient_id
- from_date
- to_date

Pagination:
- page
- limit

Administrators can view billing records for all doctors and patients.

Doctors can only view billing records related to their assigned patients.
""",
    responses={
        200: {
            "description": "Billing records retrieved successfully"
        },
        400: {
            "description": "Invalid filter values"
        },
        403: {
            "description": "Doctor access denied"
        }
    }
)
def get_all_billings(
    payment_status: str | None = Query(
        default=None,
        description="Filter by payment status: pending, paid, cancelled"
    ),
    doctor_id: int | None = Query(
        default=None,
        ge=1,
        description="Filter by doctor ID"
    ),
    patient_id: int | None = Query(
        default=None,
        ge=1,
        description="Filter by patient ID"
    ),
    from_date: datetime | None = Query(
        default=None,
        description="Return billings created on or after this date"
    ),
    to_date: datetime | None = Query(
        default=None,
        description="Return billings created on or before this date"
    ),
    page: int = Query(
        default=1,
        ge=1,
        description="Page number"
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of records per page"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    valid_payment_status = {
        "pending",
        "paid",
        "cancelled"
    }

    if (
        payment_status is not None
        and payment_status not in valid_payment_status
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid payment status"
        )

    if (
        from_date is not None
        and to_date is not None
        and from_date > to_date
    ):
        raise HTTPException(
            status_code=400,
            detail="from_date cannot be greater than to_date"
        )

    # Doctor can only view their own billing records.
    if current_user.role == "doctor":

        doctor = (
            db.query(Doctor)
            .filter(
                Doctor.email == current_user.username
            )
            .first()
        )

        if not doctor:
            raise HTTPException(
                status_code=403,
                detail="Doctor access denied"
            )

        if (
            doctor_id is not None
            and doctor_id != doctor.id
        ):
            raise HTTPException(
                status_code=403,
                detail="You can only view your own billing records"
            )

        doctor_id = doctor.id

    total, billings = get_billings(
        db=db,
        payment_status=payment_status,
        doctor_id=doctor_id,
        patient_id=patient_id,
        from_date=from_date,
        to_date=to_date,
        page=page,
        limit=limit
    )

    return billings


# ============================================================
# GET BILLING BY ID
# ============================================================

@router.get(
    "/{billing_id}",
    response_model=BillingResponse,
    summary="Get billing by ID",
    description="""
Retrieve a billing record using its ID.

Administrators can view any billing record.

Doctors can only view billing records related to their patients.
""",
    responses={
        200: {
            "description": "Billing record found"
        },
        403: {
            "description": "Doctor access denied"
        },
        404: {
            "description": "Billing record not found"
        }
    }
)
def get_billing_api(
    billing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    billing = get_billing_by_id(
        db=db,
        billing_id=billing_id
    )

    if not billing:
        raise HTTPException(
            status_code=404,
            detail="Billing not found"
        )

    # Doctor can only view billing records
    # belonging to their assigned patients.
    if current_user.role == "doctor":

        doctor = (
            db.query(Doctor)
            .filter(
                Doctor.email == current_user.username
            )
            .first()
        )

        if not doctor:
            raise HTTPException(
                status_code=403,
                detail="Doctor access denied"
            )

        if (
            billing.doctor_id != doctor.id
            and billing.patient_id is not None
        ):
            raise HTTPException(
                status_code=403,
                detail="You can only view billing records for your patients"
            )

    return billing


# ============================================================
# GET BILLINGS BY PATIENT
# ============================================================

@router.get(
    "/patients/{patient_id}/billings",
    response_model=list[BillingResponse],
    summary="Get billings by patient",
    description="""
Retrieve active billing records belonging to a patient.

Supports pagination using page and limit.

Administrators can view any patient's billing records.

Doctors can view billing records only for their assigned patients.
""",
    responses={
        200: {
            "description": "Patient billing records"
        },
        403: {
            "description": "Doctor access denied"
        },
        404: {
            "description": "Patient not found"
        }
    }
)
def get_patient_billings(
    patient_id: int,
    page: int = Query(
        default=1,
        ge=1,
        description="Page number"
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of records per page"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    if current_user.role == "doctor":

        doctor = (
            db.query(Doctor)
            .filter(
                Doctor.email == current_user.username
            )
            .first()
        )

        if not doctor:
            raise HTTPException(
                status_code=403,
                detail="Doctor access denied"
            )

        if patient.doctor_id != doctor.id:
            raise HTTPException(
                status_code=403,
                detail="You can only view billings for your patients"
            )

    _, billings = get_billings(
        db=db,
        patient_id=patient_id,
        page=page,
        limit=limit
    )

    return billings


# ============================================================
# GET BILLINGS BY DOCTOR
# ============================================================

@router.get(
    "/doctors/{doctor_id}/billings",
    response_model=list[BillingResponse],
    summary="Get billings by doctor",
    description="""
Retrieve active billing records belonging to a doctor.

Supports pagination using page and limit.

Administrators can view any doctor's billing records.

Doctors can view only their own billing records.
""",
    responses={
        200: {
            "description": "Doctor billing records"
        },
        403: {
            "description": "Doctor access denied"
        },
        404: {
            "description": "Doctor not found"
        }
    }
)
def get_doctor_billings(
    doctor_id: int,
    page: int = Query(
        default=1,
        ge=1,
        description="Page number"
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of records per page"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doctor = (
        db.query(Doctor)
        .filter(Doctor.id == doctor_id)
        .first()
    )

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    if current_user.role == "doctor":

        if current_user.username != doctor.email:
            raise HTTPException(
                status_code=403,
                detail="You can only view your own billing records"
            )

    _, billings = get_billings(
        db=db,
        doctor_id=doctor_id,
        page=page,
        limit=limit
    )

    return billings


# ============================================================
# UPDATE BILLING
# ============================================================

@router.put(
    "/{billing_id}",
    response_model=BillingResponse,
    summary="Update a billing record",
    description="""
Update an existing billing record.

Only administrators can update billing records.

The total amount is recalculated automatically.
""",
    responses={
        200: {
            "description": "Billing updated successfully"
        },
        400: {
            "description": "Invalid billing data"
        },
        403: {
            "description": "Admin access required"
        },
        404: {
            "description": "Billing, patient, doctor, or appointment not found"
        }
    }
)
def update_billing_api(
    billing_id: int,
    billing_data: BillingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    billing = get_billing_by_id(
        db=db,
        billing_id=billing_id
    )

    if not billing:
        raise HTTPException(
            status_code=404,
            detail="Billing not found"
        )

    patient_id = (
        billing_data.patient_id
        if billing_data.patient_id is not None
        else billing.patient_id
    )

    doctor_id = (
        billing_data.doctor_id
        if billing_data.doctor_id is not None
        else billing.doctor_id
    )

    appointment_id = (
        billing_data.appointment_id
        if billing_data.appointment_id is not None
        else billing.appointment_id
    )

    consultation_fee = (
        billing_data.consultation_fee
        if billing_data.consultation_fee is not None
        else billing.consultation_fee
    )

    additional_charges = (
        billing_data.additional_charges
        if billing_data.additional_charges is not None
        else billing.additional_charges
    )

    payment_status = (
        billing_data.payment_status
        if billing_data.payment_status is not None
        else billing.payment_status
    )

    payment_mode = (
        billing_data.payment_mode
        if billing_data.payment_mode is not None
        else billing.payment_mode
    )

    try:

        return update_billing(
            db=db,
            billing=billing,
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_id=appointment_id,
            consultation_fee=consultation_fee,
            additional_charges=additional_charges,
            payment_status=payment_status,
            payment_mode=payment_mode,
            is_active=billing_data.is_active
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Unable to update billing. Please check the provided data."
        )


# ============================================================
# PATCH BILLING
# ============================================================

@router.patch(
    "/{billing_id}",
    response_model=BillingResponse,
    summary="Partially update a billing record",
    description="""
Partially update an existing billing record.

Only administrators can update billing records.

Only the fields provided in the request are changed.

The total amount is recalculated automatically.
""",
    responses={
        200: {
            "description": "Billing partially updated successfully"
        },
        400: {
            "description": "Invalid billing data"
        },
        403: {
            "description": "Admin access required"
        },
        404: {
            "description": "Billing not found"
        }
    }
)
def patch_billing_api(
    billing_id: int,
    billing_data: BillingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    billing = get_billing_by_id(
        db=db,
        billing_id=billing_id
    )

    if not billing:
        raise HTTPException(
            status_code=404,
            detail="Billing not found"
        )

    patient_id = (
        billing_data.patient_id
        if billing_data.patient_id is not None
        else billing.patient_id
    )

    doctor_id = (
        billing_data.doctor_id
        if billing_data.doctor_id is not None
        else billing.doctor_id
    )

    appointment_id = (
        billing_data.appointment_id
        if billing_data.appointment_id is not None
        else billing.appointment_id
    )

    consultation_fee = (
        billing_data.consultation_fee
        if billing_data.consultation_fee is not None
        else billing.consultation_fee
    )

    additional_charges = (
        billing_data.additional_charges
        if billing_data.additional_charges is not None
        else billing.additional_charges
    )

    payment_status = (
        billing_data.payment_status
        if billing_data.payment_status is not None
        else billing.payment_status
    )

    payment_mode = (
        billing_data.payment_mode
        if billing_data.payment_mode is not None
        else billing.payment_mode
    )

    try:

        return update_billing(
            db=db,
            billing=billing,
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_id=appointment_id,
            consultation_fee=consultation_fee,
            additional_charges=additional_charges,
            payment_status=payment_status,
            payment_mode=payment_mode,
            is_active=billing_data.is_active
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Unable to update billing."
        )


# ============================================================
# SOFT DELETE BILLING
# ============================================================

@router.delete(
    "/{billing_id}",
    response_model=BillingResponse,
    summary="Soft delete a billing record",
    description="""
Soft delete a billing record.

Only administrators can delete billing records.

The record is not physically removed from the database.

The is_active field is changed to false.
""",
    responses={
        200: {
            "description": "Billing soft deleted successfully"
        },
        403: {
            "description": "Admin access required"
        },
        404: {
            "description": "Billing not found"
        }
    }
)
def delete_billing_api(
    billing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    billing = get_billing_by_id(
        db=db,
        billing_id=billing_id
    )

    if not billing:
        raise HTTPException(
            status_code=404,
            detail="Billing not found"
        )

    try:

        return delete_billing(
            db=db,
            billing=billing
        )

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Unable to delete billing."
        )