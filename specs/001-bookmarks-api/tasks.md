---

description: "Task list for the Bookmarks API"
---

# Tasks: Bookmarks API

**Input**: Design documents from `/specs/001-bookmarks-api/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md

**Tests**: Included. The constitution (Principles II and V) and SC-004 require automated tests for
every acceptance scenario, run against the real test database.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested on
its own.

**Revision 2026-10-24**: Regenerated from the revised spec (FR-004: saving an already saved link
returns the existing bookmark unchanged with 200 OK instead of 409; a new link still returns 201;
two concurrent saves of the same new link store one bookmark, one 201 and one 200). Tasks whose
requirements did not change and that were already complete keep `[X]`; tasks for the revised
duplicate rule are open `[ ]`. See "History" at the end for the replaced phases.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1 to US4)
- Paths are relative to the repository root (single project, `src/` layout)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create `pyproject.toml` with project `bookmarks-api`, `requires-python = ">=3.11"`, runtime dependencies fastapi, uvicorn, sqlalchemy>=2.0, alembic, psycopg[binary]>=3.1 (compatible ranges, Constitution IV), a `dev` dependency group with pytest and httpx2 (current Starlette test client dependency; plain httpx is deprecated there), the `src/` package `bookmarks_api`, and `[tool.pytest.ini_options]` with `testpaths = ["tests"]`
- [X] T002 Create the package skeleton `src/bookmarks_api/__init__.py` and test folders `tests/unit/`, `tests/integration/` per plan.md
- [X] T003 [P] Create `src/bookmarks_api/config.py`: read `DATABASE_URL` from the environment, defaulting to `postgresql://bookmarks:bookmarks@localhost:5432/bookmarks`, and rewrite a `postgresql://` prefix to `postgresql+psycopg://` (research.md, "Database access")

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before any user story can be implemented

- [X] T004 Create `src/bookmarks_api/db.py` with a SQLAlchemy engine built from config, a `sessionmaker`, and a FastAPI dependency `get_session()` that yields a session and closes it
- [X] T005 Create `src/bookmarks_api/models.py` mapping table `bookmarks` exactly as data-model.md: `id bigint` primary key generated always as identity; `url varchar(2048) not null`; `url_normalized varchar(2048) not null, unique`; `title varchar(200) not null, char_length(title) >= 1`; `tags text[] not null, default '{}', cardinality(tags) <= 10`; `created_at timestamptz not null, default now()`
- [X] T006 Set up Alembic: `alembic.ini` and `migrations/env.py` reading the URL from `bookmarks_api.config` (overridable by `-x url=...` or the `sqlalchemy.url` option set by tests), with target metadata from `models.py`
- [X] T007 Create migration `migrations/versions/0001_create_bookmarks.py` creating table `bookmarks` with the constraints in T005 and indexes `uq_bookmarks_url_normalized UNIQUE (url_normalized)`, `ix_bookmarks_created_at_id (created_at DESC, id DESC)`, `ix_bookmarks_tags GIN (tags)`; downgrade drops the table
- [X] T008 [P] Create `src/bookmarks_api/errors.py`: Pydantic models `ErrorBody {code, message, details}` and `ErrorResponse {error: ErrorBody}`; domain exception `NotFoundError`; exception handlers producing the envelope for `RequestValidationError` (422 `validation_error`, field errors in `details`), `StarletteHTTPException` (status-mapped code), `NotFoundError` (404 `not_found`) and any other exception (500 `internal_error`, no internals) (Constitution III)
- [X] T009 Create `src/bookmarks_api/main.py` with `create_app()` registering the handlers from T008 and the router from `routes.py`, and module-level `app = create_app()`
- [X] T010 Create `tests/conftest.py`: read `TEST_DATABASE_URL` (default `postgresql://bookmarks:bookmarks@localhost:5432/bookmarks_test`), run `alembic upgrade head` against it once per session, override `get_session` to use the test database, truncate `bookmarks` (restart identity) before every test, and provide a `client` fixture using FastAPI `TestClient` (Constitution II: no database mocks)

**Checkpoint**: Foundation ready; user story work can begin

---

## Phase 3: User Story 1 - Save a bookmark (Priority: P1) 🎯 MVP

**Goal**: A user can save a link with a title and optional tags; saving a link that is already
saved returns the existing bookmark unchanged instead of creating a duplicate.

**Independent Test**: `POST /bookmarks` returns 201 with the saved bookmark; saving an equivalent
link with a different title and tags returns 200 with the first bookmark unchanged, and there is
still one row.

### Tests for User Story 1

> Write these first and confirm they fail before implementing.

