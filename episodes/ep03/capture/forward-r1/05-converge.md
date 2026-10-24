# Step 05 — converge, round 1 (forward-r1)

Start: 2026-10-24T11:49:57Z

`.specify/extensions.yml` absent: no before_converge / after_converge hooks.

```console
$ .specify/scripts/bash/check-prerequisites.sh --json --require-spec --require-tasks --include-tasks
{"FEATURE_DIR":"/home/claude/runs/forward-r1/specs/002-idempotent-duplicate-save","AVAILABLE_DOCS":["research.md","data-model.md","contracts/","quickstart.md","tasks.md"]}
[exit 0]
```

```console
$ sha256sum specs/002-idempotent-duplicate-save/tasks.md; grep -nE "^## Phase|^- \[.\] T0" specs/002-idempotent-duplicate-save/tasks.md | tail -20
e561787ba05d81927110dcb40cd824ab059223083c0425bc160f8ce77ec02a15  specs/002-idempotent-duplicate-save/tasks.md
33:## Phase 1: Setup (Shared Infrastructure)
42:## Phase 2: Foundational (Blocking Prerequisites)
53:## Phase 3: User Story 1 - Re-saving a bookmarked link returns the existing bookmark (Priority: P1) 🎯 MVP
67:- [X] T001 [P] [US1] In `tests/integration/test_create_bookmark.py`, replace `test_equivalent_link_is_rejected_as_duplicate` with `test_equivalent_link_returns_existing_bookmark_with_200`: save `https://example.com/docs` (title "Docs"), then `HTTPS://Example.com/docs/#intro` (title "Other title", tags `["x"]`); assert the second status is 200, its JSON equals the first response's JSON (same `id`, `url`, `title`, `tags`, `created_at`), and `row_count() == 1` (spec US1 AC1, FR-002)
68:- [X] T002 [P] [US1] In `tests/integration/test_create_bookmark.py`, replace `test_duplicate_leaves_the_existing_bookmark_unchanged` with `test_duplicate_save_ignores_title_and_tags_and_changes_nothing`: save `https://example.com/docs` with title "Docs" and tags `["ref"]`, then save `https://example.com/docs` with title "Other" and tags `["x", "y"]`; assert 200 with title "Docs" and tags `["ref"]`, and that the stored row (read with the `engine` fixture: `url`, `title`, `tags`, `created_at`) is identical before and after (spec US1 AC2, FR-003)
69:- [X] T003 [P] [US1] In `tests/integration/test_create_bookmark.py`, change `test_concurrent_saves_of_the_same_link_leave_one_bookmark` to collect status and JSON for both threads and assert `sorted(statuses) == [200, 201]`, both bodies have the same `id`, and `row_count() == 1` (spec US1 AC4, FR-005)
70:- [X] T004 [P] [US1] In `tests/integration/test_create_bookmark.py`, add `test_resave_after_delete_creates_new_bookmark_with_201` (save, delete, save again → 201 with a new id) and `test_different_query_string_is_a_new_bookmark` (`https://example.com/search?q=a` then `?q=b` → both 201, two rows) (spec Edge Cases, US1 AC3)
71:- [X] T005 [P] [US1] In `tests/integration/test_errors.py`, remove `test_duplicate_error_envelope`; add `test_duplicate_save_is_not_an_error` asserting a duplicate save returns 200 with a `Bookmark` body (no `error` key); in `test_openapi_documents_every_operation`, change the POST error codes from `{"409", "422"}` to `{"422"}`, assert `"409" not in` the POST responses, and assert both `"200"` and `"201"` responses reference `/Bookmark` (spec FR-007, Constitution I)
75:- [X] T006 [US1] In `src/bookmarks_api/repository.py`, change `create_bookmark(session, data)` to return `tuple[BookmarkRow, bool]` (row, created): keep `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`; on insert commit and return `(row, True)`; when nothing is inserted, roll back, `SELECT` the row by `url_normalized` and return `(existing, False)` without writing to it; if the lookup finds nothing (deleted in between), retry the insert, at most 3 attempts (research.md "Returning the existing bookmark", "Concurrent saves"). Remove the `DuplicateUrlError` import and update the docstring
76:- [X] T007 [US1] In `src/bookmarks_api/routes.py`, make `POST /bookmarks` take a `Response` parameter, unpack `(row, created)` from `repository.create_bookmark`, set `response.status_code = 200` when not created (default stays 201), and replace the `409` entry in `responses=` with `200: {"model": Bookmark, "description": "This link was already saved; the existing bookmark is returned unchanged."}` plus `**ERROR_422` (depends on T006; contracts/openapi.yaml)
77:- [X] T008 [US1] In `src/bookmarks_api/errors.py`, delete the `DuplicateUrlError` class and its `handle_duplicate` exception handler; keep `409: "conflict"` in `STATUS_CODES` (research.md "Removing the duplicate error") (depends on T006)
83:## Phase 4: User Story 2 - Invalid saves are still rejected (Priority: P2)
93:- [X] T009 [US2] In `tests/integration/test_create_bookmark.py`, add a parametrized `test_invalid_resave_of_existing_link_is_rejected` (title `"t" * 201`; 11 tags `t0..t10`; tag `"no spaces"`): save `https://example.com/docs` first, then the invalid payload for the same link; assert 422 with code `validation_error`, `row_count() == 1`, and the stored title unchanged (spec US2 AC1, FR-006)
97:- [X] T010 [US2] Confirm no code change is needed: `BookmarkCreate` in `src/bookmarks_api/schemas.py` validates the body before the route runs; T009 must pass with T006 to T008 in place (research.md "Validation order")
103:## Phase 5: Polish & Cross-Cutting Concerns
107:- [X] T011 [P] In `README.md`, change the `POST /bookmarks` row of the endpoint table from "409 if the link is already saved" to "201 for a new link; 200 with the existing bookmark, unchanged, if the link is already saved"
108:- [X] T012 Grep `src/` and `tests/` for `DuplicateUrlError`, `duplicate_url` and `409` and confirm none remain for saving (only the generic `409: "conflict"` mapping in `src/bookmarks_api/errors.py`)
109:- [X] T013 Run the full suite on all supported versions: `uv run --python 3.11 pytest -q`, `uv run --python 3.12 pytest -q`, `uv run --python 3.13 pytest -q` (with `.env` loaded); all must pass (Constitution V, Quality Gates)
110:- [X] T014 Run the manual checks in `specs/002-idempotent-duplicate-save/quickstart.md` (steps 1 to 5, including `/openapi.json` listing 200, 201 and 422 for `POST /bookmarks` and no 409)
[exit 0]
```

```console
$ grep -n "def create_bookmark" -A 32 src/bookmarks_api/repository.py; grep -n "@router.post" -A 26 src/bookmarks_api/routes.py; grep -n "Duplicate\|duplicate\|409" src/bookmarks_api/*.py
18:def create_bookmark(session: Session, data: BookmarkCreate) -> tuple[BookmarkRow, bool]:
19-    """Save a bookmark and return ``(row, created)``.
20-
21-    A new normalized link is inserted and returned with ``created=True``. If the normalized link
22-    is already saved, the existing row is returned unchanged with ``created=False``; the title and
23-    tags in ``data`` are ignored (specs/002-idempotent-duplicate-save, FR-002/FR-003).
24-
25-    ON CONFLICT DO NOTHING relies on the unique index, so two concurrent saves of the same new link
26-    store one row: one caller gets ``created=True``, the other the same row with ``created=False``.
27-    If the conflicting row is deleted before it can be read, the insert is retried.
28-    """
29-    normalized = normalize_url(data.url)
30-    statement = (
31-        insert(BookmarkRow)
32-        .values(url=data.url, url_normalized=normalized, title=data.title, tags=data.tags)
33-        .on_conflict_do_nothing(index_elements=[BookmarkRow.url_normalized])
34-        .returning(BookmarkRow)
35-    )
36-    for _ in range(MAX_SAVE_ATTEMPTS):
37-        row = session.scalars(statement).one_or_none()
38-        if row is not None:
39-            session.commit()
40-            return row, True
41-        session.rollback()
42-        existing = session.scalars(
43-            select(BookmarkRow).where(BookmarkRow.url_normalized == normalized)
44-        ).one_or_none()
45-        # End the read-only transaction with commit, not rollback: rollback expires the loaded
46-        # row, which would reload it lazily (or fail if it was deleted meanwhile).
47-        session.commit()
48-        if existing is not None:
49-            return existing, False
50-    raise RuntimeError("Could not save or find the bookmark after repeated conflicts.")
38:@router.post(
39-    "",
40-    status_code=status.HTTP_201_CREATED,
41-    response_model=Bookmark,
42-    summary="Save a bookmark",
43-    description=(
44-        "201 with the new bookmark when the link is not saved yet; 200 with the existing "
45-        "bookmark, unchanged, when the link (after normalization) is already saved. "
46-        "The title and tags of a duplicate save are ignored."
47-    ),
48-    responses={
49-        200: {
50-            "model": Bookmark,
51-            "description": "This link was already saved; the existing bookmark is returned unchanged.",
52-        },
53-        201: {"description": "Bookmark saved."},
54-        **ERROR_422,
55-    },
56-)
57-def create_bookmark(data: BookmarkCreate, session: SessionDep, response: Response) -> Bookmark:
58-    row, created = repository.create_bookmark(session, data)
59-    if not created:
60-        response.status_code = status.HTTP_200_OK
61-    return Bookmark.model_validate(row)
62-
63-
64-@router.get(
src/bookmarks_api/errors.py:35:STATUS_CODES = {400: "bad_request", 404: "not_found", 405: "method_not_allowed", 409: "conflict"}
src/bookmarks_api/normalize.py:16:    """Return the normalized form of a link used to detect duplicates.
src/bookmarks_api/normalize.py:59:    """Normalize each tag, drop duplicates and return them sorted."""
src/bookmarks_api/repository.py:23:    tags in ``data`` are ignored (specs/002-idempotent-duplicate-save, FR-002/FR-003).
src/bookmarks_api/routes.py:46:        "The title and tags of a duplicate save are ignored."
[exit 0]
```

```console
$ grep -n "^def test_\|specs/002" tests/integration/test_create_bookmark.py tests/integration/test_errors.py
tests/integration/test_create_bookmark.py:2:rule superseded by specs/002-idempotent-duplicate-save (200 with the existing bookmark)."""
tests/integration/test_create_bookmark.py:11:def test_save_with_title_and_no_tags(client: TestClient, row_count) -> None:
tests/integration/test_create_bookmark.py:24:def test_tags_are_trimmed_lowercased_and_deduplicated(client: TestClient) -> None:
tests/integration/test_create_bookmark.py:34:def test_link_is_stored_as_given(client: TestClient) -> None:
tests/integration/test_create_bookmark.py:41:def test_equivalent_link_returns_existing_bookmark_with_200(client: TestClient, row_count) -> None:
tests/integration/test_create_bookmark.py:42:    """specs/002 US1 AC1, FR-002: a duplicate save returns the existing bookmark with 200."""
tests/integration/test_create_bookmark.py:55:def test_duplicate_save_ignores_title_and_tags_and_changes_nothing(
tests/integration/test_create_bookmark.py:58:    """specs/002 US1 AC2, FR-003: title and tags in the request are ignored; nothing is modified."""
tests/integration/test_create_bookmark.py:81:def test_concurrent_saves_of_the_same_link_leave_one_bookmark(client: TestClient, row_count) -> None:
tests/integration/test_create_bookmark.py:82:    """specs/002 US1 AC4, FR-005: one 201 and one 200, same bookmark, one row."""
tests/integration/test_create_bookmark.py:105:def test_resave_after_delete_creates_new_bookmark_with_201(client: TestClient, row_count) -> None:
tests/integration/test_create_bookmark.py:106:    """specs/002 Edge Cases: after a delete, saving the same link creates a new bookmark."""
tests/integration/test_create_bookmark.py:116:def test_different_query_string_is_a_new_bookmark(client: TestClient, row_count) -> None:
tests/integration/test_create_bookmark.py:117:    """specs/002 Edge Cases, US1 AC3: different query strings are different links (201 each)."""
tests/integration/test_create_bookmark.py:133:def test_invalid_resave_of_existing_link_is_rejected(
tests/integration/test_create_bookmark.py:136:    """specs/002 US2 AC1, FR-006: validation runs before the duplicate check."""
tests/integration/test_create_bookmark.py:174:def test_invalid_input_is_rejected_and_nothing_saved(
tests/integration/test_create_bookmark.py:184:def test_title_of_exactly_200_and_ten_tags_are_accepted(client: TestClient) -> None:
tests/integration/test_create_bookmark.py:197:def test_eleven_tags_that_dedupe_to_ten_are_accepted(client: TestClient) -> None:
tests/integration/test_errors.py:17:def test_validation_error_envelope(client: TestClient) -> None:
tests/integration/test_errors.py:25:def test_duplicate_save_is_not_an_error(client: TestClient) -> None:
tests/integration/test_errors.py:26:    """specs/002 FR-002: a duplicate save returns 200 with a bookmark, not an error envelope."""
tests/integration/test_errors.py:35:def test_not_found_error_envelope(client: TestClient) -> None:
tests/integration/test_errors.py:39:def test_unknown_route_uses_the_envelope(client: TestClient) -> None:
tests/integration/test_errors.py:43:def test_wrong_method_uses_the_envelope(client: TestClient) -> None:
tests/integration/test_errors.py:47:def test_malformed_json_uses_the_envelope(client: TestClient) -> None:
tests/integration/test_errors.py:55:def test_unexpected_errors_hide_internals(client: TestClient, monkeypatch) -> None:
tests/integration/test_errors.py:72:def test_openapi_documents_every_operation(client: TestClient, path: str, method: str) -> None:
tests/integration/test_errors.py:85:        assert "409" not in operation["responses"]  # specs/002 FR-007
[exit 0]
```

```console
$ set -a; . ./.env; set +a; uv run --python 3.13 pytest -q -rA tests/integration/test_create_bookmark.py tests/integration/test_errors.py 2>&1 | grep -E "PASSED|FAILED|ERROR|passed|failed"
ERROR    bookmarks_api.errors:errors.py:73 Unhandled error
PASSED tests/integration/test_create_bookmark.py::test_save_with_title_and_no_tags
PASSED tests/integration/test_create_bookmark.py::test_tags_are_trimmed_lowercased_and_deduplicated
PASSED tests/integration/test_create_bookmark.py::test_link_is_stored_as_given
PASSED tests/integration/test_create_bookmark.py::test_equivalent_link_returns_existing_bookmark_with_200
PASSED tests/integration/test_create_bookmark.py::test_duplicate_save_ignores_title_and_tags_and_changes_nothing
PASSED tests/integration/test_create_bookmark.py::test_concurrent_saves_of_the_same_link_leave_one_bookmark
PASSED tests/integration/test_create_bookmark.py::test_resave_after_delete_creates_new_bookmark_with_201
PASSED tests/integration/test_create_bookmark.py::test_different_query_string_is_a_new_bookmark
PASSED tests/integration/test_create_bookmark.py::test_invalid_resave_of_existing_link_is_rejected[title-over-200]
PASSED tests/integration/test_create_bookmark.py::test_invalid_resave_of_existing_link_is_rejected[eleven-tags]
PASSED tests/integration/test_create_bookmark.py::test_invalid_resave_of_existing_link_is_rejected[invalid-tag]
PASSED tests/integration/test_create_bookmark.py::test_invalid_input_is_rejected_and_nothing_saved[missing-url]
PASSED tests/integration/test_create_bookmark.py::test_invalid_input_is_rejected_and_nothing_saved[missing-title]
PASSED tests/integration/test_create_bookmark.py::test_invalid_input_is_rejected_and_nothing_saved[blank-title]
PASSED tests/integration/test_create_bookmark.py::test_invalid_input_is_rejected_and_nothing_saved[ftp-link]
PASSED tests/integration/test_create_bookmark.py::test_invalid_input_is_rejected_and_nothing_saved[no-scheme]
PASSED tests/integration/test_create_bookmark.py::test_invalid_input_is_rejected_and_nothing_saved[url-over-2048]
PASSED tests/integration/test_create_bookmark.py::test_invalid_input_is_rejected_and_nothing_saved[title-over-200]
PASSED tests/integration/test_create_bookmark.py::test_invalid_input_is_rejected_and_nothing_saved[eleven-tags]
PASSED tests/integration/test_create_bookmark.py::test_invalid_input_is_rejected_and_nothing_saved[invalid-tag]
PASSED tests/integration/test_create_bookmark.py::test_invalid_input_is_rejected_and_nothing_saved[unknown-field]
PASSED tests/integration/test_create_bookmark.py::test_title_of_exactly_200_and_ten_tags_are_accepted
PASSED tests/integration/test_create_bookmark.py::test_eleven_tags_that_dedupe_to_ten_are_accepted
PASSED tests/integration/test_errors.py::test_validation_error_envelope
PASSED tests/integration/test_errors.py::test_duplicate_save_is_not_an_error
PASSED tests/integration/test_errors.py::test_not_found_error_envelope
PASSED tests/integration/test_errors.py::test_unknown_route_uses_the_envelope
PASSED tests/integration/test_errors.py::test_wrong_method_uses_the_envelope
PASSED tests/integration/test_errors.py::test_malformed_json_uses_the_envelope
PASSED tests/integration/test_errors.py::test_unexpected_errors_hide_internals
PASSED tests/integration/test_errors.py::test_openapi_documents_every_operation[/bookmarks-post]
PASSED tests/integration/test_errors.py::test_openapi_documents_every_operation[/bookmarks-get]
PASSED tests/integration/test_errors.py::test_openapi_documents_every_operation[/bookmarks/{bookmark_id}-delete]
33 passed in 0.97s
[exit 0]
```

```console
$ set -a; . ./.env; set +a; uv run --python 3.13 python -c "
from fastapi.testclient import TestClient
from bookmarks_api.main import create_app
op = TestClient(create_app()).get(\"/openapi.json\").json()[\"paths\"][\"/bookmarks\"][\"post\"]
for k, v in sorted(op[\"responses\"].items()):
    print(k, v[\"description\"], v.get(\"content\", {}).get(\"application/json\", {}).get(\"schema\"))
"
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
200 This link was already saved; the existing bookmark is returned unchanged. {'$ref': '#/components/schemas/Bookmark'}
201 Bookmark saved. {'$ref': '#/components/schemas/Bookmark'}
422 The request is not valid. {'$ref': '#/components/schemas/ErrorResponse'}
[exit 0]
```

Note: the `ERROR    bookmarks_api.errors:errors.py:73 Unhandled error` line above is the captured log of `test_unexpected_errors_hide_internals` (it deliberately raises inside the route); that test PASSED.

## Assessment (intent inventory → code)

Sources of intent: `specs/002-idempotent-duplicate-save/spec.md`, `plan.md`, `tasks.md`, constitution v1.1.0. Code scope (from plan/tasks): `src/bookmarks_api/repository.py`, `routes.py`, `errors.py`, `schemas.py`; `tests/integration/test_create_bookmark.py`, `test_errors.py`; `README.md`.

| Key | Evidence | Gap? |
| --- | --- | --- |
| FR-001 one bookmark per normalized link, also concurrent | unique index unchanged; `ON CONFLICT DO NOTHING` kept (repository.py:30-35); race test passes | none |
| FR-002 duplicate → existing bookmark, 200, no conflict | routes.py:57-61 sets 200 when `created` is false; `DuplicateUrlError` gone; tests pass | none |
| FR-003 ignore title/tags, no modification | duplicate path only SELECTs; test compares stored row before/after | none |
| FR-004 new link → 201 | default `status_code=201`; existing tests pass | none |
| FR-005 concurrent → one 201 + one 200, same bookmark | `test_concurrent_saves_of_the_same_link_leave_one_bookmark` asserts `[200, 201]`, same id, 1 row | none |
| FR-006 validation before duplicate check | Pydantic body validation precedes route; `test_invalid_resave_of_existing_link_is_rejected` ×3 | none |
| FR-007 OpenAPI documents 200 and 201, no 409 | generated `/openapi.json`: 200 → Bookmark, 201 → Bookmark, 422 → ErrorResponse | none |
| SC-001..SC-004 | covered by the tests above; full suite 103 passed (step 04) | none |
| US1/AC1..AC4, US2/AC1 | one test each (names cite the AC) | none |
| Edge cases (equivalent forms, different query, invalid, after delete, concurrent, never 409) | tests listed above | none |
| plan: no migration, no new dependency | `migrations/` and `pyproject.toml` untouched | none |
| plan: touch-points (repository, routes, errors, two test files, README) | all changed as described | none |
| tasks T001–T014 (re-verified, not trusted from `[X]`) | each task's stated behavior present; T006 "roll back, SELECT, return without writing" — code rolls back the failed insert, SELECTs, then ends the read-only transaction with `commit()` (no write; done to avoid expiring the row) — behavior matches | none |
| Constitution I typed contracts | both outcomes use `Bookmark`; no untyped dicts | none |
| Constitution II real DB | integration tests on real PostgreSQL | none |
| Constitution III error shape | remaining errors use envelope; tests pass | none |
| Constitution IV dependencies | none added | none |
| Constitution V tests ship with feature | tests in same change; suite passes | none |
| Constitution VI cursor pagination | no list endpoint touched | n/a |
| unrequested code | route `description=` and `201` description text serve FR-007; retry loop + `RuntimeError` is required by T006 / research.md | none |

Considered and not a finding: the retry branch (row deleted between conflict and lookup) has no automated test. It is not an acceptance scenario or edge case in spec.md, and no task requires a test for it; Constitution V's requirement is per acceptance scenario. Recorded for the coordinator.

## Convergence Findings

No findings.

**Summary metrics:**

- Requirements / acceptance criteria checked: 7 FR + 4 SC + 5 acceptance scenarios + 6 edge cases = 22
- Plan decisions checked: 3 (no schema change/migration; no new dependency; named touch-points) + 14 tasks re-verified
- Constitution principles checked: 6 (VI not applicable)
- Findings by gap type: missing 0 / partial 0 / contradicts 0 / unrequested 0
- Findings by severity: CRITICAL 0 / HIGH 0 / MEDIUM 0 / LOW 0

**"✅ Converged — the implementation satisfies the spec, plan, and tasks."**

tasks.md left byte-for-byte unchanged (no Convergence phase appended):

```console
$ sha256sum specs/002-idempotent-duplicate-save/tasks.md; git status --short specs
e561787ba05d81927110dcb40cd824ab059223083c0425bc160f8ce77ec02a15  specs/002-idempotent-duplicate-save/tasks.md
[exit 0]
```

## Next actions (handoff)

Converged in round 1: no further implement pass is needed for this feature's specified scope; proceed to review / PR. (No push per run rules.)

Hooks: `.specify/extensions.yml` absent; none.

End: 2026-10-24T11:50:32Z
