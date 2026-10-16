from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LoginRequest(BaseModel):
    correo: EmailStr
    contrasena: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class RegistroDoctorInvitadoRequest(BaseModel):
    nombres: str
    apellidos: str
    telefono: Optional[str] = None
    colegiatura: str
    contrasena: str = Field(min_length=6, max_length=72)

class UsuarioPerfilUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    telefono: Optional[str] = None
    colegiatura: Optional[str] = None

    
class SolicitarRecuperacionPassword(BaseModel):
    correo: EmailStr


class RestablecerPasswordRequest(BaseModel):
    token: str = Field(min_length=1)
    nueva_contrasena: str = Field(min_length=6, max_length=72)
    confirmar_contrasena: str = Field(min_length=6, max_length=72)
