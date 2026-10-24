# Step 03: tasks (Spec Kit tasks command, existing feature)

Start: 2026-10-24T11:45:08Z

## Commands and output

```
$ cat .claude/skills/speckit-tasks/SKILL.md   # read and followed
$ export SPECIFY_FEATURE_DIRECTORY=specs/001-bookmarks-api && .specify/scripts/bash/setup-tasks.sh --json
{"FEATURE_DIR": "/home/claude/runs/living-r1/specs/001-bookmarks-api", "AVAILABLE_DOCS": ["research.md", "data-model.md", "contracts/", "quickstart.md"], "TASKS_TEMPLATE": "/home/claude/runs/living-r1/.specify/templates/tasks-template.md"}
TASKS_TEMPLATE_CONTENT: <9134 chars, identical to .specify/templates/tasks-template.md: True>
$ ls .specify/extensions.yml
ls: cannot access '.specify/extensions.yml': No such file or directory
$ cp specs/001-bookmarks-api/tasks.md <scratchpad>/tasks-before.md   # preserve old list before replacing
$ grep -cE "^- \[[ X]\] T[0-9]{3}" specs/001-bookmarks-api/tasks.md
30
$ grep -E "^- \[" specs/001-bookmarks-api/tasks.md | grep -vE "^- \[[ X]\] T[0-9]{3} "   # format violations (expect none)
```

Arguments: the change request (verbatim from the brief).
Pre-execution hooks: no `.specify/extensions.yml`; skipped silently.

Design documents loaded: plan.md, spec.md (required); research.md, data-model.md, contracts/openapi.yaml,
quickstart.md; .specify/memory/constitution.md.

Generation decision recorded: the command regenerates tasks.md from the template. The existing list held 36
tasks, all [X], including two appended convergence phases. Regenerating from scratch with all boxes empty would
tell /speckit-implement to rebuild the whole feature. Per the guide's "preserve rationale before replacing derived
artifacts", the regenerated list (a) restates every task from the current design (keyset paging is now in US2
rather than as appended corrective tasks), (b) keeps [X] on tasks whose work is already in the code and is not
changed by the revised design, (c) opens and marks "(changed 2026-10-24)" the tasks the spec change touches, and
(d) keeps the old list's history in a "History" section. Task IDs were renumbered (36 -> 30) because the
convergence phases were folded in; the History section maps old IDs to new ones.

## Completion report

- Path: specs/001-bookmarks-api/tasks.md
- Total tasks: 30 (23 already done [X], 7 open)
- Per story: Setup 3; Foundational 7 (1 open: T008); US1 6 (3 open: T012, T015, T016); US2 6 (0 open);
  US3 2 (0 open); US4 3 (0 open); Polish 3 (3 open: T028, T029, T030)
- Parallel opportunities: T012 with T011/T013/T014; T008 alongside T004-T007; T028 with T029
- Independent test criteria: US1 POST returns 201 new / 200 existing unchanged, one row; US2 cursor paging with
  no repeats or gaps; US3 tag filter newest first; US4 delete 204 then 404
- Suggested MVP scope: User Story 1 (now including the 200-on-repeat behavior)
- Format validation: all 30 tasks match `- [ ] / [X] T### [P?] [US?] description` with file paths (check above
  printed no violations)

Post-execution hooks: none registered.

