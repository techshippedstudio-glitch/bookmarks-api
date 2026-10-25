# 05-tasks (feature2-r1)

Start: 2026-10-25T12:23:55Z

Command: `/speckit-tasks` (no arguments). Read .claude/skills/speckit-tasks/SKILL.md in full.

## Pre-Execution Checks
```console
$ python3 -c "import yaml,json; d=yaml.safe_load(open('.specify/extensions.yml')); print(json.dumps(d['hooks']['before_tasks'], indent=1))"
[
 {
  "extension": "git",
  "command": "speckit.git.commit",
  "enabled": true,
  "optional": true,
  "priority": 10,
  "prompt": "Commit outstanding changes before task generation?",
  "description": "Auto-commit before task generation",
  "condition": null
 }
]
[exit 0]
```

Emitted:

```
## Extension Hooks

**Optional Pre-Hook**: git
Command: `/speckit-git-commit`
Description: Auto-commit before task generation

Prompt: Commit outstanding changes before task generation?
To execute: `/speckit-git-commit`
```

Optional hook run by run rule: `/speckit-git-commit` with event `before_tasks`.

```console
$ git status --short

[exit 0]
```

```console
$ .specify/extensions/git/scripts/bash/auto-commit.sh before_tasks

[exit 0]
```

## Outline 1: Setup
```console
$ .specify/scripts/bash/setup-tasks.sh --json | python3 -c 'import json,sys; d=json.load(sys.stdin); c=d.pop("TASKS_TEMPLATE_CONTENT"); print(json.dumps(d)); print("TASKS_TEMPLATE_CONTENT (%d chars):" % len(c)); print(c)'
{"FEATURE_DIR": "/home/claude/ep08-runs/feature2-r1/repo/specs/002-bookmark-title-search", "AVAILABLE_DOCS": ["research.md", "data-model.md", "contracts/", "quickstart.md"], "TASKS_TEMPLATE": "/home/claude/ep08-runs/feature2-r1/repo/.specify/templates/tasks-template.md"}
TASKS_TEMPLATE_CONTENT (9134 chars):
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

## Outline 2-4

Loaded plan.md, spec.md, data-model.md, contracts/openapi.yaml, research.md, quickstart.md, constitution.md; and the
existing tests/integration/test_errors.py (OpenAPI check to extend) and specs/001-bookmarks-api/tasks.md (format
reference, read only). Tests included: spec SC-004 and constitution II/V/VI require them. tasks.md generated.

## Format validation
```console
$ grep -cE '^- \[ \] T[0-9]{3} ' specs/002-bookmark-title-search/tasks.md; grep -E '^- \[ \] T[0-9]{3} ' specs/002-bookmark-title-search/tasks.md | grep -c '\[P\]'; for s in US1 US2 US3; do printf '%s ' $s; grep -cE '^- \[ \] T[0-9]{3} .*\[\]' specs/002-bookmark-title-search/tasks.md; done; grep -E '^## Phase' specs/002-bookmark-title-search/tasks.md; grep -vE '^- \[ \] T[0-9]{3} (\[P\] )?(\[US[0-9]\] )?.+' specs/002-bookmark-title-search/tasks.md | grep -cE '^- \[ \] T'
15
6
US1 1
US2 1
US3 1
## Phase 1: Setup (Shared Infrastructure)
## Phase 2: Foundational (Blocking Prerequisites)
## Phase 3: User Story 1 - Search bookmarks by title words (Priority: P1) 🎯 MVP
## Phase 4: User Story 2 - Combine search with the tag filter (Priority: P2)
## Phase 5: User Story 3 - Page through search results (Priority: P3)
## Phase 6: Polish & Cross-Cutting Concerns
0
[exit 1]
```

## Mandatory Post-Execution Hooks
```console
$ python3 -c "import yaml,json; d=yaml.safe_load(open('.specify/extensions.yml')); print(json.dumps(d['hooks']['after_tasks'], indent=1))"
[
 {
  "extension": "git",
  "command": "speckit.git.commit",
  "enabled": true,
  "optional": true,
  "priority": 10,
  "prompt": "Commit task changes?",
  "description": "Auto-commit after task generation",
  "condition": null
 }
]
[exit 0]
```

Emitted:

```
## Extension Hooks

