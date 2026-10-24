# Step 04 — analyze (forward-r4)

Start: 2026-10-24T12:38:15Z

## Pass 1

```console
$ ls .specify/extensions.yml 2>&1; .specify/scripts/bash/check-prerequisites.sh --json --require-spec --require-tasks --include-tasks
ls: cannot access '.specify/extensions.yml': No such file or directory
{"FEATURE_DIR":"/home/claude/runs/forward-r4/specs/002-idempotent-duplicate-save","AVAILABLE_DOCS":["research.md","data-model.md","contracts/","quickstart.md","tasks.md"]}
[exit 0]
```

```console
$ grep -n "" specs/002-idempotent-duplicate-save/spec.md | sed -n "60,125p"
60:exactly one bookmark is stored.
61:
62:**Acceptance Scenarios**:
63:
64:1. **Given** no bookmark exists for a link, **When** two saves of that link (possibly in different
65:   equivalent forms) happen at the same moment, **Then** exactly one bookmark is stored, one
66:   response is HTTP 201 Created and the other is HTTP 200 OK, and both responses carry the same
67:   bookmark.
68:
69:---
70:
71:### Edge Cases
72:
73:- A save whose link matches an existing bookmark only after normalization (scheme/host case,
74:  default port, trailing path slash, fragment) returns the existing bookmark with HTTP 200 OK.
75:- A save whose link differs from an existing bookmark only in its query string is a new link and
76:  returns HTTP 201 Created.
77:- A duplicate save whose title or tags are invalid (for example a title over 200 characters, more
78:  than 10 tags, or an invalid tag) is still rejected with a validation error: input is validated
79:  before the duplicate check, exactly as for any other save. Valid but different title and tags are
80:  ignored.
81:- The returned existing bookmark shows the link as it was originally given, not the form sent in
82:  the duplicate request.
83:- After a bookmark is deleted, saving the same link again creates a new bookmark (HTTP 201
84:  Created), unchanged from specs/001-bookmarks-api.
85:- A duplicate save never produces a conflict error any more.
86:
87:## Requirements *(mandatory)*
88:
89:### Functional Requirements
90:
91:- **FR-001**: System MUST NOT store two bookmarks for the same link, where links are compared
92:  after the normalization rules of FR-004 in specs/001-bookmarks-api (scheme and host lowercased,
93:  default port removed, trailing path slash removed, fragment removed, query kept). This MUST
94:  hold even when two saves happen at the same moment.
95:- **FR-002**: When a save's link (after normalization) matches an existing bookmark, the System
96:  MUST respond with success (HTTP 200 OK) and return the existing bookmark exactly as stored. It
97:  MUST NOT return a conflict error. *(Replaces the duplicate rule in FR-004 of
98:  specs/001-bookmarks-api, which required a conflict error.)*
99:- **FR-003**: When a save matches an existing bookmark, the System MUST ignore the title and tags
100:  sent in that save and MUST NOT modify the stored bookmark (identifier, link, title, tags and
101:  saved time all stay the same).
102:- **FR-004**: When a save's link does not match any existing bookmark, the System MUST store it
103:  and respond with HTTP 201 Created, as before.
104:- **FR-005**: When two saves of the same new link happen at the same moment, exactly one MUST
105:  receive HTTP 201 Created and the other MUST receive HTTP 200 OK, and both MUST return the same
106:  bookmark.
107:- **FR-006**: Save requests MUST still be validated (FR-002 and FR-011 of specs/001-bookmarks-api)
108:  before the duplicate check; an invalid request is rejected with a validation error whether or
109:  not its link is already saved.
110:
111:### Key Entities
112:
113:- **Bookmark**: Unchanged from specs/001-bookmarks-api. The normalized form of its link remains
114:  unique across all bookmarks.
115:
116:## Success Criteria *(mandatory)*
117:
118:### Measurable Outcomes
119:
120:- **SC-001**: Saving the same link any number of times, in any of its equivalent forms, always
121:  leaves exactly one bookmark for it, and every save after the first returns that bookmark with a
122:  success status.
123:- **SC-002**: In 100% of tested duplicate saves the returned bookmark is identical (identifier,
124:  link, title, tags, saved time) to the stored one, and the stored one is unchanged.
125:- **SC-003**: In repeated tests of two simultaneous saves of a new link, there is always exactly
[exit 0]
```

