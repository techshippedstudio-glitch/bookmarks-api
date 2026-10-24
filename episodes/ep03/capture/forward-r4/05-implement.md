# Step 05 — implement (forward-r4)

Start: 2026-10-24T12:41:08Z

```console
$ ls .specify/extensions.yml 2>&1; .specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
ls: cannot access '.specify/extensions.yml': No such file or directory
{"FEATURE_DIR":"/home/claude/runs/forward-r4/specs/002-idempotent-duplicate-save","AVAILABLE_DOCS":["research.md","data-model.md","contracts/","quickstart.md","tasks.md"]}
[exit 0]
```

```console
$ for f in specs/002-idempotent-duplicate-save/checklists/*.md; do t=$(grep -cE "^- \[( |x|X)\]" $f); c=$(grep -cE "^- \[(x|X)\]" $f); echo "$f total=$t checked=$c unchecked=$((t-c))"; done
specs/002-idempotent-duplicate-save/checklists/requirements.md total=16 checked=16 unchecked=0
[exit 0]
```

```console
$ git rev-parse --git-dir; ls Dockerfile* 2>&1; grep -n "docker\|Docker" specs/002-idempotent-duplicate-save/plan.md; cat .dockerignore; ls .eslintrc* eslint.config.* .prettierrc* .npmrc package.json *.tf 2>&1 | head
/home/claude/bookmarks-api/.git/worktrees/forward-r4
ls: cannot access 'Dockerfile*': No such file or directory
.git/
.venv/
__pycache__/
*.pyc
.pytest_cache/
.env
.env.*
!.env.example
*.log
ls: cannot access '.eslintrc*': No such file or directory
ls: cannot access 'eslint.config.*': No such file or directory
ls: cannot access '.prettierrc*': No such file or directory
ls: cannot access '.npmrc': No such file or directory
ls: cannot access 'package.json': No such file or directory
ls: cannot access '*.tf': No such file or directory
[exit 0]
```

Checklist gate: | requirements.md | 16 | 16 | 0 | PASS | -> proceed.
Ignore files: git repo -> .gitignore already has Python + universal patterns (`__pycache__/`, `*.py[cod]`, `.venv/`, `venv/`, `dist/`, `*.egg-info/`, `.DS_Store`, `Thumbs.db`, `.vscode/`, `.idea/`, `.env*`); no Dockerfile, ESLint, Prettier, npm or Terraform files -> nothing to create or append.

### T001 baseline

```console
$ set -a; . ./.env; set +a; uv run --python 3.13 pytest -q 2>&1 | tail -5
      Built bookmarks-api @ file:///home/claude/runs/forward-r4
Installed 29 packages in 30ms
........................................................................ [ 73%]
..........................                                               [100%]
98 passed in 3.18s
[exit 0]
```

### T002 done (repository returns (row, created)); T003, T004 tests written (T007 concurrency test written in the same edit of test_create_bookmark.py because it is the same file). TDD check before T005/T006:

```console
$ set -a; . ./.env; set +a; uv run --python 3.13 pytest -q 2>&1 | tail -25
FAILED tests/integration/test_create_bookmark.py::test_save_with_title_and_no_tags
FAILED tests/integration/test_create_bookmark.py::test_tags_are_trimmed_lowercased_and_deduplicated
FAILED tests/integration/test_create_bookmark.py::test_link_is_stored_as_given
FAILED tests/integration/test_create_bookmark.py::test_equivalent_link_returns_the_existing_bookmark
FAILED tests/integration/test_create_bookmark.py::test_duplicate_ignores_title_and_tags_and_leaves_the_bookmark_unchanged
FAILED tests/integration/test_create_bookmark.py::test_link_with_a_different_query_is_a_new_bookmark
FAILED tests/integration/test_create_bookmark.py::test_concurrent_saves_of_the_same_link_leave_one_bookmark
FAILED tests/integration/test_create_bookmark.py::test_title_of_exactly_200_and_ten_tags_are_accepted
FAILED tests/integration/test_create_bookmark.py::test_eleven_tags_that_dedupe_to_ten_are_accepted
FAILED tests/integration/test_delete_bookmark.py::test_deleted_bookmark_disappears_from_list_and_filter
FAILED tests/integration/test_delete_bookmark.py::test_deleting_twice_returns_not_found_the_second_time
FAILED tests/integration/test_delete_bookmark.py::test_link_can_be_saved_again_after_delete
FAILED tests/integration/test_errors.py::test_duplicate_save_is_not_an_error
FAILED tests/integration/test_errors.py::test_openapi_documents_every_operation[/bookmarks-post]
FAILED tests/integration/test_filter_by_tag.py::test_filter_returns_only_matching_bookmarks_newest_first
FAILED tests/integration/test_filter_by_tag.py::test_filter_is_normalized_like_tags
FAILED tests/integration/test_filter_by_tag.py::test_unknown_tag_returns_empty_list
FAILED tests/integration/test_filter_by_tag.py::test_filter_works_with_paging
FAILED tests/integration/test_list_bookmarks.py::test_lists_newest_first_with_total
FAILED tests/integration/test_list_bookmarks.py::test_pages_of_twenty_by_default
FAILED tests/integration/test_list_bookmarks.py::test_custom_limit - assert 5...
FAILED tests/integration/test_list_bookmarks.py::test_exactly_one_full_page_has_no_next_cursor
FAILED tests/integration/test_list_bookmarks.py::test_saves_between_pages_cause_no_duplicates_or_gaps
FAILED tests/integration/test_list_bookmarks.py::test_deletes_between_pages_skip_nothing
24 failed, 77 passed in 2.31s
[exit 0]
```

