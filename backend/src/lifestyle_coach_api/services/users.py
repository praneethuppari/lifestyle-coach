from lifestyle_coach_api.core.errors import ConflictError
from lifestyle_coach_api.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from lifestyle_coach_api.models.user import User
from lifestyle_coach_api.repositories.users import UserRepository
from lifestyle_coach_api.schemas.auth import RegisterRequest


class UserService:
    """Business logic for user registration and lookup."""

    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    def register(
        self,
        data: RegisterRequest,
        secret_key: str,
        expire_minutes: int,
    ) -> str:
        """Create a new user with a hashed password and return a signed JWT."""
        existing = self._repo.find_by_email(data.email)
        if existing:
            raise ConflictError(
                detail=f"A user with email '{data.email}' already exists.",
                code="USER_ALREADY_EXISTS",
            )
        user = User(
            email=data.email,
            display_name=data.display_name,
            hashed_password=hash_password(data.password),
        )
        user = self._repo.create(user)
        return create_access_token(user.id, secret_key, expire_minutes)

    def authenticate(
        self,
        email: str,
        password: str,
        secret_key: str,
        expire_minutes: int,
    ) -> str | None:
        """Verify credentials and return a signed JWT, or None if invalid.

        Runs verify_password even when the user does not exist so response
        time is constant and does not reveal whether an email is registered.
        """
        user = self._repo.find_by_email(email)
        if not verify_password(password, user.hashed_password if user else None):
            return None
        return create_access_token(user.id, secret_key, expire_minutes)  # type: ignore[union-attr]
