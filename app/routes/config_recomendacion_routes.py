
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.config_recomendacion_schema import (
    ConfigRecomendacionUpdate,
    ConfigRecomendacionResponse
)
from app.services.config_recomendacion_service import (
    obtener_config_recomendaciones,
    actualizar_config_recomendaciones,
    obtener_config_global,
    actualizar_config_global
)
from app.dependencies.auth_dependency import (
    obtener_usuario_actual,
    requerir_administrador
)
from app.models.usuario_model import Usuario


router = APIRouter(
    prefix="/api/config-recomendaciones",
    tags=["Configuración de recomendaciones"]
)


@router.get("/", response_model=list[ConfigRecomendacionResponse])
def obtener_mi_configuracion(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return obtener_config_recomendaciones(
        db,
        usuario_actual.id
    )


@router.put("/", response_model=list[ConfigRecomendacionResponse])
def actualizar_mi_configuracion(
    data: ConfigRecomendacionUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return actualizar_config_recomendaciones(
        db,
        usuario_actual.id,
        data.configuraciones
    )


@router.get(
    "/global",
    response_model=list[ConfigRecomendacionResponse]
)
def obtener_configuracion_global(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return obtener_config_global(db)


@router.put(
    "/global",
    response_model=list[ConfigRecomendacionResponse]
)
def guardar_configuracion_global(
    data: ConfigRecomendacionUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_administrador)
):
    return actualizar_config_global(
        db,
        data.configuraciones
    )
