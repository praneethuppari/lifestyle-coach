# Lifestyle Coach Backend

Minimal FastAPI scaffold for local development.

## Requirements

- Python 3.11+

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
cp .env.example .env
```

## Run the API

```bash
uvicorn lifestyle_coach_api.main:app --reload --app-dir src
```

The API will be available at `http://127.0.0.1:8000`.

## Verify the scaffold

```bash
pytest
ruff check .
ruff format --check .
```

## Current scope

Included now:

- FastAPI app entrypoint
- Typed environment-based settings
- Versioned API router
- Health endpoint
- Minimal test coverage

Intentionally deferred:

- Database setup
- Authentication
- Background jobs
- Containerization
- Domain-specific modules
