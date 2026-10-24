# Step 04 — analyze (forward-r3)

Start: 2026-10-24T12:38:38Z

## Pass 1

### Commands

```console
$ .specify/scripts/bash/check-prerequisites.sh --json --require-spec --require-tasks --include-tasks
{"FEATURE_DIR":"/home/claude/runs/forward-r3/specs/002-idempotent-duplicate-save","AVAILABLE_DOCS":["research.md","data-model.md","contracts/","quickstart.md","tasks.md"]}
[exit 0]
```

```console
$ cat .specify/feature.json; ls .specify/extensions.yml
{
  "feature_directory": "specs/002-idempotent-duplicate-save"
}
ls: cannot access '.specify/extensions.yml': No such file or directory
[exit 2]
```

```console
$ grep -n "FR-0\|SC-0" specs/002-idempotent-duplicate-save/spec.md specs/002-idempotent-duplicate-save/plan.md specs/002-idempotent-duplicate-save/tasks.md
specs/002-idempotent-duplicate-save/spec.md:9:**Input**: User description: "Saving a link that is already bookmarked must no longer be rejected. If the link (after the existing normalization rules) is already saved, return the existing bookmark unchanged with HTTP 200 OK instead of the current 409 conflict. The title and tags sent in the new request are ignored; the stored bookmark is not modified. Saving a new link still returns 201 Created. Two concurrent saves of the same new link must still store only one bookmark (one gets 201, the other gets 200 with the same bookmark). This replaces the duplicate rule in FR-004 of specs/001-bookmarks-api."
specs/002-idempotent-duplicate-save/spec.md:15:- **Supersedes**: the duplicate rule in **FR-004** of `specs/001-bookmarks-api` — the sentence "A
specs/002-idempotent-duplicate-save/spec.md:19:  are replaced by FR-001 to FR-003 below.
specs/002-idempotent-duplicate-save/spec.md:20:- **Unchanged from 001**: the rest of FR-004 still applies — the system MUST NOT store two
specs/002-idempotent-duplicate-save/spec.md:24:  requirements (FR-001 to FR-003 and FR-005 to FR-011) are unchanged.
specs/002-idempotent-duplicate-save/spec.md:98:- **FR-001**: When a user saves a link whose normalized form matches an existing bookmark (using
specs/002-idempotent-duplicate-save/spec.md:99:  the normalization rules of 001 FR-004), the system MUST return the existing bookmark with a
specs/002-idempotent-duplicate-save/spec.md:101:  FR-004 of `specs/001-bookmarks-api`.
specs/002-idempotent-duplicate-save/spec.md:102:- **FR-002**: On such a duplicate save the system MUST ignore the title and tags sent in the
specs/002-idempotent-duplicate-save/spec.md:105:- **FR-003**: Saving a link that is not already bookmarked MUST continue to store a new bookmark
specs/002-idempotent-duplicate-save/spec.md:107:- **FR-004**: The system MUST continue to store at most one bookmark per normalized link, even when
specs/002-idempotent-duplicate-save/spec.md:110:- **FR-005**: Request validation (link, title and tag rules of 001 FR-002 and FR-011) MUST still be
specs/002-idempotent-duplicate-save/spec.md:112:- **FR-006**: The published API description MUST document both success outcomes of a save (201 for
specs/002-idempotent-duplicate-save/spec.md:125:- **SC-001**: Saving the same link any number of times, in any of its equivalent forms, always
specs/002-idempotent-duplicate-save/spec.md:127:- **SC-002**: In 100% of tested duplicate saves the returned bookmark is identical to the stored
specs/002-idempotent-duplicate-save/spec.md:129:- **SC-003**: In 100% of tested concurrent double saves of a new link, exactly one bookmark is
specs/002-idempotent-duplicate-save/spec.md:131:- **SC-004**: No save request for a valid link returns a conflict error.
specs/002-idempotent-duplicate-save/spec.md:132:- **SC-005**: Every acceptance scenario above is covered by an automated test that passes, and the
specs/002-idempotent-duplicate-save/plan.md:13:[specs/001-bookmarks-api](../001-bookmarks-api/spec.md) FR-004 (superseded here). A new link still
specs/002-idempotent-duplicate-save/plan.md:43:before the duplicate check (spec FR-005)
specs/002-idempotent-duplicate-save/tasks.md:13:(SC-005) and the constitution requires tests to ship with every feature (Principle V) against the
specs/002-idempotent-duplicate-save/tasks.md:18:**Supersedes**: the duplicate rule in FR-004 of [specs/001-bookmarks-api](../001-bookmarks-api/spec.md)
specs/002-idempotent-duplicate-save/tasks.md:54:the existing bookmark, unchanged; a new link still returns 201 Created (spec FR-001, FR-002,
specs/002-idempotent-duplicate-save/tasks.md:55:FR-003, FR-005, FR-006).
specs/002-idempotent-duplicate-save/tasks.md:64:- [ ] T002 [US1] In `tests/integration/test_create_bookmark.py`, replace `test_equivalent_link_is_rejected_as_duplicate` with `test_equivalent_link_returns_existing_bookmark`: save `https://example.com/docs` with title "Docs" and tags `["python"]`, then save `HTTPS://Example.com/docs/#intro` with title "Other" and tags `["misc"]`; assert the second response is 200 and its JSON equals the first response's JSON (same `id`, `url` "https://example.com/docs", `title` "Docs", `tags` `["python"]`, `created_at`), and `row_count() == 1` (spec US1 scenario 1, FR-001, FR-002)
specs/002-idempotent-duplicate-save/tasks.md:65:- [ ] T003 [US1] In `tests/integration/test_create_bookmark.py`, replace `test_duplicate_leaves_the_existing_bookmark_unchanged` with a test that saves `https://example.com/docs` (title "Docs", tags `["python"]`), re-saves the identical payload and then `https://example.com/docs/` with title "Changed" and tags `["other"]`; assert both re-saves return 200 with the original bookmark, and the stored row's `title`, `tags` and `created_at` (read with `engine`) are unchanged (spec US1 scenario 2, FR-002, Edge Cases "never changes the stored bookmark")
specs/002-idempotent-duplicate-save/tasks.md:66:- [ ] T004 [US1] In `tests/integration/test_create_bookmark.py`, add `test_different_query_string_is_a_new_bookmark`: save `https://example.com/docs?a=1`, then `https://example.com/docs?a=2`; assert the second returns 201 with a different `id` and `row_count() == 2` (spec US1 scenario 4, FR-003). Scenario 3 (new link → 201) stays covered by the existing `test_save_with_title_and_no_tags`
specs/002-idempotent-duplicate-save/tasks.md:67:- [ ] T005 [US1] In `tests/integration/test_create_bookmark.py`, add `test_invalid_duplicate_save_is_still_rejected`: save `https://example.com/docs`, then save the same link with title `"t" * 201` and, separately, with tags `["no spaces"]`; assert each returns 422 `validation_error` and the stored row is unchanged (spec FR-005, Edge Cases first bullet)
specs/002-idempotent-duplicate-save/tasks.md:68:- [ ] T006 [P] [US1] In `tests/integration/test_errors.py`, delete `test_duplicate_error_envelope`, and change `test_openapi_documents_every_operation` so the `post` error codes are `{"422"}`, it asserts `"409" not in operation["responses"]` for `post`, and it asserts both `responses["201"]` and `responses["200"]` reference `/Bookmark` (spec FR-006, contracts/openapi.yaml)
specs/002-idempotent-duplicate-save/tasks.md:83:201, the other 200, both with the same bookmark (spec FR-004).
specs/002-idempotent-duplicate-save/tasks.md:90:- [ ] T010 [US2] In `tests/integration/test_create_bookmark.py`, update `test_concurrent_saves_of_the_same_link_leave_one_bookmark` to collect each response (status and JSON), and assert `sorted(statuses) == [200, 201]`, both JSON bodies have the same `id`, and `row_count() == 1` (spec US2 scenario 1, FR-004, SC-003)
[exit 0]
```

### Analyze report — pass 1 (verbatim)

## Specification Analysis Report

Feature: `specs/002-idempotent-duplicate-save` (active feature from `.specify/feature.json`). Artifacts: spec.md, plan.md, tasks.md; constitution v1.1.0.

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| C1 | Coverage Gap | MEDIUM | tasks.md T007; research.md "Row deleted between the conflict and the lookup" | T007 introduces a retry loop for the case where the conflicting bookmark is deleted between the insert attempt and the lookup, but no task tests it. Constitution V requires tests for the behavior a feature ships, including error paths. | Add a test task that forces the interleaving against the real database (delete the row through a separate connection between the conflict and the lookup) and asserts the save becomes a new bookmark (201); have T007 factor the lookup into a helper the test can wrap. |
| A1 | Ambiguity | MEDIUM | spec.md L15-24, L98-112 | Requirement IDs collide across specs: the "Relationship" section refers to 001's FR-001..FR-011 with bare IDs ("FR-001 to FR-003 and FR-005 to FR-011 are unchanged", "the rest of FR-004 still applies") while this spec defines its own FR-001..FR-006. A reader cannot tell which "FR-004" is meant without context. | Prefix every reference to the earlier spec's requirements with "001" (e.g. "001 FR-004") and refer to this spec's own requirements unprefixed. |
| I3 | Inconsistency | MEDIUM | specs/001-bookmarks-api/spec.md (FR-004, US1 scenario 3, Edge Cases bullet 1, Clarifications Q1), specs/001-bookmarks-api/contracts/openapi.yaml (`'409'`, `duplicate_url`), specs/001-bookmarks-api/quickstart.md step 2, specs/001-bookmarks-api/tasks.md T008/T012/T015/T016 | The earlier feature's artifacts still describe the 409 duplicate rule that this feature replaces; two contracts now describe `POST /bookmarks` differently. | Cannot be remediated in this feature: 001 is a finished, immutable historical record (flow-forward). 002 already cross-links and states what it supersedes (spec "Relationship to Earlier Specifications", contract description). Record as accepted. |
| C2 | Coverage Gap | LOW | spec.md Edge Cases bullet 4; tasks.md T003 | Edge case "a duplicate save does not move the existing bookmark in the newest-first list" is only covered indirectly (T003 checks `created_at` unchanged); no list-order assertion. | Extend T003 to save a second, newer bookmark before the duplicate save and assert `GET /bookmarks` order is unchanged afterwards. |
| I1 | Inconsistency | LOW | plan.md Constitution Check row V; tasks.md T006 | Plan says "old 409 assertions are replaced, not deleted silently", but T006 deletes `test_duplicate_error_envelope` outright (its coverage moves to T002/T006's OpenAPI assertion). | Reword plan row V: old 409 assertions are replaced by 200 assertions, and the duplicate-envelope test is removed explicitly because the error no longer exists. |
| I2 | Inconsistency | LOW | spec.md L15-19 | "Supersedes" says the 001 rule and its restatements "are replaced by FR-001 to FR-003 below", but FR-004 (concurrency outcome 201/200 instead of 201/409) and FR-006 (contract) also replace 001 behavior. | Say "replaced by FR-001 to FR-006 below" (or list FR-001, FR-002, FR-004, FR-006). |
| U1 | Underspecification | LOW | tasks.md T011, T014 | T011 is a verification step filed under "Implementation for User Story 2"; T014 allows "or confirm each is covered by an automated test", leaving the done-criterion open. | Rename T011's subsection to "Verification for User Story 2"; make T014 run the quickstart manual steps against a running API and record results. |

**Coverage Summary Table:**

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|
| FR-001 duplicate-save-returns-existing-200 | Yes | T002, T003, T007, T008 | |
| FR-002 ignore-title-tags-no-modification | Yes | T002, T003, T007 | |
| FR-003 new-link-201 | Yes | T004, T008 | Scenario 3 via existing test |
| FR-004 one-bookmark-under-concurrency | Yes | T010, T011, T007 | |
| FR-005 validation-still-applies | Yes | T005 | |
| FR-006 contract-documents-200-201-no-409 | Yes | T006, T008, T009 | |
| SC-001 | Yes | T002, T003 | |
| SC-002 | Yes | T002, T003 | |
| SC-003 | Yes | T010, T011 | |
| SC-004 | Yes | T002, T006 | |
| SC-005 | Yes | T013 | |

**Constitution Alignment Issues:** None. (Principle III mentions 409 as an allowed error class; it does not require one. Principle V gap on the retry path is logged as C1.)

**Unmapped Tasks:** T001 (baseline check, setup), T012 (README; documentation supporting FR-006).

**Metrics:**

- Total Requirements: 11 (6 FR + 5 SC)
- Total Tasks: 14
- Coverage %: 100% (11/11 requirements with >=1 task)
- Ambiguity Count: 1
- Duplication Count: 0
- Critical Issues Count: 0

Findings by severity: CRITICAL 0, HIGH 0, MEDIUM 3, LOW 4.

**Next Actions**

- No CRITICAL issues; implementation may proceed, but address C1 and A1 first (MEDIUM).
- Manually edit tasks.md to add a retry-path test task (C1) and extend T003 (C2); edit spec.md to prefix 001 requirement references (A1, I2); edit plan.md row V (I1); edit tasks.md T011/T014 (U1).
- I3 cannot be fixed without editing specs/001-bookmarks-api, which flow-forward forbids; accept it.

Would you like me to suggest concrete remediation edits for the top 7 issues?

(after_analyze hooks: `.specify/extensions.yml` does not exist — skipped.)

### Remediation decision (pass 1)

Per the run rules, remediation is accepted and applied by the build-runner to the new folder's artifacts only:

- C1 → tasks.md: new task T006 (retry-path test against the real database); T007→T008 reworded to factor `_find_existing`; later tasks renumbered (old T006→T007 … old T014→T015) and cross-references updated.
- A1, I2 → spec.md "Relationship to Earlier Specifications" and FR-001/FR-005: every reference to 001's requirements prefixed "001 FR-…"; superseded content "replaced by FR-001 to FR-006 below".
- C2 → tasks.md T003 extended with list-order assertion.
- I1 → plan.md Constitution Check row V reworded.
- U1 → tasks.md: US2 verification subsection renamed; quickstart task made concrete.
- I3 → accepted (001 immutable under flow-forward); no edit.

### Remediation diff applied after pass 1

```console
$ git diff --stat; git diff -- specs/002-idempotent-duplicate-save/
 specs/002-idempotent-duplicate-save/plan.md  |  2 +-
 specs/002-idempotent-duplicate-save/spec.md  | 18 ++++++------
 specs/002-idempotent-duplicate-save/tasks.md | 42 +++++++++++++++-------------
 3 files changed, 33 insertions(+), 29 deletions(-)