- [X] T011 [P] [US1] Unit tests in `tests/unit/test_normalize.py` for link normalization (lowercase scheme and host, default ports 80/443 removed, trailing path slashes removed, fragment removed, query kept; examples `HTTPS://Example.com:443/docs/#intro` → `https://example.com/docs`, `https://example.com/search?q=FastAPI` keeps `?q=FastAPI`; non-http(s) and host-less links rejected) and tag normalization (trim, lowercase, de-duplicate, sort; must match `^[a-z0-9-]{1,30}$`)
- [ ] T012 [P] [US1] Update integration tests in `tests/integration/test_create_bookmark.py` for the revised User Story 1 scenario 3 and FR-004: save `https://example.com/docs` (title "Docs", tags `["a"]`) then `HTTPS://Example.com/docs/#intro` with title "Other" and tags `["b"]` → second response is 200 (not 201, not 409) and its body equals the first response body exactly (same `id`, `url` as first given, `title` "Docs", `tags` `["a"]`, `created_at`); the stored row's `url`, `title`, `tags` and `created_at` are unchanged when read back from the database; still exactly one row. Replace the concurrency test: two concurrent saves (two threads) of the same new link → status codes sorted are `[200, 201]`, both bodies carry the same `id`, exactly one row. Keep the scenario 1, 2 and 4 tests as they are; remove every assertion on 409 or `duplicate_url`
- [X] T013 [P] [US1] Implement `normalize_url(url) -> str` and `normalize_tags(tags) -> list[str]` in `src/bookmarks_api/normalize.py` using only the standard library, raising `ValueError` with a clear message on invalid input
- [X] T014 [P] [US1] Create Pydantic models in `src/bookmarks_api/schemas.py`: `BookmarkCreate` (`url` str, max 2048, http/https with a host; `title` trimmed, 1 to 200 characters; `tags` list default `[]`, normalized via `normalize_tags`, at most 10 after de-duplication; extra fields forbidden) and `Bookmark` (`id`, `url`, `title`, `tags`, `created_at`)

### Implementation for User Story 1

- [ ] T015 [US1] Change `create_bookmark(session, data)` in `src/bookmarks_api/repository.py` to return `(row, created: bool)`: keep `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`; a returned row → commit and return `(row, True)`; no row → end the insert transaction, select the existing row by `url_normalized` and return `(existing_row, False)` without writing the request's title or tags (no `DO UPDATE`); if that select finds nothing (the row was deleted in between), retry the insert once (research.md, "Preventing duplicate links", revised 2026-10-24)
- [ ] T016 [US1] Update `POST /bookmarks` in `src/bookmarks_api/routes.py` to set the status code from the `created` flag (201 Created for a new link, 200 OK for an already saved link), both with the `Bookmark` response model; declare the 200 response in `responses` (description "The link was already saved; the existing bookmark, unchanged") and remove the 409 response, per contracts/openapi.yaml
- [ ] T017 [US1] Remove `DuplicateUrlError` and its 409 `duplicate_url` handler from `src/bookmarks_api/errors.py` and its import from `src/bookmarks_api/repository.py`; keep the generic `409: "conflict"` entry in `STATUS_CODES` for framework `HTTPException`s (plan.md, Constitution Check III)

**Checkpoint**: User Story 1 works and is tested on its own (MVP)

---

## Phase 4: User Story 2 - List bookmarks, newest first (Priority: P2)

**Goal**: A user can list bookmarks newest first, in cursor pages, with a total count.

**Independent Test**: `GET /bookmarks` returns saved bookmarks newest first with `total`, `limit`
and `next_cursor`; following `next_cursor` returns the rest with no repeats or gaps.

### Tests for User Story 2

- [X] T018 [P] [US2] Integration tests in `tests/integration/test_list_bookmarks.py` for User Story 2 scenarios 1 to 5: three saves listed newest first with `total == 3`; empty list with `total == 0`; 25 bookmarks → first page of 20 with `total == 25` and a `next_cursor`, next page → 5 with `next_cursor` null; `limit=101`, `limit=0`, a malformed `cursor` and any `offset` → 422 `validation_error` (the offset message names `cursor`); a test that pages through all results while bookmarks are saved between requests and finds no duplicates and no gaps (Constitution VI quality gate); unit tests for the cursor codec in `tests/unit/test_cursor.py`

### Implementation for User Story 2

- [X] T019 [P] [US2] Add `BookmarkPage {items: list[Bookmark], total, limit, next_cursor: str | None}` to `src/bookmarks_api/schemas.py`
- [X] T020 [P] [US2] Create `src/bookmarks_api/cursor.py` with an opaque cursor encoder/decoder: the last row's `created_at` and `id`, JSON-encoded then base64url-encoded (standard library only); decoding a malformed value raises `ValueError`
- [X] T021 [US2] Implement `list_bookmarks(session, limit, after=None, tag=None) -> (items, total, has_more)` in `src/bookmarks_api/repository.py` with keyset paging `WHERE (created_at, id) < (:created_at, :id)`, ordered by `created_at DESC, id DESC`, fetching `limit + 1` rows to detect more pages, with `total` from a `COUNT(*)` using the same filter (Constitution VI; no offset)
- [X] T022 [US2] Implement `GET /bookmarks` in `src/bookmarks_api/routes.py` with `limit` (1 to 100, default 20) and `cursor` query parameters, returning `BookmarkPage` with `next_cursor` only when more rows exist; a malformed `cursor` or any `offset` parameter returns 422 `validation_error` with a message that names `cursor` (spec Edge Cases)

**Checkpoint**: User Stories 1 and 2 work independently

---

