from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserSignup(BaseModel):
    email: EmailStr
    password: str = Field(
        ..., min_length=6, description="Password must be at least 6 characters"
    )


class UserSignin(BaseModel):
    email: EmailStr
    password: str


class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    mobile: Optional[str] = Field(None, max_length=10)
    picture: Optional[str] = Field(None, description="URL to profile picture")
    country: Optional[str] = Field(None, max_length=10)


class UserResponse(BaseModel):
    id: int
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    mobile: Optional[str]
    picture: Optional[str]
    country: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