diff --git a/specs/002-idempotent-duplicate-save/plan.md b/specs/002-idempotent-duplicate-save/plan.md
index a40fa98..4cb0cfb 100644
--- a/specs/002-idempotent-duplicate-save/plan.md
+++ b/specs/002-idempotent-duplicate-save/plan.md
@@ -55,7 +55,7 @@ before the duplicate check (spec FR-005)
 | II. Real-Database Testing | New and changed tests run against `bookmarks_test`; the concurrency test uses two real connections racing on the real unique index | Pass |
 | III. Consistent Error Shape | Fewer error cases: the duplicate case is no longer an error. Remaining errors (422, 404, 405, 500) keep the envelope. The principle's mention of 409 lists an allowed class, it does not require one to exist | Pass |
 | IV. Minimal Dependencies | No new dependencies | Pass |
-| V. Tests Ship With Every Feature | Every acceptance scenario of spec US1 and US2 maps to a test in the same change; old 409 assertions are replaced, not deleted silently | Pass |
+| V. Tests Ship With Every Feature | Every acceptance scenario of spec US1 and US2 maps to a test in the same change; old 409 assertions in the create and concurrency tests are replaced by 200 assertions, and the duplicate-envelope test in `test_errors.py` is removed explicitly because that error no longer exists; the retry path for a bookmark deleted mid-save gets its own real-database test | Pass |
 | VI. Cursor Pagination | No list endpoint changes; a duplicate save does not change `created_at`, so keyset positions are unaffected | Pass |
 
 Post-design re-check (after Phase 1): Pass. The contract adds a 200 response using the existing