```console
$ grep -n "def test_\|409\|duplicate" tests/integration/test_delete_bookmark.py; grep -n "Development Workflow" -A6 .specify/memory/constitution.md; grep -n "conflict\|duplicate_url" specs/002-idempotent-duplicate-save/spec.md specs/002-idempotent-duplicate-save/plan.md specs/002-idempotent-duplicate-save/tasks.md; grep -n "FR-004" specs/002-idempotent-duplicate-save/*.md
13:def test_deleted_bookmark_disappears_from_list_and_filter(client: TestClient, row_count) -> None:
26:def test_deleting_unknown_bookmark_returns_not_found(client: TestClient) -> None:
35:def test_deleting_twice_returns_not_found_the_second_time(client: TestClient) -> None:
42:def test_link_can_be_saved_again_after_delete(client: TestClient) -> None:
53:def test_invalid_id_is_a_validation_error(client: TestClient, bad_id: str) -> None:
70:## Development Workflow
71-
72-- Features follow the Spec Kit flow: specify, clarify, plan, tasks, implement, converge.
73-- Specifications describe what and why; technology choices belong in the plan.
74-- Plans MUST pass a constitution check before tasks are generated; any violation MUST be recorded
75-  with its justification in the plan's complexity tracking.
76-- A feature is complete when `/speckit-converge` reports Converged and the test suite passes.
specs/002-idempotent-duplicate-save/spec.md:9:**Input**: User description: "Saving a link that is already bookmarked must no longer be rejected. If the link (after the existing normalization rules) is already saved, return the existing bookmark unchanged with HTTP 200 OK instead of the current 409 conflict. The title and tags sent in the new request are ignored; the stored bookmark is not modified. Saving a new link still returns 201 Created. Two concurrent saves of the same new link must still store only one bookmark (one gets 201, the other gets 200 with the same bookmark). This replaces the duplicate rule in FR-004 of specs/001-bookmarks-api."
specs/002-idempotent-duplicate-save/spec.md:85:- A duplicate save never produces a conflict error any more.
specs/002-idempotent-duplicate-save/spec.md:97:  MUST NOT return a conflict error. *(Replaces the duplicate rule in FR-004 of
specs/002-idempotent-duplicate-save/spec.md:98:  specs/001-bookmarks-api, which required a conflict error.)*
specs/002-idempotent-duplicate-save/spec.md:127:- **SC-004**: No save request ever returns a conflict error.
specs/002-idempotent-duplicate-save/spec.md:139:- The `conflict` error code may no longer be produced by any endpoint; the consistent error format
specs/002-idempotent-duplicate-save/plan.md:19:`duplicate_url`** error; a new link still returns **201 Created**. The existing
specs/002-idempotent-duplicate-save/plan.md:23:flag. `DuplicateUrlError`, its 409 handler and the `duplicate_url` error code are removed. No schema
specs/002-idempotent-duplicate-save/plan.md:59:| III. Consistent Error Shape | No new error; the `duplicate_url` (409) error is removed because a duplicate is no longer an error. Remaining errors (422, 404, 405, 500) keep the one envelope. A 200 for an existing resource is a success class, so status codes still match their class | Pass |
specs/002-idempotent-duplicate-save/plan.md:88:├── repository.py        # create_bookmark -> (row, created); returns existing row on conflict
specs/002-idempotent-duplicate-save/tasks.md:13:(409 `duplicate_url`). `specs/001-bookmarks-api` is not edited; its completed tasks T008, T012,
specs/002-idempotent-duplicate-save/tasks.md:42:- [ ] T002 Change `create_bookmark(session, data)` in `src/bookmarks_api/repository.py` to return `tuple[BookmarkRow, bool]` (`(row, created)`): keep `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`; if a row is returned, commit and return `(row, True)`; if nothing is returned, roll back the transaction and `SELECT` the row where `url_normalized` equals the normalized link and return `(existing_row, False)` without writing anything; if that `SELECT` finds no row (the conflicting row was deleted in between), retry the insert, at most 3 attempts in total, then raise `RuntimeError` (research.md §1). Update the docstring and remove the `DuplicateUrlError` import
specs/002-idempotent-duplicate-save/tasks.md:62:- [ ] T004 [P] [US1] In `tests/integration/test_errors.py`, remove `test_duplicate_error_envelope` (409 `duplicate_url` no longer exists) and add a test that a duplicate save returns 200 and a body without an `error` key; in `test_openapi_documents_every_operation` change the expected `post` error codes from `{"409", "422"}` to `{"422"}`, assert `"409"` is not among the `post` responses, and assert the `post` `"200"` response schema `$ref` ends with `/Bookmark` (contracts/openapi.yaml)
specs/002-idempotent-duplicate-save/tasks.md:67:- [ ] T006 [US1] Remove `DuplicateUrlError` and its `handle_duplicate` 409 handler from `src/bookmarks_api/errors.py`; keep the generic `409: "conflict"` entry in `STATUS_CODES` for framework HTTP exceptions (research.md §3)
specs/002-idempotent-duplicate-save/tasks.md:98:- [ ] T010 Search `src/` and `tests/` for leftover `DuplicateUrlError`, `duplicate_url` and `409` references tied to duplicate saves and remove them (`grep -rn "DuplicateUrlError\|duplicate_url\|409" src tests`)
specs/002-idempotent-duplicate-save/data-model.md:28:`specs/001-bookmarks-api/data-model.md` and that spec's FR-004 describe a save of an existing link
specs/002-idempotent-duplicate-save/plan.md:7:**Supersedes**: the duplicate rule in FR-004 of [specs/001-bookmarks-api](../001-bookmarks-api/spec.md);
specs/002-idempotent-duplicate-save/spec.md:9:**Input**: User description: "Saving a link that is already bookmarked must no longer be rejected. If the link (after the existing normalization rules) is already saved, return the existing bookmark unchanged with HTTP 200 OK instead of the current 409 conflict. The title and tags sent in the new request are ignored; the stored bookmark is not modified. Saving a new link still returns 201 Created. Two concurrent saves of the same new link must still store only one bookmark (one gets 201, the other gets 200 with the same bookmark). This replaces the duplicate rule in FR-004 of specs/001-bookmarks-api."
specs/002-idempotent-duplicate-save/spec.md:11:**Supersedes**: the duplicate rule in **FR-004** of [`specs/001-bookmarks-api/spec.md`](../001-bookmarks-api/spec.md)
specs/002-idempotent-duplicate-save/spec.md:14:`specs/001-bookmarks-api` stays in force, including FR-004's normalization rules and its "never
specs/002-idempotent-duplicate-save/spec.md:55:**Why this priority**: The "never two bookmarks for one link" guarantee from FR-004 of
specs/002-idempotent-duplicate-save/spec.md:92:  after the normalization rules of FR-004 in specs/001-bookmarks-api (scheme and host lowercased,
specs/002-idempotent-duplicate-save/spec.md:97:  MUST NOT return a conflict error. *(Replaces the duplicate rule in FR-004 of
specs/002-idempotent-duplicate-save/spec.md:102:- **FR-004**: When a save's link does not match any existing bookmark, the System MUST store it
specs/002-idempotent-duplicate-save/tasks.md:12:**Supersedes**: the duplicate rule in FR-004 of [specs/001-bookmarks-api](../001-bookmarks-api/spec.md)
[exit 0]
```

