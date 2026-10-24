---

description: "Task list for idempotent duplicate save"
---

# Tasks: Idempotent Duplicate Save

**Input**: Design documents from `/specs/002-idempotent-duplicate-save/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md

**Supersedes**: the duplicate-save tasks of [specs/001-bookmarks-api/tasks.md](../001-bookmarks-api/tasks.md)
(T008's `DuplicateUrlError`/409 handler, T012's 409 expectations, T015's raise, T016's 409
response, T026's 409 envelope check). That file is a historical record and is not edited.

**Tests**: Included. The spec requires every acceptance scenario to be covered by an automated test
(SC-004) and Constitution V requires tests in the same change.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- Single project: `src/bookmarks_api/`, `tests/` at repository root (plan.md "Source Code")

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

None. The project, dependencies, database and migrations already exist; this feature adds no
dependency and no migration (plan.md, data-model.md).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

None. The `bookmarks` table and the `uq_bookmarks_url_normalized` unique index ("not null,
**unique**") are already in place (data-model.md).

**Checkpoint**: Foundation ready - user story implementation can begin.

---

## Phase 3: User Story 1 - Re-saving a bookmarked link returns the existing bookmark (Priority: P1) 🎯 MVP

**Goal**: A valid save of an already bookmarked link returns the stored bookmark unchanged with 200
OK; a new link still returns 201 Created; two concurrent saves of a new link store one bookmark and
answer one 201 and one 200 with the same bookmark (spec FR-001 to FR-005, FR-007).

**Independent Test**: Save `https://example.com/docs`, then save `HTTPS://Example.com/docs/#intro`
with a different title and tags; the second response is 200 with a body identical to the first,
and the table holds one row with the original title and tags.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T001 [P] [US1] In `tests/integration/test_create_bookmark.py`, replace `test_equivalent_link_is_rejected_as_duplicate` with `test_equivalent_link_returns_existing_bookmark_with_200`: save `https://example.com/docs` (title "Docs"), then `HTTPS://Example.com/docs/#intro` (title "Other title", tags `["x"]`); assert the second status is 200, its JSON equals the first response's JSON (same `id`, `url`, `title`, `tags`, `created_at`), and `row_count() == 1` (spec US1 AC1, FR-002)
- [ ] T002 [P] [US1] In `tests/integration/test_create_bookmark.py`, replace `test_duplicate_leaves_the_existing_bookmark_unchanged` with `test_duplicate_save_ignores_title_and_tags_and_changes_nothing`: save `https://example.com/docs` with title "Docs" and tags `["ref"]`, then save `https://example.com/docs` with title "Other" and tags `["x", "y"]`; assert 200 with title "Docs" and tags `["ref"]`, and that the stored row (read with the `engine` fixture: `url`, `title`, `tags`, `created_at`) is identical before and after (spec US1 AC2, FR-003)
- [ ] T003 [P] [US1] In `tests/integration/test_create_bookmark.py`, change `test_concurrent_saves_of_the_same_link_leave_one_bookmark` to collect status and JSON for both threads and assert `sorted(statuses) == [200, 201]`, both bodies have the same `id`, and `row_count() == 1` (spec US1 AC4, FR-005)
- [ ] T004 [P] [US1] In `tests/integration/test_create_bookmark.py`, add `test_resave_after_delete_creates_new_bookmark_with_201` (save, delete, save again → 201 with a new id) and `test_different_query_string_is_a_new_bookmark` (`https://example.com/search?q=a` then `?q=b` → both 201, two rows) (spec Edge Cases, US1 AC3)
- [ ] T005 [P] [US1] In `tests/integration/test_errors.py`, remove `test_duplicate_error_envelope`; add `test_duplicate_save_is_not_an_error` asserting a duplicate save returns 200 with a `Bookmark` body (no `error` key); in `test_openapi_documents_every_operation`, change the POST error codes from `{"409", "422"}` to `{"422"}`, assert `"409" not in` the POST responses, and assert both `"200"` and `"201"` responses reference `/Bookmark` (spec FR-007, Constitution I)

### Implementation for User Story 1

- [ ] T006 [US1] In `src/bookmarks_api/repository.py`, change `create_bookmark(session, data)` to return `tuple[BookmarkRow, bool]` (row, created): keep `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`; on insert commit and return `(row, True)`; when nothing is inserted, roll back, `SELECT` the row by `url_normalized` and return `(existing, False)` without writing to it; if the lookup finds nothing (deleted in between), retry the insert, at most 3 attempts (research.md "Returning the existing bookmark", "Concurrent saves"). Remove the `DuplicateUrlError` import and update the docstring
- [ ] T007 [US1] In `src/bookmarks_api/routes.py`, make `POST /bookmarks` take a `Response` parameter, unpack `(row, created)` from `repository.create_bookmark`, set `response.status_code = 200` when not created (default stays 201), and replace the `409` entry in `responses=` with `200: {"model": Bookmark, "description": "This link was already saved; the existing bookmark is returned unchanged."}` plus `**ERROR_422` (depends on T006; contracts/openapi.yaml)
- [ ] T008 [US1] In `src/bookmarks_api/errors.py`, delete the `DuplicateUrlError` class and its `handle_duplicate` exception handler; keep `409: "conflict"` in `STATUS_CODES` (research.md "Removing the duplicate error") (depends on T006)

