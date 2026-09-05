from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.pregunta_schema import (
    PreguntaCreate,
    PreguntaUpdate,
    PreguntaResponse
)
from app.services.pregunta_service import (
    crear_pregunta,
    listar_preguntas,
    obtener_pregunta_por_id,
    actualizar_pregunta
)
from app.dependencies.auth_dependency import obtener_usuario_actual, requerir_administrador
from app.models.usuario_model import Usuario


router = APIRouter()


@router.post("/", response_model=PreguntaResponse)
def registrar_pregunta(
    pregunta_data: PreguntaCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_administrador)
):
    return crear_pregunta(db, pregunta_data)


@router.get("/", response_model=List[PreguntaResponse])
def obtener_preguntas(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return listar_preguntas(db)


@router.get("/{pregunta_id}", response_model=PreguntaResponse)
def obtener_pregunta(
    pregunta_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return obtener_pregunta_por_id(db, pregunta_id)


@router.put("/{pregunta_id}", response_model=PreguntaResponse)
def editar_pregunta(
    pregunta_id: int,
    pregunta_data: PreguntaUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_administrador)
):
    return actualizar_pregunta(db, pregunta_id, pregunta_data)