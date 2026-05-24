# Error Handling — RFC 7807 + FastAPI Exception Handler

## The Problem This Solves

Without a centralized error handler, every route would need its own `try/except` block, and every error response would be shaped differently. The frontend can't reliably parse errors if one endpoint returns `{"error": "..."}` and another returns `{"message": "..."}`.

This design solves both problems: one handler for the whole app, one consistent response shape.

---

## The Response Shape — RFC 7807 Problem Details

[RFC 7807](https://www.rfc-editor.org/rfc/rfc7807) is an internet standard that defines a specific JSON shape for error responses:

```json
{
  "type": "about:blank",
  "title": "Conflict",
  "status": 409,
  "detail": "A user with email 'alice@example.com' already exists.",
  "code": "USER_ALREADY_EXISTS"
}
```

| Field | Purpose |
|---|---|
| `type` | A URI pointing to docs about this error type. `"about:blank"` is the default when there's no dedicated doc page. |
| `title` | Human-readable name for the HTTP status class ("Conflict", "Not Found"). |
| `status` | The HTTP status code, repeated inside the body for clients that parse the body without checking the status line. |
| `detail` | A specific, human-readable explanation of what went wrong in this request. |
| `code` | A machine-readable string the frontend uses to branch — show the right message, redirect, etc. |

The response also uses a specific HTTP content type: `application/problem+json` instead of `application/json`. This signals to any HTTP client that understands RFC 7807 that this response follows the standard shape — no guessing required.

### Why `code` exists alongside `status`

HTTP status codes describe the *class* of problem. `409 Conflict` covers every possible conflict — a duplicate email, a scheduling collision, a version mismatch. The frontend needs to know *which* conflict. `code: "USER_ALREADY_EXISTS"` is that specific signal.

```
409 → "something conflicted"
code: USER_ALREADY_EXISTS → "show the 'email already registered' message and link to login"
```

---

## How the Code Is Structured

### 1. Base exception class (`core/errors.py`)

```python
class AppError(Exception):
    def __init__(self, *, status, title, detail, code, type_uri="about:blank"):
        self.status = status
        self.title = title
        self.detail = detail
        self.code = code
        self.type_uri = type_uri
```

This is a plain Python exception. It knows nothing about HTTP or FastAPI — it just carries structured data.

### 2. Typed subclasses for each HTTP status

```python
class ConflictError(AppError):
    def __init__(self, *, detail: str, code: str) -> None:
        super().__init__(status=409, title="Conflict", detail=detail, code=code)

class NotFoundError(AppError):
    def __init__(self, *, detail: str, code: str) -> None:
        super().__init__(status=404, title="Not Found", detail=detail, code=code)
```

Services raise these. They don't know or care about HTTP — they just say "this is a conflict" or "this wasn't found."

### 3. The exception handler (`core/errors.py`)

```python
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
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
```

This is the only place that converts an `AppError` into an HTTP response.

### 4. Registered once in `main.py`

```python
app.add_exception_handler(AppError, app_error_handler)
```

This tells FastAPI: for any `AppError` (or subclass) that propagates out of any route, call this handler instead of the default behavior.

---

## The Execution Flow

```
POST /api/v1/users  {"email": "duplicate@example.com"}
           ↓
  register_user() route runs
           ↓
  service.create() is called
           ↓
  UserRepository.find_by_email() finds an existing user
           ↓
  raise ConflictError(detail="...", code="USER_ALREADY_EXISTS")
           ↓
  Exception propagates up — register_user() is dead, nothing after the raise runs
           ↓
  FastAPI's middleware catches the AppError
           ↓
  app_error_handler() is called
           ↓
  Returns JSONResponse(status_code=409, content={...}, media_type="application/problem+json")
           ↓
  Caller receives the RFC 7807 error body
```

The route function is **never returned to** after the raise. FastAPI's exception handler sits above the entire request cycle — equivalent to a `try/except` that wraps every route, written once.

---

## Why This Is a Good Design

**Separation of concerns.** Services express business failures (`ConflictError`, `NotFoundError`) without knowing anything about HTTP status codes or response shapes. The handler is the only place that translates business errors into HTTP responses.

**One place to change.** If you want to add a field to every error response (e.g. a request trace ID), you change `app_error_handler` once and every endpoint benefits.

**Testable services.** Because services raise plain Python exceptions rather than `HTTPException`, they can be tested in complete isolation with no HTTP machinery at all.

**Consistent frontend contract.** Every error from every endpoint has the same shape. The frontend can have one error-parsing function instead of handling each endpoint's quirks separately.

---

## Adding a New Error Type

One subclass, and it's immediately available everywhere:

```python
class ForbiddenError(AppError):
    def __init__(self, *, detail: str, code: str) -> None:
        super().__init__(status=403, title="Forbidden", detail=detail, code=code)
```

Then raise it from any service:

```python
raise ForbiddenError(
    detail="You do not have permission to modify this recipe.",
    code="RECIPE_NOT_OWNED_BY_USER",
)
```

---

## What FastAPI Handles Automatically (Without This System)

`422 Unprocessable Entity` responses are handled entirely by FastAPI + Pydantic. When a request body fails schema validation (missing required field, wrong type, invalid email format), FastAPI rejects the request before the route function runs and returns a `422`. You never need to raise an error for validation failures — Pydantic is the gate.
