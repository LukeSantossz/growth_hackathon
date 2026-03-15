from pydantic import BaseModel, EmailStr, ConfigDict

class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: str | None = None

class UserInDBBase(UserBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

class UserResponse(UserInDBBase):
    user_info: str | None = None
