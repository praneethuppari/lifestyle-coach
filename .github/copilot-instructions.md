# Lifestyle Coach: Copilot Instructions

## Mission
Build a personalized meal planning and cooking execution platform that helps users consistently eat food they genuinely want while still meeting nutrition goals and adapting to real life.

This product is not a generic calorie counter. It should feel like a practical AI coach that understands taste, cooking effort, schedule constraints, and adherence patterns.

## Product Context

### Core User Problem
Diet adherence usually fails for four reasons:
- Recommendations do not match the user's real taste preferences.
- Macro goals are disconnected from meals the user actually wants to eat.
- Cooking execution is poorly supported, including prep time, storage, portioning, and timing.
- Plans are brittle and do not adapt well when users skip meals, eat out, or run out of time.

### Product Differentiators
- Taste-first personalization over generic diet templates.
- Strong execution support, not just recipe suggestions.
- Adaptive planning driven by actual user behavior.
- Respect for authentic cuisines instead of flattening recipes into generic "healthy" versions.
- Import and normalization of recipes from external sources, especially Instagram and other creator-driven formats.

## MVP Goal
Deliver an MVP that proves the following loop works end to end:
1. Learn what the user likes.
2. Recommend recipes they are likely to cook.
3. Adjust those recipes to fit nutrition goals.
4. Turn recommendations into a usable weekly plan.
5. Help the user shop, cook, portion, and log outcomes.
6. Learn from what actually happened and improve the next plan.

If a feature does not strengthen this loop, treat it as lower priority.

## MVP Feature Scope

### In Scope
1. Taste profile discovery.
2. Recipe library and tagging.
3. Macro target calculation.
4. Smart recipe recommendations.
5. Recipe customization and scaling.
6. Weekly meal plan builder.
7. Shopping list generation.
8. Cooking execution guidance.
9. Post-cook time and effort tracking.
10. Instagram and external recipe import.
11. Automatic macro logging.
12. Schedule input and conflict detection.
13. User authentication and profile management.

### Out of Scope Unless Explicitly Requested
- Social features.
- Community feeds.
- Gamification.
- Enterprise nutrition coaching workflows.
- Full medical-grade nutrition or disease-treatment claims.
- Deep wearable integrations.
- Extensive marketplace or creator monetization systems.

## Product Principles
Use these principles to resolve ambiguity:

1. Taste beats theory.
If a plan is nutritionally perfect but the user will not cook or eat it, the plan has failed.

2. Execution matters as much as planning.
Time, skill, cleanup, storage life, and portioning are first-class product concerns.

3. Adapt to reality.
The system should recover gracefully when the user deviates from the plan.

4. Authenticity matters.
Do not over-sanitize culturally specific recipes into bland macro templates.

5. Be transparent with uncertainty.
Nutrition estimates, imported recipe parsing, and time predictions should be presented as estimates when precision is not guaranteed.

6. Keep trust high.
Users should understand why something was recommended, adjusted, or rescheduled.

7. Simplicity first.
"Make everything as simple as possible, but not simpler." — Einstein. Prefer the simplest design that correctly serves the use case. Do not add indexes, abstractions, caching layers, or architectural complexity before there is a demonstrated need for them. Premature optimization and over-engineering are bugs, not features.

## Instructions For AI-Assisted Development
When implementing features, act like a senior product-minded software engineer.

### Before Building
For any non-trivial feature, first clarify or infer the following:
- The user problem being solved.
- The specific MVP value.
- The minimum shippable version.
- The main edge cases and failure modes.
- The data entities and state transitions involved.

Move in the order of:
1. architectural design and data modeling
2. code quality and correctness
3. tests and documentation
4. cleanup and refinement

If the task is ambiguous, prefer the simplest version that supports the MVP loop and state your assumptions clearly.

### For Major Decisions
For architectural changes, schema design, major dependencies, or workflow design, evaluate at least three approaches and choose the one that best balances:
- Readability.
- Maintainability.
- Delivery speed.
- Performance where it materially matters.

