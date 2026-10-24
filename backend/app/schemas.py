from pydantic import BaseModel, Field
from app.models import Role

class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str

class UserOut(BaseModel):
    id: int
    username: str
    full_name: str
    role: Role
    promysel_id: int | None = None

    class Config:
        from_attributes = True