### Analyze report — pass 1 (verbatim)

Hooks: `.specify/extensions.yml` absent — before_analyze / after_analyze skipped.

## Specification Analysis Report

Feature: `specs/002-idempotent-duplicate-save` (spec.md, plan.md, tasks.md; constitution v1.1.0)

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| C1 | Constitution Alignment | MEDIUM | constitution.md:L72; spec.md (no Clarifications section) | Development Workflow lists "specify, clarify, plan, tasks, implement, converge"; this feature skipped `/speckit-clarify`. The line carries no MUST, and the spec has 0 `[NEEDS CLARIFICATION]` markers, so not CRITICAL. | Run `/speckit-clarify`, or record why it was skipped. |
| I1 | Inconsistency | MEDIUM | spec.md:L11-14, L55, L92, L97, L102; plan.md:L7; tasks.md:L12 | Identifier collision: "FR-004" is used both for specs/001's FR-004 (superseded duplicate rule) and for this spec's own FR-004 (new link → 201). A reader of "FR-004" cannot tell which is meant. | Qualify every cross-spec reference as "001 FR-004" (or renumber), and say this spec's FR IDs are local. |
| I2 | Inconsistency | MEDIUM | spec.md:L139 vs plan.md:L23, L59; research.md §3; tasks.md T006 | Spec Assumption says "The `conflict` error code may no longer be produced by any endpoint", but the removed code is `duplicate_url`; plan/research/tasks keep the generic `409 → "conflict"` mapping for framework HTTP exceptions. Terminology drift + contradictory statement. | Change the assumption to name `duplicate_url` (409) as the removed code and state the generic mapping is untouched. |
| I3 | Inconsistency (cross-feature) | MEDIUM | spec.md:L11-17; plan.md:L7-11; tasks.md:L12-14 | Supersession inventory is incomplete. specs/001 still describes the 409 behavior in places 002 does not list: 001 plan.md:L52 ("duplicate (409)"), 001 research.md:L39-40 ("raise a duplicate error") and L87 (`duplicate_url` (409)), 001 quickstart.md:L39 (step 2 → 409), 001 contracts/openapi.yaml:L25-29 and L129 (`duplicate_url` in enum). 001 is immutable, so readers of those files get no pointer forward. | Add a complete "Superseded statements in specs/001-bookmarks-api" table to plan.md (file:line → replacement in 002). |
| U1 | Underspecification | MEDIUM | tasks.md T002; research.md §1 vs spec.md Edge Cases | Plan/tasks introduce behavior not in the spec: a save that conflicts with a row deleted before the follow-up read retries the insert (max 3) and then raises `RuntimeError` (→ 500 `internal_error`). The spec's edge cases say nothing about a save racing a delete, and no task tests the retry path. | Add the save-vs-delete race to spec Edge Cases (outcome: the save behaves as a new save → 201); note in tasks that the retry branch is not deterministically testable against a real DB and is covered by review. |
| A1 | Ambiguity | LOW | tasks.md T008 | "Verify ... adjust only if T007 fails" is a conditional, non-deliverable task. | Phrase as a concrete acceptance check (T007 passes 20/20 iterations with no code beyond T002). |
| D1 | Duplication | LOW | tasks.md T003(d); tests/integration/test_delete_bookmark.py:L42 | T003(d) asks for a delete-then-resave → 201 test, which already exists as `test_link_can_be_saved_again_after_delete`. | Drop that clause from T003(d) and reference the existing test. |
| G1 | Coverage Gap | LOW | spec.md FR-004 (new link → 201); tasks.md T003(c) | FR-004 is covered only by "the existing 201 tests stay unchanged" — implicit, no task names the test. | Name the existing test(s) (`test_save_with_title_and_no_tags`) as FR-004 coverage. |

