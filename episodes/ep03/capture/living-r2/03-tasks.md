# Step 03 — tasks (Spec Kit tasks command, existing feature)

Start: 2026-10-24T12:00:39Z

```console
$ test -f .specify/extensions.yml && cat .specify/extensions.yml || echo 'no .specify/extensions.yml (before_tasks hooks skipped)'
no .specify/extensions.yml (before_tasks hooks skipped)
[exit 0]
```

```console
$ .specify/scripts/bash/setup-tasks.sh --json | python3 -c 'import json,sys; d=json.load(sys.stdin); c=d.pop("TASKS_TEMPLATE_CONTENT"); print(json.dumps(d, indent=1)); print("TASKS_TEMPLATE_CONTENT: %d chars (template printed below)" % len(c)); print(c)'
{
 "FEATURE_DIR": "/home/claude/runs/living-r2/specs/001-bookmarks-api",
 "AVAILABLE_DOCS": [
  "research.md",
  "data-model.md",
  "contracts/",
  "quickstart.md"
 ],
 "TASKS_TEMPLATE": "/home/claude/runs/living-r2/.specify/templates/tasks-template.md"
}
TASKS_TEMPLATE_CONTENT: 9134 chars (template printed below)
---

description: "Task list template for feature implementation"
---

# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

<!--
  ============================================================================
  IMPORTANT: The tasks below are SAMPLE TASKS for illustration purposes only.

  The /speckit-tasks command MUST replace these with actual tasks based on:
  - User stories from spec.md (with their priorities P1, P2, P3...)
  - Feature requirements from plan.md
  - Entities from data-model.md
  - Endpoints from contracts/

  Tasks MUST be organized by user story so each story can be:
  - Implemented independently
  - Tested independently
  - Delivered as an MVP increment

  DO NOT keep these sample tasks in the generated tasks.md file.
  ============================================================================
-->

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize [language] project with [framework] dependencies
- [ ] T003 [P] Configure linting and formatting tools

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [ ] T004 Setup database schema and migrations framework
- [ ] T005 [P] Implement authentication/authorization framework
- [ ] T006 [P] Setup API routing and middleware structure
- [ ] T007 Create base models/entities that all stories depend on
- [ ] T008 Configure error handling and logging infrastructure
- [ ] T009 Setup environment configuration management

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - [Title] (Priority: P1) 🎯 MVP

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T010 [P] [US1] Contract test for [endpoint] in tests/contract/test_[name].py
- [ ] T011 [P] [US1] Integration test for [user journey] in tests/integration/test_[name].py

### Implementation for User Story 1

- [ ] T012 [P] [US1] Create [Entity1] model in src/models/[entity1].py
- [ ] T013 [P] [US1] Create [Entity2] model in src/models/[entity2].py
- [ ] T014 [US1] Implement [Service] in src/services/[service].py (depends on T012, T013)
- [ ] T015 [US1] Implement [endpoint/feature] in src/[location]/[file].py
- [ ] T016 [US1] Add validation and error handling
- [ ] T017 [US1] Add logging for user story 1 operations

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - [Title] (Priority: P2)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [ ] T018 [P] [US2] Contract test for [endpoint] in tests/contract/test_[name].py
- [ ] T019 [P] [US2] Integration test for [user journey] in tests/integration/test_[name].py

### Implementation for User Story 2

- [ ] T020 [P] [US2] Create [Entity] model in src/models/[entity].py
- [ ] T021 [US2] Implement [Service] in src/services/[service].py
- [ ] T022 [US2] Implement [endpoint/feature] in src/[location]/[file].py
- [ ] T023 [US2] Integrate with User Story 1 components (if needed)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - [Title] (Priority: P3)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [ ] T024 [P] [US3] Contract test for [endpoint] in tests/contract/test_[name].py
- [ ] T025 [P] [US3] Integration test for [user journey] in tests/integration/test_[name].py

### Implementation for User Story 3

- [ ] T026 [P] [US3] Create [Entity] model in src/models/[entity].py
- [ ] T027 [US3] Implement [Service] in src/services/[service].py
- [ ] T028 [US3] Implement [endpoint/feature] in src/[location]/[file].py

**Checkpoint**: All user stories should now be independently functional

---

[Add more user story phases as needed, following the same pattern]

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] TXXX [P] Documentation updates in docs/
- [ ] TXXX Code cleanup and refactoring
- [ ] TXXX Performance optimization across all stories
- [ ] TXXX [P] Additional unit tests (if requested) in tests/unit/
- [ ] TXXX Security hardening
- [ ] TXXX Run quickstart.md validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for [endpoint] in tests/contract/test_[name].py"
Task: "Integration test for [user journey] in tests/integration/test_[name].py"

# Launch all models for User Story 1 together:
Task: "Create [Entity1] model in src/models/[entity1].py"
Task: "Create [Entity2] model in src/models/[entity2].py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
[exit 0]
```

