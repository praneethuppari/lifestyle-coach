# Backend Framework Decision

## Decision

Use FastAPI for the initial backend service.

## Why FastAPI

FastAPI is the best fit for the current stage of the product because it keeps the service thin while still giving us a clean long-term path for modular API growth.

It aligns with the team's existing Python familiarity, which lowers initial delivery risk for the first backend capabilities such as recipe import normalization, meal-plan APIs, scheduling logic, and adaptation workflows.

It also keeps the codebase maintainable by leaning on typed request and response models instead of requiring a heavier framework architecture before the domain has stabilized.

## Alternatives Considered

### Django REST Framework

Strong productivity, but it brings more framework surface area than this API-first MVP needs today.

### Spring Boot

Excellent long-term platform for large teams, but too heavy for the current scope and would slow early iteration.

### NestJS

A strong second choice if full-stack JavaScript alignment becomes more important later, but it adds language transition cost now without enough offsetting value for the first backend milestone.

## Initial Scope

Included:

- Single FastAPI service
- Environment-based settings
- Versioned API router
- Health endpoint
- Minimal API smoke test

Deferred until a real feature requires them:

- Database and migrations
- Authentication and authorization
- Background jobs
- Container orchestration
- Cross-service architecture
- Shared frontend-backend schema generation

## Follow-on Trigger

Add PostgreSQL and migrations only when the first persistent backend feature is implemented.

**Resolved.** PostgreSQL, SQLAlchemy, Alembic, and the `recipes` table were added when recipe storage became the next required feature. See [database-setup.md](database-setup.md) for full setup and architecture details.