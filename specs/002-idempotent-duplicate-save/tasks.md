---

description: "Task list for Idempotent Duplicate Save"
---

# Tasks: Idempotent Duplicate Save

**Input**: Design documents from `/specs/002-idempotent-duplicate-save/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md

**Supersedes**: the duplicate rule in 001 FR-004 (FR-004 of [specs/001-bookmarks-api](../001-bookmarks-api/spec.md))
(409 `duplicate_url`). `specs/001-bookmarks-api` is not edited; its completed tasks T008, T012,
T015, T016 and T026 describe the old 409 behavior and are superseded by the tasks below (full list:
plan.md, "Superseded statements in specs/001-bookmarks-api"). Requirement IDs without a prefix
(FR-###, SC-###) refer to this feature's spec.md.

**Tests**: Included. The constitution (Principles II and V) and spec SC-005 require an automated
test for every acceptance scenario, run against the real test database.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested on
its own.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2)
- Paths are relative to the repository root (single project, `src/` layout)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the starting point

- [X] T001 Run the existing suite (`set -a; . ./.env; set +a; uv run --python 3.13 pytest -q`) from the repository root and confirm it passes before any change (baseline for `tests/`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Change the repository contract that both stories depend on

- [X] T002 Change `create_bookmark(session, data)` in `src/bookmarks_api/repository.py` to return `tuple[BookmarkRow, bool]` (`(row, created)`): keep `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`; if a row is returned, commit and return `(row, True)`; if nothing is returned, roll back the transaction and `SELECT` the row where `url_normalized` equals the normalized link and return `(existing_row, False)` without writing anything; if that `SELECT` finds no row (the conflicting row was deleted in between), retry the insert, so the save is stored as new and returns `(row, True)` (spec Edge Case: save racing a delete → 201); cap the loop at 3 attempts as a safety bound and raise `RuntimeError` only if all 3 fail (research.md §1). Update the docstring and remove the `DuplicateUrlError` import. The retry branch needs a delete to land between two statements and cannot be triggered deterministically against the real database without mocks (Constitution II), so it is covered by code review rather than a test

**Checkpoint**: Repository returns the existing row instead of raising; user story work can begin

---

## Phase 3: User Story 1 - Saving an already-bookmarked link returns the existing bookmark (Priority: P1) 🎯 MVP

**Goal**: A save of a link that is already bookmarked (after normalization) returns the stored
bookmark unchanged with 200 OK; a new link still returns 201 Created; no save returns 409.

**Independent Test**: Save `https://example.com/docs`, then save `HTTPS://Example.com/docs/#intro`
with a different title and tags; the second response is 200 with the first bookmark exactly as
stored, and one row exists.

### Tests for User Story 1

> Write these tests first and confirm they fail before T005-T006.

- [X] T003 [P] [US1] In `tests/integration/test_create_bookmark.py`, replace `test_equivalent_link_is_rejected_as_duplicate` and `test_duplicate_leaves_the_existing_bookmark_unchanged` with: (a) US1 AC1 — save `https://example.com/docs` (title "Docs"), then `HTTPS://Example.com/docs/#intro` → 200 and the body equals the first response body exactly (`id`, `url` `https://example.com/docs`, `title`, `tags`, `created_at`), `row_count() == 1`; (b) US1 AC2 — save `https://example.com/docs` title "Docs" tags `["api"]`, then the same link with title "Other" tags `["python", "new"]` → 200 with title "Docs" and tags `["api"]`, and the stored row (read via `engine`) still has title "Docs", tags `{api}` and the original `created_at`, and `GET /bookmarks` returns exactly one item; (c) US1 AC3 / FR-004 — keep `test_save_with_title_and_no_tags` (201 for a new link) unchanged as the FR-004 coverage; (d) edge cases — a duplicate save with an invalid title (`"t" * 201`) or 11 tags → 422 `validation_error` and the stored bookmark unchanged (FR-006); a link differing only by query string (`https://example.com/docs?x=1`) → 201 and `row_count() == 2`. (Delete-then-resave → 201 is already covered by `test_link_can_be_saved_again_after_delete` in `tests/integration/test_delete_bookmark.py`; leave it unchanged.)
- [X] T004 [P] [US1] In `tests/integration/test_errors.py`, remove `test_duplicate_error_envelope` (409 `duplicate_url` no longer exists) and add a test that a duplicate save returns 200 and a body without an `error` key; in `test_openapi_documents_every_operation` change the expected `post` error codes from `{"409", "422"}` to `{"422"}`, assert `"409"` is not among the `post` responses, and assert the `post` `"200"` response schema `$ref` ends with `/Bookmark` (contracts/openapi.yaml)

### Implementation for User Story 1