```diff
$ git diff --stat; git diff
 specs/001-bookmarks-api/tasks.md | 94 +++++++++++++++++++++++-----------------
 1 file changed, 54 insertions(+), 40 deletions(-)
diff --git a/specs/001-bookmarks-api/tasks.md b/specs/001-bookmarks-api/tasks.md
index eca6021..f9fde86 100644
--- a/specs/001-bookmarks-api/tasks.md
+++ b/specs/001-bookmarks-api/tasks.md
@@ -15,6 +15,12 @@ every acceptance scenario, run against the real test database.
 **Organization**: Tasks are grouped by user story so each story can be implemented and tested on
 its own.
 
+**Regenerated 2026-10-24** from the revised spec (FR-004: a repeat save returns the existing
+bookmark with 200 OK instead of 409) and the revised plan. Tasks whose work is already in the code
+and unchanged by the revision keep their `[X]`; tasks the revision changes are open (`[ ]`) and
+marked "changed 2026-10-24". The rationale and history of the previous task list are kept under
+"History" at the end.
+
 ## Format: `[ID] [P?] [Story] Description`
 
 - **[P]**: Can run in parallel (different files, no dependencies)
@@ -40,8 +46,8 @@ its own.
 - [X] T004 Create `src/bookmarks_api/db.py` with a SQLAlchemy engine built from config, a `sessionmaker`, and a FastAPI dependency `get_session()` that yields a session and closes it
 - [X] T005 Create `src/bookmarks_api/models.py` mapping table `bookmarks` exactly as data-model.md: `id bigint` primary key generated always as identity; `url varchar(2048) not null`; `url_normalized varchar(2048) not null, unique`; `title varchar(200) not null, char_length(title) >= 1`; `tags text[] not null, default '{}', cardinality(tags) <= 10`; `created_at timestamptz not null, default now()`
 - [X] T006 Set up Alembic: `alembic.ini` and `migrations/env.py` reading the URL from `bookmarks_api.config` (overridable by `-x url=...` or the `sqlalchemy.url` option set by tests), with target metadata from `models.py`
-- [X] T007 Create migration `migrations/versions/0001_create_bookmarks.py` creating table `bookmarks` with the constraints in T005 and indexes `uq_bookmarks_url_normalized UNIQUE (url_normalized)`, `ix_bookmarks_created_at_id (created_at DESC, id DESC)`, `ix_bookmarks_tags GIN (tags)`; downgrade drops the table
-- [X] T008 [P] Create `src/bookmarks_api/errors.py`: Pydantic models `ErrorBody {code, message, details}` and `ErrorResponse {error: ErrorBody}`; domain exceptions `NotFoundError` and `DuplicateUrlError(existing_id)`; exception handlers producing the envelope for `RequestValidationError` (422 `validation_error`, field errors in `details`), `StarletteHTTPException` (status-mapped code), `NotFoundError` (404 `not_found`), `DuplicateUrlError` (409 `duplicate_url`, `details.existing_id`) and any other exception (500 `internal_error`, no internals) (Constitution III)
+- [X] T007 Create migration `migrations/versions/0001_create_bookmarks.py` creating table `bookmarks` with the constraints in T005 and indexes `uq_bookmarks_url_normalized UNIQUE (url_normalized)`, `ix_bookmarks_created_at_id (created_at DESC, id DESC)`, `ix_bookmarks_tags GIN (tags)`; downgrade drops the table (no new migration for the 2026-10-24 change: the unique index already gives the guarantee, plan.md)
+- [ ] T008 [P] (changed 2026-10-24) `src/bookmarks_api/errors.py`: Pydantic models `ErrorBody {code, message, details}` and `ErrorResponse {error: ErrorBody}`; domain exception `NotFoundError`; exception handlers producing the envelope for `RequestValidationError` (422 `validation_error`, field errors in `details`), `StarletteHTTPException` (status-mapped code), `NotFoundError` (404 `not_found`) and any other exception (500 `internal_error`, no internals) (Constitution III). Remove `DuplicateUrlError` and its 409 `duplicate_url` handler: a repeat save is no longer an error (FR-004, research.md "Error envelope")
 - [X] T009 Create `src/bookmarks_api/main.py` with `create_app()` registering the handlers from T008 and the router from `routes.py`, and module-level `app = create_app()`
 - [X] T010 Create `tests/conftest.py`: read `TEST_DATABASE_URL` (default `postgresql://bookmarks:bookmarks@localhost:5432/bookmarks_test`), run `alembic upgrade head` against it once per session, override `get_session` to use the test database, truncate `bookmarks` (restart identity) before every test, and provide a `client` fixture using FastAPI `TestClient` (Constitution II: no database mocks)
 
@@ -51,24 +57,25 @@ its own.
 
 ## Phase 3: User Story 1 - Save a bookmark (Priority: P1) 🎯 MVP
 
-**Goal**: A user can save a link with a title and optional tags; duplicates are rejected.
+**Goal**: A user can save a link with a title and optional tags; saving a link that is already
+saved returns the existing bookmark unchanged instead of creating a duplicate.
 
 **Independent Test**: `POST /bookmarks` returns 201 with the saved bookmark; saving an equivalent