### After T005 (route: 201/200, 409 removed, 200 declared) and T006 (DuplicateUrlError + handler removed)

```console
$ set -a; . ./.env; set +a; uv run --python 3.13 pytest -q 2>&1 | tail -15
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
........................................................................ [ 71%]
.............................                                            [100%]
101 passed in 3.12s
[exit 0]
```

### T008 check: concurrency test repeated (5 runs x 20 iterations each)

```console
$ set -a; . ./.env; set +a; for i in 1 2 3 4 5; do uv run --python 3.13 pytest -q tests/integration/test_create_bookmark.py -k concurrent 2>&1 | tail -1; done
1 passed, 20 deselected in 0.58s
1 passed, 20 deselected in 0.57s
1 passed, 20 deselected in 0.50s
1 passed, 20 deselected in 0.68s
1 passed, 20 deselected in 0.64s
[exit 0]
```

### T009 README endpoint row updated. T010 leftover search:

```console
$ grep -rn "DuplicateUrlError\|duplicate_url\|409" src tests; echo "grep exit: done"
src/bookmarks_api/errors.py:35:STATUS_CODES = {400: "bad_request", 404: "not_found", 405: "method_not_allowed", 409: "conflict"}
tests/integration/test_errors.py:26:    """002 FR-002 / SC-004: a duplicate save is a 200 success, never a 409 error envelope."""
tests/integration/test_errors.py:90:        assert "409" not in operation["responses"]
grep: tests/integration/__pycache__/test_errors.cpython-313-pytest-9.1.1.pyc: binary file matches
grep exit: done
[exit 0]
```

Remaining matches are intentional: generic `409: "conflict"` mapping kept (research.md §3) and two test assertions that 409 is absent.

### T011 full suite on 3.11, 3.12, 3.13

```console
$ set -a; . ./.env; set +a; for v in 3.11 3.12 3.13; do echo "== python $v"; uv run --python $v pytest -q 2>&1 | tail -2; done
== python 3.11
.............................                                            [100%]
101 passed in 3.83s
== python 3.12
.............................                                            [100%]
101 passed in 3.83s
== python 3.13
.............................                                            [100%]
101 passed in 3.50s
[exit 0]
```

### T011 quickstart manual table (uvicorn on port 18714 against this run's own test DB; script at /home/claude/scratch/forward-r4/quickstart.sh)

