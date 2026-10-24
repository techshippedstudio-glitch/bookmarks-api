# Implementation Plan: Idempotent Bookmark Save

**Branch**: `002-idempotent-bookmark-save` | **Date**: 2026-10-24 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-idempotent-bookmark-save/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

**Supersedes**: the duplicate rule of FR-004 in [specs/001-bookmarks-api](../001-bookmarks-api/spec.md)
(409 `duplicate_url` on a re-save). `specs/001-bookmarks-api` stays as the historical record and is
not edited; where its plan, research, contract or quickstart describe the 409 duplicate response,
this feature's artifacts take precedence.

## Summary

`POST /bookmarks` becomes idempotent per normalized link. A save of a link that is not yet
bookmarked still inserts and returns the bookmark with 201 Created. A save whose normalized link
already exists returns the stored bookmark, unchanged, with 200 OK; the request's title and tags
are ignored. The existing `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING` stays the
single point of truth for "who created it", so concurrent first saves still store one row: the
winner gets 201, the loser reads the committed row and gets 200. The `DuplicateUrlError` exception,
its 409 handler and the `duplicate_url` error code are removed. No schema change, no migration, no
new dependency.

## Technical Context

**Language/Version**: Python 3.11+ (suite run on 3.11, 3.12 and 3.13) — unchanged from 001

**Primary Dependencies**: FastAPI, Pydantic, SQLAlchemy 2.0, Alembic, psycopg 3; tests: pytest,
httpx — unchanged; no new dependency (Constitution IV)

**Storage**: PostgreSQL; existing `bookmarks` table and unique index `uq_bookmarks_url_normalized`
— unchanged, no migration

**Testing**: pytest integration tests through the HTTP API against the real test database
(Constitution II), including a two-thread concurrent first-save test

**Target Platform**: Linux server / developer machine — unchanged

**Project Type**: web-service (REST API)

**Performance Goals**: A re-save costs one insert attempt plus one indexed lookup by
`url_normalized`; no measurable change for interactive use

**Constraints**: The stored bookmark must not be modified by a re-save (no `DO UPDATE`); exactly
one row per normalized link under concurrency

**Scale/Scope**: One endpoint changes (`POST /bookmarks`); list, filter and delete are untouched

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | How the plan complies | Status |
| --- | --- | --- |
| I. Typed API Contracts | `POST /bookmarks` keeps the `BookmarkCreate` request model and returns the `Bookmark` response model for both 201 and 200; the 200 response is declared on the route so it appears in the generated OpenAPI; the stale 409 entry is removed | Pass |
| II. Real-Database Testing | Re-save, unchanged-bookmark and concurrent-first-save tests run against the real test database; no mocks | Pass |
| III. Consistent Error Shape | No new error; the 409 `duplicate_url` error disappears because a re-save is no longer an error. Validation (422) still uses the envelope. The principle's "409 conflict" mapping simply has no remaining user on this endpoint | Pass |
| IV. Minimal Dependencies | No new dependency | Pass |
| V. Tests Ship With Every Feature | Every acceptance scenario in spec.md maps to a test in the same change; tests asserting the superseded 409 behavior are replaced; full suite must pass on 3.11–3.13 | Pass |
| VI. Cursor Pagination | No list endpoint changes; a re-save does not change `created_at`, so keyset positions stay stable | Pass |

Post-design re-check (after Phase 1): Pass. The contract delta, data model note and quickstart add
no dependency, no untyped interface and no schema change.

## Project Structure

### Documentation (this feature)

```text
specs/002-idempotent-bookmark-save/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── openapi.yaml     # POST /bookmarks as changed by this feature
├── checklists/
│   └── requirements.md  # /speckit-specify quality checklist
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
src/bookmarks_api/
├── repository.py        # create_bookmark → returns (row, created); no DuplicateUrlError
├── routes.py            # POST /bookmarks sets 201 or 200; responses declare 200, drop 409
└── errors.py            # remove DuplicateUrlError and its 409 handler

tests/
└── integration/
    ├── test_create_bookmark.py   # re-save returns 200 + existing bookmark; concurrency 201/200
    └── test_errors.py            # drop 409 envelope test; OpenAPI check expects 200, not 409
```

**Structure Decision**: Single project, existing `src/` layout from 001. Only the three modules
and two test files above change; no new modules, no migration.

## Complexity Tracking

No constitution violations to justify.
