import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from lifestyle_coach_api.core.config import get_settings
from lifestyle_coach_api.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user_id(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> uuid.UUID:
    """Extract and verify the caller's user ID from the Bearer token.

    Raises 401 if the token is missing, expired, or has an invalid signature.
    All protected routes depend on this function — the call site does not
    change when auth is upgraded (e.g. refresh tokens, scopes).
    """
    settings = get_settings()
    user_id = decode_access_token(token, settings.secret_key)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id
