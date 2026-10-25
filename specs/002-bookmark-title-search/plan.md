# Implementation Plan: Bookmark Title Search

**Branch**: `002-bookmark-title-search` | **Date**: 2026-10-25 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-bookmark-title-search/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add a search over bookmark titles: `GET /bookmarks/search?q=&tag=&limit=&cursor=` returns the
bookmarks whose title contains every search word (case-insensitive, substring, wildcards treated
literally), newest first, optionally narrowed by the existing tag filter, and paged exactly like
`GET /bookmarks`: the same `BookmarkPage` response, the same opaque keyset cursor on
`(created_at, id)`, the same limits, the same error envelope. The request model
`BookmarkSearchQuery` extends the existing `BookmarkListQuery` with a required `q`; the repository's
existing `list_bookmarks` query gains an optional list of title words that become `ILIKE`
conditions with escaped wildcards. No schema change, no migration and no new dependency: at the
stated scale (10,000 bookmarks) a filtered walk of the existing `(created_at DESC, id DESC)` index
answers well inside the 1-second target.

## Technical Context

**Language/Version**: Python 3.11+ (suite run on 3.11, 3.12 and 3.13)

**Primary Dependencies**: Existing only: FastAPI, Pydantic, SQLAlchemy 2.0, Alembic, psycopg 3,
Uvicorn; tests: pytest, httpx2. No new runtime or test dependency (plan input; Constitution IV).

**Storage**: PostgreSQL (existing `bookmarks` table, unchanged); dev and test databases from
`DATABASE_URL` / `TEST_DATABASE_URL`

**Testing**: pytest; unit tests for the pure search-word parser; integration tests through the
HTTP API against the real test database (Constitution II), including the paging-while-saving test
required for every list endpoint (Constitution VI quality gate)

**Target Platform**: Linux, macOS or Windows developer machine; Linux server

**Project Type**: web-service (REST API), extending the existing service

**Performance Goals**: 95% of searches return a page in under 1 second for 10,000 bookmarks
(SC-006)

**Constraints**: `q` 1 to 200 characters and not blank; page size 1 to 100, default 20; tag filter
validated like tags; offset not accepted (Constitution VI)

**Scale/Scope**: One user, up to about 10,000 bookmarks for the search target (the list endpoint's
100k design scale is unchanged); 1 new endpoint, 0 new tables

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | How the plan complies | Status |
| --- | --- | --- |
| I. Typed API Contracts | New request model `BookmarkSearchQuery` (subclass of `BookmarkListQuery`, adds `q`) bound with `Query()`; response model is the existing `BookmarkPage`; the endpoint appears in the generated OpenAPI with both, and the OpenAPI test is extended to the new path | Pass |
| II. Real-Database Testing | All search behavior (matching, case, wildcards, tag combination, ordering, paging) is tested through the API against the real test database; no mocks | Pass |
| III. Consistent Error Shape | Invalid `q`, `limit`, `cursor`, `tag` and `offset` raise the existing validation errors, rendered by the existing global handlers as `{"error": {"code": "validation_error", ...}}` with status 422; no new error class | Pass |
| IV. Minimal Dependencies | No new dependency; matching uses SQLAlchemy's `icontains(..., autoescape=True)` and the standard library | Pass |
| V. Tests Ship With Every Feature | Every acceptance scenario of User Stories 1-3 maps to an integration test; error paths included; full suite must pass | Pass |
| VI. Cursor Pagination | Reuses the existing keyset cursor on `(created_at, id)` and `encode_cursor`/`decode_cursor`; no offset; `reject_offset` dependency applied; a test pages through search results while matching bookmarks are saved between requests | Pass |

Post-design re-check (after Phase 1): Pass. The data model adds no stored data, the contract reuses
the existing `BookmarkPage` and `ErrorResponse` schemas, and no dependency was added.

## Project Structure

### Documentation (this feature)

```text
specs/002-bookmark-title-search/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── openapi.yaml     # GET /bookmarks/search
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

Existing files this feature changes are marked `(changed)`; new files `(new)`.

```text
src/bookmarks_api/
├── normalize.py         # (changed) add search_words(): split, de-duplicate, validate q
├── schemas.py           # (changed) add BookmarkSearchQuery(BookmarkListQuery) with q
├── repository.py        # (changed) list_bookmarks() gains optional title words (ILIKE, escaped)
└── routes.py            # (changed) add GET /bookmarks/search, declared before /{bookmark_id}

tests/
├── unit/
│   └── test_search_words.py           # (new) parser: splitting, de-duplication, limits
└── integration/
    ├── test_search_bookmarks.py       # (new) User Story 1
    ├── test_search_with_tag.py        # (new) User Story 2
    ├── test_search_paging.py          # (new) User Story 3, Constitution VI gate, SC-006 timing
    └── test_errors.py                 # (changed) OpenAPI check covers GET /bookmarks/search

README.md                # (changed) endpoint table gains the search endpoint
```

No changes to `models.py`, `migrations/`, `errors.py`, `cursor.py`, `pyproject.toml` or
`uv.lock`.

**Structure Decision**: Keep the existing single project (`src/` layout, one package, unit and
integration tests). The search is one more route in `routes.py` over the existing repository query,
following the existing route, repository and error patterns as the plan input asks.

## Complexity Tracking

No constitution violations to justify.
