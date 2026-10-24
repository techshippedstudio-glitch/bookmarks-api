# 03 tasks — forward-r2

Start: 2026-10-24T12:00:48Z

```console
$ ls .specify/extensions.yml
ls: cannot access '.specify/extensions.yml': No such file or directory
[exit 2]
```

```console
$ .specify/scripts/bash/setup-tasks.sh --json
{"FEATURE_DIR":"/home/claude/runs/forward-r2/specs/002-idempotent-bookmark-save","AVAILABLE_DOCS":["research.md","data-model.md","contracts/","quickstart.md"],"TASKS_TEMPLATE":"/home/claude/runs/forward-r2/.specify/templates/tasks-template.md","TASKS_TEMPLATE_CONTENT":"---\n\ndescription: \"Task list template for feature implementation\"\n---\n\n# Tasks: [FEATURE NAME]\n\n**Input**: Design documents from `/specs/[###-feature-name]/`\n\n**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/\n\n**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.\n\n**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.\n\n## Format: `[ID] [P?] [Story] Description`\n\n- **[P]**: Can run in parallel (different files, no dependencies)\n- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)\n- Include exact file paths in descriptions\n\n## Path Conventions\n\n- **Single project**: `src/`, `tests/` at repository root\n- **Web app**: `backend/src/`, `frontend/src/`\n- **Mobile**: `api/src/`, `ios/src/` or `android/src/`\n- Paths shown below assume single project - adjust based on plan.md structure\n\n<!--\n  ============================================================================\n  IMPORTANT: The tasks below are SAMPLE TASKS for illustration purposes only.\n\n  The /speckit-tasks command MUST replace these with actual tasks based on:\n  - User stories from spec.md (with their priorities P1, P2, P3...)\n  - Feature requirements from plan.md\n  - Entities from data-model.md\n  - Endpoints from contracts/\n\n  Tasks MUST be organized by user story so each story can be:\n  - Implemented independently\n  - Tested independently\n  - Delivered as an MVP increment\n\n  DO NOT keep these sample tasks in the generated tasks.md file.\n  ============================================================================\n-->\n\n## Phase 1: Setup (Shared Infrastructure)\n\n**Purpose**: Project initialization and basic structure\n\n- [ ] T001 Create project structure per implementation plan\n- [ ] T002 Initialize [language] project with [framework] dependencies\n- [ ] T003 [P] Configure linting and formatting tools\n\n---\n\n## Phase 2: Foundational (Blocking Prerequisites)\n\n**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented\n\n**⚠️ CRITICAL**: No user story work can begin until this phase is complete\n\nExamples of foundational tasks (adjust based on your project):\n\n- [ ] T004 Setup database schema and migrations framework\n- [ ] T005 [P] Implement authentication/authorization framework\n- [ ] T006 [P] Setup API routing and middleware structure\n- [ ] T007 Create base models/entities that all stories depend on\n- [ ] T008 Configure error handling and logging infrastructure\n- [ ] T009 Setup environment configuration management\n\n**Checkpoint**: Foundation ready - user story implementation can now begin in parallel\n\n---\n\n## Phase 3: User Story 1 - [Title] (Priority: P1) 🎯 MVP\n\n**Goal**: [Brief description of what this story delivers]\n\n**Independent Test**: [How to verify this story works on its own]\n\n### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️\n\n> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**\n\n- [ ] T010 [P] [US1] Contract test for [endpoint] in tests/contract/test_[name].py\n- [ ] T011 [P] [US1] Integration test for [user journey] in tests/integration/test_[name].py\n\n### Implementation for User Story 1\n\n- [ ] T012 [P] [US1] Create [Entity1] model in src/models/[entity1].py\n- [ ] T013 [P] [US1] Create [Entity2] model in src/models/[entity2].py\n- [ ] T014 [US1] Implement [Service] in src/services/[service].py (depends on T012, T013)\n- [ ] T015 [US1] Implement [endpoint/feature] in src/[location]/[file].py\n- [ ] T016 [US1] Add validation and error handling\n- [ ] T017 [US1] Add logging for user story 1 operations\n\n**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently\n\n---\n\n## Phase 4: User Story 2 - [Title] (Priority: P2)\n\n**Goal**: [Brief description of what this story delivers]\n\n**Independent Test**: [How to verify this story works on its own]\n\n### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️\n\n- [ ] T018 [P] [US2] Contract test for [endpoint] in tests/contract/test_[name].py\n- [ ] T019 [P] [US2] Integration test for [user journey] in tests/integration/test_[name].py\n\n### Implementation for User Story 2\n\n- [ ] T020 [P] [US2] Create [Entity] model in src/models/[entity].py\n- [ ] T021 [US2] Implement [Service] in src/services/[service].py\n- [ ] T022 [US2] Implement [endpoint/feature] in src/[location]/[file].py\n- [ ] T023 [US2] Integrate with User Story 1 components (if needed)\n\n**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently\n\n---\n\n## Phase 5: User Story 3 - [Title] (Priority: P3)\n\n**Goal**: [Brief description of what this story delivers]\n\n**Independent Test**: [How to verify this story works on its own]\n\n### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️\n\n- [ ] T024 [P] [US3] Contract test for [endpoint] in tests/contract/test_[name].py\n- [ ] T025 [P] [US3] Integration test for [user journey] in tests/integration/test_[name].py\n\n### Implementation for User Story 3\n\n- [ ] T026 [P] [US3] Create [Entity] model in src/models/[entity].py\n- [ ] T027 [US3] Implement [Service] in src/services/[service].py\n- [ ] T028 [US3] Implement [endpoint/feature] in src/[location]/[file].py\n\n**Checkpoint**: All user stories should now be independently functional\n\n---\n\n[Add more user story phases as needed, following the same pattern]\n\n---\n\n## Phase N: Polish & Cross-Cutting Concerns\n\n**Purpose**: Improvements that affect multiple user stories\n\n- [ ] TXXX [P] Documentation updates in docs/\n- [ ] TXXX Code cleanup and refactoring\n- [ ] TXXX Performance optimization across all stories\n- [ ] TXXX [P] Additional unit tests (if requested) in tests/unit/\n- [ ] TXXX Security hardening\n- [ ] TXXX Run quickstart.md validation\n\n---\n\n## Dependencies & Execution Order\n\n### Phase Dependencies\n\n- **Setup (Phase 1)**: No dependencies - can start immediately\n- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories\n- **User Stories (Phase 3+)**: All depend on Foundational phase completion\n  - User stories can then proceed in parallel (if staffed)\n  - Or sequentially in priority order (P1 → P2 → P3)\n- **Polish (Final Phase)**: Depends on all desired user stories being complete\n\n### User Story Dependencies\n\n- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories\n- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable\n- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable\n\n### Within Each User Story\n\n- Tests (if included) MUST be written and FAIL before implementation\n- Models before services\n- Services before endpoints\n- Core implementation before integration\n- Story complete before moving to next priority\n\n### Parallel Opportunities\n\n- All Setup tasks marked [P] can run in parallel\n- All Foundational tasks marked [P] can run in parallel (within Phase 2)\n- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)\n- All tests for a user story marked [P] can run in parallel\n- Models within a story marked [P] can run in parallel\n- Different user stories can be worked on in parallel by different team members\n\n---\n\n## Parallel Example: User Story 1\n\n```bash\n# Launch all tests for User Story 1 together (if tests requested):\nTask: \"Contract test for [endpoint] in tests/contract/test_[name].py\"\nTask: \"Integration test for [user journey] in tests/integration/test_[name].py\"\n\n# Launch all models for User Story 1 together:\nTask: \"Create [Entity1] model in src/models/[entity1].py\"\nTask: \"Create [Entity2] model in src/models/[entity2].py\"\n```\n\n---\n\n## Implementation Strategy\n\n### MVP First (User Story 1 Only)\n\n1. Complete Phase 1: Setup\n2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)\n3. Complete Phase 3: User Story 1\n4. **STOP and VALIDATE**: Test User Story 1 independently\n5. Deploy/demo if ready\n\n### Incremental Delivery\n\n1. Complete Setup + Foundational → Foundation ready\n2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)\n3. Add User Story 2 → Test independently → Deploy/Demo\n4. Add User Story 3 → Test independently → Deploy/Demo\n5. Each story adds value without breaking previous stories\n\n### Parallel Team Strategy\n\nWith multiple developers:\n\n1. Team completes Setup + Foundational together\n2. Once Foundational is done:\n   - Developer A: User Story 1\n   - Developer B: User Story 2\n   - Developer C: User Story 3\n3. Stories complete and integrate independently\n\n---\n\n## Notes\n\n- [P] tasks = different files, no dependencies\n- [Story] label maps task to specific user story for traceability\n- Each user story should be independently completable and testable\n- Verify tests fail before implementing\n- Commit after each task or logical group\n- Stop at any checkpoint to validate story independently\n- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence\n"}
[exit 0]
```

## Agent actions (not shell commands)

- Read `.claude/skills/speckit-tasks/SKILL.md`, the tasks template (TASKS_TEMPLATE_CONTENT), and the 002 design docs (plan, spec, research, data-model, contracts/openapi.yaml, quickstart) plus the constitution.
- No `.specify/extensions.yml` → no after_tasks hooks.
- Tests included because spec SC-005 and Constitution V/II require them ("Tests are OPTIONAL - only if explicitly requested in the feature specification": the 002 spec requests them via SC-005).
- Wrote `specs/002-idempotent-bookmark-save/tasks.md` with the Write tool; one follow-up Edit to T014 (replaced a non-existent `pytest --count` option with a shell loop) before the step ended.
- Questions the command would ask: none.

```console
$ cat specs/002-idempotent-bookmark-save/tasks.md
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
[exit 0]
```

```console
$ grep -cE "^- \[ \] T[0-9]{3}" specs/002-idempotent-bookmark-save/tasks.md; grep -E "^- \[ \]" specs/002-idempotent-bookmark-save/tasks.md | grep -vcE "^- \[ \] T[0-9]{3} "
18
0
[exit 1]
```

## Spec Kit completion report (verbatim)

- **tasks.md**: `specs/002-idempotent-bookmark-save/tasks.md`
- **Total tasks**: 18 (T001–T018)
- **Per phase / story**: Setup 1 (T001); Foundational 2 (T002–T003); US1 6 (T004–T009); US2 3 (T010–T012); US3 2 (T013–T014); Polish 4 (T015–T018)
- **Parallel opportunities**: T008 ‖ T004–T007 (different test files); T010 ‖ T011; T015 independent of code tasks
- **Independent test criteria**: US1 — re-save in an equivalent form with different title/tags returns 200 with the original bookmark and one row; US2 — new link → 201, delete then save again → 201 new id; US3 — two concurrent first saves → statuses [200, 201], same id, one row
- **Suggested MVP**: Phase 1–3 (User Story 1)
- **Format validation**: all 18 tasks follow `- [ ] T### [P?] [US?] description with file path` (0 malformed lines). T001, T012, T014, T017 and T018 name commands/paths rather than a single source file.

End: 2026-10-24T12:01:46Z