```console
$ cat /home/claude/scratch/forward-r4/quickstart.sh
#!/usr/bin/env bash
# Walk specs/002-idempotent-duplicate-save/quickstart.md manual table against this run's own test DB.
cd /home/claude/runs/forward-r4
set -a; . ./.env; set +a
export DATABASE_URL="$TEST_DATABASE_URL"
PORT=18714
uv run --python 3.13 python -c "import sqlalchemy as sa; e=sa.create_engine('$TEST_DATABASE_URL'.replace('postgresql://','postgresql+psycopg://')); c=e.connect(); c.execute(sa.text('TRUNCATE bookmarks RESTART IDENTITY')); c.commit(); print('truncated own test db')"
uv run --python 3.13 uvicorn bookmarks_api.main:app --port $PORT > /home/claude/scratch/forward-r4/uvicorn.log 2>&1 &
PID=$!
for i in $(seq 1 50); do curl -s -o /dev/null http://127.0.0.1:$PORT/openapi.json && break; sleep 0.2; done
B=http://127.0.0.1:$PORT/bookmarks
j() { curl -s -w '  [HTTP %{http_code}]\n' "$@"; }
echo "1:"; j -X POST $B -H 'Content-Type: application/json' -d '{"url": "https://example.com/docs", "title": "Docs", "tags": ["api"]}'
echo "2:"; j -X POST $B -H 'Content-Type: application/json' -d '{"url": "HTTPS://Example.com/docs/#intro", "title": "Other", "tags": ["python"]}'
echo "3:"; j $B
T=$(python3 -c 'print("t"*201)')
echo "4:"; j -X POST $B -H 'Content-Type: application/json' -d "{\"url\": \"https://example.com/docs\", \"title\": \"$T\"}"
echo "5:"; j -X POST $B -H 'Content-Type: application/json' -d '{"url": "https://example.com/docs?x=1", "title": "Query"}'
echo "6a:"; j -X DELETE $B/1
echo "6b:"; j -X POST $B -H 'Content-Type: application/json' -d '{"url": "https://example.com/docs", "title": "Docs", "tags": ["api"]}'
kill $PID; wait $PID 2>/dev/null
uv run --python 3.13 python -c "import sqlalchemy as sa; e=sa.create_engine('$TEST_DATABASE_URL'.replace('postgresql://','postgresql+psycopg://')); c=e.connect(); c.execute(sa.text('TRUNCATE bookmarks RESTART IDENTITY')); c.commit(); print('truncated own test db')"
[exit 0]
```

```console
$ /home/claude/scratch/forward-r4/quickstart.sh 2>&1 | grep -v UV_NATIVE_TLS
truncated own test db
1:
{"id":1,"url":"https://example.com/docs","title":"Docs","tags":["api"],"created_at":"2026-10-24T12:43:40.314226Z"}  [HTTP 201]
2:
{"id":1,"url":"https://example.com/docs","title":"Docs","tags":["api"],"created_at":"2026-10-24T12:43:40.314226Z"}  [HTTP 200]
3:
{"items":[{"id":1,"url":"https://example.com/docs","title":"Docs","tags":["api"],"created_at":"2026-10-24T12:43:40.314226Z"}],"total":1,"limit":20,"next_cursor":null}  [HTTP 200]
4:
{"error":{"code":"validation_error","message":"The request is not valid.","details":[{"field":"title","message":"String should have at most 200 characters"}]}}  [HTTP 422]
5:
{"id":3,"url":"https://example.com/docs?x=1","title":"Query","tags":[],"created_at":"2026-10-24T12:43:40.387133Z"}  [HTTP 201]
6a:
  [HTTP 204]
6b:
{"id":4,"url":"https://example.com/docs","title":"Docs","tags":["api"],"created_at":"2026-10-24T12:43:40.417044Z"}  [HTTP 201]
truncated own test db
[exit 0]
```

Observation: step 5 got id 3, not 2 — the duplicate save in step 2 consumed an identity value (`INSERT ... ON CONFLICT DO NOTHING` still advances the identity sequence). Ids get gaps on duplicate saves; the stored bookmark is unchanged, so no FR is violated.

All 11 tasks marked [X] in tasks.md.

## Review: code and artifact diffs (ep03-forward-r4-analyze..working tree)

