from datetime import datetime, timedelta
from secrets import token_urlsafe

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.invitacion_model import InvitacionDoctor
from app.models.usuario_model import Usuario
from app.schemas.invitacion_schema import InvitacionDoctorCreate
from app.services.email_service import enviar_correo_invitacion_doctor

def crear_invitacion_doctor(
    db: Session,
    invitacion_data: InvitacionDoctorCreate,
    usuario_admin_id: int
):
    usuario_existente = db.query(Usuario).filter(
        Usuario.correo == invitacion_data.email
    ).first()

    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario registrado con este correo"
        )

    invitacion_pendiente = db.query(InvitacionDoctor).filter(
        InvitacionDoctor.email == invitacion_data.email,
        InvitacionDoctor.used == False,
        InvitacionDoctor.expires_at > datetime.now()
    ).first()

    if invitacion_pendiente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una invitación pendiente para este correo"
        )

    nuevo_token = token_urlsafe(32)

    nueva_invitacion = InvitacionDoctor(
        email=invitacion_data.email,
        token=nuevo_token,
        used=False,
        created_at=datetime.now(),
        expires_at=datetime.now() + timedelta(hours=24),
        used_at=None,
        created_by=usuario_admin_id
    )

    db.add(nueva_invitacion)
    db.commit()
    db.refresh(nueva_invitacion)

    enviar_correo_invitacion_doctor(
    email_destino=nueva_invitacion.email,
    token=nueva_invitacion.token)

    return nueva_invitacion


def validar_invitacion_doctor(db: Session, token: str):
    invitacion = db.query(InvitacionDoctor).filter(
        InvitacionDoctor.token == token
    ).first()

    if not invitacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitación no encontrada"
        )

    if invitacion.used:
        return {
            "email": invitacion.email,
            "valido": False,
            "mensaje": "La invitación ya fue utilizada"
        }

    if invitacion.expires_at < datetime.now():
        return {
            "email": invitacion.email,
            "valido": False,
            "mensaje": "La invitación ha expirado"
        }

    return {
        "email": invitacion.email,
        "valido": True,
        "mensaje": "Invitación válida"
    }


def listar_invitaciones_doctor(db: Session):
    return db.query(InvitacionDoctor).order_by(
        InvitacionDoctor.id.desc()
    ).all()

def reenviar_invitacion_doctor(
    db: Session,
    invitacion_data: InvitacionDoctorCreate
):
    invitacion = db.query(InvitacionDoctor).filter(
        InvitacionDoctor.email == invitacion_data.email,
        InvitacionDoctor.used == False
    ).order_by(
        InvitacionDoctor.id.desc()
    ).first()

    if not invitacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existe una invitación pendiente para este correo"
        )

    if invitacion.expires_at < datetime.now():
        invitacion.token = token_urlsafe(32)
        invitacion.expires_at = datetime.now() + timedelta(hours=24)

        db.commit()
        db.refresh(invitacion)

    enviar_correo_invitacion_doctor(
        email_destino=invitacion.email,
        token=invitacion.token
    )

    return invitacion