**Coverage Summary Table:**

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|
| FR-001 (one bookmark per normalized link, incl. concurrent) | Yes | T002, T003(a), T007 | |
| FR-002 (duplicate → 200 + existing, never conflict) | Yes | T002, T003(a), T004, T005, T006 | |
| FR-003 (ignore title/tags, no modification) | Yes | T003(b) | |
| FR-004 (new link → 201) | Implicit | T003(c) | G1 |
| FR-005 (concurrent: one 201, one 200, same bookmark) | Yes | T007, T008 | |
| FR-006 (validate before duplicate check) | Yes | T003(d) | |
| SC-001 | Yes | T003(a), T007 | |
| SC-002 | Yes | T003(a)(b) | |
| SC-003 | Yes | T007 (20 iterations) | |
| SC-004 (no conflict ever) | Yes | T004, T006, T010 | |
| SC-005 (every scenario tested) | Yes | T003, T004, T007, T011 | |

**Constitution Alignment Issues:** C1 (MEDIUM, workflow step skipped; no MUST violated). Principles I-VI: no violations found (plan Constitution Check verified: 200 declared with `Bookmark` model; real-DB tests; error envelope unchanged; no dependency; tests per scenario; no list endpoint change).

**Unmapped Tasks:** T001 (baseline run — setup, acceptable), T009 (README docs — polish, acceptable).