```console
$ git diff --stat; git diff -- src README.md
 README.md                                    |   2 +-
 specs/002-idempotent-duplicate-save/tasks.md |  22 ++---
 src/bookmarks_api/errors.py                  |  11 ---
 src/bookmarks_api/repository.py              |  39 ++++++---
 src/bookmarks_api/routes.py                  |  16 +++-
 tests/integration/test_create_bookmark.py    | 116 +++++++++++++++++++++------
 tests/integration/test_errors.py             |  18 +++--
 7 files changed, 154 insertions(+), 70 deletions(-)
diff --git a/README.md b/README.md
index 5c4557f..d473624 100644
--- a/README.md
+++ b/README.md
@@ -97,7 +97,7 @@ uv run pytest                                          # tests, against the book
 
 | Endpoint | What it does |
 | --- | --- |
-| `POST /bookmarks` | Save `{"url", "title", "tags"}`; 409 if the link is already saved |
+| `POST /bookmarks` | Save `{"url", "title", "tags"}`; 201 when new, 200 with the existing bookmark (unchanged) if the link is already saved |
 | `GET /bookmarks?tag=&limit=&cursor=` | List newest first, 20 per page by default, optional tag filter; pass `next_cursor` from one page as `cursor` to get the next |
 | `DELETE /bookmarks/{id}` | Delete a bookmark |
 
diff --git a/src/bookmarks_api/errors.py b/src/bookmarks_api/errors.py
index a8faf96..b2b3425 100644
--- a/src/bookmarks_api/errors.py
+++ b/src/bookmarks_api/errors.py
@@ -32,13 +32,6 @@ class NotFoundError(Exception):
         self.message = message
 
 
-class DuplicateUrlError(Exception):
-    def __init__(self, existing_id: int) -> None:
-        super().__init__(f"This link is already bookmarked (id {existing_id}).")
-        self.existing_id = existing_id
-        self.message = str(self)
-
-
 STATUS_CODES = {400: "bad_request", 404: "not_found", 405: "method_not_allowed", 409: "conflict"}
 
 
@@ -75,10 +68,6 @@ def install_error_handlers(app: FastAPI) -> None:
     async def handle_not_found(_: Request, exc: NotFoundError) -> JSONResponse:
         return error_response(404, "not_found", exc.message)
 
-    @app.exception_handler(DuplicateUrlError)
-    async def handle_duplicate(_: Request, exc: DuplicateUrlError) -> JSONResponse:
-        return error_response(409, "duplicate_url", exc.message, {"existing_id": exc.existing_id})
-
     @app.exception_handler(Exception)
     async def handle_unexpected(_: Request, exc: Exception) -> JSONResponse:
         logger.exception("Unhandled error", exc_info=exc)
diff --git a/src/bookmarks_api/repository.py b/src/bookmarks_api/repository.py
index f93517e..23b6ab8 100644
--- a/src/bookmarks_api/repository.py
+++ b/src/bookmarks_api/repository.py
@@ -6,16 +6,27 @@ from sqlalchemy import delete, func, select, tuple_
 from sqlalchemy.dialects.postgresql import insert
 from sqlalchemy.orm import Session
 
-from bookmarks_api.errors import DuplicateUrlError, NotFoundError
+from bookmarks_api.errors import NotFoundError
 from bookmarks_api.models import BookmarkRow
 from bookmarks_api.normalize import normalize_url
 from bookmarks_api.schemas import BookmarkCreate
 
 
-def create_bookmark(session: Session, data: BookmarkCreate) -> BookmarkRow:
-    """Insert a bookmark, or raise DuplicateUrlError if its normalized link already exists.
+MAX_SAVE_ATTEMPTS = 3
 
-    ON CONFLICT DO NOTHING relies on the unique index, so this holds under concurrent saves.
+
+def create_bookmark(session: Session, data: BookmarkCreate) -> tuple[BookmarkRow, bool]:
+    """Save a bookmark and return ``(row, created)``.
+
+    A new normalized link is inserted and returned with ``created=True``. If the normalized link
+    is already saved, nothing is written and the existing row is returned unchanged with
+    ``created=False``; the request's title and tags are ignored
+    (specs/002-idempotent-duplicate-save, FR-002/FR-003).
+
+    ON CONFLICT DO NOTHING relies on the unique index, so of two concurrent saves of the same new
+    link exactly one inserts; the other waits for that commit and then reads the committed row.
+    If the conflicting row is deleted before it can be read, the insert is retried (the save then
+    stores a new bookmark), at most MAX_SAVE_ATTEMPTS times.
     """
     normalized = normalize_url(data.url)
     statement = (
@@ -24,15 +35,19 @@ def create_bookmark(session: Session, data: BookmarkCreate) -> BookmarkRow:
         .on_conflict_do_nothing(index_elements=[BookmarkRow.url_normalized])
         .returning(BookmarkRow)
     )
-    row = session.scalars(statement).one_or_none()
-    if row is None:
+    for _ in range(MAX_SAVE_ATTEMPTS):
+        row = session.scalars(statement).one_or_none()
+        if row is not None:
+            session.commit()
+            return row, True
         session.rollback()
-        existing_id = session.scalar(
-            select(BookmarkRow.id).where(BookmarkRow.url_normalized == normalized)
-        )
-        raise DuplicateUrlError(existing_id)
-    session.commit()
-    return row
+        existing = session.scalars(
+            select(BookmarkRow).where(BookmarkRow.url_normalized == normalized)
+        ).one_or_none()
+        session.commit()  # end the read-only transaction; nothing was written
+        if existing is not None:
+            return existing, False
+    raise RuntimeError(f"Could not save or find a bookmark for {normalized!r}.")
 
 
 def list_bookmarks(
diff --git a/src/bookmarks_api/routes.py b/src/bookmarks_api/routes.py
index cc51123..13fb865 100644
--- a/src/bookmarks_api/routes.py
+++ b/src/bookmarks_api/routes.py
@@ -41,12 +41,22 @@ def _reject_offset(value: str | None) -> None:
     response_model=Bookmark,
     summary="Save a bookmark",
     responses={
-        409: {"model": ErrorResponse, "description": "This link is already bookmarked."},
+        200: {
+            "model": Bookmark,
+            "description": (
+                "This link is already bookmarked; the existing bookmark is returned unchanged."
+            ),
+        },
         **ERROR_422,
     },
 )
-def create_bookmark(data: BookmarkCreate, session: SessionDep) -> Bookmark:
-    return Bookmark.model_validate(repository.create_bookmark(session, data))
+def create_bookmark(data: BookmarkCreate, session: SessionDep, response: Response) -> Bookmark:
+    """201 with the new bookmark, or 200 with the existing one if the link is already saved
+    (specs/002-idempotent-duplicate-save)."""
+    row, created = repository.create_bookmark(session, data)
+    if not created:
+        response.status_code = status.HTTP_200_OK
+    return Bookmark.model_validate(row)
 
 
 @router.get(
[exit 0]
```

