from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    user_info = Column(String, nullable=True)
    onboarding_context = Column(String, nullable=True) # JSON string of history
    
    clients = relationship("Client", back_populates="owner")
    bases = relationship("ClientBaseList", back_populates="owner")