**Metrics:**

- Total Requirements: 11 (6 FR + 5 SC)
- Total Tasks: 11
- Coverage %: 100% (11/11 with ≥1 task; FR-004 implicit)
- Ambiguity Count: 1
- Duplication Count: 1
- Critical Issues Count: 0

**Next Actions:** No CRITICAL issues; `/speckit-implement` may proceed. Suggested improvements: fix I1-I3 and U1 by editing spec.md / plan.md; tighten T003, T008 in tasks.md; for C1 run `/speckit-clarify` or record the skip.

Would you like me to suggest concrete remediation edits for the top 8 issues?

### Remediation decision (pass 1)

Per run rules: remediation accepted; I apply fixes myself to `specs/002-idempotent-duplicate-save/` only.
- C1: **not remediated — recorded as accepted.** The run's rules fix the order (specify, plan, tasks, analyze, implement, converge) and do not include clarify; the spec raised no clarification questions. A note is added to the spec explaining the skip.
- I1, I2, I3, U1, A1, D1, G1: fixed by the edits below.

### Remediation edits applied after pass 1

Edits made with a Python string-replace script (each old string asserted to occur exactly once):
- spec.md: "001 FR-004" qualification everywhere; new "Requirement IDs" note; new "Clarify step" note (C1 accepted); pointer to plan.md superseded table; new Edge Case "save racing a delete -> 201"; Assumption now names `duplicate_url` (409) instead of `conflict`.
- plan.md: "001 FR-004" qualification; new section "Superseded statements in specs/001-bookmarks-api" (11 rows, file:line -> replacement).
- tasks.md: header qualification + local-ID note; T002 retry now yields 201 per new edge case, RuntimeError only as 3-attempt safety bound, retry branch covered by review (no mock, Constitution II); T003(c) names `test_save_with_title_and_no_tags` as FR-004 coverage; T003(d) drops the delete-then-resave test (exists in test_delete_bookmark.py); T008 rewritten as a concrete check.
- data-model.md: "001 FR-004" qualification.

## Pass 2

```console
$ .specify/scripts/bash/check-prerequisites.sh --json --require-spec --require-tasks --include-tasks
{"FEATURE_DIR":"/home/claude/runs/forward-r4/specs/002-idempotent-duplicate-save","AVAILABLE_DOCS":["research.md","data-model.md","contracts/","quickstart.md","tasks.md"]}
[exit 0]
```