```console
$ uv run --python 3.13 python -c "
import json
from bookmarks_api.main import create_app
op = create_app().openapi()[\"paths\"][\"/bookmarks\"][\"post\"]
print(json.dumps({k: (v.get(\"description\"), v.get(\"content\", {}).get(\"application/json\", {}).get(\"schema\")) for k, v in sorted(op[\"responses\"].items())}, indent=1))
print(\"description:\", op.get(\"description\"))
" 2>&1 | grep -v UV_NATIVE_TLS
{
 "200": [
  "This link is already bookmarked; the existing bookmark is returned unchanged.",
  {
   "$ref": "#/components/schemas/Bookmark"
  }
 ],
 "201": [
  "Successful Response",
  {
   "$ref": "#/components/schemas/Bookmark"
  }
 ],
 "422": [
  "The request is not valid.",
  {
   "$ref": "#/components/schemas/ErrorResponse"
  }
 ]
}
description: 201 with the new bookmark, or 200 with the existing one if the link is already saved
(specs/002-idempotent-duplicate-save).
[exit 0]
```

```console
$ git diff -- specs/002-idempotent-duplicate-save/tasks.md | head -80; git status --short; git diff --stat ep03-start -- specs/001-bookmarks-api
diff --git a/specs/002-idempotent-duplicate-save/tasks.md b/specs/002-idempotent-duplicate-save/tasks.md
index d47db80..3e4b513 100644
--- a/specs/002-idempotent-duplicate-save/tasks.md
+++ b/specs/002-idempotent-duplicate-save/tasks.md
@@ -33,7 +33,7 @@ its own.
 
 **Purpose**: Confirm the starting point
 
-- [ ] T001 Run the existing suite (`set -a; . ./.env; set +a; uv run --python 3.13 pytest -q`) from the repository root and confirm it passes before any change (baseline for `tests/`)
+- [X] T001 Run the existing suite (`set -a; . ./.env; set +a; uv run --python 3.13 pytest -q`) from the repository root and confirm it passes before any change (baseline for `tests/`)
 
 ---
 
@@ -41,7 +41,7 @@ its own.
 
 **Purpose**: Change the repository contract that both stories depend on
 
-- [ ] T002 Change `create_bookmark(session, data)` in `src/bookmarks_api/repository.py` to return `tuple[BookmarkRow, bool]` (`(row, created)`): keep `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`; if a row is returned, commit and return `(row, True)`; if nothing is returned, roll back the transaction and `SELECT` the row where `url_normalized` equals the normalized link and return `(existing_row, False)` without writing anything; if that `SELECT` finds no row (the conflicting row was deleted in between), retry the insert, so the save is stored as new and returns `(row, True)` (spec Edge Case: save racing a delete → 201); cap the loop at 3 attempts as a safety bound and raise `RuntimeError` only if all 3 fail (research.md §1). Update the docstring and remove the `DuplicateUrlError` import. The retry branch needs a delete to land between two statements and cannot be triggered deterministically against the real database without mocks (Constitution II), so it is covered by code review rather than a test
+- [X] T002 Change `create_bookmark(session, data)` in `src/bookmarks_api/repository.py` to return `tuple[BookmarkRow, bool]` (`(row, created)`): keep `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`; if a row is returned, commit and return `(row, True)`; if nothing is returned, roll back the transaction and `SELECT` the row where `url_normalized` equals the normalized link and return `(existing_row, False)` without writing anything; if that `SELECT` finds no row (the conflicting row was deleted in between), retry the insert, so the save is stored as new and returns `(row, True)` (spec Edge Case: save racing a delete → 201); cap the loop at 3 attempts as a safety bound and raise `RuntimeError` only if all 3 fail (research.md §1). Update the docstring and remove the `DuplicateUrlError` import. The retry branch needs a delete to land between two statements and cannot be triggered deterministically against the real database without mocks (Constitution II), so it is covered by code review rather than a test
 
 **Checkpoint**: Repository returns the existing row instead of raising; user story work can begin
 
@@ -60,13 +60,13 @@ stored, and one row exists.
 
 > Write these tests first and confirm they fail before T005-T006.
 
-- [ ] T003 [P] [US1] In `tests/integration/test_create_bookmark.py`, replace `test_equivalent_link_is_rejected_as_duplicate` and `test_duplicate_leaves_the_existing_bookmark_unchanged` with: (a) US1 AC1 — save `https://example.com/docs` (title "Docs"), then `HTTPS://Example.com/docs/#intro` → 200 and the body equals the first response body exactly (`id`, `url` `https://example.com/docs`, `title`, `tags`, `created_at`), `row_count() == 1`; (b) US1 AC2 — save `https://example.com/docs` title "Docs" tags `["api"]`, then the same link with title "Other" tags `["python", "new"]` → 200 with title "Docs" and tags `["api"]`, and the stored row (read via `engine`) still has title "Docs", tags `{api}` and the original `created_at`, and `GET /bookmarks` returns exactly one item; (c) US1 AC3 / FR-004 — keep `test_save_with_title_and_no_tags` (201 for a new link) unchanged as the FR-004 coverage; (d) edge cases — a duplicate save with an invalid title (`"t" * 201`) or 11 tags → 422 `validation_error` and the stored bookmark unchanged (FR-006); a link differing only by query string (`https://example.com/docs?x=1`) → 201 and `row_count() == 2`. (Delete-then-resave → 201 is already covered by `test_link_can_be_saved_again_after_delete` in `tests/integration/test_delete_bookmark.py`; leave it unchanged.)
-- [ ] T004 [P] [US1] In `tests/integration/test_errors.py`, remove `test_duplicate_error_envelope` (409 `duplicate_url` no longer exists) and add a test that a duplicate save returns 200 and a body without an `error` key; in `test_openapi_documents_every_operation` change the expected `post` error codes from `{"409", "422"}` to `{"422"}`, assert `"409"` is not among the `post` responses, and assert the `post` `"200"` response schema `$ref` ends with `/Bookmark` (contracts/openapi.yaml)
+- [X] T003 [P] [US1] In `tests/integration/test_create_bookmark.py`, replace `test_equivalent_link_is_rejected_as_duplicate` and `test_duplicate_leaves_the_existing_bookmark_unchanged` with: (a) US1 AC1 — save `https://example.com/docs` (title "Docs"), then `HTTPS://Example.com/docs/#intro` → 200 and the body equals the first response body exactly (`id`, `url` `https://example.com/docs`, `title`, `tags`, `created_at`), `row_count() == 1`; (b) US1 AC2 — save `https://example.com/docs` title "Docs" tags `["api"]`, then the same link with title "Other" tags `["python", "new"]` → 200 with title "Docs" and tags `["api"]`, and the stored row (read via `engine`) still has title "Docs", tags `{api}` and the original `created_at`, and `GET /bookmarks` returns exactly one item; (c) US1 AC3 / FR-004 — keep `test_save_with_title_and_no_tags` (201 for a new link) unchanged as the FR-004 coverage; (d) edge cases — a duplicate save with an invalid title (`"t" * 201`) or 11 tags → 422 `validation_error` and the stored bookmark unchanged (FR-006); a link differing only by query string (`https://example.com/docs?x=1`) → 201 and `row_count() == 2`. (Delete-then-resave → 201 is already covered by `test_link_can_be_saved_again_after_delete` in `tests/integration/test_delete_bookmark.py`; leave it unchanged.)
+- [X] T004 [P] [US1] In `tests/integration/test_errors.py`, remove `test_duplicate_error_envelope` (409 `duplicate_url` no longer exists) and add a test that a duplicate save returns 200 and a body without an `error` key; in `test_openapi_documents_every_operation` change the expected `post` error codes from `{"409", "422"}` to `{"422"}`, assert `"409"` is not among the `post` responses, and assert the `post` `"200"` response schema `$ref` ends with `/Bookmark` (contracts/openapi.yaml)
 
 ### Implementation for User Story 1
 
