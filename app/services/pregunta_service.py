from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.pregunta_model import Pregunta
from app.schemas.pregunta_schema import PreguntaCreate, PreguntaUpdate


def crear_pregunta(db: Session, pregunta_data: PreguntaCreate):
    pregunta_existente = db.query(Pregunta).filter(
        Pregunta.codigo == pregunta_data.codigo
    ).first()

    if pregunta_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una pregunta con ese código"
        )

    nueva_pregunta = Pregunta(
        codigo=pregunta_data.codigo,
        texto_pregunta=pregunta_data.texto_pregunta,
        categoria=pregunta_data.categoria,
        peso_base=pregunta_data.peso_base
    )

    db.add(nueva_pregunta)
    db.commit()
    db.refresh(nueva_pregunta)

    return nueva_pregunta


def listar_preguntas(db: Session):
    return db.query(Pregunta).order_by(Pregunta.id.asc()).all()


def obtener_pregunta_por_id(db: Session, pregunta_id: int):
    pregunta = db.query(Pregunta).filter(Pregunta.id == pregunta_id).first()

    if not pregunta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pregunta no encontrada"
        )

    return pregunta


def actualizar_pregunta(
    db: Session,
    pregunta_id: int,
    pregunta_data: PreguntaUpdate
):
    pregunta = obtener_pregunta_por_id(db, pregunta_id)

    datos_actualizados = pregunta_data.model_dump(exclude_unset=True)

    if "codigo" in datos_actualizados:
        codigo_existente = db.query(Pregunta).filter(
            Pregunta.codigo == datos_actualizados["codigo"],
            Pregunta.id != pregunta_id
        ).first()

        if codigo_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otra pregunta con ese código"
            )

    for campo, valor in datos_actualizados.items():
        setattr(pregunta, campo, valor)

    db.commit()
    db.refresh(pregunta)

    return pregunta