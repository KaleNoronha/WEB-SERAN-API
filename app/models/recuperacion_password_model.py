
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class RecuperacionPassword(Base):
    __tablename__ = "recuperacion_password"

    id = Column(Integer, primary_key=True, index=True)

    usuario_id = Column(
        Integer,
        ForeignKey("usuario.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    token_hash = Column(String(64), unique=True, nullable=False)
    fecha_expiracion = Column(DateTime, nullable=False)
    fecha_creacion = Column(DateTime, nullable=False)
    fecha_uso = Column(DateTime, nullable=True)

    usuario = relationship("Usuario")