## Phase 5: User Story 3 - Filter bookmarks by tag (Priority: P3)

**Goal**: A user can narrow the list to one tag.

**Independent Test**: `GET /bookmarks?tag=postgres` returns only bookmarks with that tag, newest
first.

### Tests for User Story 3

- [X] T023 [P] [US3] Integration tests in `tests/integration/test_filter_by_tag.py` for User Story 3 scenarios 1 to 3: filter `postgres` returns only matching bookmarks newest first with matching `total`; `Postgres` matches `postgres`; unknown tag → empty list; invalid tag value → 422; paging a filtered list with `next_cursor`

### Implementation for User Story 3

- [X] T024 [US3] Add the optional `tag` query parameter to `GET /bookmarks` in `src/bookmarks_api/routes.py`, normalized with the tag rules (invalid → 422), and apply `tags @> ARRAY[:tag]` in `list_bookmarks` in `src/bookmarks_api/repository.py`

**Checkpoint**: User Stories 1 to 3 work independently

---

## Phase 6: User Story 4 - Delete a bookmark (Priority: P4)

**Goal**: A user can delete a bookmark by id.

**Independent Test**: `DELETE /bookmarks/{id}` returns 204 and the bookmark is gone; deleting
again returns 404.

### Tests for User Story 4

- [X] T025 [P] [US4] Integration tests in `tests/integration/test_delete_bookmark.py` for User Story 4 scenarios 1 to 3: delete → 204 and absent from list and tag filter; unknown id → 404 `not_found`; id 0 or negative → 422 `validation_error`; delete then save the same link again → 201 new bookmark

### Implementation for User Story 4

- [X] T026 [US4] Implement `delete_bookmark(session, bookmark_id)` in `src/bookmarks_api/repository.py` raising `NotFoundError` when no row is deleted
- [X] T027 [US4] Implement `DELETE /bookmarks/{bookmark_id}` in `src/bookmarks_api/routes.py` with `bookmark_id >= 1`, returning 204, with the 404 response declared using `ErrorResponse`

**Checkpoint**: All user stories work independently

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T028 [P] Update `tests/integration/test_errors.py`: every error class (422, 404, and an unknown route 404) uses the envelope `{"error": {"code", "message", "details"}}` (SC-005); remove the duplicate 409 envelope test (a duplicate save is no longer an error); the `/openapi.json` check expects `POST /bookmarks` to declare 200, 201 and 422 and no 409, alongside the GET and DELETE operations with request and response schemas (Constitution I, contracts/openapi.yaml)
- [ ] T029 [P] Update the `POST /bookmarks` row in `README.md`: a new link returns 201; an already saved link returns 200 with the existing bookmark unchanged (title and tags in the request ignored), instead of 409
- [ ] T030 Run the full test suite on Python 3.11, 3.12 and 3.13 and the manual checks in `specs/001-bookmarks-api/quickstart.md` (step 2 now expects 200 with the step 1 bookmark unchanged)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup; blocks all user stories
- **User Stories (Phases 3 to 6)**: Depend on Foundational. US2 lists what US1 saves, so its tests
  use the US1 endpoint; US3 extends the US2 endpoint; US4 is independent of US2 and US3 except for
  its "absent from list" check
- **Polish (Phase 7)**: Depends on all user stories

### Open work for the 2026-10-24 revision

- T012 (tests, confirmed failing) → T015 (repository) → T016 (route) → T017 (remove the duplicate
  error); T028 and T029 can run alongside T015 to T017; T030 last.

### Within Each User Story

- Tests first, confirmed failing
- Schemas and pure functions before the repository, repository before routes

### Parallel Opportunities

- T003 alongside T001/T002; T008 alongside T004 to T007
- US1: T011, T012, T013 and T014 in parallel (different files)
- US2: T018, T019 and T020 in parallel
- Polish: T028 and T029 in parallel

## Parallel Example: User Story 1

```text
Task: "Revised duplicate and concurrency tests in tests/integration/test_create_bookmark.py" (T012)
Task: "Error envelope and OpenAPI test updates in tests/integration/test_errors.py"          (T028)
Task: "README POST row in README.md"                                                         (T029)
```

## Implementation Strategy

### MVP First (User Story 1 only)

1. Complete Phase 1 and Phase 2
2. Complete Phase 3 (save, returning the existing bookmark for an already saved link)
3. Stop and validate: run the US1 tests

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. US1 → MVP; US2 → listing; US3 → filtering; US4 → delete
3. Polish: cross-cutting error and OpenAPI checks, README, quickstart validation

## History

- 2026-10-21: the original list (T001 to T028) built offset paging in US2; Phase 8 (T029 to T031,
  delete id >= 1, tag limit after de-duplication, Python 3.11/3.12) and Phase 9 (T032 to T036,
  keyset paging with `next_cursor`, 422 for malformed cursor or `offset`, paging stability test,
  README) were appended by `/speckit-converge`. This regeneration folds those into the story
  phases (T018 to T022, T025, T027).
- 2026-10-24: duplicate saves changed from 409 `duplicate_url` with `details.existing_id` to 200
  with the existing bookmark (T012, T015, T016, T017, T028, T029, T030).
