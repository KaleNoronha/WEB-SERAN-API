from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.recomendacion_model import Recomendacion
from app.schemas.recomendacion_schema import RecomendacionCreate, RecomendacionUpdate


def crear_recomendacion(db: Session, recomendacion_data: RecomendacionCreate):
    nueva_recomendacion = Recomendacion(
        titulo=recomendacion_data.titulo,
        descripcion=recomendacion_data.descripcion,
        tipo_recomendacion=recomendacion_data.tipo_recomendacion,
        categoria = recomendacion_data.categoria,
        estado=True
    )

    db.add(nueva_recomendacion)
    db.commit()
    db.refresh(nueva_recomendacion)

    return nueva_recomendacion


def listar_recomendaciones(db: Session):
    return db.query(Recomendacion).order_by(Recomendacion.id.asc()).all()


def listar_recomendaciones_activas(db: Session):
    return db.query(Recomendacion).filter(
        Recomendacion.estado == True
    ).order_by(Recomendacion.id.asc()).all()


def obtener_recomendacion_por_id(db: Session, recomendacion_id: int):
    recomendacion = db.query(Recomendacion).filter(
        Recomendacion.id == recomendacion_id
    ).first()

    if not recomendacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recomendación no encontrada"
        )

    return recomendacion


def actualizar_recomendacion(
    db: Session,
    recomendacion_id: int,
    recomendacion_data: RecomendacionUpdate
):
    recomendacion = obtener_recomendacion_por_id(db, recomendacion_id)

    datos_actualizados = recomendacion_data.model_dump(exclude_unset=True)

    for campo, valor in datos_actualizados.items():
        setattr(recomendacion, campo, valor)

    db.commit()
    db.refresh(recomendacion)

    return recomendacion


def desactivar_recomendacion(db: Session, recomendacion_id: int):
    recomendacion = obtener_recomendacion_por_id(db, recomendacion_id)

    recomendacion.estado = False

    db.commit()
    db.refresh(recomendacion)

    return recomendacion