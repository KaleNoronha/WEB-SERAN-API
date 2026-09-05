from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.usuario_model import Usuario
from app.core.config import settings


security = HTTPBearer()


def obtener_usuario_actual(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    credenciales_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        usuario_id: str = payload.get("sub")

        if usuario_id is None:
            raise credenciales_exception

    except JWTError:
        raise credenciales_exception

    usuario = db.query(Usuario).filter(
        Usuario.id == int(usuario_id)
    ).first()

    if usuario is None:
        raise credenciales_exception

    if usuario.estado is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )

    return usuario

def requerir_administrador(
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    if usuario_actual.rol_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el administrador puede realizar esta acción"
        )

    return usuario_actual


def requerir_doctor(
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    if usuario_actual.rol_id != 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el doctor puede realizar esta acción"
        )

    return usuario_actual