Do not create artificial analysis overhead for small edits. This requirement applies to meaningful decisions, not trivial refactors.

### Default Delivery Expectations
Unless the user explicitly asks for something smaller, each meaningful feature should include:
- Implementation.
- Input validation and failure handling.
- Tests appropriate to the change.
- Documentation updates.
- A short decision note describing key tradeoffs.

### Definition Of Done
A task is not complete unless these are addressed when relevant:
- The feature works for the expected user flow.
- Obvious edge cases are handled.
- Tests cover the critical path and edge cases, and all tests pass.
- Documentation reflects the current behavior.
- New complexity is justified.

## Product Delivery Guidance

### Prioritize These Questions
When designing or reviewing a feature, ask:
- Does this help the user decide what to eat?
- Does this increase the chance they will actually cook it?
- Does this make macro adherence easier without making food less appealing?
- Does this help the system recover when the week goes off-plan?
- Does this preserve user trust?

### UX Expectations
- Favor clear workflows over dense dashboards.
- Show actionable next steps, not just data.
- Make scheduling, prep, leftovers, and storage visible.
- Keep nutrition guidance practical and understandable.
- Explain recommendation logic in plain language.

### Domain Guardrails
- Do not present nutrition estimates as medical advice.
- Flag imported recipe data as potentially incomplete until normalized.
- Preserve source attribution and legal compliance when importing external content.
- Treat user health, preference, and schedule data as sensitive.

## Local Development Setup

The backend uses a Python virtual environment located at `/Users/praneethuppari/Documents/playground/lifestyle-coach/.venv`.

**Before running any terminal command in the backend**, the virtual environment must be active. Activate it with:
```
source /Users/praneethuppari/Documents/playground/lifestyle-coach/.venv/bin/activate
```
All backend commands — `alembic`, `pytest`, `uvicorn`, `ruff`, `pip`, etc. — require this to be active first.

## Engineering Standards

### General Standards
- Write clean, readable, maintainable code.
- Follow DRY, but do not over-abstract early.
- Validate inputs early and fail with informative errors.
- Use meaningful names.
- Avoid hardcoded values; use constants, configuration, or typed domain models.
- Keep modules cohesive and responsibilities clear.
- Prefer simple solutions over clever ones.
- Preserve existing patterns unless there is a clear reason to improve them.
- Add comments only where the logic would otherwise be hard to follow.

### Documentation Standards
- Add docstrings or equivalent language-appropriate API documentation for public functions, classes, and complex modules.
- Keep the project README current as the project evolves.
- Maintain feature-level notes that capture implementation decisions, issues encountered, and how they were resolved.
- Maintain a common problems knowledge base for recurring issues that future contributors or AI agents may hit.

If the repository does not yet have a documentation structure, prefer:
- `docs/features/<feature-name>.md` for feature notes.
- `docs/knowledge-base/common-issues.md` for repeated troubleshooting knowledge.

#### Feature Documentation Template

Each feature branch must have a corresponding `docs/features/<feature-name>.md`. The file name should match the branch name without the `feature/` prefix (e.g. `feature/manual-recipe-import` → `docs/features/manual-recipe-import.md`).

The doc is a living document — start it when the branch starts and update it as each checklist item is completed. It does not need to be perfect before work begins.

Required sections:

```markdown
# <Feature Name>

## What This Feature Does
One paragraph. The user problem being solved and the MVP value delivered.

## Endpoints
List every endpoint added or modified by this branch.
For each: method, path, brief description, request shape, response shape, error cases.

## Schema and Model Changes
List every Pydantic schema and SQLAlchemy model added or changed.
Include migration file name if a DB migration was added.

## Architecture Notes
Describe any non-obvious structure, layer responsibilities, or patterns introduced.
Reference the layer table (Route / Service / Repository / Schema) if helpful.

## Design Decisions
Key choices made and why. Anything that was debated or could have gone another way.

## Test Coverage
What is tested and where. Note any important cases explicitly covered (edge cases, error paths).

## What Is Explicitly Deferred
Anything intentionally left out of this branch, with a note on which future branch will handle it.
```

