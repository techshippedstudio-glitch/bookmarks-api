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

**Regenerated 2026-10-24** from the revised spec (FR-004: a repeat save returns the existing
bookmark with 200 OK instead of 409) and the revised plan. Tasks whose work is already in the code
and unchanged by the revision keep their `[X]`; tasks the revision changes are open (`[ ]`) and
marked "changed 2026-10-24". The rationale and history of the previous task list are kept under
"History" at the end.

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
- [X] T007 Create migration `migrations/versions/0001_create_bookmarks.py` creating table `bookmarks` with the constraints in T005 and indexes `uq_bookmarks_url_normalized UNIQUE (url_normalized)`, `ix_bookmarks_created_at_id (created_at DESC, id DESC)`, `ix_bookmarks_tags GIN (tags)`; downgrade drops the table (no new migration for the 2026-10-24 change: the unique index already gives the guarantee, plan.md)
- [ ] T008 [P] (changed 2026-10-24) `src/bookmarks_api/errors.py`: Pydantic models `ErrorBody {code, message, details}` and `ErrorResponse {error: ErrorBody}`; domain exception `NotFoundError`; exception handlers producing the envelope for `RequestValidationError` (422 `validation_error`, field errors in `details`), `StarletteHTTPException` (status-mapped code), `NotFoundError` (404 `not_found`) and any other exception (500 `internal_error`, no internals) (Constitution III). Remove `DuplicateUrlError` and its 409 `duplicate_url` handler: a repeat save is no longer an error (FR-004, research.md "Error envelope")
- [X] T009 Create `src/bookmarks_api/main.py` with `create_app()` registering the handlers from T008 and the router from `routes.py`, and module-level `app = create_app()`
- [X] T010 Create `tests/conftest.py`: read `TEST_DATABASE_URL` (default `postgresql://bookmarks:bookmarks@localhost:5432/bookmarks_test`), run `alembic upgrade head` against it once per session, override `get_session` to use the test database, truncate `bookmarks` (restart identity) before every test, and provide a `client` fixture using FastAPI `TestClient` (Constitution II: no database mocks)

**Checkpoint**: Foundation ready; user story work can begin

---

## Phase 3: User Story 1 - Save a bookmark (Priority: P1) 🎯 MVP

**Goal**: A user can save a link with a title and optional tags; saving a link that is already
saved returns the existing bookmark unchanged instead of creating a duplicate.

**Independent Test**: `POST /bookmarks` returns 201 with the saved bookmark; saving an equivalent
link returns 200 with the existing bookmark, unchanged, and still one row.

### Tests for User Story 1

> Write these first and confirm they fail before implementing.

- [X] T011 [P] [US1] Unit tests in `tests/unit/test_normalize.py` for link normalization (lowercase scheme and host, default ports 80/443 removed, trailing path slashes removed, fragment removed, query kept; examples `HTTPS://Example.com:443/docs/#intro` → `https://example.com/docs`, `https://example.com/search?q=FastAPI` keeps `?q=FastAPI`; non-http(s) and host-less links rejected) and tag normalization (trim, lowercase, de-duplicate, sort; must match `^[a-z0-9-]{1,30}$`)
- [ ] T012 [P] [US1] (changed 2026-10-24) Integration tests in `tests/integration/test_create_bookmark.py` for User Story 1 scenarios 1 to 4: save with no tags (201, `tags == []`, `created_at` present); tags `["Python", " api ", "python"]` → `["api", "python"]`; `https://example.com/docs` (title "Docs", no tags) then `HTTPS://Example.com/docs/#intro` with title "Other title" and tags `["x"]` → 200 with a body equal to the first response (same `id`, `url` `https://example.com/docs`, `title` "Docs", `tags` `[]`, `created_at`), the stored row unchanged in the database, still one row; missing url, missing title, `ftp://` link, url over 2048 characters, title over 200 characters, 11 tags, and invalid tag `"no spaces"` each → 422 `validation_error` and nothing saved; two concurrent saves of equivalent new links (two threads) → exactly one 201 and one 200, both bodies carrying the same `id`, one row (FR-004)

### Implementation for User Story 1

