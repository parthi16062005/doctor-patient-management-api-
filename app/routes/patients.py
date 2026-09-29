from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.user import User

from app.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientListResponse
)

from app.dependencies import admin_required

from app.services.patient_service import (
    create_patient,
    get_patient_by_id,
    get_patients,
    update_patient,
    patch_patient,
    delete_patient
)


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


@router.post(
    "/",
    response_model=PatientResponse,
    status_code=201,
    summary="Create a new patient",
    description="""
Create a new patient in the system.

Only administrators can create patients.

A patient can optionally be assigned to an active doctor.
""",
    responses={
        201: {
            "description": "Patient created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 10,
                        "name": "Rahul Kumar",
                        "age": 35,
                        "phone": "9876543210",
                        "doctor_id": 2
                    }
                }
            }
        },
        400: {
            "description": "Invalid patient data"
        },
        404: {
            "description": "Doctor not found"
        },
        403: {
            "description": "Admin access required"
        }
    }
)
def create_patient_api(
    patient: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):

    if patient.doctor_id is not None:

        doctor = (
            db.query(Doctor)
            .filter(Doctor.id == patient.doctor_id)
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
                detail="Cannot assign patient to an inactive doctor"
            )

    try:

        return create_patient(
            db=db,
            name=patient.name,
            age=patient.age,
            phone=patient.phone,
            doctor_id=patient.doctor_id,
            user_id=current_user.id
        )

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Unable to create patient. Please check the provided data."
        )


@router.get(
    "/",
    response_model=PatientListResponse,
    summary="Get patients",
    description="""
Get a paginated list of patients.

You can optionally filter patients by age.
""",
    responses={
        200: {
            "description": "List of patients",
            "content": {
                "application/json": {
                    "example": {
                        "total": 2,
                        "page": 1,
                        "limit": 10,
                        "data": [
                            {
                                "id": 1,
                                "name": "Rahul Kumar",
                                "age": 35,
                                "phone": "9876543210",
                                "doctor_id": 2
                            },
                            {
                                "id": 2,
                                "name": "Priya",
                                "age": 28,
                                "phone": "9876501234",
                                "doctor_id": None
                            }
                        ]
                    }
                }
            }
        }
    }
)
def get_patients_api(
    age_gt: int | None = Query(
        default=None,
        gt=0,
        description="Return patients older than this age",
        examples=[30]
    ),
    page: int = Query(
        default=1,
        ge=1,
        description="Page number",
        examples=[1]
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of patients per page",
        examples=[10]
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):

    total, patients = get_patients(
        db=db,
        age_gt=age_gt,
        page=page,
        limit=limit
    )

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": patients
    }


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Get patient by ID",
    description="""
Retrieve a single patient using the patient's ID.

Only administrators can access this endpoint.
""",
    responses={
        200: {
            "description": "Patient found",
            "content": {
                "application/json": {
                    "example": {
                        "id": 4,
                        "name": "Rahul Kumar",
                        "age": 35,
                        "phone": "9876543210",
                        "doctor_id": 2
                    }
                }
            }
        },
        404: {
            "description": "Patient not found"
        },
        403: {
            "description": "Admin access required"
        }
    }
)
def get_patient_api(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):

    patient = get_patient_by_id(
        db=db,
        patient_id=patient_id
    )

    if not patient:

        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return patient


@router.put(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Update a patient",
    description="""
Update all editable information for an existing patient.

Only administrators can update patients.
""",
    responses={
        200: {
            "description": "Patient updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 4,
                        "name": "Rahul Kumar Updated",
                        "age": 36,
                        "phone": "9876543210",
                        "doctor_id": 2
                    }
                }
            }
        },
        400: {
            "description": "Invalid patient data"
        },
        404: {
            "description": "Patient or doctor not found"
        },
        403: {
            "description": "Admin access required"
        }
    }
)
def update_patient_api(
    patient_id: int,
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):

    patient = get_patient_by_id(
        db=db,
        patient_id=patient_id
    )

    if not patient:

        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    if patient_data.doctor_id is not None:

        doctor = (
            db.query(Doctor)
            .filter(Doctor.id == patient_data.doctor_id)
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
                detail="Cannot assign patient to an inactive doctor"
            )

    try:

        return update_patient(
            db=db,
            patient=patient,
            name=patient_data.name,
            age=patient_data.age,
            phone=patient_data.phone,
            doctor_id=patient_data.doctor_id,
            user_id=current_user.id
        )

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Unable to update patient. Please check the provided data."
        )


@router.patch(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Partially update a patient",
    description="""
Update one or more fields of an existing patient.

Only the fields provided in the request will be changed.
""",
    responses={
        200: {
            "description": "Patient updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 4,
                        "name": "Rahul Kumar",
                        "age": 36,
                        "phone": "9876543210",
                        "doctor_id": 2
                    }
                }
            }
        },
        400: {
            "description": "Invalid patient data"
        },
        404: {
            "description": "Patient or doctor not found"
        },
        403: {
            "description": "Admin access required"
        }
    }
)
def patch_patient_api(
    patient_id: int,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):

    patient = get_patient_by_id(
        db=db,
        patient_id=patient_id
    )

    if not patient:

        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    update_data = patient_data.model_dump(
        exclude_unset=True
    )

    if "doctor_id" in update_data:

        doctor_id = update_data["doctor_id"]

        if doctor_id is not None:

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
                    detail="Cannot assign patient to an inactive doctor"
                )

    try:

        return patch_patient(
            db=db,
            patient=patient,
            update_data=update_data,
            user_id=current_user.id
        )

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Unable to update patient. Please check the provided data."
        )


@router.delete(
    "/{patient_id}",
    status_code=204,
    summary="Delete a patient",
    description="""
Delete a patient from the system.

Only administrators can delete patients.
""",
    responses={
        204: {
            "description": "Patient deleted successfully"
        },
        404: {
            "description": "Patient not found"
        },
        403: {
            "description": "Admin access required"
        }
    }
)
def delete_patient_api(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):

    patient = get_patient_by_id(
        db=db,
        patient_id=patient_id
    )

    if not patient:

        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    try:

        delete_patient(
            db=db,
            patient=patient,
            user_id=current_user.id
        )

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Unable to delete patient."
        )

    return None