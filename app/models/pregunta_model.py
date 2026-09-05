from sqlalchemy import Column, Integer, String
from app.database.database import Base


class Pregunta(Base):
    __tablename__ = "preguntas"

    id = Column(Integer, primary_key=True, index=True)

    codigo = Column(String(50), unique=True, nullable=False)
    texto_pregunta = Column(String(300), nullable=False)
    categoria = Column(String(80), nullable=False)
    peso_base = Column(Integer, nullable=False)