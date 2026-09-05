from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.database.database import Base


class Recomendacion(Base):
    __tablename__ = "recomendacion"

    id = Column(Integer, primary_key=True, index=True)

    titulo = Column(String(100), nullable=False)
    descripcion = Column(String(300), nullable=False)
    tipo_recomendacion = Column(String(80), nullable=False)
    categoria = Column(String, nullable=False)
    estado = Column(Boolean, default=True)


class RecomendacionEvaluacion(Base):
    __tablename__ = "recomendacion_evaluacion"

    evaluacion_id = Column(
        Integer,
        ForeignKey("evaluacion.id"),
        primary_key=True
    )

    recomendacion_id = Column(
        Integer,
        ForeignKey("recomendacion.id"),
        primary_key=True
    )


class RecomendacionUsuario(Base):
    __tablename__ = "recomendacion_usuario"

    usuario_id = Column(
        Integer,
        ForeignKey("usuario.id"),
        primary_key=True
    )

    recomendacion_id = Column(
        Integer,
        ForeignKey("recomendacion.id"),
        primary_key=True
    )

    activo = Column(Boolean, default=True)