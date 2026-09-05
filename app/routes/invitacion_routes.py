from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.invitacion_schema import (
    InvitacionDoctorCreate,
    InvitacionDoctorResponse,
    InvitacionDoctorValidacionResponse
)
from app.services.invitacion_service import (
    crear_invitacion_doctor,
    validar_invitacion_doctor,
    listar_invitaciones_doctor,
    reenviar_invitacion_doctor
)
from app.dependencies.auth_dependency import (
    obtener_usuario_actual,
    requerir_administrador
)
from app.models.usuario_model import Usuario


router = APIRouter()


@router.post("/doctores", response_model=InvitacionDoctorResponse)
def invitar_doctor(
    invitacion_data: InvitacionDoctorCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_administrador)
):
    return crear_invitacion_doctor(
        db=db,
        invitacion_data=invitacion_data,
        usuario_admin_id=usuario_actual.id
    )

@router.post("/doctores/reenviar", response_model=InvitacionDoctorResponse)
def reenviar_invitacion(
    invitacion_data: InvitacionDoctorCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_administrador)
):
    return reenviar_invitacion_doctor(
        db=db,
        invitacion_data=invitacion_data
    )

@router.get("/", response_model=List[InvitacionDoctorResponse])
def obtener_invitaciones(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_administrador)
):
    return listar_invitaciones_doctor(db)


@router.get("/validar/{token}", response_model=InvitacionDoctorValidacionResponse)
def validar_token_invitacion(
    token: str,
    db: Session = Depends(get_db)
):
    return validar_invitacion_doctor(db, token)