-link returns 409 with `details.existing_id`.
+link returns 200 with the existing bookmark, unchanged, and still one row.
 
 ### Tests for User Story 1
 
 > Write these first and confirm they fail before implementing.
 
 - [X] T011 [P] [US1] Unit tests in `tests/unit/test_normalize.py` for link normalization (lowercase scheme and host, default ports 80/443 removed, trailing path slashes removed, fragment removed, query kept; examples `HTTPS://Example.com:443/docs/#intro` → `https://example.com/docs`, `https://example.com/search?q=FastAPI` keeps `?q=FastAPI`; non-http(s) and host-less links rejected) and tag normalization (trim, lowercase, de-duplicate, sort; must match `^[a-z0-9-]{1,30}$`)
-- [X] T012 [P] [US1] Integration tests in `tests/integration/test_create_bookmark.py` for User Story 1 scenarios 1 to 4: save with no tags (201, `tags == []`, `created_at` present); tags `["Python", " api ", "python"]` → `["api", "python"]`; `https://example.com/docs` then `HTTPS://Example.com/docs/#intro` → 409 `duplicate_url` with `details.existing_id`, still one row; missing url, missing title, `ftp://` link, url over 2048 characters, title over 200 characters, 11 tags, and invalid tag `"no spaces"` each → 422 `validation_error` and nothing saved; two concurrent saves of equivalent links (two threads) → exactly one 201 and one 409, one row (FR-004)
+- [ ] T012 [P] [US1] (changed 2026-10-24) Integration tests in `tests/integration/test_create_bookmark.py` for User Story 1 scenarios 1 to 4: save with no tags (201, `tags == []`, `created_at` present); tags `["Python", " api ", "python"]` → `["api", "python"]`; `https://example.com/docs` (title "Docs", no tags) then `HTTPS://Example.com/docs/#intro` with title "Other title" and tags `["x"]` → 200 with a body equal to the first response (same `id`, `url` `https://example.com/docs`, `title` "Docs", `tags` `[]`, `created_at`), the stored row unchanged in the database, still one row; missing url, missing title, `ftp://` link, url over 2048 characters, title over 200 characters, 11 tags, and invalid tag `"no spaces"` each → 422 `validation_error` and nothing saved; two concurrent saves of equivalent new links (two threads) → exactly one 201 and one 200, both bodies carrying the same `id`, one row (FR-004)
 
 ### Implementation for User Story 1
 
 - [X] T013 [P] [US1] Implement `normalize_url(url) -> str` and `normalize_tags(tags) -> list[str]` in `src/bookmarks_api/normalize.py` using only the standard library, raising `ValueError` with a clear message on invalid input
 - [X] T014 [P] [US1] Create Pydantic models in `src/bookmarks_api/schemas.py`: `BookmarkCreate` (`url` str, max 2048, http/https with a host; `title` trimmed, 1 to 200 characters; `tags` list default `[]`, normalized via `normalize_tags`, at most 10 after de-duplication; extra fields forbidden) and `Bookmark` (`id`, `url`, `title`, `tags`, `created_at`)
-- [X] T015 [US1] Implement `create_bookmark(session, data)` in `src/bookmarks_api/repository.py` using `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`, raising `DuplicateUrlError(existing_id)` when nothing is inserted (research.md, "Preventing duplicate links")
-- [X] T016 [US1] Implement `POST /bookmarks` in `src/bookmarks_api/routes.py` returning 201 with `Bookmark`, with 409 and 422 responses declared using `ErrorResponse`
+- [ ] T015 [US1] (changed 2026-10-24) Implement `create_bookmark(session, data) -> tuple[BookmarkRow, bool]` in `src/bookmarks_api/repository.py` returning the row and whether it was inserted: `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`; on insert commit and return `(row, True)`; when nothing is inserted, end the transaction, select the existing row by `url_normalized` in a new statement and return `(row, False)` without writing to it; if that select finds nothing (deleted in between), retry the insert once (research.md, "Preventing duplicate links")
+- [ ] T016 [US1] (changed 2026-10-24) Implement `POST /bookmarks` in `src/bookmarks_api/routes.py` returning 201 with `Bookmark` for a new bookmark and 200 with the existing `Bookmark` when the link is already saved; declare the 200 response with the `Bookmark` model and the 422 response with `ErrorResponse`; remove the 409 response (contracts/openapi.yaml)
 
 **Checkpoint**: User Story 1 works and is tested on its own (MVP)
 
@@ -76,23 +83,22 @@ link returns 409 with `details.existing_id`.
 
 ## Phase 4: User Story 2 - List bookmarks, newest first (Priority: P2)
 