diff --git a/specs/002-idempotent-duplicate-save/spec.md b/specs/002-idempotent-duplicate-save/spec.md
index d15eb86..7a1e6b6 100644
--- a/specs/002-idempotent-duplicate-save/spec.md
+++ b/specs/002-idempotent-duplicate-save/spec.md
@@ -12,16 +12,18 @@
 
 - **Builds on**: [specs/001-bookmarks-api](../001-bookmarks-api/spec.md) (Bookmarks API). That
   feature directory is a finished historical record and is not edited.
-- **Supersedes**: the duplicate rule in **FR-004** of `specs/001-bookmarks-api` — the sentence "A
-  save of an existing link MUST be rejected with a conflict error that includes the existing
-  bookmark's identifier" — together with the parts of 001 that restate it (User Story 1 acceptance
-  scenario 3, the first Edge Case bullet, and the first Clarification of Session 2026-10-21). Those
-  are replaced by FR-001 to FR-003 below.
-- **Unchanged from 001**: the rest of FR-004 still applies — the system MUST NOT store two
+- **Supersedes**: the duplicate rule in **001 FR-004** of `specs/001-bookmarks-api` — the sentence
+  "A save of an existing link MUST be rejected with a conflict error that includes the existing
+  bookmark's identifier" — together with the parts of 001 that restate it (001 User Story 1
+  acceptance scenario 3, 001's first Edge Case bullet, and 001's first Clarification of Session
+  2026-10-21). Those are replaced by FR-001 to FR-006 below.
+- **Unchanged from 001**: the rest of 001 FR-004 still applies — the system MUST NOT store two
   bookmarks for the same link, links are compared after the existing normalization rules (scheme
   and host lowercased, default port removed, trailing path slash removed, fragment removed, query
   kept), and the guarantee holds when two saves happen at the same moment. All other 001
