# Implementation Plan: Idempotent Duplicate Save

**Branch**: `002-idempotent-duplicate-save` | **Date**: 2026-10-24 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-idempotent-duplicate-save/spec.md`

**Supersedes**: the duplicate rule in 001 FR-004 (FR-004 of [specs/001-bookmarks-api](../001-bookmarks-api/spec.md));
the 409 response of `POST /bookmarks` in
[specs/001-bookmarks-api/contracts/openapi.yaml](../001-bookmarks-api/contracts/openapi.yaml) is
replaced by the 200 response in [contracts/openapi.yaml](contracts/openapi.yaml). The
`specs/001-bookmarks-api` folder is a historical record and is not edited; every statement there
that this feature replaces is listed in
[Superseded statements](#superseded-statements-in-specs001-bookmarks-api) below.

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

`POST /bookmarks` becomes idempotent per normalized link: a save of a link that is already
bookmarked returns the stored bookmark unchanged with **200 OK** instead of the **409
`duplicate_url`** error; a new link still returns **201 Created**. The existing
`INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING` stays as the single race-safe write
path; when it inserts nothing, the repository reads and returns the existing row (instead of
raising `DuplicateUrlError`) and reports `created=False`. The route sets the status code from that
flag. `DuplicateUrlError`, its 409 handler and the `duplicate_url` error code are removed. No schema
migration, no new dependency.

## Technical Context

**Language/Version**: Python 3.11+ (suite run on 3.11, 3.12 and 3.13)

**Primary Dependencies**: Unchanged from specs/001-bookmarks-api: FastAPI, SQLAlchemy 2.0, Alembic,
psycopg 3, Uvicorn; tests: pytest, httpx2. No new dependency (Constitution IV).

**Storage**: PostgreSQL; existing `bookmarks` table and unique index `uq_bookmarks_url_normalized`
(see [data-model.md](data-model.md)). No migration.

**Testing**: pytest integration tests through the HTTP API against the real test database
(`TEST_DATABASE_URL`, Constitution II), including a two-thread concurrency test.

**Target Platform**: Linux server / developer machine (unchanged)

**Project Type**: web-service (REST API)

**Performance Goals**: A duplicate save costs one extra indexed lookup by `url_normalized`; no
measurable change for a single user.

**Constraints**: Exactly one stored bookmark per normalized link under concurrent saves; the
stored bookmark is never modified by a duplicate save.

**Scale/Scope**: One endpoint (`POST /bookmarks`) changes; list, filter and delete are untouched.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | How the plan complies | Status |
| --- | --- | --- |
| I. Typed API Contracts | `POST /bookmarks` keeps `BookmarkCreate` as request model and `Bookmark` as response model for both 201 and 200; the 200 response is declared on the route so the generated OpenAPI lists it; the 409 response is removed from the route and the contract | Pass |
| II. Real-Database Testing | Duplicate-save, unchanged-row and concurrent-save tests run against the real PostgreSQL test database; no mocks | Pass |
| III. Consistent Error Shape | No new error; the `duplicate_url` (409) error is removed because a duplicate is no longer an error. Remaining errors (422, 404, 405, 500) keep the one envelope. A 200 for an existing resource is a success class, so status codes still match their class | Pass |
| IV. Minimal Dependencies | No new dependency | Pass |
| V. Tests Ship With Every Feature | Each acceptance scenario of spec.md (US1 AC1-AC3, US2 AC1) and the validation-before-duplicate edge case get tests in the same change; the old 409 tests are rewritten | Pass |
| VI. Cursor Pagination | No list endpoint changes | Pass (n/a) |

Post-design re-check (after Phase 1): Pass. The data model is unchanged, the contract only swaps
409 for 200 on one operation, and no dependency or untyped interface is introduced.

## Project Structure

### Documentation (this feature)

```text
specs/002-idempotent-duplicate-save/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── openapi.yaml     # POST /bookmarks only; supersedes that operation in 001's contract
├── checklists/
│   └── requirements.md  # /speckit-specify quality checklist
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
src/bookmarks_api/
├── repository.py        # create_bookmark -> (row, created); returns existing row on conflict
├── routes.py            # POST /bookmarks: 201 when created, 200 when existing; 409 removed
└── errors.py            # DuplicateUrlError and its 409 handler removed

tests/integration/
├── test_create_bookmark.py   # duplicate -> 200 + existing bookmark; unchanged row; concurrency 201/200
└── test_errors.py            # duplicate envelope test removed/replaced; OpenAPI post has 200, no 409

README.md                # endpoint table: "200 with the existing bookmark if the link is already saved"
```

**Structure Decision**: Same single-project `src/` layout as specs/001-bookmarks-api; only the
files listed above change.

## Complexity Tracking

No constitution violations to justify.

## Superseded statements in specs/001-bookmarks-api

`specs/001-bookmarks-api` is immutable, so these lines still describe the old 409 behavior. Each
is replaced by the 002 artifact named on the right. Lines not listed (normalization, uniqueness
index, tags, paging, delete) remain in force.

| 001 location | Old statement (summary) | Replaced by |
| --- | --- | --- |
| spec.md:L15 (Clarifications) | Duplicate save → reject with conflict error incl. existing id | spec.md FR-002, FR-003 |
| spec.md:L44-46 (US1 AC3) | Equivalent link → conflict error incl. existing id | spec.md US1 AC1 |
| spec.md:L125-127 (Edge Cases) | Duplicate with other title/tags → conflict error | spec.md US1 AC2, Edge Cases |
| spec.md:L152-156 (FR-004) | Save of existing link MUST be rejected with conflict error | spec.md FR-001 (uniqueness kept), FR-002, FR-005 |
| plan.md:L52 (Constitution III row) | Envelope used for "duplicate (409)" | plan.md Constitution Check III |
| research.md:L36-40 ("Preventing duplicate links") | On no insert, raise a duplicate error carrying its id | research.md §1 |
| research.md:L86-87 ("Error envelope") | Codes include `duplicate_url` (409, `details.existing_id`) | research.md §3 |
| contracts/openapi.yaml:L25-29 | `POST /bookmarks` `409` response | contracts/openapi.yaml `200` response |
| contracts/openapi.yaml:L129, L132 | `duplicate_url` in error code enum; `existing_id` in details | contracts/openapi.yaml `ErrorResponse` |
| quickstart.md:L39 (step 2) | Re-save → 409 `duplicate_url` | quickstart.md steps 1-3 |
| tasks.md T008, T012, T015, T016, T026 | `DuplicateUrlError`, 409 tests, 409 route response | tasks.md T002-T007 |