-**Goal**: A user can list bookmarks newest first, in pages, with a total count.
+**Goal**: A user can list bookmarks newest first, in keyset pages, with a total count.
 
 **Independent Test**: `GET /bookmarks` returns saved bookmarks newest first with `total`, `limit`
-and `offset`.
-
-> Note (constitution v1.1.0): T017-T020 built offset paging, which Principle VI now forbids. Corrective
-> tasks are appended by /speckit-converge; these tasks are kept as history.
+and `next_cursor`; following `next_cursor` returns the rest with no repeats or gaps.
 
 ### Tests for User Story 2
 
-- [X] T017 [P] [US2] Integration tests in `tests/integration/test_list_bookmarks.py` for User Story 2 scenarios 1 to 4: three saves listed newest first with `total == 3`; empty list with `total == 0`; 25 bookmarks → first page of 20 with `total == 25`, `offset=20` → 5; `limit=101`, `limit=0` and `offset=-1` → 422 `validation_error`; offset past the end → empty page with correct total
+- [X] T017 [P] [US2] Integration tests in `tests/integration/test_list_bookmarks.py` for User Story 2 scenarios 1 to 5: three saves listed newest first with `total == 3`; empty list with `total == 0` and `next_cursor` null; 25 bookmarks → first page of 20 with `total == 25` and a `next_cursor`, next page → 5 with `next_cursor` null; `limit=101` and `limit=0` → 422 `validation_error`; malformed `cursor` → 422; any `offset` → 422 with a message naming `cursor`; paging through all results while bookmarks are saved (and deleted) between requests sees no duplicates and no gaps (Constitution VI quality gate)
+- [X] T018 [P] [US2] Unit tests in `tests/unit/test_cursor.py`: cursor round trip keeps microseconds and id, cursor is URL-safe, malformed cursors raise `ValueError`
 
 ### Implementation for User Story 2
 
-- [X] T018 [P] [US2] Add `BookmarkPage {items: list[Bookmark], total, limit, offset}` to `src/bookmarks_api/schemas.py`
-- [X] T019 [US2] Implement `list_bookmarks(session, limit, offset, tag=None) -> (items, total)` in `src/bookmarks_api/repository.py`, ordered by `created_at DESC, id DESC`, with `total` from a `COUNT(*)` using the same filter
-- [X] T020 [US2] Implement `GET /bookmarks` in `src/bookmarks_api/routes.py` with `limit` (1 to 100, default 20) and `offset` (0 or greater, default 0) query parameters, returning `BookmarkPage`
+- [X] T019 [P] [US2] Add `BookmarkPage {items: list[Bookmark], total, limit, next_cursor: str | None}` to `src/bookmarks_api/schemas.py`
+- [X] T020 [P] [US2] Implement the opaque base64url cursor encoder/decoder over `(created_at, id)` in `src/bookmarks_api/cursor.py` (standard library only; research.md, "Ordering and paging")
+- [X] T021 [US2] Implement `list_bookmarks(session, *, limit, after=None, tag=None) -> (items, total, has_more)` in `src/bookmarks_api/repository.py`, ordered by `created_at DESC, id DESC`, keyset condition `WHERE (created_at, id) < (:created_at, :id)`, fetching `limit + 1` rows, with `total` from a `COUNT(*)` using the same filter; no offset (Constitution VI)
+- [X] T022 [US2] Implement `GET /bookmarks` in `src/bookmarks_api/routes.py` with `limit` (1 to 100, default 20) and `cursor` query parameters, rejecting a malformed cursor and any `offset` with 422 naming `cursor`, returning `BookmarkPage` with `next_cursor` only when more rows exist
 
 **Checkpoint**: User Stories 1 and 2 work independently
 
@@ -107,11 +113,11 @@ first.
 
 ### Tests for User Story 3
 
-- [X] T021 [P] [US3] Integration tests in `tests/integration/test_filter_by_tag.py` for User Story 3 scenarios 1 to 3: filter `postgres` returns only matching bookmarks newest first with matching `total`; `Postgres` matches `postgres`; unknown tag → empty list; invalid tag value → 422
+- [X] T023 [P] [US3] Integration tests in `tests/integration/test_filter_by_tag.py` for User Story 3 scenarios 1 to 3: filter `postgres` returns only matching bookmarks newest first with matching `total`; `Postgres` matches `postgres`; unknown tag → empty list; filter combined with cursor paging; invalid tag value → 422
 
 ### Implementation for User Story 3
 
