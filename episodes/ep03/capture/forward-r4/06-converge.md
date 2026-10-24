# Step 06 — converge (forward-r4)

Start: 2026-10-24T12:44:13Z

## Round 1 — converge

```console
$ ls .specify/extensions.yml 2>&1; .specify/scripts/bash/check-prerequisites.sh --json --require-spec --require-tasks --include-tasks
ls: cannot access '.specify/extensions.yml': No such file or directory
{"FEATURE_DIR":"/home/claude/runs/forward-r4/specs/002-idempotent-duplicate-save","AVAILABLE_DOCS":["research.md","data-model.md","contracts/","quickstart.md","tasks.md"]}
[exit 0]
```

```console
$ grep -n "^## Phase\|^- \[.\] T" specs/002-idempotent-duplicate-save/tasks.md | cut -c1-90
32:## Phase 1: Setup (Shared Infrastructure)
36:- [X] T001 Run the existing suite (`set -a; . ./.env; set +a; uv run --python 3.13 pyte
40:## Phase 2: Foundational (Blocking Prerequisites)
44:- [X] T002 Change `create_bookmark(session, data)` in `src/bookmarks_api/repository.py`
50:## Phase 3: User Story 1 - Saving an already-bookmarked link returns the existing bookm
63:- [X] T003 [P] [US1] In `tests/integration/test_create_bookmark.py`, replace `test_equi
64:- [X] T004 [P] [US1] In `tests/integration/test_errors.py`, remove `test_duplicate_erro
68:- [X] T005 [US1] Update `POST /bookmarks` in `src/bookmarks_api/routes.py`: keep `statu
69:- [X] T006 [US1] Remove `DuplicateUrlError` and its `handle_duplicate` 409 handler from
75:## Phase 4: User Story 2 - Concurrent saves of the same new link still store one bookma
85:- [X] T007 [US2] In `tests/integration/test_create_bookmark.py`, update `test_concurren
89:- [X] T008 [US2] Confirm `create_bookmark` in `src/bookmarks_api/repository.py` (T002) 
95:## Phase 5: Polish & Cross-Cutting Concerns
99:- [X] T009 [P] Update the endpoint table in `README.md`: `POST /bookmarks` row reads "S
100:- [X] T010 Search `src/` and `tests/` for leftover `DuplicateUrlError`, `duplicate_url
101:- [X] T011 Run the full suite on Python 3.11, 3.12 and 3.13 (`uv run --python 3.1X pyt
[exit 0]
```

```console
$ grep -n "def test_\|invalid-tag\|no spaces\|tags\"\] ==\|items\"\]" tests/integration/test_create_bookmark.py | head -40; grep -n "\"\"\"" -A2 src/bookmarks_api/routes.py | sed -n 1,20p
10:def test_save_with_title_and_no_tags(client: TestClient, row_count) -> None:
17:    assert body["tags"] == []
23:def test_tags_are_trimmed_lowercased_and_deduplicated(client: TestClient) -> None:
30:    assert response.json()["tags"] == ["api", "python"]
33:def test_link_is_stored_as_given(client: TestClient) -> None:
40:def test_equivalent_link_returns_the_existing_bookmark(client: TestClient, row_count) -> None:
55:def test_duplicate_ignores_title_and_tags_and_leaves_the_bookmark_unchanged(
69:    assert second.json()["tags"] == ["api"]
80:    assert [item["title"] for item in listing["items"]] == ["Docs"]
97:def test_invalid_duplicate_is_still_a_validation_error(
112:def test_link_with_a_different_query_is_a_new_bookmark(client: TestClient, row_count) -> None:
122:def test_concurrent_saves_of_the_same_link_leave_one_bookmark(
167:            {"url": "https://example.com", "title": "Bad tag", "tags": ["no spaces"]},
168:            id="invalid-tag",
175:def test_invalid_input_is_rejected_and_nothing_saved(
185:def test_title_of_exactly_200_and_ten_tags_are_accepted(client: TestClient) -> None:
198:def test_eleven_tags_that_dedupe_to_ten_are_accepted(client: TestClient) -> None:
1:"""HTTP endpoints for /bookmarks."""
2-
3-from typing import Annotated
--
54:    """201 with the new bookmark, or 200 with the existing one if the link is already saved
55:    (specs/002-idempotent-duplicate-save)."""
56-    row, created = repository.create_bookmark(session, data)
57-    if not created:
[exit 0]
```

```console
$ uv run --python 3.13 python -c "from bookmarks_api.main import create_app; print(repr(create_app().openapi()[\"paths\"][\"/bookmarks\"][\"post\"].get(\"description\")))" 2>&1 | grep -v UV_NATIVE; grep -n "description: >" -A3 specs/002-idempotent-duplicate-save/contracts/openapi.yaml | sed -n 5,12p
'201 with the new bookmark, or 200 with the existing one if the link is already saved\n(specs/002-idempotent-duplicate-save).'
--
18:      description: >
19-        Saves a link. If the link, after normalization, is already bookmarked, nothing is
20-        written and the existing bookmark is returned unchanged with 200; the title and tags in
21-        the request are ignored. Request validation runs first in both cases.
--
34:          description: >
35-            The normalized link is already bookmarked; the existing bookmark is returned
[exit 0]
```

### Converge report — round 1 (verbatim)

Code scope assessed (from plan.md / tasks.md paths): `src/bookmarks_api/repository.py`, `src/bookmarks_api/routes.py`, `src/bookmarks_api/errors.py`, `tests/integration/test_create_bookmark.py`, `tests/integration/test_errors.py`, `tests/integration/test_delete_bookmark.py` (referenced by T003), `README.md`; generated OpenAPI compared with `contracts/openapi.yaml`.

## Convergence Findings

| ID | Gap Type | Severity | Source | Evidence | Remaining Work |
|----|----------|----------|--------|----------|----------------|
| F1 | partial | LOW | Edge Cases (invalid duplicate: "a title over 200 characters, more than 10 tags, or an invalid tag"), FR-006 | `test_invalid_duplicate_is_still_a_validation_error` (tests/integration/test_create_bookmark.py:L84-110) parametrizes title-over-200 and eleven-tags only; the invalid-tag case of the edge case is not exercised on a duplicate link (only on a new link at L167). | Add an invalid-tag duplicate case. |
| F2 | partial | LOW | US1/AC2 ("listing bookmarks afterwards still shows exactly one bookmark for that link with title "Docs" and tags "api"") | `test_duplicate_ignores_title_and_tags_and_leaves_the_bookmark_unchanged` checks listing `total == 1` and titles (L78-80) but not the tags in the listing (tags only checked via direct DB read). | Assert the listed item's tags are `["api"]`. |
| F3 | unrequested | LOW | contracts/openapi.yaml (`POST /bookmarks` description); Constitution I (OpenAPI generated from code) | Route docstring (routes.py:L54-55) is published as the operation description in `/openapi.json`: "201 with the new bookmark, or 200 ... (specs/002-idempotent-duplicate-save)." — not asked for by any task, differs from the contract's description and exposes an internal spec path to API consumers. | Align the docstring with the contract description (drop the spec path). |

Checked with no gap: FR-001-FR-006, SC-001-SC-005, US1/AC1, US1/AC3, US2/AC1, Edge Cases (normalized match → 200; query differs → 201; link shown as originally given; delete then resave → 201 via `test_link_can_be_saved_again_after_delete`; save racing a delete → retry implemented in repository.py, untested by design per T002; no conflict ever), plan decisions (single ON CONFLICT write path, `(row, created)` return, 200 declared with `Bookmark`, `DuplicateUrlError`/409 removed, generic 409 mapping kept, no migration, no dependency, README row), Constitution I-VI (no violations; VI n/a).

**Summary metrics:**
- Requirements / acceptance criteria checked: 6 FR + 5 SC + 4 acceptance scenarios + 7 edge cases = 22
- Plan decisions checked: 8
- Constitution principles checked: 6
- Findings by gap type: missing 0 / partial 2 / contradicts 0 / unrequested 1
- Findings by severity: CRITICAL 0 / HIGH 0 / MEDIUM 0 / LOW 3

Outcome: **tasks_appended** — 3 tasks (T012-T014) appended under `## Phase 6: Convergence`. Next: run `/speckit-implement`; a follow-up converge should find fewer or no items.

Extension hooks (after_converge): `.specify/extensions.yml` absent — skipped.

```console
$ git diff --stat; tail -6 specs/002-idempotent-duplicate-save/tasks.md
 specs/002-idempotent-duplicate-save/tasks.md | 6 ++++++
 1 file changed, 6 insertions(+)

## Phase 6: Convergence

- [ ] T012 Add an invalid-tag case (`{"url": "https://example.com/docs", "title": "Bad tag", "tags": ["no spaces"]}`) to `test_invalid_duplicate_is_still_a_validation_error` in `tests/integration/test_create_bookmark.py` per Edge Cases / FR-006 (partial)
- [ ] T013 Assert the listed bookmark's tags are `["api"]` in `test_duplicate_ignores_title_and_tags_and_leaves_the_bookmark_unchanged` in `tests/integration/test_create_bookmark.py` per US1/AC2 (partial)
- [ ] T014 Align the `create_bookmark` docstring in `src/bookmarks_api/routes.py` (published as the `POST /bookmarks` OpenAPI description) with the description in `specs/002-idempotent-duplicate-save/contracts/openapi.yaml` and drop the internal spec path per contracts/openapi.yaml, Constitution I (unrequested)
[exit 0]
```

End: 2026-10-24T12:44:55Z