-  requirements (FR-001 to FR-003 and FR-005 to FR-011) are unchanged.
+  requirements (001 FR-001 to 001 FR-003 and 001 FR-005 to 001 FR-011) are unchanged.
+- **Requirement IDs**: in this spec, "001 FR-###" always means a requirement of
+  `specs/001-bookmarks-api`; an unprefixed "FR-###" means a requirement of this spec.
 
 ## User Scenarios & Testing *(mandatory)*
 
@@ -98,7 +100,7 @@ bookmark is stored.
 - **FR-001**: When a user saves a link whose normalized form matches an existing bookmark (using
   the normalization rules of 001 FR-004), the system MUST return the existing bookmark with a
   200 OK success response instead of rejecting the save. This supersedes the duplicate rule in
-  FR-004 of `specs/001-bookmarks-api`.
+  001 FR-004 of `specs/001-bookmarks-api`.
 - **FR-002**: On such a duplicate save the system MUST ignore the title and tags sent in the
   request and MUST NOT modify the stored bookmark in any way (identifier, link, title, tags and
   saved time stay the same).
diff --git a/specs/002-idempotent-duplicate-save/tasks.md b/specs/002-idempotent-duplicate-save/tasks.md
index a6ff091..ded574b 100644
--- a/specs/002-idempotent-duplicate-save/tasks.md
+++ b/specs/002-idempotent-duplicate-save/tasks.md
@@ -62,16 +62,17 @@ the second response is 200 with the first bookmark exactly as stored, and one ro
 > **NOTE: Write these tests FIRST, ensure they FAIL before implementation**
 
 - [ ] T002 [US1] In `tests/integration/test_create_bookmark.py`, replace `test_equivalent_link_is_rejected_as_duplicate` with `test_equivalent_link_returns_existing_bookmark`: save `https://example.com/docs` with title "Docs" and tags `["python"]`, then save `HTTPS://Example.com/docs/#intro` with title "Other" and tags `["misc"]`; assert the second response is 200 and its JSON equals the first response's JSON (same `id`, `url` "https://example.com/docs", `title` "Docs", `tags` `["python"]`, `created_at`), and `row_count() == 1` (spec US1 scenario 1, FR-001, FR-002)
-- [ ] T003 [US1] In `tests/integration/test_create_bookmark.py`, replace `test_duplicate_leaves_the_existing_bookmark_unchanged` with a test that saves `https://example.com/docs` (title "Docs", tags `["python"]`), re-saves the identical payload and then `https://example.com/docs/` with title "Changed" and tags `["other"]`; assert both re-saves return 200 with the original bookmark, and the stored row's `title`, `tags` and `created_at` (read with `engine`) are unchanged (spec US1 scenario 2, FR-002, Edge Cases "never changes the stored bookmark")
+- [ ] T003 [US1] In `tests/integration/test_create_bookmark.py`, replace `test_duplicate_leaves_the_existing_bookmark_unchanged` with a test that saves `https://example.com/docs` (title "Docs", tags `["python"]`), re-saves the identical payload and then `https://example.com/docs/` with title "Changed" and tags `["other"]`; assert both re-saves return 200 with the original bookmark, and the stored row's `title`, `tags` and `created_at` (read with `engine`) are unchanged; also save a second, newer bookmark `https://example.com/newer` before the re-saves and assert `GET /bookmarks` returns the same order (newer first, then docs) before and after them (spec US1 scenario 2, FR-002, Edge Cases "never changes the stored bookmark" and "does not move the existing bookmark")
 - [ ] T004 [US1] In `tests/integration/test_create_bookmark.py`, add `test_different_query_string_is_a_new_bookmark`: save `https://example.com/docs?a=1`, then `https://example.com/docs?a=2`; assert the second returns 201 with a different `id` and `row_count() == 2` (spec US1 scenario 4, FR-003). Scenario 3 (new link → 201) stays covered by the existing `test_save_with_title_and_no_tags`
 - [ ] T005 [US1] In `tests/integration/test_create_bookmark.py`, add `test_invalid_duplicate_save_is_still_rejected`: save `https://example.com/docs`, then save the same link with title `"t" * 201` and, separately, with tags `["no spaces"]`; assert each returns 422 `validation_error` and the stored row is unchanged (spec FR-005, Edge Cases first bullet)
