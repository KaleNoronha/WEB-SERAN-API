from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.database.database import Base



class ConfigRecomendacionUsuario(Base):
    __tablename__ = "config_recomendacion_usuario"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    categoria = Column(String(100), nullable=False)
    activo = Column(Boolean, default=True)