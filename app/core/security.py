from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generar_hash_contrasena(contrasena: str) -> str:
    return pwd_context.hash(contrasena)


def verificar_contrasena(contrasena_plana: str, contrasena_hash: str) -> bool:
    return pwd_context.verify(contrasena_plana, contrasena_hash)


def crear_token_acceso(data: dict) -> str:
    datos = data.copy()

    tiempo_expiracion = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    datos.update({"exp": tiempo_expiracion})

    token = jwt.encode(
        datos,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return token