## Rationale in the old tasks.md preserved before regeneration

- Tests are included because Constitution II/V and SC-004 require an automated test for every
  acceptance scenario, against the real test database (header "Tests: Included").
- T001: `httpx2` rather than plain `httpx` for FastAPI's TestClient (current Starlette deprecates
  plain httpx there); compatible version ranges (Constitution IV).
- T003 / research: `postgresql://` URLs rewritten to `postgresql+psycopg://`.
- T015: duplicate protection via `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`
  (research.md, "Preventing duplicate links").
- Note before T017: "T017-T020 built offset paging, which Principle VI now forbids. Corrective
  tasks are appended by /speckit-converge; these tasks are kept as history." Phase 9 (T032-T036)
  replaced offset with keyset paging on `(created_at, id)`, an opaque base64url cursor in
  `cursor.py`, 422 for a malformed cursor or any `offset`, and a no-duplicates/no-gaps paging test.
- Phase 8 (T029-T031): `bookmark_id >= 1` on DELETE (422 for 0/negative); 10-tag limit applies
  after normalization and de-duplication; suite must pass on 3.11 and 3.12 as well as 3.13.
- Within-story order: tests first (confirmed failing), schemas and pure functions before the
  repository, repository before routes.

Decision for this regeneration (recorded because the tasks command does not say how to treat a
feature that is already implemented): tasks.md is regenerated in full from the template and the
current design documents, so the paging work is written as keyset from the start instead of as
offset + convergence history. A task whose requirement is unchanged by the 2026-10-24 revision
and that was already complete (`[X]`) in the old list keeps `[X]`; every task the revised FR-004
touches is new and unchecked (`[ ]`). A short History section records the replaced phases.

