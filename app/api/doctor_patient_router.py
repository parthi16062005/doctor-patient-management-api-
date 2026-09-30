from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.user import User

from app.schemas.patient import PatientResponse

from app.dependencies import (
    get_current_user,
    admin_required
)


router = APIRouter(
    prefix="/doctor-patient",
    tags=["Doctor-Patient"]
)


# ==================================================
# ASSIGN PATIENT TO DOCTOR
# ==================================================

@router.post(
    "/{doctor_id}/patients/{patient_id}",
    response_model=PatientResponse,
    status_code=200
)
def assign_patient(
    doctor_id: int,
    patient_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        admin_required
    )
):

    # Check doctor exists
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    # Check doctor is active
    if not doctor.is_active:
        raise HTTPException(
            status_code=400,
            detail="Cannot assign patient to an inactive doctor"
        )

    # Check patient exists
    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    # Assign patient
    patient.doctor_id = doctor_id

    db.commit()
    db.refresh(patient)

    return patient


# ==================================================
# GET PATIENTS OF A DOCTOR
# ==================================================

@router.get(
    "/{doctor_id}/patients",
    response_model=list[PatientResponse]
)
def get_doctor_patients(
    doctor_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # Check doctor exists
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    # Check doctor is active
    if not doctor.is_active:
        raise HTTPException(
            status_code=400,
            detail="Doctor is inactive"
        )

    # Admin can view any doctor's patients
    if current_user.role == "admin":

        return db.query(Patient).filter(
            Patient.doctor_id == doctor_id
        ).all()

    # Doctor can view only their own patients
    if current_user.username != doctor.email:

        raise HTTPException(
            status_code=403,
            detail="You can only view your own patients"
        )

    return db.query(Patient).filter(
        Patient.doctor_id == doctor_id
    ).all()