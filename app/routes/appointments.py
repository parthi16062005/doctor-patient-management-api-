from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.user import User

from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse
)

from app.dependencies import (
    get_current_user,
    admin_required
)

from app.services.appointment_service import (
    create_appointment,
    get_appointment_by_id,
    get_appointments,
    get_appointments_by_doctor,
    get_appointments_by_patient,
    update_appointment,
    delete_appointment
)


router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)


@router.post(
    "/",
    response_model=AppointmentResponse,
    status_code=201,
    summary="Create an appointment",
    description="""
Create a new appointment.

Only administrators can create appointments.

The doctor must exist and be active.
The patient must exist.
The appointment status must be scheduled, completed, or cancelled.
A doctor cannot have two scheduled appointments at the same time.
""",
    responses={
        201: {
            "description": "Appointment created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 10,
                        "doctor_id": 2,
                        "patient_id": 4,
                        "appointment_date": "2030-06-20T10:00:00",
                        "status": "scheduled"
                    }
                }
            }
        },
        400: {
            "description": "Invalid status, inactive doctor, or appointment conflict"
        },
        404: {
            "description": "Doctor or patient not found"
        },
        403: {
            "description": "Admin access required"
        }
    }
)
def create_appointment_api(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):

    if appointment.status not in [
        "scheduled",
        "completed",
        "cancelled"
    ]:
        raise HTTPException(
            status_code=400,
            detail="Invalid appointment status"
        )

    doctor = (
        db.query(Doctor)
        .filter(Doctor.id == appointment.doctor_id)
        .first()
    )

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    if not doctor.is_active:
        raise HTTPException(
            status_code=400,
            detail="Cannot create appointment for an inactive doctor"
        )

    patient = (
        db.query(Patient)
        .filter(Patient.id == appointment.patient_id)
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    existing_appointment = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == appointment.doctor_id,
            Appointment.appointment_date == appointment.appointment_date,
            Appointment.status == "scheduled"
        )
        .first()
    )

    if existing_appointment:
        raise HTTPException(
            status_code=400,
            detail="Doctor already has an appointment at this time"
        )

    try:

        return create_appointment(
            db=db,
            doctor_id=appointment.doctor_id,
            patient_id=appointment.patient_id,
            appointment_date=appointment.appointment_date,
            status=appointment.status,
            user_id=current_user.id
        )

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Unable to create appointment. Please check the provided data."
        )


@router.get(
    "/",
    response_model=list[AppointmentResponse],
    summary="Get all appointments",
    description="""
Retrieve all appointments in the system.

Authenticated users can access this endpoint.
""",
    responses={
        200: {
            "description": "List of appointments",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "doctor_id": 2,
                            "patient_id": 4,
                            "appointment_date": "2030-06-20T10:00:00",
                            "status": "scheduled"
                        }
                    ]
                }
            }
        }
    }
)
def get_appointments_api(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    _, appointments = get_appointments(
        db=db
    )

    return appointments


@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    summary="Get appointment by ID",
    description="""
Retrieve a single appointment using its ID.
""",
    responses={
        200: {
            "description": "Appointment found",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "doctor_id": 2,
                        "patient_id": 4,
                        "appointment_date": "2030-06-20T10:00:00",
                        "status": "scheduled"
                    }
                }
            }
        },
        404: {
            "description": "Appointment not found"
        }
    }
)
def get_appointment_api(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    appointment = get_appointment_by_id(
        db=db,
        appointment_id=appointment_id
    )

    if not appointment:

        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    return appointment


@router.put(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    summary="Update an appointment",
    description="""
Update an existing appointment.

Only administrators can update appointments.

The doctor must be active and the patient must exist.
""",
    responses={
        200: {
            "description": "Appointment updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "doctor_id": 2,
                        "patient_id": 4,
                        "appointment_date": "2030-06-20T11:00:00",
                        "status": "completed"
                    }
                }
            }
        },
        400: {
            "description": "Invalid status, inactive doctor, or appointment conflict"
        },
        404: {
            "description": "Appointment, doctor, or patient not found"
        },
        403: {
            "description": "Admin access required"
        }
    }
)
def update_appointment_api(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):

    appointment = get_appointment_by_id(
        db=db,
        appointment_id=appointment_id
    )

    if not appointment:

        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    doctor_id = (
        appointment_data.doctor_id
        if appointment_data.doctor_id is not None
        else appointment.doctor_id
    )

    patient_id = (
        appointment_data.patient_id
        if appointment_data.patient_id is not None
        else appointment.patient_id
    )

    appointment_date = (
        appointment_data.appointment_date
        if appointment_data.appointment_date is not None
        else appointment.appointment_date
    )

    status = (
        appointment_data.status
        if appointment_data.status is not None
        else appointment.status
    )

    if status not in [
        "scheduled",
        "completed",
        "cancelled"
    ]:
        raise HTTPException(
            status_code=400,
            detail="Invalid appointment status"
        )

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

    if not doctor.is_active:

        raise HTTPException(
            status_code=400,
            detail="Cannot assign appointment to an inactive doctor"
        )

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

    existing_appointment = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == appointment_date,
            Appointment.status == "scheduled",
            Appointment.id != appointment_id
        )
        .first()
    )

    if existing_appointment:

        raise HTTPException(
            status_code=400,
            detail="Doctor already has an appointment at this time"
        )

    try:

        return update_appointment(
            db=db,
            appointment=appointment,
            doctor_id=doctor_id,
            patient_id=patient_id,
            appointment_date=appointment_date,
            status=status,
            user_id=current_user.id
        )

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Unable to update appointment. Please check the provided data."
        )


@router.delete(
    "/{appointment_id}",
    status_code=204,
    summary="Delete an appointment",
    description="""
Delete an appointment from the system.

Only administrators can delete appointments.
""",
    responses={
        204: {
            "description": "Appointment deleted successfully"
        },
        404: {
            "description": "Appointment not found"
        },
        403: {
            "description": "Admin access required"
        }
    }
)
def delete_appointment_api(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):

    appointment = get_appointment_by_id(
        db=db,
        appointment_id=appointment_id
    )

    if not appointment:

        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    try:

        delete_appointment(
            db=db,
            appointment=appointment,
            user_id=current_user.id
        )

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Unable to delete appointment."
        )

    return None


@router.get(
    "/doctors/{doctor_id}/appointments",
    response_model=list[AppointmentResponse],
    summary="Get appointments by doctor",
    description="""
Retrieve all appointments belonging to a specific doctor.
""",
    responses={
        200: {
            "description": "Doctor appointments",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "doctor_id": 2,
                            "patient_id": 4,
                            "appointment_date": "2030-06-20T10:00:00",
                            "status": "scheduled"
                        }
                    ]
                }
            }
        },
        404: {
            "description": "Doctor not found"
        }
    }
)
def get_doctor_appointments(
    doctor_id: int,
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

    appointments = get_appointments_by_doctor(
        db=db,
        doctor_id=doctor_id
    )

    return appointments


@router.get(
    "/patients/{patient_id}/appointments",
    response_model=list[AppointmentResponse],
    summary="Get appointments by patient",
    description="""
Retrieve all appointments belonging to a specific patient.
""",
    responses={
        200: {
            "description": "Patient appointments",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "doctor_id": 2,
                            "patient_id": 4,
                            "appointment_date": "2030-06-20T10:00:00",
                            "status": "scheduled"
                        }
                    ]
                }
            }
        },
        404: {
            "description": "Patient not found"
        }
    }
)
def get_patient_appointments(
    patient_id: int,
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

    appointments = get_appointments_by_patient(
        db=db,
        patient_id=patient_id
    )

    return appointments