```console
$ grep -c -E '^- \[[ X]\] T[0-9]{3} ' specs/001-bookmarks-api/tasks.md; grep -E '^- \[ \] ' specs/001-bookmarks-api/tasks.md | cut -c1-90; grep -E '^- \[' specs/001-bookmarks-api/tasks.md | grep -v -E '^- \[[ X]\] T[0-9]{3} ' || echo 'format: all task lines match - [ ]/[X] Tnnn'
30
- [ ] T012 [P] [US1] Update integration tests in `tests/integration/test_create_bookmark.p
- [ ] T015 [US1] Change `create_bookmark(session, data)` in `src/bookmarks_api/repository.
- [ ] T016 [US1] Update `POST /bookmarks` in `src/bookmarks_api/routes.py` to set the stat
- [ ] T017 [US1] Remove `DuplicateUrlError` and its 409 `duplicate_url` handler from `src/
- [ ] T028 [P] Update `tests/integration/test_errors.py`: every error class (422, 404, and
- [ ] T029 [P] Update the `POST /bookmarks` row in `README.md`: a new link returns 201; an
- [ ] T030 Run the full test suite on Python 3.11, 3.12 and 3.13 and the manual checks in 
format: all task lines match - [ ]/[X] Tnnn
[exit 0]
```

```console
$ git diff --stat -- specs/001-bookmarks-api/tasks.md
 specs/001-bookmarks-api/tasks.md | 97 +++++++++++++++++++++-------------------
 1 file changed, 51 insertions(+), 46 deletions(-)
[exit 0]
```

```console
$ git diff -- specs/001-bookmarks-api/tasks.md
diff --git a/specs/001-bookmarks-api/tasks.md b/specs/001-bookmarks-api/tasks.md
index eca6021..eeaa936 100644
--- a/specs/001-bookmarks-api/tasks.md
+++ b/specs/001-bookmarks-api/tasks.md
@@ -15,6 +15,12 @@ every acceptance scenario, run against the real test database.
 **Organization**: Tasks are grouped by user story so each story can be implemented and tested on
 its own.
 
+**Revision 2026-10-24**: Regenerated from the revised spec (FR-004: saving an already saved link
+returns the existing bookmark unchanged with 200 OK instead of 409; a new link still returns 201;
+two concurrent saves of the same new link store one bookmark, one 201 and one 200). Tasks whose
+requirements did not change and that were already complete keep `[X]`; tasks for the revised
+duplicate rule are open `[ ]`. See "History" at the end for the replaced phases.
+
 ## Format: `[ID] [P?] [Story] Description`
 
 - **[P]**: Can run in parallel (different files, no dependencies)
@@ -41,7 +47,7 @@ its own.
 - [X] T005 Create `src/bookmarks_api/models.py` mapping table `bookmarks` exactly as data-model.md: `id bigint` primary key generated always as identity; `url varchar(2048) not null`; `url_normalized varchar(2048) not null, unique`; `title varchar(200) not null, char_length(title) >= 1`; `tags text[] not null, default '{}', cardinality(tags) <= 10`; `created_at timestamptz not null, default now()`
 - [X] T006 Set up Alembic: `alembic.ini` and `migrations/env.py` reading the URL from `bookmarks_api.config` (overridable by `-x url=...` or the `sqlalchemy.url` option set by tests), with target metadata from `models.py`
 - [X] T007 Create migration `migrations/versions/0001_create_bookmarks.py` creating table `bookmarks` with the constraints in T005 and indexes `uq_bookmarks_url_normalized UNIQUE (url_normalized)`, `ix_bookmarks_created_at_id (created_at DESC, id DESC)`, `ix_bookmarks_tags GIN (tags)`; downgrade drops the table
-- [X] T008 [P] Create `src/bookmarks_api/errors.py`: Pydantic models `ErrorBody {code, message, details}` and `ErrorResponse {error: ErrorBody}`; domain exceptions `NotFoundError` and `DuplicateUrlError(existing_id)`; exception handlers producing the envelope for `RequestValidationError` (422 `validation_error`, field errors in `details`), `StarletteHTTPException` (status-mapped code), `NotFoundError` (404 `not_found`), `DuplicateUrlError` (409 `duplicate_url`, `details.existing_id`) and any other exception (500 `internal_error`, no internals) (Constitution III)
+- [X] T008 [P] Create `src/bookmarks_api/errors.py`: Pydantic models `ErrorBody {code, message, details}` and `ErrorResponse {error: ErrorBody}`; domain exception `NotFoundError`; exception handlers producing the envelope for `RequestValidationError` (422 `validation_error`, field errors in `details`), `StarletteHTTPException` (status-mapped code), `NotFoundError` (404 `not_found`) and any other exception (500 `internal_error`, no internals) (Constitution III)
 - [X] T009 Create `src/bookmarks_api/main.py` with `create_app()` registering the handlers from T008 and the router from `routes.py`, and module-level `app = create_app()`
 - [X] T010 Create `tests/conftest.py`: read `TEST_DATABASE_URL` (default `postgresql://bookmarks:bookmarks@localhost:5432/bookmarks_test`), run `alembic upgrade head` against it once per session, override `get_session` to use the test database, truncate `bookmarks` (restart identity) before every test, and provide a `client` fixture using FastAPI `TestClient` (Constitution II: no database mocks)
 
@@ -51,24 +57,27 @@ its own.
 
 ## Phase 3: User Story 1 - Save a bookmark (Priority: P1) 🎯 MVP
 
-**Goal**: A user can save a link with a title and optional tags; duplicates are rejected.
+**Goal**: A user can save a link with a title and optional tags; saving a link that is already
+saved returns the existing bookmark unchanged instead of creating a duplicate.
 
 **Independent Test**: `POST /bookmarks` returns 201 with the saved bookmark; saving an equivalent
-link returns 409 with `details.existing_id`.
+link with a different title and tags returns 200 with the first bookmark unchanged, and there is
+still one row.
 
 ### Tests for User Story 1
 
 > Write these first and confirm they fail before implementing.
 
 - [X] T011 [P] [US1] Unit tests in `tests/unit/test_normalize.py` for link normalization (lowercase scheme and host, default ports 80/443 removed, trailing path slashes removed, fragment removed, query kept; examples `HTTPS://Example.com:443/docs/#intro` → `https://example.com/docs`, `https://example.com/search?q=FastAPI` keeps `?q=FastAPI`; non-http(s) and host-less links rejected) and tag normalization (trim, lowercase, de-duplicate, sort; must match `^[a-z0-9-]{1,30}$`)
-- [X] T012 [P] [US1] Integration tests in `tests/integration/test_create_bookmark.py` for User Story 1 scenarios 1 to 4: save with no tags (201, `tags == []`, `created_at` present); tags `["Python", " api ", "python"]` → `["api", "python"]`; `https://example.com/docs` then `HTTPS://Example.com/docs/#intro` → 409 `duplicate_url` with `details.existing_id`, still one row; missing url, missing title, `ftp://` link, url over 2048 characters, title over 200 characters, 11 tags, and invalid tag `"no spaces"` each → 422 `validation_error` and nothing saved; two concurrent saves of equivalent links (two threads) → exactly one 201 and one 409, one row (FR-004)
+- [ ] T012 [P] [US1] Update integration tests in `tests/integration/test_create_bookmark.py` for the revised User Story 1 scenario 3 and FR-004: save `https://example.com/docs` (title "Docs", tags `["a"]`) then `HTTPS://Example.com/docs/#intro` with title "Other" and tags `["b"]` → second response is 200 (not 201, not 409) and its body equals the first response body exactly (same `id`, `url` as first given, `title` "Docs", `tags` `["a"]`, `created_at`); the stored row's `url`, `title`, `tags` and `created_at` are unchanged when read back from the database; still exactly one row. Replace the concurrency test: two concurrent saves (two threads) of the same new link → status codes sorted are `[200, 201]`, both bodies carry the same `id`, exactly one row. Keep the scenario 1, 2 and 4 tests as they are; remove every assertion on 409 or `duplicate_url`
+- [X] T013 [P] [US1] Implement `normalize_url(url) -> str` and `normalize_tags(tags) -> list[str]` in `src/bookmarks_api/normalize.py` using only the standard library, raising `ValueError` with a clear message on invalid input
+- [X] T014 [P] [US1] Create Pydantic models in `src/bookmarks_api/schemas.py`: `BookmarkCreate` (`url` str, max 2048, http/https with a host; `title` trimmed, 1 to 200 characters; `tags` list default `[]`, normalized via `normalize_tags`, at most 10 after de-duplication; extra fields forbidden) and `Bookmark` (`id`, `url`, `title`, `tags`, `created_at`)
 
 ### Implementation for User Story 1
 
-- [X] T013 [P] [US1] Implement `normalize_url(url) -> str` and `normalize_tags(tags) -> list[str]` in `src/bookmarks_api/normalize.py` using only the standard library, raising `ValueError` with a clear message on invalid input
-- [X] T014 [P] [US1] Create Pydantic models in `src/bookmarks_api/schemas.py`: `BookmarkCreate` (`url` str, max 2048, http/https with a host; `title` trimmed, 1 to 200 characters; `tags` list default `[]`, normalized via `normalize_tags`, at most 10 after de-duplication; extra fields forbidden) and `Bookmark` (`id`, `url`, `title`, `tags`, `created_at`)
-- [X] T015 [US1] Implement `create_bookmark(session, data)` in `src/bookmarks_api/repository.py` using `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`, raising `DuplicateUrlError(existing_id)` when nothing is inserted (research.md, "Preventing duplicate links")
-- [X] T016 [US1] Implement `POST /bookmarks` in `src/bookmarks_api/routes.py` returning 201 with `Bookmark`, with 409 and 422 responses declared using `ErrorResponse`
+- [ ] T015 [US1] Change `create_bookmark(session, data)` in `src/bookmarks_api/repository.py` to return `(row, created: bool)`: keep `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`; a returned row → commit and return `(row, True)`; no row → end the insert transaction, select the existing row by `url_normalized` and return `(existing_row, False)` without writing the request's title or tags (no `DO UPDATE`); if that select finds nothing (the row was deleted in between), retry the insert once (research.md, "Preventing duplicate links", revised 2026-10-24)
+- [ ] T016 [US1] Update `POST /bookmarks` in `src/bookmarks_api/routes.py` to set the status code from the `created` flag (201 Created for a new link, 200 OK for an already saved link), both with the `Bookmark` response model; declare the 200 response in `responses` (description "The link was already saved; the existing bookmark, unchanged") and remove the 409 response, per contracts/openapi.yaml
+- [ ] T017 [US1] Remove `DuplicateUrlError` and its 409 `duplicate_url` handler from `src/bookmarks_api/errors.py` and its import from `src/bookmarks_api/repository.py`; keep the generic `409: "conflict"` entry in `STATUS_CODES` for framework `HTTPException`s (plan.md, Constitution Check III)
 
 **Checkpoint**: User Story 1 works and is tested on its own (MVP)
 
@@ -76,23 +85,21 @@ link returns 409 with `details.existing_id`.
 
 ## Phase 4: User Story 2 - List bookmarks, newest first (Priority: P2)
 
-**Goal**: A user can list bookmarks newest first, in pages, with a total count.
+**Goal**: A user can list bookmarks newest first, in cursor pages, with a total count.
 
 **Independent Test**: `GET /bookmarks` returns saved bookmarks newest first with `total`, `limit`
-and `offset`.
-
-> Note (constitution v1.1.0): T017-T020 built offset paging, which Principle VI now forbids. Corrective
-> tasks are appended by /speckit-converge; these tasks are kept as history.
+and `next_cursor`; following `next_cursor` returns the rest with no repeats or gaps.
 
 ### Tests for User Story 2
 
-- [X] T017 [P] [US2] Integration tests in `tests/integration/test_list_bookmarks.py` for User Story 2 scenarios 1 to 4: three saves listed newest first with `total == 3`; empty list with `total == 0`; 25 bookmarks → first page of 20 with `total == 25`, `offset=20` → 5; `limit=101`, `limit=0` and `offset=-1` → 422 `validation_error`; offset past the end → empty page with correct total
+- [X] T018 [P] [US2] Integration tests in `tests/integration/test_list_bookmarks.py` for User Story 2 scenarios 1 to 5: three saves listed newest first with `total == 3`; empty list with `total == 0`; 25 bookmarks → first page of 20 with `total == 25` and a `next_cursor`, next page → 5 with `next_cursor` null; `limit=101`, `limit=0`, a malformed `cursor` and any `offset` → 422 `validation_error` (the offset message names `cursor`); a test that pages through all results while bookmarks are saved between requests and finds no duplicates and no gaps (Constitution VI quality gate); unit tests for the cursor codec in `tests/unit/test_cursor.py`
 
 ### Implementation for User Story 2
 
-- [X] T018 [P] [US2] Add `BookmarkPage {items: list[Bookmark], total, limit, offset}` to `src/bookmarks_api/schemas.py`
-- [X] T019 [US2] Implement `list_bookmarks(session, limit, offset, tag=None) -> (items, total)` in `src/bookmarks_api/repository.py`, ordered by `created_at DESC, id DESC`, with `total` from a `COUNT(*)` using the same filter
-- [X] T020 [US2] Implement `GET /bookmarks` in `src/bookmarks_api/routes.py` with `limit` (1 to 100, default 20) and `offset` (0 or greater, default 0) query parameters, returning `BookmarkPage`
+- [X] T019 [P] [US2] Add `BookmarkPage {items: list[Bookmark], total, limit, next_cursor: str | None}` to `src/bookmarks_api/schemas.py`
+- [X] T020 [P] [US2] Create `src/bookmarks_api/cursor.py` with an opaque cursor encoder/decoder: the last row's `created_at` and `id`, JSON-encoded then base64url-encoded (standard library only); decoding a malformed value raises `ValueError`
+- [X] T021 [US2] Implement `list_bookmarks(session, limit, after=None, tag=None) -> (items, total, has_more)` in `src/bookmarks_api/repository.py` with keyset paging `WHERE (created_at, id) < (:created_at, :id)`, ordered by `created_at DESC, id DESC`, fetching `limit + 1` rows to detect more pages, with `total` from a `COUNT(*)` using the same filter (Constitution VI; no offset)
+- [X] T022 [US2] Implement `GET /bookmarks` in `src/bookmarks_api/routes.py` with `limit` (1 to 100, default 20) and `cursor` query parameters, returning `BookmarkPage` with `next_cursor` only when more rows exist; a malformed `cursor` or any `offset` parameter returns 422 `validation_error` with a message that names `cursor` (spec Edge Cases)
 
 **Checkpoint**: User Stories 1 and 2 work independently
 
@@ -107,11 +114,11 @@ first.
 
 ### Tests for User Story 3
 
-- [X] T021 [P] [US3] Integration tests in `tests/integration/test_filter_by_tag.py` for User Story 3 scenarios 1 to 3: filter `postgres` returns only matching bookmarks newest first with matching `total`; `Postgres` matches `postgres`; unknown tag → empty list; invalid tag value → 422
+- [X] T023 [P] [US3] Integration tests in `tests/integration/test_filter_by_tag.py` for User Story 3 scenarios 1 to 3: filter `postgres` returns only matching bookmarks newest first with matching `total`; `Postgres` matches `postgres`; unknown tag → empty list; invalid tag value → 422; paging a filtered list with `next_cursor`
 
 ### Implementation for User Story 3
 
-- [X] T022 [US3] Add the optional `tag` query parameter to `GET /bookmarks` in `src/bookmarks_api/routes.py`, normalized with the tag rules (invalid → 422), and apply `tags @> ARRAY[:tag]` in `list_bookmarks` in `src/bookmarks_api/repository.py`
+- [X] T024 [US3] Add the optional `tag` query parameter to `GET /bookmarks` in `src/bookmarks_api/routes.py`, normalized with the tag rules (invalid → 422), and apply `tags @> ARRAY[:tag]` in `list_bookmarks` in `src/bookmarks_api/repository.py`
 
 **Checkpoint**: User Stories 1 to 3 work independently
 
@@ -126,12 +133,12 @@ again returns 404.
 
 ### Tests for User Story 4
 
-- [X] T023 [P] [US4] Integration tests in `tests/integration/test_delete_bookmark.py` for User Story 4 scenarios 1 to 3: delete → 204 and absent from list and tag filter; unknown id → 404 `not_found`; delete then save the same link again → 201 new bookmark
+- [X] T025 [P] [US4] Integration tests in `tests/integration/test_delete_bookmark.py` for User Story 4 scenarios 1 to 3: delete → 204 and absent from list and tag filter; unknown id → 404 `not_found`; id 0 or negative → 422 `validation_error`; delete then save the same link again → 201 new bookmark
 
 ### Implementation for User Story 4
 
-- [X] T024 [US4] Implement `delete_bookmark(session, bookmark_id)` in `src/bookmarks_api/repository.py` raising `NotFoundError` when no row is deleted
-- [X] T025 [US4] Implement `DELETE /bookmarks/{bookmark_id}` in `src/bookmarks_api/routes.py` returning 204, with the 404 response declared using `ErrorResponse`
+- [X] T026 [US4] Implement `delete_bookmark(session, bookmark_id)` in `src/bookmarks_api/repository.py` raising `NotFoundError` when no row is deleted
+- [X] T027 [US4] Implement `DELETE /bookmarks/{bookmark_id}` in `src/bookmarks_api/routes.py` with `bookmark_id >= 1`, returning 204, with the 404 response declared using `ErrorResponse`
 
 **Checkpoint**: All user stories work independently
 
@@ -141,9 +148,9 @@ again returns 404.
 
 **Purpose**: Improvements that affect multiple user stories
 
-- [X] T026 [P] Integration tests in `tests/integration/test_errors.py` asserting every error class (422, 404, 409, and an unknown route 404) uses the envelope `{"error": {"code", "message", "details"}}` (SC-005), and that `/openapi.json` lists all three operations with request and response schemas (Constitution I)
-- [X] T027 [P] Update `README.md` with run instructions: `uv sync`, `uv run alembic upgrade head`, `uv run uvicorn bookmarks_api.main:app --reload`, `uv run pytest`
-- [X] T028 Run the full test suite and the manual checks in `specs/001-bookmarks-api/quickstart.md`
+- [ ] T028 [P] Update `tests/integration/test_errors.py`: every error class (422, 404, and an unknown route 404) uses the envelope `{"error": {"code", "message", "details"}}` (SC-005); remove the duplicate 409 envelope test (a duplicate save is no longer an error); the `/openapi.json` check expects `POST /bookmarks` to declare 200, 201 and 422 and no 409, alongside the GET and DELETE operations with request and response schemas (Constitution I, contracts/openapi.yaml)
+- [ ] T029 [P] Update the `POST /bookmarks` row in `README.md`: a new link returns 201; an already saved link returns 200 with the existing bookmark unchanged (title and tags in the request ignored), instead of 409
+- [ ] T030 Run the full test suite on Python 3.11, 3.12 and 3.13 and the manual checks in `specs/001-bookmarks-api/quickstart.md` (step 2 now expects 200 with the step 1 bookmark unchanged)
 
 ---
 
@@ -158,6 +165,11 @@ again returns 404.
   its "absent from list" check
 - **Polish (Phase 7)**: Depends on all user stories
 
+### Open work for the 2026-10-24 revision
+
+- T012 (tests, confirmed failing) → T015 (repository) → T016 (route) → T017 (remove the duplicate
+  error); T028 and T029 can run alongside T015 to T017; T030 last.
+
 ### Within Each User Story
 
 - Tests first, confirmed failing
@@ -167,16 +179,15 @@ again returns 404.
 
 - T003 alongside T001/T002; T008 alongside T004 to T007
 - US1: T011, T012, T013 and T014 in parallel (different files)
-- US2: T017 and T018 in parallel
-- Polish: T026 and T027 in parallel
+- US2: T018, T019 and T020 in parallel
+- Polish: T028 and T029 in parallel
 
 ## Parallel Example: User Story 1
 
 ```text
-Task: "Unit tests for normalization in tests/unit/test_normalize.py"          (T011)
-Task: "Integration tests for saving in tests/integration/test_create_bookmark.py" (T012)
-Task: "normalize_url / normalize_tags in src/bookmarks_api/normalize.py"         (T013)
-Task: "BookmarkCreate / Bookmark in src/bookmarks_api/schemas.py"                (T014)
+Task: "Revised duplicate and concurrency tests in tests/integration/test_create_bookmark.py" (T012)
+Task: "Error envelope and OpenAPI test updates in tests/integration/test_errors.py"          (T028)
+Task: "README POST row in README.md"                                                         (T029)
 ```
 
 ## Implementation Strategy
@@ -184,7 +195,7 @@ Task: "BookmarkCreate / Bookmark in src/bookmarks_api/schemas.py"
 ### MVP First (User Story 1 only)
 
 1. Complete Phase 1 and Phase 2
-2. Complete Phase 3 (save with duplicate protection)
+2. Complete Phase 3 (save, returning the existing bookmark for an already saved link)
 3. Stop and validate: run the US1 tests
 
 ### Incremental Delivery
@@ -193,18 +204,12 @@ Task: "BookmarkCreate / Bookmark in src/bookmarks_api/schemas.py"
 2. US1 → MVP; US2 → listing; US3 → filtering; US4 → delete
 3. Polish: cross-cutting error and OpenAPI checks, README, quickstart validation
 
----
-
-## Phase 8: Convergence
-
-- [X] T029 Require `bookmark_id >= 1` on `DELETE /bookmarks/{bookmark_id}` in `src/bookmarks_api/routes.py` so 0 and negative ids return 422 `validation_error`, with a test in `tests/integration/test_delete_bookmark.py`, per contracts/openapi.yaml (contradicts)
-- [X] T030 Align `specs/001-bookmarks-api/contracts/openapi.yaml` so the 10-tag limit applies after normalization and de-duplication, matching data-model.md, per FR-011 (contradicts)
-- [X] T031 Run the full test suite on Python 3.11 and 3.12 and fix any incompatibility, per plan: Technical Context (partial)
-
-## Phase 9: Convergence
+## History
 
-- [X] T032 CRITICAL: Replace offset paging in `src/bookmarks_api/repository.py` and `src/bookmarks_api/routes.py` with keyset paging on `(created_at, id)` (`WHERE (created_at, id) < (:created_at, :id)`), per Constitution VI (contradicts)
-- [X] T033 Add `next_cursor` to `BookmarkPage` in `src/bookmarks_api/schemas.py` and an opaque base64url cursor encoder/decoder in `src/bookmarks_api/cursor.py`; return `next_cursor` only when more rows exist, per FR-006 and contracts/openapi.yaml (missing)
-- [X] T034 Return 422 `validation_error` for a malformed `cursor` and for any request that sends `offset`, with a message that names `cursor`, per spec Edge Cases (missing)
-- [X] T035 Rewrite the paging tests in `tests/integration/test_list_bookmarks.py` and `tests/integration/test_filter_by_tag.py` for cursors, and add a test that pages through all results while bookmarks are saved between requests and finds no duplicates and no gaps, per US2/AC3-AC5 and the Constitution VI quality gate (missing)
-- [X] T036 Update the `GET /bookmarks` row in `README.md` to document `cursor` and `next_cursor` instead of `offset`, per contracts/openapi.yaml (partial)
+- 2026-10-21: the original list (T001 to T028) built offset paging in US2; Phase 8 (T029 to T031,
+  delete id >= 1, tag limit after de-duplication, Python 3.11/3.12) and Phase 9 (T032 to T036,
+  keyset paging with `next_cursor`, 422 for malformed cursor or `offset`, paging stability test,
+  README) were appended by `/speckit-converge`. This regeneration folds those into the story
+  phases (T018 to T022, T025, T027).
+- 2026-10-24: duplicate saves changed from 409 `duplicate_url` with `details.existing_id` to 200
+  with the existing bookmark (T012, T015, T016, T017, T028, T029, T030).
[exit 0]
```

```console
$ test -f .specify/extensions.yml && cat .specify/extensions.yml || echo 'no .specify/extensions.yml (after_tasks hooks skipped)'
no .specify/extensions.yml (after_tasks hooks skipped)
[exit 0]
```

## Completion report (tasks command)

- Path: `specs/001-bookmarks-api/tasks.md` (regenerated in full from the template; 30 tasks, T001-T030)
- Task count per phase / story: Setup 3 (T001-T003), Foundational 7 (T004-T010), US1 7
  (T011-T017), US2 5 (T018-T022), US3 2 (T023-T024), US4 3 (T025-T027), Polish 3 (T028-T030)
- Open tasks (the change): 7 — T012, T015, T016, T017 (US1), T028, T029, T030 (Polish).
  23 tasks carried as `[X]` (requirements unchanged and already built).
- Parallel opportunities: T012 ∥ T028 ∥ T029 (different files); T015 → T016 → T017 sequential
  (repository, routes, errors are touched in order and T017 removes an import T015 stops using).
- Independent test criteria: US1 — `POST /bookmarks` 201 for a new link; equivalent link with a
  different title/tags → 200 with the first bookmark unchanged and one row; concurrent saves →
  [200, 201], same id, one row. US2-US4 unchanged (cursor paging; tag filter; delete 204/404/422).
- Suggested MVP scope: User Story 1 (it is the only story the change touches).
- Format validation: all 30 task lines match `- [ ]|[X] Tnnn [P?] [USn?] description with file path`
  (check above prints no non-matching lines).
- Note: T008's text (already `[X]`) was rewritten to no longer list `DuplicateUrlError`, so it
  describes the target state; the code still has `DuplicateUrlError` until T017 runs. Recorded as
  a known inconsistency of the "keep [X] for unchanged requirements" decision.
- Extension hooks: none (no `.specify/extensions.yml`).

End: 2026-10-24T12:02:48Z
