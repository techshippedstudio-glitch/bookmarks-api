---

description: "Task list for bookmark title search"
---

# Tasks: Bookmark Title Search

**Input**: Design documents from `/specs/002-bookmark-title-search/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md

**Tests**: Included. The spec requires every acceptance scenario to be covered by an automated test
(SC-004), and the constitution requires tests against the real test database (Principles II and V)
plus a paging-while-saving test for every list endpoint (Principle VI quality gate).

**Organization**: Tasks are grouped by user story so each story can be implemented and tested on
its own.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1 to US3)
- Paths are relative to the repository root (single project, `src/` layout)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the starting point; this feature adds no dependency, table or migration

- [X] T001 Run the existing suite (`uv run pytest`) with `TEST_DATABASE_URL` exported and confirm it passes before any change; confirm `pyproject.toml` and `uv.lock` need no change (plan.md, Constitution IV: no new dependency)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The search-word parser and the request model every story uses

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 [P] Write unit tests in `tests/unit/test_search_words.py` for `search_words()`: `"postgres"` → `["postgres"]`; `"  Postgres   guide postgres "` → `["Postgres", "guide"]` (split on whitespace, empty pieces dropped, repeats dropped case-insensitively, first spelling kept, order of first appearance); tabs count as whitespace; `"c"` → `["c"]` (no minimum word length); `""` and `"   "` raise `ValueError`; a 201-character string raises `ValueError` and a 200-character one does not ("`q` 1 to 200 characters; must contain a non-space character", data-model.md); `%`, `_` and `/` are kept as ordinary characters
- [X] T003 Add `MAX_SEARCH_LENGTH = 200` and `search_words(q: str) -> list[str]` to `src/bookmarks_api/normalize.py`: reject `len(q) > 200` and blank input with `ValueError` messages that say what is allowed ("1 to 200 characters", "at least one non-space character"); split with `str.split()`, de-duplicate by `casefold()` keeping the first spelling (makes T002 pass)
- [X] T004 Add `BookmarkSearchQuery(BookmarkListQuery)` to `src/bookmarks_api/schemas.py` with `q: str = Field(min_length=1, max_length=200, description="One or more words separated by spaces; every word must appear in the title.")` and a `field_validator("q")` that calls `search_words()` so a blank `q` becomes a validation error on `query.q`; inherit `limit` (`ge=1, le=100`, default 20), `cursor` (decoded or rejected) and `tag` (normalized like tags) unchanged (Constitution I)
- [X] T005 Extend `list_bookmarks()` in `src/bookmarks_api/repository.py` with a keyword argument `title_words: list[str] | None = None`; for each word add `BookmarkRow.title.icontains(word, autoescape=True)` to the shared `conditions` list so it applies to both the `COUNT(*)` total and the page query; keep ordering `created_at DESC, id DESC`, the `(created_at, id) <` keyset condition and `limit + 1` unchanged (research.md, "Ordering, paging and totals")

**Checkpoint**: Foundation ready; user story work can begin

---

## Phase 3: User Story 1 - Search bookmarks by title words (Priority: P1) 🎯 MVP

**Goal**: A user finds bookmarks by words in the title, newest first, regardless of letter case.

**Independent Test**: Save bookmarks with different titles, call `GET /bookmarks/search?q=...` and
confirm only titles containing every word come back, newest first, with the right `total`.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T006 [P] [US1] Write integration tests in `tests/integration/test_search_bookmarks.py` for spec User Story 1: scenario 1 ("postgres" returns "Advanced Postgres tuning" then "Postgres indexing guide", `total` 2); scenario 2 ("fastapi", "FASTAPI", "FastAPI" all find "FastAPI Tutorial"); scenario 3 ("postgres guide" returns only "Postgres indexing guide"; words in any order); scenario 4 (no match → 200 `{"items": [], "total": 0, "limit": 20, "next_cursor": null}`); scenario 5 (`q=""`, `q="   "`, `q` of 201 characters and a missing `q` each return 422 `validation_error` with `details[0].field == "query.q"`); edge cases: "post" finds "Postgres" (substring), "c" matches every title containing c, `%`, `_`, `*` and `/` in `q` match only titles containing that literal character, accented capitals fold too ("ÉCOLE" finds "école", spec Assumptions), repeating a word changes nothing; each result item has the same fields and values as in `GET /bookmarks` (FR-010); a search changes no bookmark (FR-011)

### Implementation for User Story 1

- [X] T007 [US1] Add `GET /bookmarks/search` to `src/bookmarks_api/routes.py`, declared before `DELETE /{bookmark_id}`: `response_model=BookmarkPage`, `summary="Search bookmarks by title words, newest first"`, `responses=ERROR_422`, `dependencies=[Depends(reject_offset)]`, query bound as `Annotated[BookmarkSearchQuery, Query()]`; decode the cursor, call `repository.list_bookmarks(session, limit=..., after=..., tag=query.tag, title_words=search_words(query.q))` and build the page and `next_cursor` exactly as `list_bookmarks` does (makes T006 pass)
- [X] T008 [US1] Extend `test_openapi_documents_every_operation` in `tests/integration/test_errors.py` with `("/bookmarks/search", "get")`: summary present, 422 response is `ErrorResponse`, 200 response is `BookmarkPage`, and a required query parameter `q` is listed (Constitution I quality gate)

**Checkpoint**: User Story 1 is fully functional and testable on its own

---

## Phase 4: User Story 2 - Combine search with the tag filter (Priority: P2)

**Goal**: A search can be narrowed to one tag.

**Independent Test**: Save bookmarks with overlapping title words and different tags; search with
`tag=` and confirm only bookmarks matching both come back, newest first.

### Tests for User Story 2

- [X] T009 [P] [US2] Write integration tests in `tests/integration/test_search_with_tag.py` for spec User Story 2: scenario 1 ("indexing" with `tag=postgres` returns only "Indexing basics" tagged postgres); scenario 2 (`q=INDEXING&tag=Postgres` still finds it); scenario 3 (matching titles but an absent tag → empty list, `total` 0); an invalid tag filter (`tag="bad tag!"`) returns 422 `validation_error` on `query.tag`

### Implementation for User Story 2

- [X] T010 [US2] Verification task: T007 already delivers this; confirm `GET /bookmarks/search` in `src/bookmarks_api/routes.py` passes the normalized `query.tag` to `repository.list_bookmarks` together with `title_words` so both conditions are ANDed in the count and the page; fix if T009 fails

**Checkpoint**: User Stories 1 and 2 both work on their own

---

## Phase 5: User Story 3 - Page through search results (Priority: P3)

**Goal**: Search results page exactly like the bookmark list.

**Independent Test**: Save more matching bookmarks than one page holds, follow `next_cursor` to the
end and confirm every match appears once, newest first.

### Tests for User Story 3

- [X] T011 [P] [US3] Write integration tests in `tests/integration/test_search_paging.py` for spec User Story 3: scenario 1 (25 "python" titles and 5 others: first page 20 newest matches, `total` 25, `next_cursor` set; second page the remaining 5, `next_cursor` null); scenario 2 (a new matching bookmark saved before every page request, paging with `limit=10` sees every original match exactly once with no gaps — Constitution VI quality gate); a matching bookmark deleted between pages skips nothing; exactly 20 matches → one page with no `next_cursor`; scenario 3 (`limit=101`, `limit=0`, malformed cursor → 422 `validation_error`, same fields as `GET /bookmarks`); `offset` → 422 on `query.offset` with a message pointing to `cursor`; a cursor from one search sent with a different `q` returns the matches of the new `q` after that position (Clarifications)
- [X] T012 [P] [US3] Add a timing test in `tests/integration/test_search_paging.py` for SC-006: insert 10,000 bookmarks in one statement through the test engine, then run 20 searches (mixed one-word, two-word and with-tag) through the API and assert at least 19 (95%) answer in under 1 second

### Implementation for User Story 3

- [X] T013 [US3] Verification task: T007 already delivers this; confirm `GET /bookmarks/search` in `src/bookmarks_api/routes.py` reuses `encode_cursor`/`decode_cursor`, the list's `limit` bounds and `reject_offset` so T011 and T012 pass; fix any difference from `GET /bookmarks`

**Checkpoint**: All user stories are independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and final validation

- [X] T014 [P] Add `GET /bookmarks/search?q=&tag=&limit=&cursor=` to the endpoint table in `README.md` ("Search titles: every word, any letter case, newest first; pages like the list")
- [X] T015 Run the full suite on Python 3.13 (`uv run pytest`) and the manual checks in `specs/002-bookmark-title-search/quickstart.md`; all existing and new tests pass (SC-004, Constitution quality gates)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup; blocks all user stories. T003 after T002; T004 after T003; T005 independent of T003/T004 (different file)
- **User Stories (Phase 3+)**: Depend on Foundational. US2 and US3 use the route added in US1 (T007)
- **Polish (Phase 6)**: Depends on all user stories

### User Story Dependencies

- **User Story 1 (P1)**: After Foundational; no dependency on other stories
- **User Story 2 (P2)**: After T007 (the route); its tests are independent of US1's tests
- **User Story 3 (P3)**: After T007 (the route); its tests are independent of US1's and US2's tests

### Within Each User Story

- Tests are written first and fail before the implementation task
- Implementation tasks in `routes.py` are sequential (same file)

### Parallel Opportunities

- T002 and T005 (different files) can run in parallel
- T006, T009 and T011/T012 are in different test files and can be written in parallel once the foundation exists
- T014 can run in parallel with any test task

---

## Parallel Example: User Story 3

```bash
# Write the User Story 3 tests while US2 is in progress:
Task: "Integration tests for search paging in tests/integration/test_search_paging.py"
Task: "README endpoint table in README.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) and Phase 2 (Foundational)
2. Complete Phase 3 (User Story 1)
3. **STOP and VALIDATE**: run `tests/integration/test_search_bookmarks.py` and the full suite

### Incremental Delivery

1. Setup + Foundational → parser, request model and query ready
2. User Story 1 → search endpoint (MVP)
3. User Story 2 → tag combination verified
4. User Story 3 → paging and performance verified
5. Polish → README and final suite run

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- No migration, model or dependency change in this feature (plan.md)
- Commit after each task or logical group

---

## Phase 7: Convergence

- [ ] T016 CRITICAL: Reject a search `q` that contains a NUL character with 422 `validation_error` on `query.q` (validator in `src/bookmarks_api/normalize.py` `search_words()` / `src/bookmarks_api/schemas.py` `BookmarkSearchQuery`) instead of the current 500 `internal_error`, and add a case to `tests/integration/test_search_bookmarks.py` per Constitution III (contradicts)
- [ ] T017 De-duplicate search words in `src/bookmarks_api/normalize.py` `search_words()` with `str.lower()` (the folding PostgreSQL `ILIKE` uses) instead of `str.casefold()`, so words such as "Straße" and "STRASSE" are both kept and word order never changes results; add unit and integration tests per FR-001 (partial)
