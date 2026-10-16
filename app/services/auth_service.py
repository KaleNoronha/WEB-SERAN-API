import hashlib
import secrets

from datetime import timedelta, timezone
from sqlalchemy.exc import SQLAlchemyError

from app.models.recuperacion_password_model import RecuperacionPassword
from app.services.email_service import enviar_correo_recuperacion_password
from app.schemas.auth_schema import (
    SolicitarRecuperacionPassword,
    RestablecerPasswordRequest
)
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
    hospital="Hospital Nacional Edgardo Rebagliati Martins",
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
        hospital="Hospital Nacional Edgardo Rebagliati Martins",
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


def _ahora_utc():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _hash_token(token: str):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def solicitar_recuperacion_password(
    db: Session,
    datos: SolicitarRecuperacionPassword
):
    correo = str(datos.correo).strip().lower()

    usuario = db.query(Usuario).filter(
        Usuario.correo.ilike(correo)
    ).first()

    # Criterio solicitado en la HU 03.
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El correo ingresado no está registrado"
        )

    if not usuario.estado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta se encuentra deshabilitada"
        )

    token = secrets.token_urlsafe(32)
    ahora = _ahora_utc()

    registro = RecuperacionPassword(
        usuario_id=usuario.id,
        token_hash=_hash_token(token),
        fecha_creacion=ahora,
        fecha_expiracion=ahora + timedelta(minutes=15),
        fecha_uso=None
    )

    try:
        db.add(registro)
        db.flush()

        enviar_correo_recuperacion_password(
            email_destino=usuario.correo,
            token=token
        )

        db.commit()

    except Exception:
        db.rollback()

        # No revelar detalles del proveedor de correo al cliente.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "No fue posible enviar el correo de recuperación. "
                "Inténtalo nuevamente."
            )
        )

    return {
        "mensaje": (
            "Enlace de recuperación enviado exitosamente. "
            "Revisa tu correo electrónico."
        )
    }


def restablecer_password(
    db: Session,
    datos: RestablecerPasswordRequest
):
    if datos.nueva_contrasena != datos.confirmar_contrasena:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Las contraseñas no coinciden"
        )

    if len(datos.nueva_contrasena.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña es demasiado larga"
        )

    ahora = _ahora_utc()

    # Bloqueo de fila para impedir el uso simultáneo del token.
    registro = db.query(RecuperacionPassword).filter(
        RecuperacionPassword.token_hash == _hash_token(datos.token)
    ).with_for_update().first()

    if registro is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El enlace de recuperación no es válido"
        )

    if registro.fecha_uso is not None:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este enlace ya fue utilizado"
        )

    if registro.fecha_expiracion <= ahora:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El enlace de recuperación ha expirado"
        )

    usuario = db.query(Usuario).filter(
        Usuario.id == registro.usuario_id,
        Usuario.estado == True
    ).first()

    if usuario is None:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La cuenta no está disponible"
        )

    try:
        usuario.contrasena = generar_hash_contrasena(
            datos.nueva_contrasena
        )
        usuario.fecha_actualizacion = date.today()

        # Invalidar todos los enlaces pendientes del usuario.
        db.query(RecuperacionPassword).filter(
            RecuperacionPassword.usuario_id == usuario.id,
            RecuperacionPassword.fecha_uso.is_(None)
        ).update(
            {"fecha_uso": ahora},
            synchronize_session=False
        )

        db.commit()

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible actualizar la contraseña"
        )

    return {
        "mensaje": (
            "Contraseña actualizada correctamente. "
            "Ya puedes iniciar sesión."
        )
    }
