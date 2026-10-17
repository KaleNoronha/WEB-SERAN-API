from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.recomendacion_schema import (
    RecomendacionCreate,
    RecomendacionUpdate,
    RecomendacionResponse
)
from app.services.recomendacion_service import (
    crear_recomendacion,
    listar_recomendaciones,
    listar_recomendaciones_activas,
    obtener_recomendacion_por_id,
    actualizar_recomendacion,
    desactivar_recomendacion
)

from app.services.config_recomendacion_service import (
    obtener_categorias_efectivas
)

from app.dependencies.auth_dependency import obtener_usuario_actual, requerir_administrador
from app.models.usuario_model import Usuario


router = APIRouter()


@router.post("/", response_model=RecomendacionResponse)
def registrar_recomendacion(
    recomendacion_data: RecomendacionCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_administrador)
):
    return crear_recomendacion(db, recomendacion_data)


@router.get("/", response_model=List[RecomendacionResponse])
def obtener_recomendaciones(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    recomendaciones = listar_recomendaciones(db)

    categorias_activas = set(
        obtener_categorias_efectivas(db, usuario_actual.id)
    )

    return [
        {
            "id": rec.id,
            "titulo": rec.titulo,
            "descripcion": rec.descripcion,
            "tipo_recomendacion": rec.tipo_recomendacion,
            "categoria": rec.categoria,
            "estado": rec.estado,
            "estado_efectivo": (
                bool(rec.estado)
                and rec.categoria in categorias_activas
            )
        }
        for rec in recomendaciones
    ]


@router.get("/activas", response_model=List[RecomendacionResponse])
def obtener_recomendaciones_activas(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return listar_recomendaciones_activas(db)


@router.get("/{recomendacion_id}", response_model=RecomendacionResponse)
def obtener_recomendacion(
    recomendacion_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return obtener_recomendacion_por_id(db, recomendacion_id)


@router.put("/{recomendacion_id}", response_model=RecomendacionResponse)
def editar_recomendacion(
    recomendacion_id: int,
    recomendacion_data: RecomendacionUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_administrador)
):
    return actualizar_recomendacion(db, recomendacion_id, recomendacion_data)


@router.delete("/{recomendacion_id}", response_model=RecomendacionResponse)
def eliminar_recomendacion(
    recomendacion_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_administrador)
):
    return desactivar_recomendacion(db, recomendacion_id)