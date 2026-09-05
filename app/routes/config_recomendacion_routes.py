from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.config_recomendacion_schema import ConfigRecomendacionUpdate, ConfigRecomendacionResponse
from app.services.config_recomendacion_service import obtener_config_recomendaciones, actualizar_config_recomendaciones
from app.dependencies.auth_dependency import obtener_usuario_actual

router = APIRouter(prefix="/api/config-recomendaciones", tags=["Configuración de recomendaciones"])


@router.get("/", response_model=list[ConfigRecomendacionResponse])
def obtener_mi_configuracion(
    db: Session = Depends(get_db),
    usuario_actual=Depends(obtener_usuario_actual)
):
    return obtener_config_recomendaciones(db, usuario_actual.id)


@router.put("/", response_model=list[ConfigRecomendacionResponse])
def actualizar_mi_configuracion(
    data: ConfigRecomendacionUpdate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(obtener_usuario_actual)
):
    return actualizar_config_recomendaciones(db, usuario_actual.id, data.configuraciones)