- [X] T013 [P] [US1] Implement `normalize_url(url) -> str` and `normalize_tags(tags) -> list[str]` in `src/bookmarks_api/normalize.py` using only the standard library, raising `ValueError` with a clear message on invalid input
- [X] T014 [P] [US1] Create Pydantic models in `src/bookmarks_api/schemas.py`: `BookmarkCreate` (`url` str, max 2048, http/https with a host; `title` trimmed, 1 to 200 characters; `tags` list default `[]`, normalized via `normalize_tags`, at most 10 after de-duplication; extra fields forbidden) and `Bookmark` (`id`, `url`, `title`, `tags`, `created_at`)
- [ ] T015 [US1] (changed 2026-10-24) Implement `create_bookmark(session, data) -> tuple[BookmarkRow, bool]` in `src/bookmarks_api/repository.py` returning the row and whether it was inserted: `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`; on insert commit and return `(row, True)`; when nothing is inserted, end the transaction, select the existing row by `url_normalized` in a new statement and return `(row, False)` without writing to it; if that select finds nothing (deleted in between), retry the insert once (research.md, "Preventing duplicate links")
- [ ] T016 [US1] (changed 2026-10-24) Implement `POST /bookmarks` in `src/bookmarks_api/routes.py` returning 201 with `Bookmark` for a new bookmark and 200 with the existing `Bookmark` when the link is already saved; declare the 200 response with the `Bookmark` model and the 422 response with `ErrorResponse`; remove the 409 response (contracts/openapi.yaml)

**Checkpoint**: User Story 1 works and is tested on its own (MVP)

---

## Phase 4: User Story 2 - List bookmarks, newest first (Priority: P2)

**Goal**: A user can list bookmarks newest first, in keyset pages, with a total count.

**Independent Test**: `GET /bookmarks` returns saved bookmarks newest first with `total`, `limit`
and `next_cursor`; following `next_cursor` returns the rest with no repeats or gaps.

### Tests for User Story 2

- [X] T017 [P] [US2] Integration tests in `tests/integration/test_list_bookmarks.py` for User Story 2 scenarios 1 to 5: three saves listed newest first with `total == 3`; empty list with `total == 0` and `next_cursor` null; 25 bookmarks → first page of 20 with `total == 25` and a `next_cursor`, next page → 5 with `next_cursor` null; `limit=101` and `limit=0` → 422 `validation_error`; malformed `cursor` → 422; any `offset` → 422 with a message naming `cursor`; paging through all results while bookmarks are saved (and deleted) between requests sees no duplicates and no gaps (Constitution VI quality gate)
- [X] T018 [P] [US2] Unit tests in `tests/unit/test_cursor.py`: cursor round trip keeps microseconds and id, cursor is URL-safe, malformed cursors raise `ValueError`

### Implementation for User Story 2

- [X] T019 [P] [US2] Add `BookmarkPage {items: list[Bookmark], total, limit, next_cursor: str | None}` to `src/bookmarks_api/schemas.py`
- [X] T020 [P] [US2] Implement the opaque base64url cursor encoder/decoder over `(created_at, id)` in `src/bookmarks_api/cursor.py` (standard library only; research.md, "Ordering and paging")
- [X] T021 [US2] Implement `list_bookmarks(session, *, limit, after=None, tag=None) -> (items, total, has_more)` in `src/bookmarks_api/repository.py`, ordered by `created_at DESC, id DESC`, keyset condition `WHERE (created_at, id) < (:created_at, :id)`, fetching `limit + 1` rows, with `total` from a `COUNT(*)` using the same filter; no offset (Constitution VI)
- [X] T022 [US2] Implement `GET /bookmarks` in `src/bookmarks_api/routes.py` with `limit` (1 to 100, default 20) and `cursor` query parameters, rejecting a malformed cursor and any `offset` with 422 naming `cursor`, returning `BookmarkPage` with `next_cursor` only when more rows exist

**Checkpoint**: User Stories 1 and 2 work independently

---

## Phase 5: User Story 3 - Filter bookmarks by tag (Priority: P3)

**Goal**: A user can narrow the list to one tag.

**Independent Test**: `GET /bookmarks?tag=postgres` returns only bookmarks with that tag, newest
first.

### Tests for User Story 3

- [X] T023 [P] [US3] Integration tests in `tests/integration/test_filter_by_tag.py` for User Story 3 scenarios 1 to 3: filter `postgres` returns only matching bookmarks newest first with matching `total`; `Postgres` matches `postgres`; unknown tag → empty list; filter combined with cursor paging; invalid tag value → 422

### Implementation for User Story 3

- [X] T024 [US3] Add the optional `tag` query parameter to `GET /bookmarks` in `src/bookmarks_api/routes.py`, normalized with the tag rules (invalid → 422), and apply `tags @> ARRAY[:tag]` in `list_bookmarks` in `src/bookmarks_api/repository.py`

**Checkpoint**: User Stories 1 to 3 work independently

---

## Phase 6: User Story 4 - Delete a bookmark (Priority: P4)

**Goal**: A user can delete a bookmark by id.

**Independent Test**: `DELETE /bookmarks/{id}` returns 204 and the bookmark is gone; deleting
again returns 404.

### Tests for User Story 4

