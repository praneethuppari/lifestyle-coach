# Database Setup

## Decision

Use PostgreSQL 16 with SQLAlchemy 2 (ORM), Alembic (migrations), and psycopg v3 (driver).

## Stack

| Layer | Tool | Version |
|---|---|---|
| Database | PostgreSQL | 16 (Homebrew) |
| Python driver | psycopg | >=3.2 |
| ORM | SQLAlchemy | >=2.0 |
| Migrations | Alembic | >=1.15 |

## Why This Stack

- **SQLAlchemy 2** — modern async-ready ORM with full type support via `Mapped` and `mapped_column`. Keeps models readable and typed without boilerplate.
- **Alembic** — the standard migration tool for SQLAlchemy. Autogenerates migration scripts by diffing models against the live database.
- **psycopg v3** — the modern PostgreSQL driver. Replaces the older `psycopg2`, with better async support and a cleaner API.
- **PostgreSQL** — robust, widely supported, and required for the `ARRAY` column type used on recipe tags.

## Local Setup

### 1. Install and start PostgreSQL

```bash
brew install postgresql@16
brew services start postgresql@16
```

### 2. Create the database and user

```bash
psql postgres
```

```sql
CREATE USER lifestyle_coach WITH PASSWORD 'localpassword';
CREATE DATABASE lifestyle_coach_db OWNER lifestyle_coach;
GRANT ALL PRIVILEGES ON DATABASE lifestyle_coach_db TO lifestyle_coach;
\q
```

### 3. Configure the environment

In `backend/.env`:

```
DATABASE_URL=postgresql+psycopg://lifestyle_coach:localpassword@localhost:5432/lifestyle_coach_db
```

The `postgresql+psycopg` prefix tells SQLAlchemy to use the psycopg v3 driver.

### 4. Install dependencies

```bash
cd backend
pip install -e ".[dev]"
```

### 5. Apply migrations

```bash
alembic upgrade head
```

### 6. Verify

```bash
psql postgresql://lifestyle_coach:localpassword@localhost:5432/lifestyle_coach_db
\dt
```

Expected output: `alembic_version` and `recipes` tables.

## Architecture

### Session management (`core/database.py`)

- `create_engine` builds one engine for the app's lifetime with `pool_pre_ping=True` to handle stale connections.
- `SessionLocal` is a session factory (`autocommit=False`, `autoflush=False`) — the caller controls transaction boundaries.
- `get_db()` is a FastAPI dependency that opens a session per request, yields it to the route, then closes it in a `finally` block. The connection pool is shared across requests so this is not wasteful.
- `Base` is the SQLAlchemy declarative base all models inherit from.

### Migrations (`alembic/`)

- `alembic/env.py` pulls the database URL from `get_settings()` at runtime — no credentials are hardcoded anywhere.
- `alembic/env.py` imports `lifestyle_coach_api.models` to ensure all models are registered with `Base.metadata` before autogenerate runs.
- `alembic.ini` sets `prepend_sys_path = src` so Alembic can import the application package.

### Adding a new model

1. Create the model in `src/lifestyle_coach_api/models/<name>.py` inheriting from `Base`.
2. Add it to `src/lifestyle_coach_api/models/__init__.py`.
3. Run `alembic revision --autogenerate -m "describe change"`.
4. Run `alembic upgrade head`.

## Current Tables

### `recipes`

Stores recipe data including source attribution, cooking metadata, per-serving macros, and string array tags.

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key, auto-generated |
| `title` | VARCHAR(255) | Required |
| `description` | TEXT | Optional |
| `source_url` | VARCHAR(2048) | Where the recipe came from |
| `source_type` | VARCHAR(50) | e.g. `manual`, `instagram`, `url` |
| `is_verified` | BOOLEAN | False until normalized/confirmed |
| `prep_time_minutes` | INTEGER | Optional |
| `cook_time_minutes` | INTEGER | Optional |
| `servings` | INTEGER | Optional |
| `calories` | NUMERIC(7,2) | Per serving |
| `protein_g` | NUMERIC(7,2) | Per serving |
| `carbs_g` | NUMERIC(7,2) | Per serving |
| `fat_g` | NUMERIC(7,2) | Per serving |
| `tags` | ARRAY(VARCHAR) | e.g. `["italian", "high-protein"]` |
| `created_at` | TIMESTAMPTZ | Auto-set on insert |
| `updated_at` | TIMESTAMPTZ | Auto-updated on change |

### `alembic_version`

Alembic-managed table. Stores the revision ID of the last applied migration. Never edit manually.
