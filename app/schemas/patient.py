
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class PatientCreate(BaseModel):

    name: str

    age: int = Field(
        gt=0
    )

    phone: str = Field(
        pattern=r"^\d{10}$"
    )

    doctor_id: int | None = None


class PatientUpdate(BaseModel):

    name: str | None = None

    age: int | None = Field(
        default=None,
        gt=0
    )

    phone: str | None = Field(
        default=None,
        pattern=r"^\d{10}$"
    )

    doctor_id: int | None = None


class PatientResponse(BaseModel):

    id: int
    name: str
    age: int
    phone: str
    doctor_id: int | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None
    created_by: int | None = None
    updated_by: int | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


class PatientListResponse(BaseModel):

    total: int
    page: int
    limit: int
    data: list[PatientResponse]
