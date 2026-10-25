---

description: "Task list for Search Bookmarks by Title"
---

# Tasks: Search Bookmarks by Title

**Input**: Design documents from `/specs/002-bookmark-title-search/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included. The spec requires them (SC-005: every acceptance scenario is covered by an automated test) and so does the constitution (Principle V; Principle II: real database; Principle VI quality gate).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project: `src/bookmarks_api/`, `tests/`, `migrations/` at repository root (plan.md)
- Run tests with `TEST_DATABASE_URL` exported; integration tests use the existing fixtures in `tests/conftest.py` (`client`, `clean_database` via `tests/integration/conftest.py`)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the starting point; the project, dependencies and test database already exist

- [ ] T001 Run the existing suite (`uv run pytest` over `tests/`) with `TEST_DATABASE_URL` exported and confirm it passes before any change (baseline for FR-011); `pyproject.toml` and `uv.lock` stay unchanged for the whole feature (plan: no new dependencies)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The word rule, the index and the shared query and request model that every story uses

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T002 [P] Add `MAX_SEARCH_LENGTH = 200` and a pure function `has_word_character(query: str) -> bool` to `src/bookmarks_api/normalize.py`: true when any character is a letter or a decimal digit (`c.isalpha() or c.isdecimal()`). It only pre-checks FR-008; the search is split into words in the database by `title_words` (T004), never in Python (research.md, analyze I1)
- [ ] T003 [P] Write unit tests for `has_word_character` in `tests/unit/test_search_query.py`: true for "postgres", "Python3", "3", "ΣΟΦΙΑ", "  a  "; false for "", "   ", "  -- !", "_", "½", "²"
- [ ] T004 Add a `title_words(expr)` helper returning the SQL expression `array_remove(regexp_split_to_array(lower(expr), '[^[:alnum:]]+'), '')` for any text expression (the title column or the bound search) (pattern and empty string as literal constants, not bound parameters, so the planner matches the index) and declare `Index("ix_bookmarks_title_words", title_words(title), postgresql_using="gin")` in `BookmarkRow.__table_args__` in `src/bookmarks_api/models.py`
- [ ] T005 Create Alembic revision `migrations/versions/0002_title_words_index.py` (`revision = "0002"`, `down_revision = "0001"`): `upgrade()` creates GIN index `ix_bookmarks_title_words` on `bookmarks` over exactly the expression in T004; `downgrade()` drops it (depends on T004 for the expression text)
- [ ] T006 Extend `list_bookmarks` in `src/bookmarks_api/repository.py` with an optional keyword `search: str | None = None`; when given, add `title_words(BookmarkRow.title).contains(title_words(bindparam(search)))` (`@>`) and `func.cardinality(title_words(<same bound search>)) > 0` to the conditions used by both the `total` count and the page query, keeping the existing tag condition, `(created_at, id)` keyset, `created_at DESC, id DESC` order and `limit + 1` look-ahead; with `search=None` the function behaves exactly as before (FR-011) (depends on T004)
- [ ] T007 Add `BookmarkSearchQuery(BookmarkListQuery)` to `src/bookmarks_api/schemas.py` with `q: str = Field(min_length=1, max_length=MAX_SEARCH_LENGTH, description=...)` ("q: Required; 1 to 200 characters as sent; at least one letter or decimal digit") and a validator that raises `ValueError` with a message naming letters or digits when `has_word_character(q)` is false; `q` is passed on unchanged (not trimmed); `limit` ("1 to 100, default 20"), `cursor` and `tag` are inherited unchanged (depends on T002)

**Checkpoint**: Foundation ready; `uv run pytest` still passes (existing tests only touch `search=None`)

---

## Phase 3: User Story 1 - Search bookmarks by title words (Priority: P1) 🎯 MVP

**Goal**: `GET /bookmarks/search?q=...` returns bookmarks whose title contains every search word as a whole word, ignoring case, newest first

**Independent Test**: Save bookmarks with different titles, search for a word in some of them, and confirm only those come back, newest first, with the right total

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T008 [P] [US1] Write integration tests in `tests/integration/test_search_bookmarks.py` for spec US1 scenarios 1 to 5 (matching titles newest first with `total` 2; "postgresql", "POSTGRESQL", "PostgreSQL" all match; no match → `{"items": [], "total": 0, "limit": 20, "next_cursor": null}`; "indexing postgres" matches and "postgres backups" does not; missing `q`, `q=""`, `q="  -- !"` and a 201-character `q` → 422 `validation_error` with `details[0].field == "query.q"`, while a 200-character `q` is accepted) and the Edge Cases (extra spaces ignored; "spec-kit" finds "Spec-Kit guide"; "post" and "gres" do not find "Postgres"; letter case is ignored for non-English letters (title "ΟΔΟΣ" found by "ΟΔΟΣ" and "οδοσ"; title "İstanbul guide" found by "İstanbul"); "½" separates words ("x½y" title found by "x"); `q="½"` → 422; a word only in the link or tags does not match; a deleted bookmark no longer appears)
- [ ] T009 [US1] Add a test in `tests/integration/test_search_bookmarks.py` that `/openapi.json` lists `GET /bookmarks/search` with required query parameter `q`, a `200` response referencing `BookmarkPage` and a `422` response referencing `ErrorResponse` (Constitution I quality gate)

### Implementation for User Story 1

- [ ] T010 [US1] Add `GET /bookmarks/search` to `src/bookmarks_api/routes.py`, following `list_bookmarks`: `response_model=BookmarkPage`, `summary="Search bookmarks by words in the title, newest first"`, `responses=ERROR_422`, `dependencies=[Depends(reject_offset)]`, `query: Annotated[BookmarkSearchQuery, Query()]`; decode the cursor, call `repository.list_bookmarks(session, limit=query.limit, after=after, search=query.q)`, and build `next_cursor` and the page exactly as the list route does (depends on T006, T007)
- [ ] T011 [US1] Run `tests/integration/test_search_bookmarks.py` and `tests/unit/test_search_query.py` and make them pass; run the full suite to confirm the existing list, filter, save and delete tests are unchanged (FR-011)

**Checkpoint**: User Story 1 is fully functional and testable on its own (MVP)

---

## Phase 4: User Story 2 - Combine search with the tag filter (Priority: P2)

**Goal**: A search narrowed by `tag` returns only bookmarks matching both, with the list's tag rules

**Independent Test**: Save bookmarks with overlapping titles and tags; a search plus a tag returns only bookmarks matching both

### Tests for User Story 2 ⚠️

- [ ] T012 [P] [US2] Write integration tests in `tests/integration/test_search_with_tag.py` for spec US2 scenarios 1 to 4: "testing" + tag "python" returns only "Testing in Python" with `total` 1; tag "Python" is normalized and matches; a matching search with a tag none of the matches carry returns an empty page with `total` 0; invalid tags ("no spaces", 31 characters, "c++") return 422 `validation_error` with `details[0].field == "query.tag"`, the same as `GET /bookmarks`; also a bookmark matching the tag but not the words, and the reverse, are not returned

### Implementation for User Story 2

- [ ] T013 [US2] Pass `tag=query.tag` from the search route to `repository.list_bookmarks` in `src/bookmarks_api/routes.py`, so the tag condition applies to both the page and `total` (FR-006) (depends on T010)

**Checkpoint**: User Stories 1 and 2 both work independently

---

## Phase 5: User Story 3 - Page through search results (Priority: P3)

**Goal**: Search pages exactly like the bookmark list: 20 by default, 1 to 100, opaque `next_cursor`, stable when bookmarks are saved or deleted between pages

**Independent Test**: Save more matches than fit on one page and follow `next_cursor` until it is null; every match is seen exactly once

### Tests for User Story 3 ⚠️

- [ ] T014 [P] [US3] Write integration tests in `tests/integration/test_search_paging.py` for spec US3 scenarios 1 to 4: 25 "guide" matches + 5 others → first page of 20 newest with `total` 25 and a `next_cursor`, second page of 5 with `next_cursor` null; `limit=2` returns 2 with `limit` 2; exactly 20 matches → no `next_cursor`; `limit` 101, 0 and "many", malformed cursors and `offset` → 422 `validation_error` with the same fields as the list (`query.limit`, `query.cursor`, `query.offset` with a message naming `cursor`)
- [ ] T015 [US3] Add the Constitution VI quality-gate tests to `tests/integration/test_search_paging.py`: page through all matches with `limit=10` while a new matching bookmark is saved before every page request and see every original match exactly once, newest first; a delete between pages skips nothing; paging with `tag` and `cursor` together across pages; a `next_cursor` from one search sent with different words or a different tag is accepted and starts after that position (Clarification Q3)

### Implementation for User Story 3

- [ ] T016 [US3] Make `tests/integration/test_search_paging.py` pass; paging comes from the shared keyset in `src/bookmarks_api/repository.py` (T006) and the cursor handling in the search route in `src/bookmarks_api/routes.py` (T010), so change those files only if a T014 or T015 test fails

**Checkpoint**: All user stories are independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Performance target, documentation and final validation

- [ ] T017 [P] Write `tests/integration/test_search_performance.py` for SC-004: insert 100,000 bookmarks with one `INSERT ... SELECT ... FROM generate_series(1, 100000)` through the `engine` fixture (1,000 of them titled with "postgres guide"), then assert `GET /bookmarks/search?q=postgres%20guide` returns its first page of 20 in under one second
- [ ] T018 [P] Add `GET /bookmarks/search?q=&tag=&limit=&cursor=` to the endpoint table in `README.md`
- [ ] T019 Run the full suite on Python 3.11, 3.12 and 3.13 (`uv run --python <version> pytest`) with `TEST_DATABASE_URL` exported; all tests pass
- [ ] T020 Run the migration round trip on the dev database: `uv run alembic upgrade head`, `uv run alembic downgrade -1`, `uv run alembic upgrade head`; each succeeds and `ix_bookmarks_title_words` exists at the end (quickstart.md)
- [ ] T021 Run the manual checks in `specs/002-bookmark-title-search/quickstart.md` against the running API and confirm each expected result

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup; BLOCKS all user stories. T002 and T003 in parallel; T004 → T005 and T004 → T006; T002 → T007
- **User Stories (Phase 3+)**: All depend on Foundational
- **Polish (Phase 6)**: Depends on the user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: After Foundational; no dependency on other stories
- **User Story 2 (P2)**: After Foundational; T013 edits the route added in T010 (same file), so it follows US1's route task; its tests are independent
- **User Story 3 (P3)**: After Foundational and T010 (it pages through the search route); independent of US2

### Within Each User Story

- Tests are written first and fail before implementation
- Request model and repository (Foundational) before the route
- Story complete before moving to the next priority

### Parallel Opportunities

- T002 and T003 (different files)
- T008, T012 and T014 (different test files); T009 follows T008 and T015 follows T014 (same files)
- T017 and T018 (different files)

---

## Parallel Example: User Story 1

```bash
# Draft the first test file of each story together:
Task: "Integration tests for US1 scenarios and edge cases in tests/integration/test_search_bookmarks.py"
Task: "Integration tests for US2 in tests/integration/test_search_with_tag.py"
Task: "Integration tests for US3 in tests/integration/test_search_paging.py"

# Foundational work in parallel before US1:
Task: "has_word_character() in src/bookmarks_api/normalize.py"
Task: "Unit tests in tests/unit/test_search_query.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: run the US1 tests and the full suite
5. Demo if ready

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. User Story 1 → search works (MVP)
3. User Story 2 → search plus tag
4. User Story 3 → paging verified, Constitution VI gate in place
5. Polish → performance, docs, three Python versions, migration round trip

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