Omit a section only if it is genuinely not applicable (e.g. a docs-only branch has no Endpoints section). Do not leave sections blank — either fill them or remove them.

### Testing Standards
- Prefer test-driven development when it is practical.
- Add unit tests for core logic.
- Add integration tests where system boundaries or workflows matter.
- Test error states and validation paths, not just happy paths.

### Language And Platform Conventions
- JavaScript and TypeScript: follow Airbnb style guidance unless the repository already uses a different enforced style.
- Python: follow PEP 8.
- CSS: follow BEM where it fits the codebase.
- HTML: use semantic, accessible markup.
- SQL: follow a consistent readable style, preferably Simon Holywell's conventions.
- APIs: use clear RESTful patterns unless the existing system uses a different standard.

### REST API Endpoint Design Guidelines

#### Foundations: What REST Actually Is

REST (Representational State Transfer) is an architectural style defined by Roy Fielding in his 2000 dissertation. It is not a protocol — it is a set of constraints on top of HTTP. The core HTTP specs that REST builds on are RFC 9110 (HTTP Semantics) and RFC 9112 (HTTP/1.1), which replaced the older RFC 7230–7235 series in 2022.

The six architectural constraints Fielding defined:

1. **Client-Server** — UI concerns and data storage concerns are separated. The client does not know how data is stored; the server does not know how data is rendered.
2. **Stateless** — Every request must contain all information needed to process it. The server holds no client session state. Authentication tokens, pagination cursors, and filters all travel in requests, not server memory.
3. **Cacheable** — Responses must declare themselves as cacheable or not. This allows intermediaries (CDNs, proxies) to serve cached responses and reduce load.
4. **Uniform Interface** — This is the most important constraint in practice. It has four sub-rules:
   - Resources are identified by URIs. `/recipes/42` names a thing; it does not describe an action.
   - Resources are manipulated through representations. The server sends a JSON/XML/etc. representation of the resource, not the resource itself.
   - Messages are self-descriptive. A request or response contains enough information to understand how to process it (content-type, method, status code).
   - HATEOAS (Hypermedia as the Engine of Application State): responses can include links to related actions. Most production JSON APIs skip this in practice.
5. **Layered System** — The client cannot tell if it is talking directly to the server or through a load balancer, cache, or gateway. This enables scalable infrastructure without client changes.
6. **Code on Demand** (optional) — Servers can send executable code to clients (e.g., JavaScript). Rarely relevant for JSON APIs.

Most "REST APIs" in the industry implement constraints 1–4 well and treat 5–6 as infrastructure concerns. A fully HATEOAS-compliant API is rare outside academic contexts.

#### Resource Naming

- Use nouns for resources, not verbs.
  - Good: `GET /recipes`, `DELETE /users/42`
  - Bad: `GET /getRecipes`, `POST /deleteUser`
- Use plural resource names consistently: `/recipes`, `/ingredients`, `/users`.
- Keep URLs readable, lowercase, and hyphen-separated if needed: `/meal-plans`.
- Avoid exposing database structure or ORM relationships in routes.
- Design endpoints around domain semantics and API consumer intent, not internal implementation.
- Use consistent identifier formats across the API (UUIDs preferred for user-facing IDs).

#### HTTP Methods

Use HTTP methods to express the action, not the URL:

| Method | Semantics | Notes |
|--------|-----------|-------|
| `GET` | Read | Safe and idempotent. Never causes side effects. |
| `POST` | Create | Not idempotent. Creates a new resource. |
| `PUT` | Full replace | Idempotent. Replaces the entire resource. |
| `PATCH` | Partial update | Updates only the fields provided. Prefer over PUT for partial edits. |
| `DELETE` | Remove | Idempotent. Repeated deletes should return 404, not error. |

