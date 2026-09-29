
from sqlalchemy.orm import Session

from app.models.appointment import Appointment


# ==================================================
# CREATE APPOINTMENT
# ==================================================

def create_appointment(
    db: Session,
    doctor_id: int,
    patient_id: int,
    appointment_date,
    status: str,
    user_id: int
):

    appointment = Appointment(
        doctor_id=doctor_id,
        patient_id=patient_id,
        appointment_date=appointment_date,
        status=status,
        created_by=user_id,
        updated_by=user_id
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return appointment


# ==================================================
# GET APPOINTMENT BY ID
# ==================================================

def get_appointment_by_id(
    db: Session,
    appointment_id: int
):

    return db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()


# ==================================================
# GET APPOINTMENTS
# ==================================================

def get_appointments(
    db: Session,
    page: int = 1,
    limit: int = 10
):

    query = db.query(Appointment)

    total = query.count()

    offset = (page - 1) * limit

    appointments = query.offset(
        offset
    ).limit(
        limit
    ).all()

    return total, appointments


# ==================================================
# GET APPOINTMENTS BY DOCTOR
# ==================================================

def get_appointments_by_doctor(
    db: Session,
    doctor_id: int
):

    return db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id
    ).all()


# ==================================================
# GET APPOINTMENTS BY PATIENT
# ==================================================

def get_appointments_by_patient(
    db: Session,
    patient_id: int
):

    return db.query(Appointment).filter(
        Appointment.patient_id == patient_id
    ).all()


# ==================================================
# UPDATE APPOINTMENT
# ==================================================

def update_appointment(
    db: Session,
    appointment,
    doctor_id: int,
    patient_id: int,
    appointment_date,
    status: str,
    user_id: int
):

    appointment.doctor_id = doctor_id
    appointment.patient_id = patient_id
    appointment.appointment_date = appointment_date
    appointment.status = status
    appointment.updated_by = user_id

    db.commit()
    db.refresh(appointment)

    return appointment


# ==================================================
# DELETE APPOINTMENT
# ==================================================

def delete_appointment(
    db: Session,
    appointment,
    user_id: int
):

    appointment.updated_by = user_id

    db.delete(appointment)
    db.commit()
