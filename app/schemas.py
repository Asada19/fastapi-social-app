from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, EmailStr, validator, Field


class TokenBase(BaseModel):
    token: UUID4 = Field(..., alias="access_token")
    expires: datetime
    token_type: Optional[str] = "bearer"

    class Config:
        allow_population_by_field_name = True

    @validator("token")
    def hexlify_token(cls, value):
        return value.hex


class UserBase(BaseModel):
    id: int
    email: EmailStr
    name: str


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str


class User(UserBase):
    token: TokenBase = {}


class DweetModel(BaseModel):
    title: str
    content: str


class DweetDetailsModel(DweetModel):
    id: int
    created_at: datetime
    user_name: str