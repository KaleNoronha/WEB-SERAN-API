from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class InvitacionDoctorCreate(BaseModel):
    email: EmailStr


class InvitacionDoctorResponse(BaseModel):
    id: int
    email: EmailStr
    token: str
    used: bool
    created_at: datetime
    expires_at: datetime
    used_at: Optional[datetime] = None
    created_by: int

    class Config:
        from_attributes = True


class InvitacionDoctorValidacionResponse(BaseModel):
    email: EmailStr
    valido: bool
    mensaje: str