```console
$ git diff --stat; grep -n "FR-0[0-9][0-9] of\|of FR-0\|FR-004" specs/002-idempotent-duplicate-save/*.md | grep -v "001 FR-004" ; grep -n "conflict\b" specs/002-idempotent-duplicate-save/spec.md; grep -n "describe a save" -A2 specs/002-idempotent-duplicate-save/data-model.md
 specs/002-idempotent-duplicate-save/data-model.md |  2 +-
 specs/002-idempotent-duplicate-save/plan.md       | 26 ++++++++++++++++--
 specs/002-idempotent-duplicate-save/spec.md       | 33 +++++++++++++++--------
 specs/002-idempotent-duplicate-save/tasks.md      | 14 +++++-----
 4 files changed, 55 insertions(+), 20 deletions(-)
specs/002-idempotent-duplicate-save/plan.md:119:| spec.md:L152-156 (FR-004) | Save of existing link MUST be rejected with conflict error | spec.md FR-001 (uniqueness kept), FR-002, FR-005 |
specs/002-idempotent-duplicate-save/spec.md:9:**Input**: User description: "Saving a link that is already bookmarked must no longer be rejected. If the link (after the existing normalization rules) is already saved, return the existing bookmark unchanged with HTTP 200 OK instead of the current 409 conflict. The title and tags sent in the new request are ignored; the stored bookmark is not modified. Saving a new link still returns 201 Created. Two concurrent saves of the same new link must still store only one bookmark (one gets 201, the other gets 200 with the same bookmark). This replaces the duplicate rule in FR-004 of specs/001-bookmarks-api."
specs/002-idempotent-duplicate-save/spec.md:113:- **FR-004**: When a save's link does not match any existing bookmark, the System MUST store it
specs/002-idempotent-duplicate-save/tasks.md:63:- [ ] T003 [P] [US1] In `tests/integration/test_create_bookmark.py`, replace `test_equivalent_link_is_rejected_as_duplicate` and `test_duplicate_leaves_the_existing_bookmark_unchanged` with: (a) US1 AC1 — save `https://example.com/docs` (title "Docs"), then `HTTPS://Example.com/docs/#intro` → 200 and the body equals the first response body exactly (`id`, `url` `https://example.com/docs`, `title`, `tags`, `created_at`), `row_count() == 1`; (b) US1 AC2 — save `https://example.com/docs` title "Docs" tags `["api"]`, then the same link with title "Other" tags `["python", "new"]` → 200 with title "Docs" and tags `["api"]`, and the stored row (read via `engine`) still has title "Docs", tags `{api}` and the original `created_at`, and `GET /bookmarks` returns exactly one item; (c) US1 AC3 / FR-004 — keep `test_save_with_title_and_no_tags` (201 for a new link) unchanged as the FR-004 coverage; (d) edge cases — a duplicate save with an invalid title (`"t" * 201`) or 11 tags → 422 `validation_error` and the stored bookmark unchanged (FR-006); a link differing only by query string (`https://example.com/docs?x=1`) → 201 and `row_count() == 2`. (Delete-then-resave → 201 is already covered by `test_link_can_be_saved_again_after_delete` in `tests/integration/test_delete_bookmark.py`; leave it unchanged.)
9:**Input**: User description: "Saving a link that is already bookmarked must no longer be rejected. If the link (after the existing normalization rules) is already saved, return the existing bookmark unchanged with HTTP 200 OK instead of the current 409 conflict. The title and tags sent in the new request are ignored; the stored bookmark is not modified. Saving a new link still returns 201 Created. Two concurrent saves of the same new link must still store only one bookmark (one gets 201, the other gets 200 with the same bookmark). This replaces the duplicate rule in FR-004 of specs/001-bookmarks-api."
96:- A duplicate save never produces a conflict error any more.
108:  MUST NOT return a conflict error. *(Replaces the duplicate rule in 001 FR-004,
109:  which required a conflict error.)*
138:- **SC-004**: No save request ever returns a conflict error.
150:- The `duplicate_url` error (the 409 conflict for a duplicate save) is no longer produced by any
28:`specs/001-bookmarks-api/data-model.md` and 001 FR-004 describe a save of an existing link
29-as rejected with 409 `duplicate_url` and `details.existing_id`. That rejection is replaced by the
30-"Existing" outcome above (spec FR-002). The uniqueness rule itself is unchanged.
[exit 0]
```

### Analyze report — pass 2 (verbatim)

## Specification Analysis Report

Feature: `specs/002-idempotent-duplicate-save` (re-run after pass-1 remediation)

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| C1 | Constitution Alignment | MEDIUM (accepted) | constitution.md:L72; spec.md "Clarify step" note | `/speckit-clarify` not run; skip is now recorded in the spec with its reason. No MUST violated. | Accepted — no further action. |
| I4 | Inconsistency | LOW | spec.md Edge Cases (save racing a delete: "never an error and never a missing bookmark") vs tasks.md T002 / research.md §1 (raise `RuntimeError` → 500 after 3 failed attempts) | The spec promises the race never errors; the plan keeps a 3-attempt safety bound that would error. | Drop the absolute "never an error" wording from the spec edge case, or document the bound in research.md §1 as the only (practically unreachable) error path. |
| L1 | Inconsistency | LOW | data-model.md:L28-29 | Says `specs/001-bookmarks-api/data-model.md` describes the 409 `duplicate_url` rejection; it does not (001 data-model only names `url_normalized` as used for duplicate detection). The 409 is in 001 FR-004, 001 research.md and the 001 contract. | Point to 001 FR-004, 001 research.md and 001 contracts/openapi.yaml instead. |

**Coverage Summary Table:**

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|
| FR-001 | Yes | T002, T003(a), T007 | |
| FR-002 | Yes | T002, T003(a), T004, T005, T006 | |
| FR-003 | Yes | T003(b) | |
| FR-004 | Yes | T003(c) (`test_save_with_title_and_no_tags`) | G1 resolved |
| FR-005 | Yes | T007, T008 | |
| FR-006 | Yes | T003(d) | |
| SC-001 | Yes | T003(a), T007 | |
| SC-002 | Yes | T003(a)(b) | |
| SC-003 | Yes | T007 | |
| SC-004 | Yes | T004, T006, T010 | |
| SC-005 | Yes | T003, T004, T007, T011 | |

**Constitution Alignment Issues:** C1 only (accepted). Principles I-VI: no violations.

**Unmapped Tasks:** T001 (setup), T009 (README) — acceptable.

**Metrics:**

- Total Requirements: 11
- Total Tasks: 11
- Coverage %: 100%
- Ambiguity Count: 0
- Duplication Count: 0
- Critical Issues Count: 0

Pass-1 findings I1, I2, I3, U1, A1, D1, G1: resolved.

**Next Actions:** No CRITICAL/HIGH issues; may proceed to `/speckit-implement`. Two LOW wording fixes suggested (I4, L1).

Would you like me to suggest concrete remediation edits for the top 2 issues?

### Remediation decision (pass 2)

Accepted; applying I4 and L1 fixes to the 002 folder.

## Pass 3

```console
$ .specify/scripts/bash/check-prerequisites.sh --json --require-spec --require-tasks --include-tasks
{"FEATURE_DIR":"/home/claude/runs/forward-r4/specs/002-idempotent-duplicate-save","AVAILABLE_DOCS":["research.md","data-model.md","contracts/","quickstart.md","tasks.md"]}
[exit 0]
```

```console
$ grep -n "never an error\|RuntimeError\|safety bound" specs/002-idempotent-duplicate-save/*.md; grep -n "describe a save" -B1 -A4 specs/002-idempotent-duplicate-save/data-model.md; grep -c "^- \[ \] T" specs/002-idempotent-duplicate-save/tasks.md; grep -n "TODO\|TKTK\|???\|NEEDS CLARIFICATION" specs/002-idempotent-duplicate-save/spec.md specs/002-idempotent-duplicate-save/plan.md specs/002-idempotent-duplicate-save/tasks.md
specs/002-idempotent-duplicate-save/research.md:18:  a safety bound; only if a row with the same link is inserted and deleted again around every
specs/002-idempotent-duplicate-save/tasks.md:44:- [ ] T002 Change `create_bookmark(session, data)` in `src/bookmarks_api/repository.py` to return `tuple[BookmarkRow, bool]` (`(row, created)`): keep `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`; if a row is returned, commit and return `(row, True)`; if nothing is returned, roll back the transaction and `SELECT` the row where `url_normalized` equals the normalized link and return `(existing_row, False)` without writing anything; if that `SELECT` finds no row (the conflicting row was deleted in between), retry the insert, so the save is stored as new and returns `(row, True)` (spec Edge Case: save racing a delete → 201); cap the loop at 3 attempts as a safety bound and raise `RuntimeError` only if all 3 fail (research.md §1). Update the docstring and remove the `DuplicateUrlError` import. The retry branch needs a delete to land between two statements and cannot be triggered deterministically against the real database without mocks (Constitution II), so it is covered by code review rather than a test
28-001 FR-004, `specs/001-bookmarks-api/research.md` ("Preventing duplicate links", "Error
29:envelope") and `specs/001-bookmarks-api/contracts/openapi.yaml` describe a save of an existing link
30-as rejected with 409 `duplicate_url` and `details.existing_id`
31-(`specs/001-bookmarks-api/data-model.md` itself only names `url_normalized` as the duplicate key). That rejection is replaced by the
32-"Existing" outcome above (spec FR-002). The uniqueness rule itself is unchanged.
11
specs/002-idempotent-duplicate-save/spec.md:24:question (0 `[NEEDS CLARIFICATION]` markers) and the delivery order for this change is specify,
[exit 0]
```

### Analyze report — pass 3 (verbatim)

## Specification Analysis Report

Feature: `specs/002-idempotent-duplicate-save` (re-run after pass-2 remediation)

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| C1 | Constitution Alignment | MEDIUM (accepted) | constitution.md:L72; spec.md "Clarify step" note | `/speckit-clarify` not run; reason recorded in spec. No MUST violated. | Accepted — no action. |

The only `NEEDS CLARIFICATION` match (spec.md:L24) is the explanatory note itself, not an open marker. Pass-2 findings I4 and L1: resolved (spec edge case no longer promises "never an error"; research.md §1 documents the 3-attempt bound as the single, practically unreachable error path; data-model.md now cites the correct 001 files).

**Coverage Summary Table:** unchanged from pass 2 — all 6 FR and 5 SC have ≥1 task (100%).

**Constitution Alignment Issues:** C1 (accepted). Principles I-VI: no violations.

**Unmapped Tasks:** T001 (setup), T009 (README) — acceptable.

**Metrics:**

- Total Requirements: 11
- Total Tasks: 11
- Coverage %: 100%
- Ambiguity Count: 0
- Duplication Count: 0
- Critical Issues Count: 0

**Next Actions:** Proceed to `/speckit-implement`.

### Analyze summary across passes

| Pass | CRITICAL | HIGH | MEDIUM | LOW | Outcome |
|------|----------|------|--------|-----|---------|
| 1 | 0 | 0 | 5 (C1, I1, I2, I3, U1) | 3 (A1, D1, G1) | C1 accepted; 7 fixed |
| 2 | 0 | 0 | 1 (C1, accepted) | 2 (I4, L1) | 2 fixed |
| 3 | 0 | 0 | 1 (C1, accepted) | 0 | Done: only an accepted finding remains |

Extension hooks (after_analyze): `.specify/extensions.yml` absent — skipped.

End: 2026-10-24T12:41:04Z
