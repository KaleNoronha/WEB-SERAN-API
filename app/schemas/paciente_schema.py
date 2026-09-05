from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from decimal import Decimal


class PacienteBase(BaseModel):
    nombres: str
    apellidos: str
    fecha_nacimiento: date
    dni: Optional[str] = None
    sexo: Optional[str] = None
    departamento: Optional[str] = None


class PacienteCreate(PacienteBase):
    # Validación estricta para nuevos registros
    peso: Optional[Decimal] = Field(default=None, ge=2, le=30)
    talla: Optional[Decimal] = Field(default=None, ge=0.45, le=1.20)


class PacienteUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    dni: Optional[str] = None
    sexo: Optional[str] = None

    # Validación estricta para edición
    peso: Optional[Decimal] = Field(default=None, ge=2, le=30)
    talla: Optional[Decimal] = Field(default=None, ge=0.45, le=1.20)

    departamento: Optional[str] = None


class PacienteResponse(PacienteBase):
    id: int
    fecha_registro: Optional[date] = None

    # En respuesta no ponemos ge/le para evitar que datos antiguos rompan el listado
    peso: Optional[Decimal] = None
    talla: Optional[Decimal] = None

    evaluaciones: int = 0
    ultimo_riesgo: Optional[str] = None
    ultimo_puntaje: Optional[int] = None

    class Config:
        from_attributes = True