-- [ ] T006 [P] [US1] In `tests/integration/test_errors.py`, delete `test_duplicate_error_envelope`, and change `test_openapi_documents_every_operation` so the `post` error codes are `{"422"}`, it asserts `"409" not in operation["responses"]` for `post`, and it asserts both `responses["201"]` and `responses["200"]` reference `/Bookmark` (spec FR-006, contracts/openapi.yaml)
+- [ ] T006 [US1] In `tests/integration/test_create_bookmark.py`, add `test_bookmark_deleted_mid_save_is_saved_as_new`: save `https://example.com/gone` (keep its `id`), then monkeypatch `repository._find_existing` with a wrapper that, on its first call only, deletes that row through a separate committed connection from the `engine` fixture and then calls the original; POST the same link again and assert 201, a new `id` different from the first, and `row_count() == 1`. The database stays real (Constitution II): only the timing of a real delete is forced (research.md, "Row deleted between the conflict and the lookup")
+- [ ] T007 [P] [US1] In `tests/integration/test_errors.py`, delete `test_duplicate_error_envelope`, and change `test_openapi_documents_every_operation` so the `post` error codes are `{"422"}`, it asserts `"409" not in operation["responses"]` for `post`, and it asserts both `responses["201"]` and `responses["200"]` reference `/Bookmark` (spec FR-006, contracts/openapi.yaml)
 
 ### Implementation for User Story 1
 
-- [ ] T007 [US1] In `src/bookmarks_api/repository.py`, change `create_bookmark(session, data)` to return `tuple[BookmarkRow, bool]` (row, created): keep `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`; on an inserted row commit and return `(row, True)`; when nothing is inserted roll back, `SELECT` the row by `url_normalized` and return `(row, False)` without writing; if that `SELECT` finds nothing (row deleted in between), retry the insert, at most 3 attempts in total, then raise `RuntimeError` (rendered as 500 `internal_error`). Remove the `DuplicateUrlError` import and update the docstring (research.md, "Returning the existing bookmark" and "Row deleted between the conflict and the lookup")
-- [ ] T008 [US1] In `src/bookmarks_api/routes.py`, change `create_bookmark` to accept `response: Response`, unpack `(row, created)` from the repository, set `response.status_code = status.HTTP_200_OK` when not created (default stays 201), and replace the route's `responses` with `{200: {"model": Bookmark, "description": "This link is already bookmarked; the existing bookmark is returned unchanged."}, **ERROR_422}` — no 409 entry (research.md, "Response status and contract"; Constitution I)
-- [ ] T009 [US1] In `src/bookmarks_api/errors.py`, delete the `DuplicateUrlError` class and its `handle_duplicate` 409 exception handler; keep the generic `409: "conflict"` entry in `STATUS_CODES` (research.md, "Removing the duplicate error")
+- [ ] T008 [US1] In `src/bookmarks_api/repository.py`, change `create_bookmark(session, data)` to return `tuple[BookmarkRow, bool]` (row, created): keep `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`; on an inserted row commit and return `(row, True)`; when nothing is inserted roll back, look the row up by `url_normalized` through a module-level helper `_find_existing(session, normalized) -> BookmarkRow | None` and return `(row, False)` without writing; if the helper finds nothing (row deleted in between), retry the insert, at most 3 attempts in total, then raise `RuntimeError` (rendered as 500 `internal_error`). Remove the `DuplicateUrlError` import and update the docstring (research.md, "Returning the existing bookmark" and "Row deleted between the conflict and the lookup")
+- [ ] T009 [US1] In `src/bookmarks_api/routes.py`, change `create_bookmark` to accept `response: Response`, unpack `(row, created)` from the repository, set `response.status_code = status.HTTP_200_OK` when not created (default stays 201), and replace the route's `responses` with `{200: {"model": Bookmark, "description": "This link is already bookmarked; the existing bookmark is returned unchanged."}, **ERROR_422}` — no 409 entry (research.md, "Response status and contract"; Constitution I)
+- [ ] T010 [US1] In `src/bookmarks_api/errors.py`, delete the `DuplicateUrlError` class and its `handle_duplicate` 409 exception handler; keep the generic `409: "conflict"` entry in `STATUS_CODES` (research.md, "Removing the duplicate error")
 
 **Checkpoint**: User Story 1 is fully functional and testable independently
 
@@ -87,11 +88,11 @@ are `[200, 201]`, both bodies have the same `id`, and one row exists.
 
 ### Tests for User Story 2
 