-- [X] T022 [US3] Add the optional `tag` query parameter to `GET /bookmarks` in `src/bookmarks_api/routes.py`, normalized with the tag rules (invalid → 422), and apply `tags @> ARRAY[:tag]` in `list_bookmarks` in `src/bookmarks_api/repository.py`
+- [X] T024 [US3] Add the optional `tag` query parameter to `GET /bookmarks` in `src/bookmarks_api/routes.py`, normalized with the tag rules (invalid → 422), and apply `tags @> ARRAY[:tag]` in `list_bookmarks` in `src/bookmarks_api/repository.py`
 
 **Checkpoint**: User Stories 1 to 3 work independently
 
@@ -126,12 +132,12 @@ again returns 404.
 
 ### Tests for User Story 4
 
-- [X] T023 [P] [US4] Integration tests in `tests/integration/test_delete_bookmark.py` for User Story 4 scenarios 1 to 3: delete → 204 and absent from list and tag filter; unknown id → 404 `not_found`; delete then save the same link again → 201 new bookmark
+- [X] T025 [P] [US4] Integration tests in `tests/integration/test_delete_bookmark.py` for User Story 4 scenarios 1 to 3: delete → 204 and absent from list and tag filter; unknown id → 404 `not_found`; delete then save the same link again → 201 new bookmark; id 0, negative and non-integer → 422 `validation_error`
 
 ### Implementation for User Story 4
 
-- [X] T024 [US4] Implement `delete_bookmark(session, bookmark_id)` in `src/bookmarks_api/repository.py` raising `NotFoundError` when no row is deleted
-- [X] T025 [US4] Implement `DELETE /bookmarks/{bookmark_id}` in `src/bookmarks_api/routes.py` returning 204, with the 404 response declared using `ErrorResponse`
+- [X] T026 [US4] Implement `delete_bookmark(session, bookmark_id)` in `src/bookmarks_api/repository.py` raising `NotFoundError` when no row is deleted
+- [X] T027 [US4] Implement `DELETE /bookmarks/{bookmark_id}` in `src/bookmarks_api/routes.py` with `bookmark_id >= 1`, returning 204, with the 404 and 422 responses declared using `ErrorResponse`
 
 **Checkpoint**: All user stories work independently
 
@@ -141,9 +147,9 @@ again returns 404.
 
 **Purpose**: Improvements that affect multiple user stories
 
-- [X] T026 [P] Integration tests in `tests/integration/test_errors.py` asserting every error class (422, 404, 409, and an unknown route 404) uses the envelope `{"error": {"code", "message", "details"}}` (SC-005), and that `/openapi.json` lists all three operations with request and response schemas (Constitution I)
-- [X] T027 [P] Update `README.md` with run instructions: `uv sync`, `uv run alembic upgrade head`, `uv run uvicorn bookmarks_api.main:app --reload`, `uv run pytest`
-- [X] T028 Run the full test suite and the manual checks in `specs/001-bookmarks-api/quickstart.md`
+- [ ] T028 [P] (changed 2026-10-24) Integration tests in `tests/integration/test_errors.py` asserting every error class (422, 404, 405, 500, and an unknown route 404) uses the envelope `{"error": {"code", "message", "details"}}` (SC-005), with the 409 `duplicate_url` envelope test removed; and that `/openapi.json` lists all three operations with request and response schemas (Constitution I): `POST /bookmarks` declares 201 and 200 with `Bookmark`, 422 with `ErrorResponse`, and no 409
+- [ ] T029 [P] (changed 2026-10-24) Update the `POST /bookmarks` row in `README.md`: 201 for a new link, 200 with the existing bookmark (unchanged) if the link is already saved, instead of "409 if the link is already saved"
+- [ ] T030 Run the full test suite on Python 3.11, 3.12 and 3.13 and the manual checks in `specs/001-bookmarks-api/quickstart.md` (step 2 now expects 200 with the unchanged step 1 bookmark)
 
 ---
 
@@ -158,6 +164,11 @@ again returns 404.
   its "absent from list" check
 - **Polish (Phase 7)**: Depends on all user stories
 
+### Open work for the 2026-10-24 change
+
+T012 (tests first, confirm they fail) → T015 → T016; T008 after T015 (nothing raises
+`DuplicateUrlError` any more); T028 and T029 after T016; T030 last.
+
 ### Within Each User Story
 
 - Tests first, confirmed failing
