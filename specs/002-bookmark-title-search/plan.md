# Implementation Plan: Search Bookmarks by Title

**Branch**: `002-bookmark-title-search` | **Date**: 2026-10-25 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-bookmark-title-search/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add a title search to the existing single-user bookmarks API: `GET /bookmarks/search?q=...`
returns the bookmarks whose titles contain every word of `q` as a whole word, ignoring letter
case, newest first, optionally narrowed by the existing `tag` filter, and paged with the existing
opaque keyset cursor (`limit`, `cursor`, `next_cursor`, `total`). A word is an unbroken run of
letters and digits. Both the title's words and the search's words are computed in PostgreSQL by
one immutable expression (`title_words(x) = array_remove(regexp_split_to_array(lower(x),
'[^[:alnum:]]+'), '')`), so the two sides always split and lowercase the same way; a title
matches when `title_words(title) @> title_words(q)`. A new GIN expression index added in Alembic
revision 0002 serves the title side. No new table, column or dependency. The endpoint reuses the existing
routes, repository, cursor, schema and error modules; `GET /bookmarks` is unchanged.

## Technical Context

**Language/Version**: Python 3.11+ (suite run on 3.11, 3.12 and 3.13)

**Primary Dependencies**: Existing only: FastAPI, Pydantic 2, SQLAlchemy 2, Alembic, psycopg 3;
tests: pytest, httpx2. No new runtime or test dependency (plan input; Constitution IV).

**Storage**: PostgreSQL (16 locally, 18 in the repo's `docker-compose.yml`); existing `bookmarks`
table; one new GIN expression index `ix_bookmarks_title_words` (migration `0002`). Case folding
and the letter class follow the database's character type; the databases must use a UTF-8 ctype
(C.UTF-8 locally, en_US.utf8 in the postgres:18 image)

**Testing**: pytest; unit tests for the pure "has a word character" check; integration tests
through the HTTP API against the real test database (Constitution II), one file per user story;
word splitting is tested through the API because it runs in PostgreSQL

**Naming**: The spec's "next-page token" is the `cursor` query parameter and the `next_cursor`
response field, as in specs/001.

**Target Platform**: Linux, macOS or Windows developer machine; Linux server

**Project Type**: web-service (REST API)

**Performance Goals**: SC-004: first page of a search over 100,000 bookmarks in under one second
on a developer machine (measured in research: about 7 ms with the GIN index)

**Constraints**: `q` 1 to 200 characters with at least one word; page size 1 to 100, default 20;
keyset paging only (Constitution VI); `GET /bookmarks` behavior unchanged (FR-011)

**Scale/Scope**: One user, up to about 100k bookmarks; 1 new endpoint, 1 new migration

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | How the plan complies | Status |
| --- | --- | --- |
| I. Typed API Contracts | New request model `BookmarkSearchQuery` (extends `BookmarkListQuery` with `q`) bound with `Query()`; response model is the existing `BookmarkPage`; errors declared with `ErrorResponse`; OpenAPI generated from the models | Pass |
| II. Real-Database Testing | Integration tests hit the real test database migrated with Alembic (including 0002); table truncated before each test by the existing fixture; no mocks | Pass |
| III. Consistent Error Shape | Invalid `q`, `tag`, `limit`, `cursor` and `offset` raise `RequestValidationError` and go through the existing handler: 422 `validation_error` in the shared envelope; no new error codes | Pass |
| IV. Minimal Dependencies | No new dependency; word splitting uses built-in PostgreSQL functions; the request check uses `str` methods | Pass |
| V. Tests Ship With Every Feature | Every acceptance scenario of US1 to US3 and every edge case maps to a test (see tasks); full suite must pass on 3.11 to 3.13 | Pass |
| VI. Cursor Pagination | Search reuses the `(created_at, id)` keyset and the opaque cursor from `cursor.py`; no offset in API or query; a test pages through all matches while matching bookmarks are added between requests | Pass |

Quality gates: the new list endpoint gets the paging-while-adding test (VI gate); the endpoint
appears in `/openapi.json` with request and response models (I gate); no dependency table change
(IV gate).

Post-design re-check (after Phase 1): Pass. The data model adds only an index; the contract reuses
`BookmarkPage` and `ErrorResponse`; nothing untyped crosses the boundary.

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

```text
migrations/versions/
├── 0001_create_bookmarks.py
└── 0002_title_words_index.py      # NEW: GIN expression index on the title's words

src/bookmarks_api/
├── normalize.py         # + has_word_character(): pure pre-check for FR-008
├── models.py            # + title_words(): the SQL expression; + Index ix_bookmarks_title_words
├── schemas.py           # + BookmarkSearchQuery (q, plus the inherited limit, cursor, tag)
├── repository.py        # list_bookmarks gains an optional search= filter (default None: unchanged)
└── routes.py            # + GET /bookmarks/search (reuses reject_offset, cursor, BookmarkPage)

tests/
├── unit/
│   └── test_search_query.py                   # NEW
└── integration/
    ├── test_search_bookmarks.py               # NEW: US1
    ├── test_search_with_tag.py                # NEW: US2
    └── test_search_paging.py                  # NEW: US3 (includes the Constitution VI gate)
```

`cursor.py`, `errors.py`, `db.py`, `config.py`, `main.py` and the existing tests are reused
unchanged.

**Structure Decision**: Existing single project (`src/` layout), extended in place. Search lives
in the same modules as the list it mirrors (routes, repository, schemas), so it follows the
existing patterns rather than adding a service layer.

## Complexity Tracking

No constitution violations to justify.
