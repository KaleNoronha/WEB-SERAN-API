from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.usuario_schema import UsuarioCreate, UsuarioResponse
from app.schemas.auth_schema import LoginRequest, RegistroDoctorInvitadoRequest, UsuarioPerfilUpdate
from app.services.auth_service import (
    registrar_usuario,
    autenticar_usuario,
    registrar_doctor_por_invitacion
)
from app.dependencies.auth_dependency import obtener_usuario_actual, requerir_administrador
from app.models.usuario_model import Usuario


router = APIRouter()


@router.post("/register", response_model=UsuarioResponse)
def register(
    usuario_data: UsuarioCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_administrador)
):
    return registrar_usuario(db, usuario_data)


@router.post("/login")
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    return autenticar_usuario(db, login_data)


@router.get("/me", response_model=UsuarioResponse)
def obtener_mi_usuario(
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return usuario_actual


@router.put("/me", response_model=UsuarioResponse)
def actualizar_mi_usuario(
    usuario_data: UsuarioPerfilUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    datos_actualizados = usuario_data.model_dump(exclude_unset=True)

    for campo, valor in datos_actualizados.items():
        setattr(usuario_actual, campo, valor)

    db.commit()
    db.refresh(usuario_actual)

    return usuario_actual

@router.post("/registro-doctor/{token}", response_model=UsuarioResponse)
def registro_doctor_invitado(
    token: str,
    doctor_data: RegistroDoctorInvitadoRequest,
    db: Session = Depends(get_db)
):
    return registrar_doctor_por_invitacion(
        db=db,
        token=token,
        doctor_data=doctor_data
    )