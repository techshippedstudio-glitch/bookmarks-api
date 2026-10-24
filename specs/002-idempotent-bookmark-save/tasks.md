---

description: "Task list for feature 002: idempotent bookmark save"
---

# Tasks: Idempotent Bookmark Save

**Input**: Design documents from `/specs/002-idempotent-bookmark-save/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included. The spec requires every acceptance scenario to be covered by an automated test
(SC-005) and the constitution requires tests to ship with every feature (Principle V) against the
real database (Principle II).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Supersedes**: This feature replaces the duplicate rule of FR-004 in `specs/001-bookmarks-api`
(409 `duplicate_url`). `specs/001-bookmarks-api` is a finished record and MUST NOT be edited by
any task below.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/bookmarks_api/`, `tests/` at repository root (plan.md Structure Decision)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the starting point

- [ ] T001 Run the existing suite against the test database (`set -a; . ./.env; set +a; uv run --python 3.13 pytest -q`) and confirm it passes before any change; no new dependencies or migrations are needed (plan.md Technical Context)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Change the save primitive that every user story depends on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T002 Change `create_bookmark` in src/bookmarks_api/repository.py to return `tuple[BookmarkRow, bool]` (`(row, created)`): keep `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`; when a row is returned, commit and return `(row, True)`; when nothing is returned, roll back, `SELECT` the existing row by `url_normalized` and return `(existing, False)` without modifying it (no `DO UPDATE`, title/tags/created_at untouched — spec FR-002); if the lookup finds nothing (deleted meanwhile) retry the insert, bounded to 3 attempts (research.md "Row deleted between the conflict and the lookup"); update the docstring to cite specs/002 FR-001/FR-004
- [ ] T003 Remove `DuplicateUrlError` and its `handle_duplicate` exception handler from src/bookmarks_api/errors.py, and remove its import from src/bookmarks_api/repository.py; keep the generic `409: "conflict"` entry in `STATUS_CODES` (research.md "Removing the duplicate error")

**Checkpoint**: Repository reports created vs existing; no code path raises a duplicate error

---

## Phase 3: User Story 1 - Re-saving a saved link returns the existing bookmark (Priority: P1) 🎯 MVP

**Goal**: A save of an already-bookmarked link (any equivalent form, any title/tags) returns the existing bookmark unchanged with 200 OK.

**Independent Test**: Save a link, save it again in an equivalent form with a different title and tags; the second response is 200 with the original bookmark, and only one bookmark exists.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T004 [US1] In tests/integration/test_create_bookmark.py replace `test_equivalent_link_is_rejected_as_duplicate` with `test_equivalent_link_returns_existing_bookmark_with_200`: save `https://example.com/docs`, then save `HTTPS://Example.com/docs/#intro` with another title and tags; assert 200, the body equals the first response body (same `id`, `url`, `title`, `tags`, `created_at`) and `row_count() == 1` (spec US1 scenario 1, FR-001)
- [ ] T005 [US1] In tests/integration/test_create_bookmark.py replace `test_duplicate_leaves_the_existing_bookmark_unchanged` with `test_resave_ignores_title_and_tags_and_changes_nothing`: save `https://example.com/docs` with title "Docs" and tags ["python"], re-save with title "Other" and tags ["api", "new"]; assert the response has title "Docs" and tags ["python"], and `GET /bookmarks` shows one bookmark with title "Docs", tags ["python"] and the original `created_at` (spec US1 scenario 2, FR-002)
- [ ] T006 [US1] In tests/integration/test_create_bookmark.py add `test_different_query_string_is_a_new_bookmark`: with `https://example.com/docs` saved, saving `https://example.com/docs?page=2` returns 201 with a new `id` and `row_count() == 2` (spec US1 scenario 3)
- [ ] T007 [US1] In tests/integration/test_create_bookmark.py add `test_invalid_resave_is_still_rejected`: with `https://example.com/docs` saved, re-saving it with `"title": ""` (and separately with 11 tags) returns 422 `validation_error` and the stored bookmark is unchanged (spec FR-005, Edge Cases)
- [ ] T008 [P] [US1] In tests/integration/test_errors.py delete `test_duplicate_error_envelope` (the 409 response no longer exists), and in `test_openapi_documents_every_operation` change the POST expectations: error codes `{"422"}` only, assert `"409" not in operation["responses"]`, and assert both `responses["201"]` and `responses["200"]` reference the `Bookmark` schema (contracts/openapi.yaml, Constitution I)

### Implementation for User Story 1

- [ ] T009 [US1] In src/bookmarks_api/routes.py change `create_bookmark` to take `response: Response`, unpack `(row, created)` from `repository.create_bookmark`, set `response.status_code = status.HTTP_200_OK` when `created` is False (default stays 201), and return `Bookmark.model_validate(row)`; in the route's `responses` remove the `409` entry and add `200: {"model": Bookmark, "description": "This link was already bookmarked; the existing bookmark is returned unchanged."}`; update the summary/description to say the save is idempotent per normalized link (contracts/openapi.yaml)

