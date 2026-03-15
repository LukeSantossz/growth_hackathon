from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
    has_profile: bool = False

class TokenPayload(BaseModel):
    sub: str | None = None
