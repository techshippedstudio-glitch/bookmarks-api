# Implementation Plan: Idempotent Duplicate Save

**Branch**: `002-idempotent-duplicate-save` | **Date**: 2026-10-24 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-idempotent-duplicate-save/spec.md`

**Supersedes**: the duplicate-save behavior planned in
[specs/001-bookmarks-api](../001-bookmarks-api/plan.md) (its research decision "Preventing
duplicate links", the 409 response in its [contract](../001-bookmarks-api/contracts/openapi.yaml)
and the `duplicate_url` error). `specs/001-bookmarks-api` is a historical record and is not edited.

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

`POST /bookmarks` becomes idempotent on the normalized link: a new link is stored and returned
with 201 Created (unchanged); a link that is already saved returns the stored bookmark, untouched,
with 200 OK instead of a 409 `duplicate_url` error. The existing `INSERT ... ON CONFLICT
(url_normalized) DO NOTHING RETURNING` stays, so the unique index still decides the race between
concurrent saves; when nothing is inserted the repository now reads and returns the existing row
together with a `created=False` flag, and the route sets the status code from that flag. No schema
change, no migration, no new dependency. The `DuplicateUrlError` exception, its 409 handler and the
409 entry on `POST /bookmarks` in the generated OpenAPI are removed. Tests that expected 409 are
rewritten for 200, and new tests cover "title and tags ignored" and the 201/200 concurrent race.

## Technical Context

**Language/Version**: Python 3.11+ (suite run on 3.11, 3.12 and 3.13)

**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Alembic, psycopg 3, Uvicorn; tests: pytest,
httpx2. Unchanged from `specs/001-bookmarks-api`; no new dependency (Constitution IV).

**Storage**: PostgreSQL, existing `bookmarks` table and `uq_bookmarks_url_normalized` unique index.
No schema change and no new migration.

**Testing**: pytest integration tests through the HTTP API against the real `bookmarks_test`
database (Constitution II), including a two-thread concurrent-save test.

**Target Platform**: Linux, macOS or Windows developer machine; Linux server

**Project Type**: web-service (REST API)

**Performance Goals**: Unchanged. A duplicate save costs one extra indexed lookup by
`url_normalized` (unique index), as it already did to build the 409 body.

**Constraints**: The stored bookmark must not be modified by a duplicate save (no upsert/UPDATE);
the response body for 200 and 201 is the same `Bookmark` model.

**Scale/Scope**: One endpoint (`POST /bookmarks`) changes behavior; list and delete are untouched.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | How the plan complies | Status |
| --- | --- | --- |
| I. Typed API Contracts | Both outcomes return the existing `Bookmark` response model; the route declares `201` (default) and `200` with `model=Bookmark` so the generated OpenAPI lists both; `422` keeps `ErrorResponse`. No untyped dicts. | Pass |
| II. Real-Database Testing | New and rewritten tests run against real PostgreSQL; the concurrent test relies on the real unique index and `ON CONFLICT`. | Pass |
| III. Consistent Error Shape | Fewer error cases: the 409 `duplicate_url` error is no longer produced. Validation (422) and other errors keep the envelope. 409 stays a valid status/class in the shared mapping for any future conflict. | Pass |
| IV. Minimal Dependencies | No new dependency. | Pass |
| V. Tests Ship With Every Feature | Each acceptance scenario of spec 002 maps to an integration test in the same change; old 409 expectations are replaced; full suite must pass. | Pass |
| VI. Cursor Pagination | No list endpoint changes. | Pass (not affected) |

Post-design re-check (after Phase 1): Pass. The contract delta, data model note and quickstart
introduce no dependency, no untyped interface and no list endpoint.

## Project Structure

### Documentation (this feature)

```text
specs/002-idempotent-duplicate-save/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── openapi.yaml     # delta: POST /bookmarks only; supersedes that operation in 001's contract
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
src/bookmarks_api/
├── repository.py        # create_bookmark returns (row, created); no DuplicateUrlError
├── routes.py            # POST /bookmarks sets 201 or 200; declares 200 + 422, drops 409
└── errors.py            # remove DuplicateUrlError and its 409 handler

tests/integration/
├── test_create_bookmark.py   # 409 tests rewritten for 200; new ignore-title/tags and race tests
└── test_errors.py            # drop the 409 envelope test; OpenAPI check expects 200/201/422 on POST

README.md                # endpoint table: 200 with the existing bookmark if already saved
```

**Structure Decision**: Same single project (`src/` layout) as `specs/001-bookmarks-api`. Only the
files above change; no new modules.

## Complexity Tracking

No constitution violations to justify.
