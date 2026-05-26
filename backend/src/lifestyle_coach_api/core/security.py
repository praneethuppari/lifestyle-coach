"""Low-level security utilities: password hashing and JWT encoding/decoding.

These are pure functions with no FastAPI or database dependencies.
The routes and dependencies are responsible for wiring settings in.
"""

import uuid
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

_password_hash = PasswordHash.recommended()

# Used in verify_password when no hash exists — prevents timing attacks that
# could let an attacker discover which email addresses are registered.
_DUMMY_HASH: str = _password_hash.hash("__lifestyle_coach_dummy__")


def hash_password(plain: str) -> str:
    """Return an Argon2 hash of the given plaintext password."""
    return _password_hash.hash(plain)


def verify_password(plain: str, hashed: str | None) -> bool:
    """Return True if plain matches hashed.

    If hashed is None (user has no password set), a dummy hash is verified
    instead so the call takes constant time regardless of whether the user
    exists.
    """
    if hashed is None:
        _password_hash.verify(plain, _DUMMY_HASH)
        return False
    return _password_hash.verify(plain, hashed)


def create_access_token(
    user_id: uuid.UUID,
    secret_key: str,
    expire_minutes: int,
) -> str:
    """Encode a signed JWT containing the user's ID as the subject claim."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, secret_key, algorithm="HS256")


def decode_access_token(token: str, secret_key: str) -> uuid.UUID | None:
    """Decode and verify a JWT, returning the user UUID or None if invalid."""
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        sub = payload.get("sub")
        if sub is None:
            return None
        return uuid.UUID(sub)
    except (jwt.InvalidTokenError, ValueError):
        return None
