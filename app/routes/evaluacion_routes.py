from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.evaluacion_schema import (
    EvaluacionCreate,
    EvaluacionIniciarCreate,
    EvaluacionFinalizarCreate,
    EvaluacionResponse,
    EvaluacionResumenResponse
)

from app.services.evaluacion_service import (
    iniciar_evaluacion,
    crear_evaluacion,
    finalizar_evaluacion,
    cancelar_evaluacion,
    listar_evaluaciones,
    obtener_evaluacion_por_id,
    listar_evaluaciones_por_paciente,
    listar_evaluaciones_en_progreso_por_usuario,
    listar_evaluaciones_culminadas_por_usuario
)

from app.dependencies.auth_dependency import obtener_usuario_actual, requerir_doctor
from app.models.usuario_model import Usuario


router = APIRouter()

@router.post("/iniciar", response_model=EvaluacionResumenResponse)
def iniciar_nueva_evaluacion(
    evaluacion_data: EvaluacionIniciarCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_doctor)
):
    return iniciar_evaluacion(
        db=db,
        paciente_id=evaluacion_data.paciente_id,
        usuario_id=usuario_actual.id
    )


@router.post("/{evaluacion_id}/finalizar", response_model=EvaluacionResponse)
def finalizar_evaluacion_en_progreso(
    evaluacion_id: int,
    evaluacion_data: EvaluacionFinalizarCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_doctor)
):
    return finalizar_evaluacion(
        db=db,
        evaluacion_id=evaluacion_id,
        evaluacion_data=evaluacion_data,
        usuario_id=usuario_actual.id
    )

@router.post("/{evaluacion_id}/cancelar", response_model=EvaluacionResumenResponse)
def cancelar_evaluacion_en_progreso(
    evaluacion_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_doctor)
):
    return cancelar_evaluacion(
        db=db,
        evaluacion_id=evaluacion_id,
        usuario_id=usuario_actual.id
    )

@router.post("/", response_model=EvaluacionResponse)
def registrar_evaluacion(
    evaluacion_data: EvaluacionCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_doctor)
):
    return crear_evaluacion(
        db=db,
        evaluacion_data=evaluacion_data,
        usuario_id=usuario_actual.id
    )


@router.get("/", response_model=List[EvaluacionResumenResponse])
def obtener_evaluaciones(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return listar_evaluaciones(db)

@router.get("/paciente/{paciente_id}", response_model=List[EvaluacionResumenResponse])
def obtener_evaluaciones_por_paciente(
    paciente_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return listar_evaluaciones_por_paciente(db, paciente_id)


@router.get("/estado/en-progreso", response_model=List[EvaluacionResumenResponse])
def obtener_mis_evaluaciones_en_progreso(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return listar_evaluaciones_en_progreso_por_usuario(
        db=db,
        usuario_id=usuario_actual.id
    )


@router.get("/estado/culminadas", response_model=List[EvaluacionResumenResponse])
def obtener_mis_evaluaciones_culminadas(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return listar_evaluaciones_culminadas_por_usuario(
        db=db,
        usuario_id=usuario_actual.id
    )

@router.get("/{evaluacion_id}", response_model=EvaluacionResponse)
def obtener_evaluacion(
    evaluacion_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return obtener_evaluacion_por_id(db, evaluacion_id)