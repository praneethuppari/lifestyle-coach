from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from lifestyle_coach_api.core.database import get_db
from lifestyle_coach_api.repositories.users import UserRepository
from lifestyle_coach_api.schemas.users import UserCreate, UserResponse
from lifestyle_coach_api.services.users import UserService

router = APIRouter(prefix="/users", tags=["users"])


def get_user_service(db: Annotated[Session, Depends(get_db)]) -> UserService:
    return UserService(UserRepository(db))


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register_user(
    body: UserCreate,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    user = service.create(body)
    return UserResponse.model_validate(user)
