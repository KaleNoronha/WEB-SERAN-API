from datetime import date, datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.usuario_model import Usuario
from app.schemas.usuario_schema import UsuarioCreate
from app.schemas.auth_schema import LoginRequest
from app.core.security import (
    generar_hash_contrasena,
    verificar_contrasena,
    crear_token_acceso
)
from app.models.invitacion_model import InvitacionDoctor
from app.schemas.auth_schema import RegistroDoctorInvitadoRequest


def registrar_usuario(db: Session, usuario_data: UsuarioCreate):
    usuario_existente = db.query(Usuario).filter(
        Usuario.correo == usuario_data.correo
    ).first()

    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya se encuentra registrado"
        )

    nuevo_usuario = Usuario(
    rol_id=usuario_data.rol_id,
    nombres=usuario_data.nombres,
    apellidos=usuario_data.apellidos,
    correo=usuario_data.correo,
    contrasena=generar_hash_contrasena(usuario_data.contrasena),
    telefono=usuario_data.telefono,
    colegiatura=usuario_data.colegiatura,
    fecha_registro=date.today(),
    fecha_actualizacion=date.today(),
    estado=True
)

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return nuevo_usuario


def autenticar_usuario(db: Session, login_data: LoginRequest):
    usuario = db.query(Usuario).filter(
        Usuario.correo == login_data.correo
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"
        )

    if not verificar_contrasena(login_data.contrasena, usuario.contrasena):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"
        )

    if not usuario.estado:
        raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Usuario deshabilitado. Contacte con el administrador."
    )

    token = crear_token_acceso(
        data={
            "sub": str(usuario.id),
            "correo": usuario.correo,
            "rol_id": usuario.rol_id
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "nombres": usuario.nombres,
            "apellidos": usuario.apellidos,
            "correo": usuario.correo,
            "rol_id": usuario.rol_id
        }
    }

def registrar_doctor_por_invitacion(
    db: Session,
    token: str,
    doctor_data: RegistroDoctorInvitadoRequest
):
    invitacion = db.query(InvitacionDoctor).filter(
        InvitacionDoctor.token == token
    ).first()

    if not invitacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitación no encontrada"
        )

    if invitacion.used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La invitación ya fue utilizada"
        )

    if invitacion.expires_at < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La invitación ha expirado"
        )

    usuario_existente = db.query(Usuario).filter(
        Usuario.correo == invitacion.email
    ).first()

    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario registrado con este correo"
        )

    nuevo_doctor = Usuario(
        rol_id=2,
        nombres=doctor_data.nombres,
        apellidos=doctor_data.apellidos,
        correo=invitacion.email,
        contrasena=generar_hash_contrasena(doctor_data.contrasena),
        telefono=doctor_data.telefono,
        colegiatura=doctor_data.colegiatura,
        fecha_registro=date.today(),
        fecha_actualizacion=date.today(),
        estado=True
    )

    db.add(nuevo_doctor)

    invitacion.used = True
    invitacion.used_at = datetime.now()

    db.commit()
    db.refresh(nuevo_doctor)

    return nuevo_doctor