#### Nesting: When and How Deep

The single rule: **nest a resource under a parent only if the child cannot exist meaningfully without that parent and is always accessed in that context.**

- Test: "Would a consumer ever browse this resource without knowing its parent?" If yes, keep it flat.
- Maximum nesting depth is 2 levels (`/parent/{id}/child/{id}`). Deeper than that becomes difficult to read, maintain, and authorize.
- A resource that can exist independently should always have a top-level endpoint, even if it also appears nested.

**Independent existence → flat top-level endpoint:**
```
GET  /recipes          # recipes stand alone
GET  /ingredients      # ingredients stand alone
```

**No independent existence → nested under parent:**
```
GET    /recipes/{id}/ingredients        # a recipe-ingredient only exists within a recipe
POST   /recipes/{id}/ingredients        # add an ingredient to a specific recipe
PATCH  /recipes/{id}/ingredients/{ingredient_id}   # edit quantity/unit/prep notes
DELETE /recipes/{id}/ingredients/{ingredient_id}   # remove from recipe
```

This mirrors established API patterns: Spotify's `GET /playlists/{id}/tracks` (a playlist entry only exists within a playlist) and GitHub's `GET /repos/{owner}/{repo}/issues/{number}/comments` (a comment only exists within an issue).

Nesting also implies authorization inheritance: a request to `/recipes/{id}/ingredients` should verify ownership of the recipe before exposing its ingredients.

**Containment vs. endpoint granularity are separate decisions.** The nesting rule answers "does this resource need its own endpoints?" — but even when a sub-resource has no independent existence, that does not automatically mean it needs individual CRUD endpoints. Ask the second question: *what is the natural unit of work for the consumer?*

If the consumer always edits the parent and its children together as one document (e.g., a recipe form that submits title, instructions, and ingredients at once), then embedding the child as a field in the parent's POST/PATCH payload is cleaner than separate nested endpoints. Full-replacement semantics keep the server logic simple: if the child array is present in the payload, delete the current set and insert the new set in one transaction; if absent, leave it untouched.

Use nested endpoints only when the sub-resource is large enough or accessed frequently enough in isolation to justify the extra API surface. If no real user action maps to "add one ingredient to a recipe independently of everything else," the endpoint should not exist.

For many-to-many relationships, prefer a dedicated join resource at the top level alongside nested access:
```
GET /recipes/{id}/ingredients     # nested access
GET /ingredients                  # top-level browse
```

#### Query Parameters vs Path Segments

- Use query parameters for filtering, sorting, searching, and pagination — these are *properties* of the resource, not part of its identity.
  - Good: `GET /recipes?cuisine=japanese&max_time=30`
  - Bad: `GET /recipes/japanese/quick`
- Do not use query parameters to switch between fundamentally different resource types (see below).

#### Separating User-Owned Resources from System Catalogs

When an API has both user-owned resources (full CRUD, scoped to the authenticated user) and a read-only system catalog (shared across all users), these must be **separate endpoints**, not one endpoint with a `?source=personal|global` query parameter.

A query parameter is correct for filtering *properties* of a homogeneous resource. It is wrong when it switches between resources that differ in:
- **Authorization** — catalog items cannot be mutated by users; a unified endpoint forces authorization branching inside handler logic instead of at the routing layer.
- **Ownership semantics** — personal resources have an `owner_id`; catalog resources are system-owned.
- **CRUD surface** — a unified endpoint implies all verbs might work, which misleads consumers.
- **Maintainability** — a single handler serving two resource types with different rules grows complex and hard to reason about.

Use a `/catalog` namespace for system-owned, read-only resources:

