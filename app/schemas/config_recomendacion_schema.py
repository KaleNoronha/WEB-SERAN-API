from pydantic import BaseModel


class ConfigRecomendacionItem(BaseModel):
    categoria: str
    activo: bool


class ConfigRecomendacionUpdate(BaseModel):
    configuraciones: list[ConfigRecomendacionItem]


class ConfigRecomendacionResponse(BaseModel):
    categoria: str
    activo: bool

    class Config:
        from_attributes = True