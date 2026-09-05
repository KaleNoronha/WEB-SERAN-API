from sqlalchemy import Column, Integer, String, Date, DECIMAL
from app.database.database import Base


class Paciente(Base):
    __tablename__ = "paciente"

    id = Column(Integer, primary_key=True, index=True)

    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)

    dni = Column(String(15), unique=True, nullable=True)
    sexo = Column(String(20), nullable=True)

    peso = Column(DECIMAL(5, 2), nullable=True)
    talla = Column(DECIMAL(4, 2), nullable=True)

    fecha_registro = Column(Date, nullable=True)

    departamento = Column(String(100), nullable=True)