-- [ ] T010 [US2] In `tests/integration/test_create_bookmark.py`, update `test_concurrent_saves_of_the_same_link_leave_one_bookmark` to collect each response (status and JSON), and assert `sorted(statuses) == [200, 201]`, both JSON bodies have the same `id`, and `row_count() == 1` (spec US2 scenario 1, FR-004, SC-003)
+- [ ] T011 [US2] In `tests/integration/test_create_bookmark.py`, update `test_concurrent_saves_of_the_same_link_leave_one_bookmark` to collect each response (status and JSON), and assert `sorted(statuses) == [200, 201]`, both JSON bodies have the same `id`, and `row_count() == 1` (spec US2 scenario 1, FR-004, SC-003)
 
-### Implementation for User Story 2
+### Verification for User Story 2
 
-- [ ] T011 [US2] Confirm no further code is needed beyond T007/T008 (the unique index arbitrates the race, research.md): run the concurrency test in `tests/integration/test_create_bookmark.py` 20 times in a shell loop (`for i in $(seq 20); do uv run --python 3.13 pytest -q -k concurrent tests/integration/test_create_bookmark.py || break; done`) and confirm every run passes
+- [ ] T012 [US2] Confirm no further code is needed beyond T008/T009 (the unique index arbitrates the race, research.md): run the concurrency test in `tests/integration/test_create_bookmark.py` 20 times in a shell loop (`for i in $(seq 20); do uv run --python 3.13 pytest -q -k concurrent tests/integration/test_create_bookmark.py || break; done`) and confirm every run passes
 
 **Checkpoint**: User Stories 1 and 2 both work independently
 
@@ -101,9 +102,9 @@ are `[200, 201]`, both bodies have the same `id`, and one row exists.
 
 **Purpose**: Documentation and full validation
 
-- [ ] T012 [P] In `README.md`, change the endpoint table row for `POST /bookmarks` from "409 if the link is already saved" to "201 for a new link; 200 with the existing bookmark, unchanged, if the link is already saved"
-- [ ] T013 Run the full suite on Python 3.11, 3.12 and 3.13 (`uv run --python 3.1X pytest -q` with `.env` loaded) over `tests/` and confirm all pass (Constitution quality gate)
-- [ ] T014 Run the manual checks in `specs/002-idempotent-duplicate-save/quickstart.md` (steps 1-5) against a locally started API, or confirm each is covered by an automated test
+- [ ] T013 [P] In `README.md`, change the endpoint table row for `POST /bookmarks` from "409 if the link is already saved" to "201 for a new link; 200 with the existing bookmark, unchanged, if the link is already saved"
+- [ ] T014 Run the full suite on Python 3.11, 3.12 and 3.13 (`uv run --python 3.1X pytest -q` with `.env` loaded) over `tests/` and confirm all pass (Constitution quality gate)
+- [ ] T015 Run the manual checks in `specs/002-idempotent-duplicate-save/quickstart.md` (steps 1-5) against a locally started API (`uv run uvicorn bookmarks_api.main:app` with `DATABASE_URL` pointing at the test database) and record each step's actual status and body against the expected column
 
 ---
 
@@ -114,24 +115,25 @@ are `[200, 201]`, both bodies have the same `id`, and one row exists.
 - **Setup (Phase 1)**: No dependencies - start immediately
 - **Foundational (Phase 2)**: Empty
 - **User Story 1 (Phase 3)**: After Setup
-- **User Story 2 (Phase 4)**: T010 can be written after Setup; T011 depends on T007 and T008
+- **User Story 2 (Phase 4)**: T011 can be written after Setup; T012 depends on T008 and T009
 - **Polish (Phase 5)**: After US1 and US2
 
 ### User Story Dependencies
 
 - **User Story 1 (P1)**: No dependencies on other stories
-- **User Story 2 (P2)**: Uses the US1 repository/route change (T007, T008); its test is independent
+- **User Story 2 (P2)**: Uses the US1 repository/route change (T008, T009); its test is independent
 
 ### Within Each User Story
 
-- Tests (T002-T006, T010) MUST be written and FAIL before implementation
-- T007 (repository) before T008 (route); T009 after T007 removes the last import of `DuplicateUrlError`
-- T002-T005 and T010 edit the same file, so they run sequentially
+- Tests (T002-T007, T011) MUST be written and FAIL before implementation
+- T008 (repository) before T009 (route); T010 after T008 removes the last import of `DuplicateUrlError`
+- T006 wraps the `_find_existing` helper that T008 introduces, so it fails until T008 is done
+- T002-T006 and T011 edit the same file, so they run sequentially
 
 ### Parallel Opportunities
 
-- T006 (`tests/integration/test_errors.py`) can run in parallel with T002-T005 (`tests/integration/test_create_bookmark.py`)
-- T012 (`README.md`) can run in parallel with any implementation task
+- T007 (`tests/integration/test_errors.py`) can run in parallel with T002-T006 (`tests/integration/test_create_bookmark.py`)
+- T013 (`README.md`) can run in parallel with any implementation task
 
 ---
 
@@ -139,8 +141,8 @@ are `[200, 201]`, both bodies have the same `id`, and one row exists.
 
 ```bash
 # Different files, no dependencies between them:
-Task: "T002-T005 duplicate-save tests in tests/integration/test_create_bookmark.py"
-Task: "T006 OpenAPI/envelope test changes in tests/integration/test_errors.py"
+Task: "T002-T006 duplicate-save tests in tests/integration/test_create_bookmark.py"
+Task: "T007 OpenAPI/envelope test changes in tests/integration/test_errors.py"
 ```
 
 ---
