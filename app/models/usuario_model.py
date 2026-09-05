from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base


class Rol(Base):
    __tablename__ = "rol"

    id = Column(Integer, primary_key=True, index=True)
    rol = Column(String(30), nullable=False)

    usuarios = relationship("Usuario", back_populates="rol")


class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True, index=True)
    rol_id = Column(Integer, ForeignKey("rol.id"), nullable=False)

    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True, nullable=False, index=True)
    contrasena = Column(String(255), nullable=False)
    telefono = Column(String(20), nullable=True)
    colegiatura = Column(String(30), nullable=True)
    
    fecha_registro = Column(Date, nullable=True)
    fecha_actualizacion = Column(Date, nullable=True)

    estado = Column(Boolean, default=True)

    rol = relationship("Rol", back_populates="usuarios")