- [X] T005 [US1] Update `POST /bookmarks` in `src/bookmarks_api/routes.py`: keep `status_code=201` and `response_model=Bookmark`; inject `response: Response`; call `repository.create_bookmark` (T002) and set `response.status_code = status.HTTP_200_OK` when `created` is false; in `responses`, remove the `409` entry and add `200: {"model": Bookmark, "description": "This link is already bookmarked; the existing bookmark is returned unchanged."}` (contracts/openapi.yaml)
- [X] T006 [US1] Remove `DuplicateUrlError` and its `handle_duplicate` 409 handler from `src/bookmarks_api/errors.py`; keep the generic `409: "conflict"` entry in `STATUS_CODES` for framework HTTP exceptions (research.md §3)

**Checkpoint**: User Story 1 is fully functional and testable on its own

---

## Phase 4: User Story 2 - Concurrent saves of the same new link still store one bookmark (Priority: P2)

**Goal**: Two simultaneous saves of the same new link store exactly one bookmark; one gets 201 and
the other 200, both with the same bookmark.

**Independent Test**: Two threads save equivalent forms of a new link at the same moment; statuses
are `[200, 201]`, both bodies have the same `id`, one row exists.

### Tests for User Story 2

- [X] T007 [US2] In `tests/integration/test_create_bookmark.py`, update `test_concurrent_saves_of_the_same_link_leave_one_bookmark`: collect each response (status and body) from the two threads (`https://example.com/race` and `https://EXAMPLE.com/race/`, `threading.Barrier(2)`), assert `sorted(statuses) == [200, 201]`, both bodies have the same `id`, and `row_count() == 1`; run the race 20 times in a loop (truncating via `DELETE /bookmarks/{id}` between iterations) so a flaky interleaving would be caught (FR-005, SC-003)

### Implementation for User Story 2

- [X] T008 [US2] Confirm `create_bookmark` in `src/bookmarks_api/repository.py` (T002) needs no extra locking: T007 passes all 20 iterations with no code beyond T002 (the losing `INSERT ... ON CONFLICT DO NOTHING` waits for the winner's commit, then its fresh `SELECT` sees the committed row, research.md §1). Done when T007 passes; record the result in the implement capture

**Checkpoint**: User Stories 1 and 2 both work independently

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and final validation

- [X] T009 [P] Update the endpoint table in `README.md`: `POST /bookmarks` row reads "Save `{"url", "title", "tags"}`; 201 when new, 200 with the existing bookmark (unchanged) if the link is already saved"
- [X] T010 Search `src/` and `tests/` for leftover `DuplicateUrlError`, `duplicate_url` and `409` references tied to duplicate saves and remove them (`grep -rn "DuplicateUrlError\|duplicate_url\|409" src tests`)
- [X] T011 Run the full suite on Python 3.11, 3.12 and 3.13 (`uv run --python 3.1X pytest -q` after `set -a; . ./.env; set +a`) and walk the manual table in `specs/002-idempotent-duplicate-save/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup; BLOCKS both user stories (T002 changes the repository return type the route uses)
- **User Story 1 (Phase 3)**: Depends on T002
- **User Story 2 (Phase 4)**: Depends on T002; its test also relies on the 200 status set in T005
- **Polish (Phase 5)**: Depends on both stories

### Within Each User Story

- Tests (T003, T004 / T007) are written first and fail before implementation
- T005 before T006 (the route must stop declaring 409 before the exception is deleted, so the app keeps importing)

### Parallel Opportunities

- T003 and T004 touch different files and can run in parallel
- T009 can run in parallel with T010

---

## Parallel Example: User Story 1

```bash
Task: "Rewrite duplicate tests in tests/integration/test_create_bookmark.py (T003)"
Task: "Update envelope/OpenAPI tests in tests/integration/test_errors.py (T004)"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. T001 baseline, T002 repository change
2. T003-T006: duplicate save returns 200 with the existing bookmark
3. **STOP and VALIDATE**: run the suite

### Incremental Delivery

1. Add User Story 2 (T007-T008): concurrency test with 201/200
2. Polish (T009-T011): README, leftover references, three-Python run

---

## Notes

- [P] tasks = different files, no dependencies
- No migration and no new dependency (plan.md)
- Never edit files under `specs/001-bookmarks-api/`

## Phase 6: Convergence

- [ ] T012 Add an invalid-tag case (`{"url": "https://example.com/docs", "title": "Bad tag", "tags": ["no spaces"]}`) to `test_invalid_duplicate_is_still_a_validation_error` in `tests/integration/test_create_bookmark.py` per Edge Cases / FR-006 (partial)
- [ ] T013 Assert the listed bookmark's tags are `["api"]` in `test_duplicate_ignores_title_and_tags_and_leaves_the_bookmark_unchanged` in `tests/integration/test_create_bookmark.py` per US1/AC2 (partial)
- [ ] T014 Align the `create_bookmark` docstring in `src/bookmarks_api/routes.py` (published as the `POST /bookmarks` OpenAPI description) with the description in `specs/002-idempotent-duplicate-save/contracts/openapi.yaml` and drop the internal spec path per contracts/openapi.yaml, Constitution I (unrequested)
