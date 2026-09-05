from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.usuario_model import Usuario
from app.schemas.usuario_schema import UsuarioResponse
from app.dependencies.auth_dependency import requerir_administrador


router = APIRouter()


@router.get("/doctores", response_model=List[UsuarioResponse])
def listar_doctores(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_administrador)
):
    return db.query(Usuario).filter(
        Usuario.rol_id == 2
    ).order_by(
        Usuario.id.desc()
    ).all()

@router.patch("/{usuario_id}/estado", response_model=UsuarioResponse)
def cambiar_estado_usuario(
    usuario_id: int,
    estado: bool,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_administrador)
):
    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id
    ).first()

    if not usuario:
        raise HTTPException(
        status_code=404,
        detail="Usuario no encontrado"
    )

    usuario.estado = estado

    db.commit()
    db.refresh(usuario)

    return usuario