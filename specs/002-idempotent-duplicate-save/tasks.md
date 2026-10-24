---

description: "Task list for 002-idempotent-duplicate-save"
---

# Tasks: Idempotent Duplicate Save

**Input**: Design documents from `/specs/002-idempotent-duplicate-save/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included. The spec requires every acceptance scenario to be covered by an automated test
(SC-005) and the constitution requires tests to ship with every feature (Principle V) against the
real test database (Principle II).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Supersedes**: the duplicate rule in FR-004 of [specs/001-bookmarks-api](../001-bookmarks-api/spec.md)
(409 `duplicate_url` → 200 with the existing bookmark). `specs/001-bookmarks-api/` is not edited.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- Single project: `src/bookmarks_api/`, `tests/` at repository root (plan.md, Project Structure)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the starting point is green before behavior changes

- [ ] T001 Run the existing suite against the test database (`set -a; . ./.env; set +a; uv run --python 3.13 pytest -q` from the repository root, covering `tests/`) and confirm it passes before any change

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: None required. Storage, schema, models and migrations are unchanged
(data-model.md: "No storage change"); the `uq_bookmarks_url_normalized` unique index from 001 is
reused as is.

**Checkpoint**: Foundation ready - user story implementation can begin

---

## Phase 3: User Story 1 - Saving an already-saved link returns the existing bookmark (Priority: P1) 🎯 MVP

**Goal**: `POST /bookmarks` for a link whose normalized form is already stored returns 200 OK with
the existing bookmark, unchanged; a new link still returns 201 Created (spec FR-001, FR-002,
FR-003, FR-005, FR-006).

**Independent Test**: Save a link, then save an equivalent form with a different title and tags;
the second response is 200 with the first bookmark exactly as stored, and one row exists.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T002 [US1] In `tests/integration/test_create_bookmark.py`, replace `test_equivalent_link_is_rejected_as_duplicate` with `test_equivalent_link_returns_existing_bookmark`: save `https://example.com/docs` with title "Docs" and tags `["python"]`, then save `HTTPS://Example.com/docs/#intro` with title "Other" and tags `["misc"]`; assert the second response is 200 and its JSON equals the first response's JSON (same `id`, `url` "https://example.com/docs", `title` "Docs", `tags` `["python"]`, `created_at`), and `row_count() == 1` (spec US1 scenario 1, FR-001, FR-002)
- [ ] T003 [US1] In `tests/integration/test_create_bookmark.py`, replace `test_duplicate_leaves_the_existing_bookmark_unchanged` with a test that saves `https://example.com/docs` (title "Docs", tags `["python"]`), re-saves the identical payload and then `https://example.com/docs/` with title "Changed" and tags `["other"]`; assert both re-saves return 200 with the original bookmark, and the stored row's `title`, `tags` and `created_at` (read with `engine`) are unchanged (spec US1 scenario 2, FR-002, Edge Cases "never changes the stored bookmark")
- [ ] T004 [US1] In `tests/integration/test_create_bookmark.py`, add `test_different_query_string_is_a_new_bookmark`: save `https://example.com/docs?a=1`, then `https://example.com/docs?a=2`; assert the second returns 201 with a different `id` and `row_count() == 2` (spec US1 scenario 4, FR-003). Scenario 3 (new link → 201) stays covered by the existing `test_save_with_title_and_no_tags`
- [ ] T005 [US1] In `tests/integration/test_create_bookmark.py`, add `test_invalid_duplicate_save_is_still_rejected`: save `https://example.com/docs`, then save the same link with title `"t" * 201` and, separately, with tags `["no spaces"]`; assert each returns 422 `validation_error` and the stored row is unchanged (spec FR-005, Edge Cases first bullet)
- [ ] T006 [P] [US1] In `tests/integration/test_errors.py`, delete `test_duplicate_error_envelope`, and change `test_openapi_documents_every_operation` so the `post` error codes are `{"422"}`, it asserts `"409" not in operation["responses"]` for `post`, and it asserts both `responses["201"]` and `responses["200"]` reference `/Bookmark` (spec FR-006, contracts/openapi.yaml)

### Implementation for User Story 1

