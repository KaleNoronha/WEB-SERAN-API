from pydantic import BaseModel
from typing import Optional


class RecomendacionBase(BaseModel):
    titulo: str
    descripcion: str
    tipo_recomendacion: str
    categoria: str


class RecomendacionCreate(RecomendacionBase):
    pass


class RecomendacionUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    tipo_recomendacion: Optional[str] = None
    categoria: Optional [str] = None
    estado: Optional[bool] = None


class RecomendacionResponse(RecomendacionBase):
    id: int
    estado: bool

    class Config:
        from_attributes = True