import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Request body for POST /auth/register."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = Field(default=None, max_length=100)


class TokenResponse(BaseModel):
    """Returned by both /auth/register and /auth/login."""

    access_token: str
    token_type: str = "bearer"


class AuthenticatedUserResponse(BaseModel):
    """The caller's own profile, returned alongside the token on register."""

    id: uuid.UUID
    email: str
    display_name: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
