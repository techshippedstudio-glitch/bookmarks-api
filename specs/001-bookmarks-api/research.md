# Research: Bookmarks API

All Technical Context items were resolved; there were no open NEEDS CLARIFICATION markers after
`/speckit-clarify`. Each decision below records what was chosen, why, and what else was
considered.

## Web framework

- **Decision**: FastAPI.
- **Rationale**: The plan input asks for FastAPI with Pydantic models. FastAPI derives request
  validation and the OpenAPI document from Pydantic models, which satisfies Constitution I with no
  extra code.
- **Alternatives considered**: Flask with marshmallow (two libraries for what FastAPI does in one),
  Django REST Framework (far heavier than three endpoints need).

## Database access: SQLAlchemy 2.0, synchronous, psycopg 3

- **Decision**: SQLAlchemy 2.0 Core/ORM in synchronous mode with the psycopg 3 driver
  (`psycopg[binary]`).
- **Rationale**: Requested in the plan input. Sync endpoints run in FastAPI's thread pool, which is
  ample for one user and keeps the code and tests simpler than async. psycopg 3 is the maintained
  PostgreSQL driver; the binary extra avoids needing a C compiler.
- **Alternatives considered**: async SQLAlchemy with asyncpg (more moving parts for no benefit at
  this scale); raw psycopg without SQLAlchemy (hand-written mapping and no Alembic integration).
- **Note**: `.env.example` uses plain `postgresql://` URLs. `config.py` rewrites them to
  `postgresql+psycopg://` so SQLAlchemy uses psycopg 3 instead of looking for psycopg2.

## Migrations

- **Decision**: Alembic, one initial revision; the test suite runs `alembic upgrade head` against
  `bookmarks_test` at session start.
- **Rationale**: Requested in the plan input; using the same migrations for tests guarantees tests
  run on the real schema, including indexes and constraints (Constitution II).
- **Alternatives considered**: `metadata.create_all()` in tests (would not catch migration bugs).

## Preventing duplicate links

- **Decision**: Store the link as given (`url`) and a normalized form (`url_normalized`) with a
  unique index. Insert with `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING ...`; if
  nothing is returned, look up the existing row and raise a duplicate error carrying its id.
- **Rationale**: The database guarantees uniqueness even when two saves race (spec edge case);
  `ON CONFLICT` avoids relying on catching exceptions mid-transaction.
- **Alternatives considered**: check-then-insert in application code (races under concurrency);
  catching `IntegrityError` (works, but leaves the transaction aborted and is noisier).

## Link normalization

- **Decision**: Standard library `urllib.parse`: lowercase scheme and host, drop default ports
  (80 for http, 443 for https), strip one or more trailing slashes from the path (an empty path
  stays empty), drop the fragment, keep the query string exactly. Validation requires scheme http
  or https and a host.
- **Rationale**: Matches the clarified rules exactly with no dependency (Constitution IV). It is a
  pure function, so it gets fast unit tests.
- **Alternatives considered**: Pydantic `HttpUrl` (it rewrites the link, for example adding a
  trailing slash to bare hosts, which conflicts with storing the link as given and with our
  trailing-slash rule); third-party URL normalizers (extra dependency, different rules).

## Tags storage and filtering

- **Decision**: A `tags text[]` column on `bookmarks`, normalized before insert, with a GIN index;
  filter with `tags @> ARRAY[:tag]`. A check constraint limits the array to 10 elements.
- **Rationale**: Tags have no attributes of their own in this version and are never edited
  independently, so a join table adds two tables and joins for no gain. PostgreSQL arrays with a
  GIN index make the containment filter fast.
- **Alternatives considered**: `tags` and `bookmark_tags` tables (normalized, worth it once tags
  gain attributes or renames); a comma-separated string (cannot be indexed or validated well).

## Ordering and paging

- **Decision**: Order by `created_at DESC, id DESC` (the id breaks ties for bookmarks saved in the
  same instant). Limit/offset paging, default 20, max 100; the response includes `total` from a
  `COUNT(*)` with the same filter. Index on `(created_at DESC, id DESC)`.
- **Rationale**: Matches the clarification; offset paging is simple for clients and fine at the
  stated scale.
- **Alternatives considered**: cursor (keyset) paging, better for very large or fast-changing lists;
  noted as a future change if scale grows.

## Error envelope

- **Decision**: `{"error": {"code": str, "message": str, "details": object | null}}`. Codes:
  `validation_error` (422), `not_found` (404), `duplicate_url` (409, `details.existing_id`).
  FastAPI's `RequestValidationError` and `HTTPException` handlers are replaced so framework errors
  use the same shape; unexpected errors return 500 `internal_error` without internals.
- **Rationale**: Constitution III.
- **Alternatives considered**: RFC 9457 problem details (a fine standard, but the constitution
  names a `code`/`message` shape).

## Configuration

- **Decision**: Read `DATABASE_URL` from the environment, defaulting to the dev URL in
  `.env.example`; tests read `TEST_DATABASE_URL` with the matching default.
- **Rationale**: No settings library needed (Constitution IV); defaults make the local setup work
  without exporting anything.
- **Alternatives considered**: pydantic-settings or python-dotenv (an extra dependency for two
  variables).

## Dependencies and justification (Constitution IV)

| Dependency | Used for | Why not avoid it |
| --- | --- | --- |
| fastapi | HTTP API, validation, OpenAPI | Required by the plan input |
| uvicorn | Running the app locally | FastAPI needs an ASGI server |
| sqlalchemy | Queries and mapping | Required by the plan input; Alembic builds on it |
| alembic | Schema migrations | Required by the plan input |
| psycopg[binary] | PostgreSQL driver | Required to talk to PostgreSQL |
| pytest (test) | Test runner | De facto standard; far less code than unittest for fixtures |
| httpx2 (test) | FastAPI `TestClient` | Required by FastAPI's test client (current Starlette deprecates plain httpx for it) |