**Checkpoint**: User Story 1 is fully functional; `uv run --python 3.13 pytest -q tests/integration/test_create_bookmark.py tests/integration/test_errors.py` passes.

---

## Phase 4: User Story 2 - Invalid saves are still rejected (Priority: P2)

**Goal**: Validation still runs first: an invalid request for an already saved link returns 422
and changes nothing (spec FR-006).

**Independent Test**: With `https://example.com/docs` stored, send the same link with a 201-character
title, 11 tags, or tag `"no spaces"`; each returns 422 `validation_error` and the row is unchanged.

### Tests for User Story 2 ⚠️

- [ ] T009 [US2] In `tests/integration/test_create_bookmark.py`, add a parametrized `test_invalid_resave_of_existing_link_is_rejected` (title `"t" * 201`; 11 tags `t0..t10`; tag `"no spaces"`): save `https://example.com/docs` first, then the invalid payload for the same link; assert 422 with code `validation_error`, `row_count() == 1`, and the stored title unchanged (spec US2 AC1, FR-006)

### Implementation for User Story 2

- [ ] T010 [US2] Confirm no code change is needed: `BookmarkCreate` in `src/bookmarks_api/schemas.py` validates the body before the route runs; T009 must pass with T006 to T008 in place (research.md "Validation order")

**Checkpoint**: User Stories 1 and 2 both pass independently.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T011 [P] In `README.md`, change the `POST /bookmarks` row of the endpoint table from "409 if the link is already saved" to "201 for a new link; 200 with the existing bookmark, unchanged, if the link is already saved"
- [ ] T012 Grep `src/` and `tests/` for `DuplicateUrlError`, `duplicate_url` and `409` and confirm none remain for saving (only the generic `409: "conflict"` mapping in `src/bookmarks_api/errors.py`)
- [ ] T013 Run the full suite on all supported versions: `uv run --python 3.11 pytest -q`, `uv run --python 3.12 pytest -q`, `uv run --python 3.13 pytest -q` (with `.env` loaded); all must pass (Constitution V, Quality Gates)
- [ ] T014 Run the manual checks in `specs/002-idempotent-duplicate-save/quickstart.md` (steps 1 to 5, including `/openapi.json` listing 200, 201 and 422 for `POST /bookmarks` and no 409)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)** and **Foundational (Phase 2)**: empty; nothing blocks the stories
- **User Story 1 (Phase 3)**: start immediately
- **User Story 2 (Phase 4)**: test T009 can be written at any time; it passes on the current code
  only if validation already precedes the duplicate check (it does), and must still pass after T006–T008
- **Polish (Phase 5)**: after US1 and US2

### Within User Story 1

- T001–T005 (tests) first; they fail against the current 409 behavior
- T006 (repository) → T007 (route) and T008 (errors); T007 and T008 touch different files but both
  depend on T006 removing the `DuplicateUrlError` usage

### Parallel Opportunities

- T001–T004 edit the same file (`tests/integration/test_create_bookmark.py`) — [P] only in the
  sense that they are independent tests; apply them in one edit pass to avoid conflicts
- T005 (`tests/integration/test_errors.py`) is independent of T001–T004
- T007 and T008 can run in parallel after T006
- T011 (README) can run any time

---

## Parallel Example: User Story 1

```bash
# Tests for User Story 1 together:
Task: "T001–T004 duplicate-save tests in tests/integration/test_create_bookmark.py"
Task: "T005 envelope/OpenAPI tests in tests/integration/test_errors.py"

# After T006:
Task: "T007 POST /bookmarks status and responses in src/bookmarks_api/routes.py"
Task: "T008 remove DuplicateUrlError in src/bookmarks_api/errors.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 3: write T001–T005, see them fail, implement T006–T008, see them pass
2. **STOP and VALIDATE**: run the US1 independent test
3. US1 alone delivers the change request

### Incremental Delivery

1. US1 → test → MVP
2. US2 → regression guard for validation order
3. Polish → README, grep, full suite on 3.11/3.12/3.13, quickstart

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- `specs/001-bookmarks-api/` MUST NOT be edited; this feature supersedes its duplicate rule
- No migration and no new dependency
