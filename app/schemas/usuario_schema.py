from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date


class UsuarioBase(BaseModel):
    nombres: str
    apellidos: str
    correo: EmailStr
    telefono: Optional[str] = None
    colegiatura: Optional[str] = None
    rol_id: int


class UsuarioCreate(UsuarioBase):
    contrasena: str = Field(
        min_length=6,
        max_length=72,
        description="La contraseña debe tener entre 6 y 72 caracteres"
    )


class UsuarioResponse(UsuarioBase):
    id: int
    fecha_registro: Optional[date] = None
    fecha_actualizacion: Optional[date] = None
    estado: bool

    class Config:
        from_attributes = True