**Optional Hook**: git
Command: `/speckit-git-commit`
Description: Auto-commit after task generation

Prompt: Commit task changes?
To execute: `/speckit-git-commit`
```

Optional hook run by run rule: `/speckit-git-commit` with event `after_tasks`.

```console
$ git status --short
?? specs/002-bookmark-title-search/tasks.md
[exit 0]
```

```console
$ .specify/extensions/git/scripts/bash/auto-commit.sh after_tasks
[OK] Changes committed after tasks
[exit 0]
```

```console
$ git status --short

[exit 0]
```

```console
$ git diff --stat ep08-feature2-r1-checklist HEAD
 specs/002-bookmark-title-search/tasks.md | 181 +++++++++++++++++++++++++++++++
 1 file changed, 181 insertions(+)
[exit 0]
```

Recount (the per-story grep above used an unescaped [USn] character class and is wrong; the final 'exit 1' is grep -c counting 0 malformed task lines):
```console
$ for s in US1 US2 US3; do printf '%s ' $s; grep -F "[$s]" specs/002-bookmark-title-search/tasks.md | grep -cE '^- \[ \] T'; done; grep -E '^- \[ \] T' specs/002-bookmark-title-search/tasks.md | grep -F '[P]' | cut -c1-12; grep -E '^- \[ \] T' specs/002-bookmark-title-search/tasks.md | grep -E 'tests/integration/test_errors.py|README.md|normalize.py|schemas.py|repository.py|routes.py|pyproject' | cut -c7-10 | tr '\n' ' '
US1 3
US2 2
US3 3
- [ ] T002 [
- [ ] T006 [
- [ ] T009 [
- [ ] T011 [
- [ ] T012 [
- [ ] T014 [
T001 T003 T004 T005 T007 T008 T010 T013 T014 
[exit 0]
```

## Final report (verbatim)

> Tasks generated: `/home/claude/ep08-runs/feature2-r1/repo/specs/002-bookmark-title-search/tasks.md`
>
> - Total tasks: 15 (T001-T015) in 6 phases: Setup 1, Foundational 4, US1 3, US2 2, US3 3, Polish 2.
> - Parallel opportunities: 6 tasks marked [P] (T002, T006, T009, T011, T012, T014).
> - Independent test criteria: US1 - search returns only titles containing every word, newest first, any case;
>   US2 - search plus `tag=` returns only bookmarks matching both; US3 - following `next_cursor` returns every match
>   once, newest first, even with saves between pages.
> - Suggested MVP: Phases 1-3 (User Story 1).
> - Format validation: all 15 tasks follow `- [ ] T### [P?] [US?] description with file path`; story labels only in
>   phases 3-5.
> - Tasks touching existing files: T001 (pyproject.toml/uv.lock, check only), T003 normalize.py, T004 schemas.py,
>   T005 repository.py, T007/T010/T013 routes.py, T008 tests/integration/test_errors.py, T014 README.md.
> - `after_tasks` optional hook run: "[OK] Changes committed after tasks".

## Post-step state

```console
$ git branch
* 002-bookmark-title-search
  main
[exit 0]
```

```console
$ git rev-parse --abbrev-ref HEAD
002-bookmark-title-search
[exit 0]
```

```console
$ git log --oneline -5
8323fea [Spec Kit] Add tasks
8a8a34f [Spec Kit] Add checklist
1866387 [Spec Kit] Add implementation plan
903de72 [Spec Kit] Clarify specification
c3865fa [Spec Kit] Add specification
[exit 0]
```

```console
$ cat .specify/feature.json
{
  "feature_directory": "specs/002-bookmark-title-search"
}
[exit 0]
```

```console
$ git tag ep08-feature2-r1-tasks && git rev-parse --short ep08-feature2-r1-tasks
8323fea
[exit 0]
```

End: 2026-10-25T12:25:02Z