-- [ ] T005 [US1] Update `POST /bookmarks` in `src/bookmarks_api/routes.py`: keep `status_code=201` and `response_model=Bookmark`; inject `response: Response`; call `repository.create_bookmark` (T002) and set `response.status_code = status.HTTP_200_OK` when `created` is false; in `responses`, remove the `409` entry and add `200: {"model": Bookmark, "description": "This link is already bookmarked; the existing bookmark is returned unchanged."}` (contracts/openapi.yaml)
-- [ ] T006 [US1] Remove `DuplicateUrlError` and its `handle_duplicate` 409 handler from `src/bookmarks_api/errors.py`; keep the generic `409: "conflict"` entry in `STATUS_CODES` for framework HTTP exceptions (research.md §3)
+- [X] T005 [US1] Update `POST /bookmarks` in `src/bookmarks_api/routes.py`: keep `status_code=201` and `response_model=Bookmark`; inject `response: Response`; call `repository.create_bookmark` (T002) and set `response.status_code = status.HTTP_200_OK` when `created` is false; in `responses`, remove the `409` entry and add `200: {"model": Bookmark, "description": "This link is already bookmarked; the existing bookmark is returned unchanged."}` (contracts/openapi.yaml)
+- [X] T006 [US1] Remove `DuplicateUrlError` and its `handle_duplicate` 409 handler from `src/bookmarks_api/errors.py`; keep the generic `409: "conflict"` entry in `STATUS_CODES` for framework HTTP exceptions (research.md §3)
 
 **Checkpoint**: User Story 1 is fully functional and testable on its own
 