@@ -167,8 +178,8 @@ again returns 404.
 
 - T003 alongside T001/T002; T008 alongside T004 to T007
 - US1: T011, T012, T013 and T014 in parallel (different files)
-- US2: T017 and T018 in parallel
-- Polish: T026 and T027 in parallel
+- US2: T017, T018, T019 and T020 in parallel
+- Polish: T028 and T029 in parallel
 
 ## Parallel Example: User Story 1
 
@@ -184,7 +195,7 @@ Task: "BookmarkCreate / Bookmark in src/bookmarks_api/schemas.py"
 ### MVP First (User Story 1 only)
 
 1. Complete Phase 1 and Phase 2
-2. Complete Phase 3 (save with duplicate protection)
+2. Complete Phase 3 (save, returning the existing bookmark for a repeat save)
 3. Stop and validate: run the US1 tests
 
 ### Incremental Delivery
@@ -195,16 +206,19 @@ Task: "BookmarkCreate / Bookmark in src/bookmarks_api/schemas.py"
 
 ---
 
-## Phase 8: Convergence
-
-- [X] T029 Require `bookmark_id >= 1` on `DELETE /bookmarks/{bookmark_id}` in `src/bookmarks_api/routes.py` so 0 and negative ids return 422 `validation_error`, with a test in `tests/integration/test_delete_bookmark.py`, per contracts/openapi.yaml (contradicts)
-- [X] T030 Align `specs/001-bookmarks-api/contracts/openapi.yaml` so the 10-tag limit applies after normalization and de-duplication, matching data-model.md, per FR-011 (contradicts)
-- [X] T031 Run the full test suite on Python 3.11 and 3.12 and fix any incompatibility, per plan: Technical Context (partial)
-
-## Phase 9: Convergence
-
-- [X] T032 CRITICAL: Replace offset paging in `src/bookmarks_api/repository.py` and `src/bookmarks_api/routes.py` with keyset paging on `(created_at, id)` (`WHERE (created_at, id) < (:created_at, :id)`), per Constitution VI (contradicts)
-- [X] T033 Add `next_cursor` to `BookmarkPage` in `src/bookmarks_api/schemas.py` and an opaque base64url cursor encoder/decoder in `src/bookmarks_api/cursor.py`; return `next_cursor` only when more rows exist, per FR-006 and contracts/openapi.yaml (missing)
-- [X] T034 Return 422 `validation_error` for a malformed `cursor` and for any request that sends `offset`, with a message that names `cursor`, per spec Edge Cases (missing)
-- [X] T035 Rewrite the paging tests in `tests/integration/test_list_bookmarks.py` and `tests/integration/test_filter_by_tag.py` for cursors, and add a test that pages through all results while bookmarks are saved between requests and finds no duplicates and no gaps, per US2/AC3-AC5 and the Constitution VI quality gate (missing)
-- [X] T036 Update the `GET /bookmarks` row in `README.md` to document `cursor` and `next_cursor` instead of `offset`, per contracts/openapi.yaml (partial)
+## History (preserved from the previous task list, 2026-10-21 to 2026-10-23)
+
+- The first list built offset paging for US2 (old T017-T020: `limit`/`offset`, `BookmarkPage
+  {items, total, limit, offset}`). Constitution v1.1.0 (Principle VI) then forbade offset paging;
+  `/speckit-converge` appended Phase 9 (old T032-T036) to replace it with keyset paging on
+  `(created_at, id)`, an opaque base64url cursor in `cursor.py`, 422 for a malformed cursor or any
+  `offset`, cursor-based paging tests including saves between pages, and the README update. In
+  this list those are folded into T017-T022 as the design now states them.
+- Old Phase 8 (convergence pass 1): T029 required `bookmark_id >= 1` on delete (now T025/T027);
+  T030 aligned the contract so the 10-tag limit applies after de-duplication (contract only); T031
+  ran the suite on 3.11 and 3.12 (now T030, extended to 3.13).
+- Old T008, T012, T015, T016 and T026 built and tested the 409 `duplicate_url` response with
+  `details.existing_id` for a repeat save (rationale: the database's unique index plus
+  `ON CONFLICT DO NOTHING` guarantees one row under races, without catching exceptions
+  mid-transaction). The 2026-10-24 spec change keeps that mechanism and replaces the 409 with 200
+  and the existing bookmark (now T008, T012, T015, T016, T028).
```

End: 2026-10-24T11:47:38Z