```
# User-owned — full CRUD, auth required, scoped to authenticated user
GET    /recipes
POST   /recipes
GET    /recipes/{id}
PATCH  /recipes/{id}
DELETE /recipes/{id}

GET    /ingredients
POST   /ingredients
GET    /ingredients/{id}
PATCH  /ingredients/{id}
DELETE /ingredients/{id}

# System catalog — read-only, auth still required, not user-scoped
GET /catalog/recipes
GET /catalog/recipes/{id}
GET /catalog/recipes/{id}/ingredients

GET /catalog/ingredients
GET /catalog/ingredients/{id}
```

The `/catalog` prefix communicates read-only intent at the URL level. A consumer reading the API surface immediately knows they cannot POST to `/catalog/recipes`. Authorization middleware can enforce read-only on the entire `/catalog/*` path in one rule.

If combined search across personal and catalog resources is needed, that is a distinct use case deserving its own endpoint:
```
GET /search/recipes?q=chicken&source=all
```
Search is not the same as CRUD browse and should not be conflated with it.

#### Additional Rules

- Nested routes imply authorization and context inheritance. Always validate parent ownership before processing child operations.
- Do not surface the `is_global` flag or other schema implementation details as URL segments or query parameters. The URL expresses domain semantics.
- Use standard HTTP status codes: `200 OK`, `201 Created`, `204 No Content`, `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `422 Unprocessable Entity`, `409 Conflict`.
- Return `404` for resources that do not exist or that the authenticated user is not permitted to know exist (prefer over `403` to avoid leaking resource existence to unauthorized callers).
- Rule of thumb:
  - If a resource can exist independently, give it a top-level endpoint.
  - If it only exists within a parent, nest it under that parent.
  - If it requires different CRUD semantics or authorization, give it a separate namespace.

### Dependency Guidance
- Prefer proven, well-maintained libraries when they materially reduce complexity or risk.
- Do not add dependencies for small problems that can be solved cleanly in existing code.
- When adding a dependency, justify why it is better than a lightweight in-house solution.

### Git and Commit Standards

**Never commit without explicit user approval of the commit message.**
Always stage changes and present the proposed commit message for review. Only run `git commit` after the user confirms the message. Do not amend, squash, rebase, push, or run any destructive git operation without explicit instruction.

**Commits must be small, focused units of work.** Each commit should represent one logical change that could be reviewed, reverted, or cherry-picked independently. Industry standard guidance:

- One commit per logical concern: schema change, new endpoint, test coverage, docs update — not all at once.
- If a task requires multiple types of changes (migration + schema + route + tests), commit them as separate steps unless they are genuinely atomic (e.g. a migration and the model change it reflects are always committed together).
- Write commit messages in the imperative mood, present tense: `Add RecipeInstructionStep schema` not `Added` or `Adding`.
- Message format: a short subject line (50 chars or less), optionally followed by a blank line and a body explaining *why*, not *what*.
- Do not bundle unrelated fixes into a commit just because they were touched during a session.


## Implementation Guardrails For AI Tools
- Do not invent product requirements that were not asked for.
- Do not expand scope just because a broader system could be imagined.
- Do not introduce breaking architecture changes without a concrete reason.
- Do not optimize prematurely.
- Do not add speculative abstractions for future features that do not exist yet.
- Do not silently change behavior that affects nutrition calculations, scheduling logic, or imported recipe interpretation without documenting it.

## Preferred Working Style For Copilot
- Be proactive, but stay within MVP priorities.
- Surface assumptions explicitly.
- Recommend simpler iterations before complex systems.
- When reviewing code or plans, focus first on correctness, trust, user value, and maintainability.
- When there is a tradeoff between theoretical completeness and shipping a useful MVP, bias toward the useful MVP unless the shortcut would create trust or data integrity risks.

## Current North Star
The first versions of this product should prove that personalized, realistic meal planning can outperform generic diet apps because the system understands:
- what the user actually wants to eat,
- what they are realistically able to cook,
- what nutrition target they are trying to hit, and
- how to adapt when the plan meets real life.


