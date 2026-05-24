from sqlalchemy import select
from sqlalchemy.orm import Session

from lifestyle_coach_api.models.user import User


class UserRepository:
    """Data access for the User entity."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def find_by_email(self, email: str) -> User | None:
        return self._db.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

    def create(self, user: User) -> User:
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user
