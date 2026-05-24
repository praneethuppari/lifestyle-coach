from lifestyle_coach_api.core.errors import ConflictError
from lifestyle_coach_api.models.user import User
from lifestyle_coach_api.repositories.users import UserRepository
from lifestyle_coach_api.schemas.users import UserCreate


class UserService:
    """Business logic for user registration and lookup."""

    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    def create(self, data: UserCreate) -> User:
        existing = self._repo.find_by_email(data.email)
        if existing:
            raise ConflictError(
                detail=f"A user with email '{data.email}' already exists.",
                code="USER_ALREADY_EXISTS",
            )
        user = User(email=data.email, display_name=data.display_name)
        return self._repo.create(user)
