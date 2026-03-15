from pydantic import BaseModel, ConfigDict
from typing import Optional
from models.client import ClientStatus

class ClientBase(BaseModel):
    nome: Optional[str] = None
    telefone: str
    localidade: Optional[str] = None
    categoria: Optional[str] = None
    categoria_especifica: Optional[str] = None
    status: ClientStatus = ClientStatus.COLD_LEAD
    base_id: Optional[int] = None

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    status: Optional[ClientStatus] = None
    base_id: Optional[int] = None

class ClientResponse(ClientBase):
    id: int
    owner_id: int
    
    model_config = ConfigDict(from_attributes=True)
