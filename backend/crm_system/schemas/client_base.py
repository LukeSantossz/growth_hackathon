from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class ClientBaseListBase(BaseModel):
    name: str
    description: Optional[str] = None

class ClientBaseListCreate(ClientBaseListBase):
    pass

class ClientBaseListResponse(ClientBaseListBase):
    id: int
    owner_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
