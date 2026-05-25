from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from lifestyle_coach_api.core.config import get_settings
from lifestyle_coach_api.core.database import get_db
from lifestyle_coach_api.repositories.users import UserRepository
from lifestyle_coach_api.schemas.auth import RegisterRequest, TokenResponse
from lifestyle_coach_api.services.users import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_user_service(db: Annotated[Session, Depends(get_db)]) -> UserService:
    return UserService(UserRepository(db))


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
def register(
    body: RegisterRequest,
    service: Annotated[UserService, Depends(get_user_service)],
) -> TokenResponse:
    settings = get_settings()
    token = service.register(body, settings.secret_key, settings.access_token_expire_minutes)
    return TokenResponse(access_token=token)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in and receive a JWT access token",
)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: Annotated[UserService, Depends(get_user_service)],
) -> TokenResponse:
    """Accepts OAuth2 password form data.

    The `username` field carries the user's email address — this is an
    OAuth2 spec constraint, not a product decision.
    """
    settings = get_settings()
    token = service.authenticate(
        email=form_data.username,
        password=form_data.password,
        secret_key=settings.secret_key,
        expire_minutes=settings.access_token_expire_minutes,
    )
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=token)
