from sqlalchemy import Column, Integer, String, Date, ForeignKey
from app.database.database import Base


class Evaluacion(Base):
    __tablename__ = "evaluacion"

    id = Column(Integer, primary_key=True, index=True)

    usuario_id = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    paciente_id = Column(Integer, ForeignKey("paciente.id"), nullable=False)

    fecha_evaluacion = Column(Date, nullable=False)

    estado_evaluacion = Column(String(30), nullable=False, default="En progreso")

    puntaje_total = Column(Integer, nullable=True)
    nivel_riesgo = Column(String(50), nullable=True)


class EvaluacionPregunta(Base):
    __tablename__ = "evaluacion_preguntas"

    evaluacion_id = Column(
        Integer,
        ForeignKey("evaluacion.id"),
        primary_key=True
    )

    pregunta_id = Column(
        Integer,
        ForeignKey("preguntas.id"),
        primary_key=True
    )

    respuesta = Column(String(100), nullable=False)
    puntaje_obtenido = Column(Integer, nullable=False)