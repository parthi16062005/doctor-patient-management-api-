from pydantic import BaseModel, ConfigDict, EmailStr


class DoctorCreate(BaseModel):

    name: str
    specialization: str
    email: EmailStr


class DoctorUpdate(BaseModel):

    name: str | None = None
    specialization: str | None = None
    email: EmailStr | None = None


class DoctorResponse(BaseModel):

    id: int
    name: str
    specialization: str
    email: EmailStr
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )


class DoctorListResponse(BaseModel):

    total: int
    page: int
    limit: int
    data: list[DoctorResponse]