[exit 0]
```

## Pass 2

### Commands

```console
$ .specify/scripts/bash/check-prerequisites.sh --json --require-spec --require-tasks --include-tasks
{"FEATURE_DIR":"/home/claude/runs/forward-r3/specs/002-idempotent-duplicate-save","AVAILABLE_DOCS":["research.md","data-model.md","contracts/","quickstart.md","tasks.md"]}
[exit 0]
```

```console
$ grep -cE "^- \[ \] T[0-9]{3}" specs/002-idempotent-duplicate-save/tasks.md; grep -n "FR-0" specs/002-idempotent-duplicate-save/spec.md | sed -n 1,12p; git diff --quiet ep03-start -- specs/001-bookmarks-api && echo "001 untouched"
15
9:**Input**: User description: "Saving a link that is already bookmarked must no longer be rejected. If the link (after the existing normalization rules) is already saved, return the existing bookmark unchanged with HTTP 200 OK instead of the current 409 conflict. The title and tags sent in the new request are ignored; the stored bookmark is not modified. Saving a new link still returns 201 Created. Two concurrent saves of the same new link must still store only one bookmark (one gets 201, the other gets 200 with the same bookmark). This replaces the duplicate rule in FR-004 of specs/001-bookmarks-api."
15:- **Supersedes**: the duplicate rule in **001 FR-004** of `specs/001-bookmarks-api` — the sentence
19:  2026-10-21). Those are replaced by FR-001 to FR-006 below.
20:- **Unchanged from 001**: the rest of 001 FR-004 still applies — the system MUST NOT store two
24:  requirements (001 FR-001 to 001 FR-003 and 001 FR-005 to 001 FR-011) are unchanged.
100:- **FR-001**: When a user saves a link whose normalized form matches an existing bookmark (using
101:  the normalization rules of 001 FR-004), the system MUST return the existing bookmark with a
103:  001 FR-004 of `specs/001-bookmarks-api`.
104:- **FR-002**: On such a duplicate save the system MUST ignore the title and tags sent in the
107:- **FR-003**: Saving a link that is not already bookmarked MUST continue to store a new bookmark
109:- **FR-004**: The system MUST continue to store at most one bookmark per normalized link, even when
112:- **FR-005**: Request validation (link, title and tag rules of 001 FR-002 and FR-011) MUST still be
001 untouched
[exit 0]
```

### Analyze report — pass 2 (verbatim)

## Specification Analysis Report

Feature: `specs/002-idempotent-duplicate-save`. Re-run after pass-1 remediation.

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| A2 | Ambiguity | LOW | spec.md L112 (FR-005) | Residual instance of A1: "link, title and tag rules of 001 FR-002 and FR-011" — the second ID is unprefixed, which under the spec's own "Requirement IDs" convention would mean this spec's FR-011 (which does not exist). | Change to "001 FR-002 and 001 FR-011". |
| I3 | Inconsistency | MEDIUM (accepted) | specs/001-bookmarks-api/spec.md FR-004, US1 scenario 3, Edge Cases bullet 1, Clarifications Q1; specs/001-bookmarks-api/contracts/openapi.yaml `'409'`/`duplicate_url`; specs/001-bookmarks-api/quickstart.md step 2; specs/001-bookmarks-api/tasks.md T008/T012/T015/T016 | Unchanged from pass 1: the earlier feature's artifacts still describe the 409 rule. | Accepted: 001 is immutable under flow-forward; 002 cross-links and states what it supersedes. |

Pass-1 findings C1, A1, C2, I1, I2, U1: resolved (verified: T006 adds the real-database retry-path test and T008 introduces `_find_existing`; spec references prefixed "001 FR-…" except A2; T003 asserts list order; plan row V reworded; "replaced by FR-001 to FR-006"; T012 under "Verification", T015 concrete).

**Coverage Summary Table:**

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|
| FR-001 duplicate-save-returns-existing-200 | Yes | T002, T003, T008, T009 | |
| FR-002 ignore-title-tags-no-modification | Yes | T002, T003, T008 | |
| FR-003 new-link-201 | Yes | T004, T006, T009 | |
| FR-004 one-bookmark-under-concurrency | Yes | T011, T012, T008 | |
| FR-005 validation-still-applies | Yes | T005 | |
| FR-006 contract-documents-200-201-no-409 | Yes | T007, T009, T010 | |
| SC-001 | Yes | T002, T003 | |
| SC-002 | Yes | T002, T003 | |
| SC-003 | Yes | T011, T012 | |
| SC-004 | Yes | T002, T007 | |
| SC-005 | Yes | T014 | |

**Constitution Alignment Issues:** None.

**Unmapped Tasks:** T001 (baseline check, setup), T013 (README; documentation supporting FR-006), T015 (quickstart validation).

**Metrics:**

- Total Requirements: 11 (6 FR + 5 SC)
- Total Tasks: 15
- Coverage %: 100%
- Ambiguity Count: 1
- Duplication Count: 0
- Critical Issues Count: 0

Findings by severity: CRITICAL 0, HIGH 0, MEDIUM 1 (accepted), LOW 1.

**Next Actions**

- No CRITICAL issues; safe to proceed to `/speckit-implement` after the one-word fix for A2.
- I3 remains accepted.

Would you like me to suggest concrete remediation edits for the top 1 issue?

(after_analyze hooks: `.specify/extensions.yml` does not exist — skipped.)

### Remediation decision (pass 2)

- A2 → spec.md FR-005: "001 FR-002 and FR-011" → "001 FR-002 and 001 FR-011". Applied.
- I3 → accepted, no edit.

### Remediation diff applied after pass 2

```console
$ git diff -- specs/002-idempotent-duplicate-save/spec.md | tail -8
 - **FR-004**: The system MUST continue to store at most one bookmark per normalized link, even when
   saves of the same new link happen at the same moment; in that case exactly one save MUST receive
   201 Created and every other MUST receive 200 OK with the same bookmark.