- [X] T025 [P] [US4] Integration tests in `tests/integration/test_delete_bookmark.py` for User Story 4 scenarios 1 to 3: delete → 204 and absent from list and tag filter; unknown id → 404 `not_found`; delete then save the same link again → 201 new bookmark; id 0, negative and non-integer → 422 `validation_error`

### Implementation for User Story 4

- [X] T026 [US4] Implement `delete_bookmark(session, bookmark_id)` in `src/bookmarks_api/repository.py` raising `NotFoundError` when no row is deleted
- [X] T027 [US4] Implement `DELETE /bookmarks/{bookmark_id}` in `src/bookmarks_api/routes.py` with `bookmark_id >= 1`, returning 204, with the 404 and 422 responses declared using `ErrorResponse`

**Checkpoint**: All user stories work independently

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T028 [P] (changed 2026-10-24) Integration tests in `tests/integration/test_errors.py` asserting every error class (422, 404, 405, 500, and an unknown route 404) uses the envelope `{"error": {"code", "message", "details"}}` (SC-005), with the 409 `duplicate_url` envelope test removed; and that `/openapi.json` lists all three operations with request and response schemas (Constitution I): `POST /bookmarks` declares 201 and 200 with `Bookmark`, 422 with `ErrorResponse`, and no 409
- [ ] T029 [P] (changed 2026-10-24) Update the `POST /bookmarks` row in `README.md`: 201 for a new link, 200 with the existing bookmark (unchanged) if the link is already saved, instead of "409 if the link is already saved"
- [ ] T030 Run the full test suite on Python 3.11, 3.12 and 3.13 and the manual checks in `specs/001-bookmarks-api/quickstart.md` (step 2 now expects 200 with the unchanged step 1 bookmark)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup; blocks all user stories
- **User Stories (Phases 3 to 6)**: Depend on Foundational. US2 lists what US1 saves, so its tests
  use the US1 endpoint; US3 extends the US2 endpoint; US4 is independent of US2 and US3 except for
  its "absent from list" check
- **Polish (Phase 7)**: Depends on all user stories

### Open work for the 2026-10-24 change

T012 (tests first, confirm they fail) → T015 → T016; T008 after T015 (nothing raises
`DuplicateUrlError` any more); T028 and T029 after T016; T030 last.

### Within Each User Story

- Tests first, confirmed failing
- Schemas and pure functions before the repository, repository before routes

### Parallel Opportunities

- T003 alongside T001/T002; T008 alongside T004 to T007
- US1: T011, T012, T013 and T014 in parallel (different files)
- US2: T017, T018, T019 and T020 in parallel
- Polish: T028 and T029 in parallel

## Parallel Example: User Story 1

```text
Task: "Unit tests for normalization in tests/unit/test_normalize.py"          (T011)
Task: "Integration tests for saving in tests/integration/test_create_bookmark.py" (T012)
Task: "normalize_url / normalize_tags in src/bookmarks_api/normalize.py"         (T013)
Task: "BookmarkCreate / Bookmark in src/bookmarks_api/schemas.py"                (T014)
```

## Implementation Strategy

### MVP First (User Story 1 only)

1. Complete Phase 1 and Phase 2
2. Complete Phase 3 (save, returning the existing bookmark for a repeat save)
3. Stop and validate: run the US1 tests

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. US1 → MVP; US2 → listing; US3 → filtering; US4 → delete
3. Polish: cross-cutting error and OpenAPI checks, README, quickstart validation

---

## History (preserved from the previous task list, 2026-10-21 to 2026-10-23)

- The first list built offset paging for US2 (old T017-T020: `limit`/`offset`, `BookmarkPage
  {items, total, limit, offset}`). Constitution v1.1.0 (Principle VI) then forbade offset paging;
  `/speckit-converge` appended Phase 9 (old T032-T036) to replace it with keyset paging on
  `(created_at, id)`, an opaque base64url cursor in `cursor.py`, 422 for a malformed cursor or any
  `offset`, cursor-based paging tests including saves between pages, and the README update. In
  this list those are folded into T017-T022 as the design now states them.
- Old Phase 8 (convergence pass 1): T029 required `bookmark_id >= 1` on delete (now T025/T027);
  T030 aligned the contract so the 10-tag limit applies after de-duplication (contract only); T031
  ran the suite on 3.11 and 3.12 (now T030, extended to 3.13).
- Old T008, T012, T015, T016 and T026 built and tested the 409 `duplicate_url` response with
  `details.existing_id` for a repeat save (rationale: the database's unique index plus
  `ON CONFLICT DO NOTHING` guarantees one row under races, without catching exceptions
  mid-transaction). The 2026-10-24 spec change keeps that mechanism and replaces the 409 with 200
  and the existing bookmark (now T008, T012, T015, T016, T028).
