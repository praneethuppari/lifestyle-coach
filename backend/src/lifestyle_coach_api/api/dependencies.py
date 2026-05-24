import uuid
from typing import Annotated

from fastapi import Header


def get_current_user_id(x_user_id: Annotated[uuid.UUID, Header()]) -> uuid.UUID:
    """Extract the caller's user ID from the X-User-Id request header.

    This is a temporary pre-auth stub. In feature/basic-auth, replace this
    dependency with JWT token extraction — all call sites stay the same.

    FastAPI returns 422 automatically if the header is absent or not a valid UUID.
    """
    return x_user_id
