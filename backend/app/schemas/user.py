"""User and authentication schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr = Field(..., description="User email address")
    username: str = Field(
        ..., min_length=3, max_length=100, description="Unique username"
    )
    full_name: str | None = Field(None, max_length=255, description="User's full name")


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=8, description="User password")


class UserUpdate(BaseModel):
    """User update schema."""

    email: EmailStr | None = None
    username: str | None = Field(None, min_length=3, max_length=100)
    full_name: str | None = Field(None, max_length=255)
    password: str | None = Field(None, min_length=8)
    is_active: bool | None = None


class User(UserBase):
    """User response schema."""

    id: UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: datetime | None

    model_config = {"from_attributes": True}


class UserInDB(User):
    """User schema with hashed password for internal use."""

    hashed_password: str


class Token(BaseModel):
    """JWT token response schema."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data schema."""

    user_id: UUID | None = None
    username: str | None = None


class LoginRequest(BaseModel):
    """Login request schema."""

    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")
