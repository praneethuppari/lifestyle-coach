from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ProblemDetail(BaseModel):
    """RFC 7807 Problem Details response body.

    Returned for all application-level errors with Content-Type: application/problem+json.
    """

    type: str
    title: str
    status: int
    detail: str
    code: str


class AppError(Exception):
    """Base class for all application errors.

    Raise a subclass from a service or route; the registered exception handler
    converts it to an RFC 7807 response automatically.
    """

    def __init__(
        self,
        *,
        status: int,
        title: str,
        detail: str,
        code: str,
        type_uri: str = "about:blank",
    ) -> None:
        self.status = status
        self.title = title
        self.detail = detail
        self.code = code
        self.type_uri = type_uri
        super().__init__(detail)


class ConflictError(AppError):
    """409 Conflict — the request cannot be completed due to a state conflict."""

    def __init__(self, *, detail: str, code: str) -> None:
        super().__init__(status=409, title="Conflict", detail=detail, code=code)


class NotFoundError(AppError):
    """404 Not Found — the requested resource does not exist."""

    def __init__(self, *, detail: str, code: str) -> None:
        super().__init__(status=404, title="Not Found", detail=detail, code=code)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """FastAPI exception handler for all AppError subclasses."""
    body = ProblemDetail(
        type=exc.type_uri,
        title=exc.title,
        status=exc.status,
        detail=exc.detail,
        code=exc.code,
    )
    return JSONResponse(
        status_code=exc.status,
        content=body.model_dump(),
        media_type="application/problem+json",
    )