@@ -82,11 +82,11 @@ are `[200, 201]`, both bodies have the same `id`, one row exists.
 
 ### Tests for User Story 2
 
-- [ ] T007 [US2] In `tests/integration/test_create_bookmark.py`, update `test_concurrent_saves_of_the_same_link_leave_one_bookmark`: collect each response (status and body) from the two threads (`https://example.com/race` and `https://EXAMPLE.com/race/`, `threading.Barrier(2)`), assert `sorted(statuses) == [200, 201]`, both bodies have the same `id`, and `row_count() == 1`; run the race 20 times in a loop (truncating via `DELETE /bookmarks/{id}` between iterations) so a flaky interleaving would be caught (FR-005, SC-003)
+- [X] T007 [US2] In `tests/integration/test_create_bookmark.py`, update `test_concurrent_saves_of_the_same_link_leave_one_bookmark`: collect each response (status and body) from the two threads (`https://example.com/race` and `https://EXAMPLE.com/race/`, `threading.Barrier(2)`), assert `sorted(statuses) == [200, 201]`, both bodies have the same `id`, and `row_count() == 1`; run the race 20 times in a loop (truncating via `DELETE /bookmarks/{id}` between iterations) so a flaky interleaving would be caught (FR-005, SC-003)
 
 ### Implementation for User Story 2
 