- [ ] T007 [US1] In `src/bookmarks_api/repository.py`, change `create_bookmark(session, data)` to return `tuple[BookmarkRow, bool]` (row, created): keep `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`; on an inserted row commit and return `(row, True)`; when nothing is inserted roll back, `SELECT` the row by `url_normalized` and return `(row, False)` without writing; if that `SELECT` finds nothing (row deleted in between), retry the insert, at most 3 attempts in total, then raise `RuntimeError` (rendered as 500 `internal_error`). Remove the `DuplicateUrlError` import and update the docstring (research.md, "Returning the existing bookmark" and "Row deleted between the conflict and the lookup")
- [ ] T008 [US1] In `src/bookmarks_api/routes.py`, change `create_bookmark` to accept `response: Response`, unpack `(row, created)` from the repository, set `response.status_code = status.HTTP_200_OK` when not created (default stays 201), and replace the route's `responses` with `{200: {"model": Bookmark, "description": "This link is already bookmarked; the existing bookmark is returned unchanged."}, **ERROR_422}` — no 409 entry (research.md, "Response status and contract"; Constitution I)
- [ ] T009 [US1] In `src/bookmarks_api/errors.py`, delete the `DuplicateUrlError` class and its `handle_duplicate` 409 exception handler; keep the generic `409: "conflict"` entry in `STATUS_CODES` (research.md, "Removing the duplicate error")

**Checkpoint**: User Story 1 is fully functional and testable independently

---

## Phase 4: User Story 2 - Concurrent saves of the same new link store one bookmark (Priority: P2)

**Goal**: Two saves of the same new link at the same moment store one bookmark; one response is
201, the other 200, both with the same bookmark (spec FR-004).

**Independent Test**: Two threads save equivalent forms of a new link behind a barrier; statuses
are `[200, 201]`, both bodies have the same `id`, and one row exists.

### Tests for User Story 2

- [ ] T010 [US2] In `tests/integration/test_create_bookmark.py`, update `test_concurrent_saves_of_the_same_link_leave_one_bookmark` to collect each response (status and JSON), and assert `sorted(statuses) == [200, 201]`, both JSON bodies have the same `id`, and `row_count() == 1` (spec US2 scenario 1, FR-004, SC-003)

### Implementation for User Story 2

- [ ] T011 [US2] Confirm no further code is needed beyond T007/T008 (the unique index arbitrates the race, research.md): run the concurrency test in `tests/integration/test_create_bookmark.py` 20 times in a shell loop (`for i in $(seq 20); do uv run --python 3.13 pytest -q -k concurrent tests/integration/test_create_bookmark.py || break; done`) and confirm every run passes

**Checkpoint**: User Stories 1 and 2 both work independently

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and full validation

- [ ] T012 [P] In `README.md`, change the endpoint table row for `POST /bookmarks` from "409 if the link is already saved" to "201 for a new link; 200 with the existing bookmark, unchanged, if the link is already saved"
- [ ] T013 Run the full suite on Python 3.11, 3.12 and 3.13 (`uv run --python 3.1X pytest -q` with `.env` loaded) over `tests/` and confirm all pass (Constitution quality gate)
- [ ] T014 Run the manual checks in `specs/002-idempotent-duplicate-save/quickstart.md` (steps 1-5) against a locally started API, or confirm each is covered by an automated test

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Empty
- **User Story 1 (Phase 3)**: After Setup
- **User Story 2 (Phase 4)**: T010 can be written after Setup; T011 depends on T007 and T008
- **Polish (Phase 5)**: After US1 and US2

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies on other stories
- **User Story 2 (P2)**: Uses the US1 repository/route change (T007, T008); its test is independent

### Within Each User Story

- Tests (T002-T006, T010) MUST be written and FAIL before implementation
- T007 (repository) before T008 (route); T009 after T007 removes the last import of `DuplicateUrlError`
- T002-T005 and T010 edit the same file, so they run sequentially

### Parallel Opportunities

- T006 (`tests/integration/test_errors.py`) can run in parallel with T002-T005 (`tests/integration/test_create_bookmark.py`)
- T012 (`README.md`) can run in parallel with any implementation task

---

## Parallel Example: User Story 1

```bash
# Different files, no dependencies between them:
Task: "T002-T005 duplicate-save tests in tests/integration/test_create_bookmark.py"
Task: "T006 OpenAPI/envelope test changes in tests/integration/test_errors.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1: confirm green baseline
2. Phase 3: User Story 1 (tests first, then repository, route, errors)
3. **STOP and VALIDATE**: duplicate save returns 200 with the existing bookmark

### Incremental Delivery

1. US1 → duplicate saves succeed (MVP)
2. US2 → concurrency test updated to the new 201/200 outcome
3. Polish → README and full-suite validation on 3.11-3.13

---

## Notes

- [P] tasks = different files, no dependencies
- `specs/001-bookmarks-api/` is a finished historical record: never edit it
- Commit after each logical group
