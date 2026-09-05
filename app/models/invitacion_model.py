from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from app.database.database import Base


class InvitacionDoctor(Base):
    __tablename__ = "invitacion_doctor"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String(100), nullable=False, index=True)
    token = Column(String(255), unique=True, nullable=False, index=True)

    used = Column(Boolean, default=False)

    created_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)

    created_by = Column(Integer, ForeignKey("usuario.id"), nullable=False)