-- **FR-005**: Request validation (link, title and tag rules of 001 FR-002 and FR-011) MUST still be
+- **FR-005**: Request validation (link, title and tag rules of 001 FR-002 and 001 FR-011) MUST still be
   applied to every save, including a save of a link that is already bookmarked.
 - **FR-006**: The published API description MUST document both success outcomes of a save (201 for
   a new bookmark, 200 for an existing one) and MUST no longer list a conflict error for the save
[exit 0]
```

## Pass 3

### Commands

```console
$ .specify/scripts/bash/check-prerequisites.sh --json --require-spec --require-tasks --include-tasks
{"FEATURE_DIR":"/home/claude/runs/forward-r3/specs/002-idempotent-duplicate-save","AVAILABLE_DOCS":["research.md","data-model.md","contracts/","quickstart.md","tasks.md"]}
[exit 0]
```

```console
$ grep -nE "(^|[^0-9] )FR-0[0-9]{2}" specs/002-idempotent-duplicate-save/spec.md | grep -v "001 FR-" ; echo "---"; grep -n "001 FR-0[0-9]* and FR\|and FR-01" specs/002-idempotent-duplicate-save/spec.md; echo "bare refs to 001-only IDs (FR-007..FR-011) without prefix:"; grep -nE "(^|[^1] )FR-0(0[7-9]|1[01])" specs/002-idempotent-duplicate-save/spec.md || echo none
9:**Input**: User description: "Saving a link that is already bookmarked must no longer be rejected. If the link (after the existing normalization rules) is already saved, return the existing bookmark unchanged with HTTP 200 OK instead of the current 409 conflict. The title and tags sent in the new request are ignored; the stored bookmark is not modified. Saving a new link still returns 201 Created. Two concurrent saves of the same new link must still store only one bookmark (one gets 201, the other gets 200 with the same bookmark). This replaces the duplicate rule in FR-004 of specs/001-bookmarks-api."
19:  2026-10-21). Those are replaced by FR-001 to FR-006 below.
---
bare refs to 001-only IDs (FR-007..FR-011) without prefix:
none
[exit 0]
```

### Analyze report — pass 3 (verbatim)

## Specification Analysis Report

Feature: `specs/002-idempotent-duplicate-save`. Re-run after pass-2 remediation.

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| I3 | Inconsistency | MEDIUM (accepted) | specs/001-bookmarks-api/spec.md FR-004, US1 scenario 3, Edge Cases bullet 1, Clarifications Q1; specs/001-bookmarks-api/contracts/openapi.yaml; specs/001-bookmarks-api/quickstart.md step 2; specs/001-bookmarks-api/tasks.md | The earlier feature's artifacts still describe the 409 duplicate rule. | Accepted: 001 is immutable under flow-forward; 002 cross-links and states what it supersedes. |

A2 resolved (FR-005 now reads "001 FR-002 and 001 FR-011"). The only remaining unprefixed "FR-004 of specs/001-bookmarks-api" is inside the verbatim **Input** line (the user's own words), which is not edited. No new findings in spec.md, plan.md or tasks.md.

**Coverage Summary Table:** unchanged from pass 2 — 11/11 requirements covered (FR-001..FR-006, SC-001..SC-005).

**Constitution Alignment Issues:** None.

**Unmapped Tasks:** T001 (setup), T013 (README), T015 (quickstart validation) — supporting tasks, not gaps.

**Metrics:**

- Total Requirements: 11
- Total Tasks: 15
- Coverage %: 100%
- Ambiguity Count: 0
- Duplication Count: 0
- Critical Issues Count: 0

Findings by severity: CRITICAL 0, HIGH 0, MEDIUM 1 (accepted: I3), LOW 0.

**Next Actions**

- Ready for `/speckit-implement`.

(after_analyze hooks: `.specify/extensions.yml` does not exist — skipped.)

## Analyze summary across passes

| Pass | CRITICAL | HIGH | MEDIUM | LOW | Outcome |
|------|----------|------|--------|-----|---------|
| 1 | 0 | 0 | 3 (C1, A1, I3) | 4 (C2, I1, I2, U1) | 6 remediated in 002 artifacts; I3 accepted |
| 2 | 0 | 0 | 1 (I3 accepted) | 1 (A2) | A2 remediated |
| 3 | 0 | 0 | 1 (I3 accepted) | 0 | Stop: only accepted finding remains |

Accepted finding recorded: **I3** — specs/001-bookmarks-api still states the 409 duplicate rule (spec, contract, quickstart, tasks); flow-forward forbids editing 001.
End: 2026-10-24T12:40:35Z
