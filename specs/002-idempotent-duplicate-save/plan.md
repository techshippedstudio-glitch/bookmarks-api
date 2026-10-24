# Implementation Plan: Idempotent Duplicate Save

**Branch**: `002-idempotent-duplicate-save` | **Date**: 2026-10-24 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-idempotent-duplicate-save/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Change `POST /bookmarks` so that saving a link whose normalized form is already stored returns the
existing bookmark, unchanged, with **200 OK** instead of the 409 `duplicate_url` error defined by
[specs/001-bookmarks-api](../001-bookmarks-api/spec.md) FR-004 (superseded here). A new link still
returns **201 Created**. The existing `INSERT ... ON CONFLICT (url_normalized) DO NOTHING
RETURNING` statement and the unique index stay; when nothing is inserted, the repository now loads
and returns the existing row together with a `created=False` flag instead of raising, and the route
sets the response status from that flag. Concurrency is still decided by the unique index, so two
racing saves of a new link store one row: the winner gets 201, the loser waits on the index, does
nothing, then reads the committed row and gets 200. The `DuplicateUrlError` exception, its 409
handler and the 409 entry in the OpenAPI responses are removed. No schema, migration or dependency
change.

## Technical Context

**Language/Version**: Python 3.11+ (suite run on 3.11, 3.12 and 3.13)

**Primary Dependencies**: Unchanged from 001 — FastAPI, SQLAlchemy 2.0, Alembic, psycopg 3, Uvicorn;
tests: pytest, httpx2. No new dependency (Constitution IV).

**Storage**: PostgreSQL, existing `bookmarks` table and `uq_bookmarks_url_normalized` unique index
from 001; no migration

**Testing**: pytest integration tests through the HTTP API against the real `bookmarks_test`
database (Constitution II), including a two-thread concurrency test

**Target Platform**: Linux server / developer machine (unchanged)

**Project Type**: web-service (REST API)

**Performance Goals**: Unchanged; a duplicate save costs one insert attempt plus one indexed lookup

**Constraints**: Stored bookmark must not be modified by a duplicate save; validation still runs
before the duplicate check (spec FR-005)

**Scale/Scope**: One endpoint changed (`POST /bookmarks`); `repository.create_bookmark`,
`routes.create_bookmark`, `errors.py`, the create/error tests, README endpoint table

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | How the plan complies | Status |
| --- | --- | --- |
| I. Typed API Contracts | Both outcomes of `POST /bookmarks` use the existing `Bookmark` response model; the 200 response is declared on the route so the generated OpenAPI lists 200 and 201 with the `Bookmark` schema; the 409 entry is removed | Pass |
| II. Real-Database Testing | New and changed tests run against `bookmarks_test`; the concurrency test uses two real connections racing on the real unique index | Pass |
| III. Consistent Error Shape | Fewer error cases: the duplicate case is no longer an error. Remaining errors (422, 404, 405, 500) keep the envelope. The principle's mention of 409 lists an allowed class, it does not require one to exist | Pass |
| IV. Minimal Dependencies | No new dependencies | Pass |
| V. Tests Ship With Every Feature | Every acceptance scenario of spec US1 and US2 maps to a test in the same change; old 409 assertions in the create and concurrency tests are replaced by 200 assertions, and the duplicate-envelope test in `test_errors.py` is removed explicitly because that error no longer exists; the retry path for a bookmark deleted mid-save gets its own real-database test | Pass |
| VI. Cursor Pagination | No list endpoint changes; a duplicate save does not change `created_at`, so keyset positions are unaffected | Pass |

Post-design re-check (after Phase 1): Pass. The contract adds a 200 response using the existing
`Bookmark` schema, removes 409 and the `duplicate_url` error code; no new dependencies, models or
untyped interfaces.

## Project Structure

### Documentation (this feature)

```text
specs/002-idempotent-duplicate-save/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── openapi.yaml     # Full API contract; supersedes specs/001-bookmarks-api/contracts/openapi.yaml for POST /bookmarks
├── checklists/
│   └── requirements.md  # /speckit-specify quality checklist
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

`specs/001-bookmarks-api/` is a finished historical record and is not edited.

### Source Code (repository root)

```text
src/bookmarks_api/
├── repository.py        # create_bookmark returns (row, created) instead of raising on duplicate
├── routes.py            # POST /bookmarks sets 201 or 200 from `created`; declares 200, drops 409
└── errors.py            # DuplicateUrlError and its 409 handler removed

tests/integration/
├── test_create_bookmark.py  # duplicate → 200 with existing bookmark unchanged; concurrency → one 201 + one 200, same id
└── test_errors.py           # duplicate-envelope test removed; OpenAPI check expects 200+201, no 409 for POST

README.md                # endpoint table: POST returns 200 with the existing bookmark if already saved
```

**Structure Decision**: Existing single project (`src/` layout) from 001; no new modules, files or
migrations.

## Complexity Tracking

No constitution violations to justify.
