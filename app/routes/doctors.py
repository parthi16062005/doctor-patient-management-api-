from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.doctor import Doctor
from app.models.user import User

from app.schemas.doctor import (
    DoctorCreate,
    DoctorUpdate,
    DoctorResponse,
    DoctorListResponse
)

from app.dependencies import (
    get_current_user,
    admin_required
)

from app.services.doctor_service import (
    create_doctor,
    get_doctor_by_id,
    get_doctors,
    update_doctor,
    patch_doctor,
    delete_doctor
)


router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"]
)


@router.post(
    "/",
    response_model=DoctorResponse,
    status_code=201,
    summary="Create a new doctor",
    description="""
Create a new doctor in the system.

Only administrators can create doctors.

The doctor's email address must be unique.
""",
    responses={
        201: {
            "description": "Doctor created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 10,
                        "name": "Dr. Arun Kumar",
                        "specialization": "Cardiology",
                        "email": "arun@example.com",
                        "is_active": True
                    }
                }
            }
        },
        400: {
            "description": "Doctor email already exists"
        },
        401: {
            "description": "Authentication required"
        },
        403: {
            "description": "Admin access required"
        }
    }
)
def create_doctor_api(
    doctor: DoctorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):

    existing_doctor = (
        db.query(Doctor)
        .filter(Doctor.email == doctor.email)
        .first()
    )

    if existing_doctor:
        raise HTTPException(
            status_code=400,
            detail="Doctor email already exists"
        )

    try:

        return create_doctor(
            db=db,
            name=doctor.name,
            specialization=doctor.specialization,
            email=doctor.email,
            user_id=current_user.id
        )

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Unable to create doctor. Please check the provided data."
        )


@router.get(
    "/",
    response_model=DoctorListResponse,
    summary="Get doctors",
    description="""
Get a paginated list of doctors.

Optional filters:

- specialization
- active/inactive status
- page number
- page size
""",
    responses={
        200: {
            "description": "List of doctors",
            "content": {
                "application/json": {
                    "example": {
                        "total": 2,
                        "page": 1,
                        "limit": 10,
                        "data": [
                            {
                                "id": 1,
                                "name": "Dr. Arun Kumar",
                                "specialization": "Cardiology",
                                "email": "arun@example.com",
                                "is_active": True
                            },
                            {
                                "id": 2,
                                "name": "Dr. Kumar",
                                "specialization": "Neurology",
                                "email": "kumar@example.com",
                                "is_active": True
                            }
                        ]
                    }
                }
            }
        }
    }
)
def get_doctors_api(
    specialization: str | None = Query(
        default=None,
        description="Filter doctors by specialization",
        examples=["Cardiology"]
    ),
    is_active: bool | None = Query(
        default=None,
        description="Filter doctors by active status",
        examples=[True]
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
        description="Number of doctors per page",
        examples=[10]
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    total, doctors = get_doctors(
        db=db,
        specialization=specialization,
        is_active=is_active,
        page=page,
        limit=limit
    )

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": doctors
    }


@router.get(
    "/{doctor_id}",
    response_model=DoctorResponse,
    summary="Get doctor by ID",
    description="""
Retrieve a single doctor using the doctor's ID.
""",
    responses={
        200: {
            "description": "Doctor found",
            "content": {
                "application/json": {
                    "example": {
                        "id": 2,
                        "name": "Dr. Kumar",
                        "specialization": "Neurology",
                        "email": "kumar@example.com",
                        "is_active": True
                    }
                }
            }
        },
        404: {
            "description": "Doctor not found"
        }
    }
)
def get_doctor_api(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    doctor = get_doctor_by_id(
        db=db,
        doctor_id=doctor_id
    )

    if not doctor:

        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    return doctor


@router.put(
    "/{doctor_id}",
    response_model=DoctorResponse,
    summary="Update a doctor",
    description="""
Update all editable information for an existing doctor.

Only administrators can update doctors.
""",
    responses={
        200: {
            "description": "Doctor updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 2,
                        "name": "Dr. Kumar Updated",
                        "specialization": "Neurology",
                        "email": "kumar.updated@example.com",
                        "is_active": True
                    }
                }
            }
        },
        400: {
            "description": "Invalid or duplicate doctor data"
        },
        404: {
            "description": "Doctor not found"
        },
        403: {
            "description": "Admin access required"
        }
    }
)
def update_doctor_api(
    doctor_id: int,
    doctor_data: DoctorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):

    doctor = get_doctor_by_id(
        db=db,
        doctor_id=doctor_id
    )

    if not doctor:

        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    existing_doctor = (
        db.query(Doctor)
        .filter(
            Doctor.email == doctor_data.email,
            Doctor.id != doctor_id
        )
        .first()
    )

    if existing_doctor:

        raise HTTPException(
            status_code=400,
            detail="Doctor email already exists"
        )

    try:

        return update_doctor(
            db=db,
            doctor=doctor,
            name=doctor_data.name,
            specialization=doctor_data.specialization,
            email=doctor_data.email,
            user_id=current_user.id
        )

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Unable to update doctor. Please check the provided data."
        )


@router.patch(
    "/{doctor_id}",
    response_model=DoctorResponse,
    summary="Partially update a doctor",
    description="""
Update one or more fields of an existing doctor.

Only the fields provided in the request will be changed.
""",
    responses={
        200: {
            "description": "Doctor updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 2,
                        "name": "Dr. Kumar",
                        "specialization": "Cardiology",
                        "email": "kumar@example.com",
                        "is_active": False
                    }
                }
            }
        },
        400: {
            "description": "Invalid or duplicate data"
        },
        404: {
            "description": "Doctor not found"
        },
        403: {
            "description": "Admin access required"
        }
    }
)
def patch_doctor_api(
    doctor_id: int,
    doctor_data: DoctorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):

    doctor = get_doctor_by_id(
        db=db,
        doctor_id=doctor_id
    )

    if not doctor:

        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    update_data = doctor_data.model_dump(
        exclude_unset=True
    )

    if "email" in update_data:

        existing_doctor = (
            db.query(Doctor)
            .filter(
                Doctor.email == update_data["email"],
                Doctor.id != doctor_id
            )
            .first()
        )

        if existing_doctor:

            raise HTTPException(
                status_code=400,
                detail="Doctor email already exists"
            )

    try:

        return patch_doctor(
            db=db,
            doctor=doctor,
            update_data=update_data,
            user_id=current_user.id
        )

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Unable to update doctor. Please check the provided data."
        )


@router.delete(
    "/{doctor_id}",
    response_model=DoctorResponse,
    summary="Delete a doctor",
    description="""
Delete a doctor from the system.

Only administrators can delete doctors.
""",
    responses={
        200: {
            "description": "Doctor deleted successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 2,
                        "name": "Dr. Kumar",
                        "specialization": "Neurology",
                        "email": "kumar@example.com",
                        "is_active": True
                    }
                }
            }
        },
        404: {
            "description": "Doctor not found"
        },
        403: {
            "description": "Admin access required"
        }
    }
)
def delete_doctor_api(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):

    doctor = get_doctor_by_id(
        db=db,
        doctor_id=doctor_id
    )

    if not doctor:

        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    return delete_doctor(
        db=db,
        doctor=doctor,
        user_id=current_user.id
    )