from pydantic import BaseModel, Field
from typing import Optional


class PreguntaBase(BaseModel):
    codigo: str
    texto_pregunta: str
    categoria: str
    peso_base: int = Field(ge=0)


class PreguntaCreate(PreguntaBase):
    pass


class PreguntaUpdate(BaseModel):
    codigo: Optional[str] = None
    texto_pregunta: Optional[str] = None
    categoria: Optional[str] = None
    peso_base: Optional[int] = Field(default=None, ge=0)


class PreguntaResponse(PreguntaBase):
    id: int

    class Config:
        from_attributes = True