-- [ ] T008 [US2] Confirm `create_bookmark` in `src/bookmarks_api/repository.py` (T002) needs no extra locking: T007 passes all 20 iterations with no code beyond T002 (the losing `INSERT ... ON CONFLICT DO NOTHING` waits for the winner's commit, then its fresh `SELECT` sees the committed row, research.md §1). Done when T007 passes; record the result in the implement capture
+- [X] T008 [US2] Confirm `create_bookmark` in `src/bookmarks_api/repository.py` (T002) needs no extra locking: T007 passes all 20 iterations with no code beyond T002 (the losing `INSERT ... ON CONFLICT DO NOTHING` waits for the winner's commit, then its fresh `SELECT` sees the committed row, research.md §1). Done when T007 passes; record the result in the implement capture
 
 **Checkpoint**: User Stories 1 and 2 both work independently
 
@@ -96,9 +96,9 @@ are `[200, 201]`, both bodies have the same `id`, one row exists.
 
 **Purpose**: Documentation and final validation
 
-- [ ] T009 [P] Update the endpoint table in `README.md`: `POST /bookmarks` row reads "Save `{"url", "title", "tags"}`; 201 when new, 200 with the existing bookmark (unchanged) if the link is already saved"
-- [ ] T010 Search `src/` and `tests/` for leftover `DuplicateUrlError`, `duplicate_url` and `409` references tied to duplicate saves and remove them (`grep -rn "DuplicateUrlError\|duplicate_url\|409" src tests`)
-- [ ] T011 Run the full suite on Python 3.11, 3.12 and 3.13 (`uv run --python 3.1X pytest -q` after `set -a; . ./.env; set +a`) and walk the manual table in `specs/002-idempotent-duplicate-save/quickstart.md`
+- [X] T009 [P] Update the endpoint table in `README.md`: `POST /bookmarks` row reads "Save `{"url", "title", "tags"}`; 201 when new, 200 with the existing bookmark (unchanged) if the link is already saved"
+- [X] T010 Search `src/` and `tests/` for leftover `DuplicateUrlError`, `duplicate_url` and `409` references tied to duplicate saves and remove them (`grep -rn "DuplicateUrlError\|duplicate_url\|409" src tests`)
+- [X] T011 Run the full suite on Python 3.11, 3.12 and 3.13 (`uv run --python 3.1X pytest -q` after `set -a; . ./.env; set +a`) and walk the manual table in `specs/002-idempotent-duplicate-save/quickstart.md`
 
 ---
 
 M README.md
 M specs/002-idempotent-duplicate-save/tasks.md
 M src/bookmarks_api/errors.py
 M src/bookmarks_api/repository.py
 M src/bookmarks_api/routes.py
 M tests/integration/test_create_bookmark.py
 M tests/integration/test_errors.py
?? episodes/ep03/capture/forward-r4/05-implement.md
[exit 0]
```

### Review findings (code + artifact diffs)

- Code matches plan/research: single `INSERT ... ON CONFLICT DO NOTHING RETURNING` write path; existing row read with a fresh statement and returned with `created=False`; retry loop bounded at 3 (`MAX_SAVE_ATTEMPTS`); route sets 200 via injected `Response`; `DuplicateUrlError` and its 409 handler deleted; generic `409: "conflict"` mapping kept (research.md §3).
- Generated OpenAPI for `POST /bookmarks` = {200 Bookmark, 201 Bookmark, 422 ErrorResponse}, no 409 — matches `specs/002-idempotent-duplicate-save/contracts/openapi.yaml`. Side effect: the route docstring becomes the operation `description` in the generated OpenAPI (it mentions `specs/002-idempotent-duplicate-save`); harmless, left as is.
- `git diff --stat ep03-start -- specs/001-bookmarks-api` is empty: 001 untouched. Its spec/plan/research/contract/quickstart/tasks still describe 409 (expected under flow-forward; inventoried in 002 plan.md "Superseded statements").
- Minor, not changed: module docstring of `tests/integration/test_create_bookmark.py` still reads "User Story 1 - Save a bookmark (spec.md, scenarios 1 to 4)." (refers to 001's spec); the new tests carry "002 ..." docstrings.
- Retry branch (delete between INSERT and SELECT) has no automated test, as recorded in T002 (no mocks per Constitution II).
- Identity gaps on duplicate saves (see quickstart observation) — not covered by any spec statement.

## Spec Kit completion report (verbatim)

- Tasks: 11/11 complete and marked [X] in `specs/002-idempotent-duplicate-save/tasks.md`.
- Phases: Setup (T001) ✓, Foundational (T002) ✓, US1 (T003-T006) ✓, US2 (T007-T008) ✓, Polish (T009-T011) ✓.
- TDD: new tests failed before T005/T006 (24 failed / 77 passed), all pass after (101 passed).
- Tests: 101 passed on Python 3.11, 3.12, 3.13. Concurrency test (20 races per run) passed 5/5 extra runs.
- Quickstart manual table: all 6 steps gave the expected statuses (201, 200 identical body, 1 item, 422, 201, 204 then 201).
- Files changed: src/bookmarks_api/{repository,routes,errors}.py, tests/integration/{test_create_bookmark,test_errors}.py, README.md, specs/002-idempotent-duplicate-save/tasks.md.
- Extension hooks (after_implement): `.specify/extensions.yml` absent — skipped.

End: 2026-10-24T12:44:09Z