**Checkpoint**: User Story 1 tests T004–T008 pass

---

## Phase 4: User Story 2 - Saving a new link is unchanged (Priority: P2)

**Goal**: A save of a link that is not bookmarked still returns 201 Created.

**Independent Test**: Save a new link → 201; delete it and save again → 201 with a new id.

### Tests for User Story 2 ⚠️

- [ ] T010 [P] [US2] Confirm tests/integration/test_create_bookmark.py `test_save_with_title_and_no_tags` still asserts 201 for a new link (spec US2 scenario 1) and leave it unchanged
- [ ] T011 [P] [US2] In tests/integration/test_delete_bookmark.py confirm the "save again after delete" test asserts 201 and a new bookmark (spec US2 scenario 2); if it does not assert the status code, add `assert response.status_code == 201`

### Implementation for User Story 2

- [ ] T012 [US2] No production change beyond T002/T009; verify the 201 path by running `uv run --python 3.13 pytest -q tests/integration/test_create_bookmark.py tests/integration/test_delete_bookmark.py`

**Checkpoint**: New-link saves behave exactly as in 001

---

## Phase 5: User Story 3 - Concurrent saves of the same new link (Priority: P3)

**Goal**: Two simultaneous first saves of one link store one bookmark; one gets 201, the other 200, both with the same bookmark.

**Independent Test**: Two threads behind a barrier save `https://example.com/race` and `https://EXAMPLE.com/race/`; statuses are `[200, 201]`, both bodies have the same `id`, one row exists.

### Tests for User Story 3 ⚠️

- [ ] T013 [US3] In tests/integration/test_create_bookmark.py update `test_concurrent_saves_of_the_same_link_leave_one_bookmark`: collect `(status_code, json)` per thread, assert `sorted(statuses) == [200, 201]`, both bodies carry the same `id`, and `row_count() == 1` (spec US3 scenario 1, FR-004)

### Implementation for User Story 3

- [ ] T014 [US3] No production change beyond T002 (the unique index plus `ON CONFLICT DO NOTHING` decides the winner; the loser's follow-up `SELECT` sees the committed row — research.md); run the concurrent test 20 times in a shell loop (`for i in $(seq 20); do uv run --python 3.13 pytest -q tests/integration/test_create_bookmark.py -k concurrent || break; done`) to check it is not flaky

**Checkpoint**: All user stories independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Keep docs and contract truthful; full verification

- [ ] T015 [P] Update README.md where it describes the API so it says saving an already-bookmarked link returns the existing bookmark (200) instead of being rejected, and link to specs/002-idempotent-bookmark-save (do not edit anything under specs/001-bookmarks-api)
- [ ] T016 Compare the running app's `/openapi.json` POST `/bookmarks` responses with specs/002-idempotent-bookmark-save/contracts/openapi.yaml (200, 201, 422; no 409; no `duplicate_url`) and fix any drift in src/bookmarks_api/routes.py
- [ ] T017 Run the full suite on Python 3.11, 3.12 and 3.13 (`uv run --python 3.1X pytest -q`) and confirm all pass
- [ ] T018 Walk through specs/002-idempotent-bookmark-save/quickstart.md "Manual validation" steps 1–7 with the TestClient or a local server and confirm each expected result

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup; T003 depends on T002 (shared file repository.py)
- **User Stories (Phase 3+)**: All depend on Foundational
  - US1 (P1): T004–T008 first (fail), then T009
  - US2 (P2): verification only; can run after T009
  - US3 (P3): T013 after T009; T014 after T013
- **Polish (Phase 6)**: After all stories

### Within Each User Story

- Tests are written first and must fail before implementation
- T004–T007 and T013 all edit tests/integration/test_create_bookmark.py, so they are sequential (no [P])

### Parallel Opportunities

- T008 (test_errors.py) can run in parallel with T004–T007 (test_create_bookmark.py)
- T010 and T011 touch different files
- T015 (README.md) is independent of the code tasks

---

## Parallel Example: User Story 1

```bash
# Different files, can proceed together:
Task: "T004–T007 re-save tests in tests/integration/test_create_bookmark.py"
Task: "T008 OpenAPI/envelope test changes in tests/integration/test_errors.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 (baseline green) → Phase 2 (repository returns created flag, duplicate error removed)
2. Phase 3: US1 tests, then the route change → re-save returns 200
3. **STOP and VALIDATE**: US1 tests pass; this alone delivers the change request's main behavior

### Incremental Delivery

1. US1 → MVP
2. US2 → confirm no regression on 201
3. US3 → confirm concurrency outcome 201/200
4. Polish → README, contract check, 3-version suite, quickstart

---

## Notes

- [P] tasks = different files, no dependencies
- Commit after each phase or logical group
- Never edit files under specs/001-bookmarks-api (finished record; this feature supersedes its FR-004 duplicate rule by cross-link)
