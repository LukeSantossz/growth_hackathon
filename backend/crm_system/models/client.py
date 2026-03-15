import enum
from sqlalchemy import Column, Integer, String, Enum as SQLAlchemyEnum, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class ClientStatus(str, enum.Enum):
    TRASH_LEAD = "trash lead"
    COLD_LEAD = "cold lead"
    ENGAJED_LEAD = "engajed lead"
    CUSTOMER = "customer"

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True, nullable=True)
    telefone = Column(String, index=True, nullable=False)
    localidade = Column(String, nullable=True)
    categoria = Column(String, nullable=True)
    categoria_especifica = Column(String, nullable=True)
    status = Column(SQLAlchemyEnum(ClientStatus), default=ClientStatus.COLD_LEAD, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    base_id = Column(Integer, ForeignKey("client_bases.id"), nullable=True)

    owner = relationship("User", back_populates="clients")
    base = relationship("ClientBaseList", back_populates="clients")

