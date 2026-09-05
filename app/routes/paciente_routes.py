from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.paciente_schema import (
    PacienteCreate,
    PacienteUpdate,
    PacienteResponse
)
from app.services.paciente_service import (
    crear_paciente,
    listar_pacientes,
    obtener_paciente_por_id,
    actualizar_paciente
)
from app.dependencies.auth_dependency import obtener_usuario_actual
from app.models.usuario_model import Usuario


router = APIRouter()


@router.post("/", response_model=PacienteResponse)
def registrar_paciente(
    paciente_data: PacienteCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return crear_paciente(db, paciente_data)


@router.get("/", response_model=List[PacienteResponse])
def obtener_pacientes(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return listar_pacientes(db)


@router.get("/{paciente_id}", response_model=PacienteResponse)
def obtener_paciente(
    paciente_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return obtener_paciente_por_id(db, paciente_id)


@router.put("/{paciente_id}", response_model=PacienteResponse)
def editar_paciente(
    paciente_id: int,
    paciente_data: PacienteUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return actualizar_paciente(db, paciente_id, paciente_data)