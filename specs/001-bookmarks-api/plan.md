# Implementation Plan: Bookmarks API

**Branch**: `001-bookmarks-api` | **Date**: 2026-10-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-bookmarks-api/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

A single-user REST API to save, list (newest first, paged), filter by tag and delete bookmarks,
with no duplicate links after normalization. Built as a FastAPI service with Pydantic request and
response models, PostgreSQL storage through SQLAlchemy 2.0 (sync, psycopg 3), and Alembic
migrations. Uniqueness is enforced by a unique index on the normalized link, so it holds under
concurrent saves; tags are a normalized `text[]` column with a GIN index for filtering. All errors
use one JSON envelope. Tests run with pytest against the real `bookmarks_test` database from the
existing `docker-compose.yml`.

## Technical Context

**Language/Version**: Python 3.11+ (tested on 3.12 and 3.13)

**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Alembic, psycopg 3 (binary), Uvicorn; tests:
pytest, httpx2. Each is justified in [research.md](research.md) (Constitution IV).

**Storage**: PostgreSQL (18 via the repo's `docker-compose.yml`); databases `bookmarks` (dev) and
`bookmarks_test` (tests), URLs as in `.env.example`

**Testing**: pytest; unit tests for pure functions (link and tag normalization); integration tests
through the HTTP API against the real test database (Constitution II)

**Target Platform**: Linux, macOS or Windows developer machine; Linux server

**Project Type**: web-service (REST API)

**Performance Goals**: Interactive use by one person; list and filter requests answer in well
under a second for 100k bookmarks (indexed queries)

**Constraints**: Page size at most 100; link at most 2048 characters; title at most 200; at most
10 tags of 1 to 30 characters

**Scale/Scope**: One user, up to about 100k bookmarks; 3 endpoints

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | How the plan complies | Status |
| --- | --- | --- |
| I. Typed API Contracts | Pydantic models for the create request, the list query (`BookmarkListQuery`, T037), bookmark, page and error responses; FastAPI generates OpenAPI from them; no untyped dicts cross the boundary | Pass |
| II. Real-Database Testing | Integration tests hit `bookmarks_test` on real PostgreSQL; schema created by running the Alembic migrations; tables truncated before each test; no database mocks | Pass |
| III. Consistent Error Shape | One envelope `{"error": {"code", "message", "details"}}` for validation (422), not found (404) and duplicate (409), installed as global exception handlers | Pass |
| IV. Minimal Dependencies | Six runtime/test dependencies, each justified in research.md; standard library used for link normalization and config | Pass |
| V. Tests Ship With Every Feature | Each user story's tasks include tests for its acceptance scenarios; suite must pass before converge | Pass |
| VI. Cursor Pagination | `GET /bookmarks` uses keyset paging on `(created_at, id)` with an opaque `next_cursor`; no offset in the API or queries; a test pages through all results while bookmarks are added between requests | Pass |

Post-design re-check (after Phase 1): Pass. The data model, contract and quickstart introduce no
new dependencies or untyped interfaces.

## Project Structure

### Documentation (this feature)

```text
specs/001-bookmarks-api/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── openapi.yaml
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
pyproject.toml           # project metadata, dependencies, pytest config
alembic.ini
migrations/
├── env.py
└── versions/
    └── 0001_create_bookmarks.py

src/bookmarks_api/
├── __init__.py
├── main.py              # FastAPI app factory, router and exception handlers
├── config.py            # DATABASE_URL from the environment (defaults match .env.example)
├── db.py                # engine and session dependency
├── models.py            # SQLAlchemy table mapping
├── schemas.py           # Pydantic request/response models
├── normalize.py         # link and tag normalization (pure functions)
├── errors.py            # error envelope, domain exceptions and handlers
├── repository.py        # queries: create, list/filter with total, delete
└── routes.py            # /bookmarks endpoints

tests/
├── conftest.py          # test database setup (migrations, truncate per test), API client
├── unit/
│   └── test_normalize.py
└── integration/
    ├── test_create_bookmark.py
    ├── test_list_bookmarks.py
    ├── test_filter_by_tag.py
    ├── test_delete_bookmark.py
    └── test_errors.py
```

**Structure Decision**: Single project (`src/` layout) with one Python package, Alembic
migrations at the root and tests split into unit and integration. There is no frontend.

## Complexity Tracking

No constitution violations to justify.
