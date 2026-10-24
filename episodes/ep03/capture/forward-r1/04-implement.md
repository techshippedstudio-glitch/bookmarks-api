# Step 04 — implement (forward-r1)

Start: 2026-10-24T11:45:49Z

`.specify/extensions.yml` absent: no before_implement / after_implement hooks.

Note on step 03 capture: the format check printed `[exit 1]` because `grep -vc` found 0 malformed lines (grep exits 1 on no match); 14 tasks, 0 malformed.

```console
$ .specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
{"FEATURE_DIR":"/home/claude/runs/forward-r1/specs/002-idempotent-duplicate-save","AVAILABLE_DOCS":["research.md","data-model.md","contracts/","quickstart.md","tasks.md"]}
[exit 0]
```

```console
$ for f in specs/002-idempotent-duplicate-save/checklists/*.md; do t=$(grep -cE "^- \[( |x|X)\]" $f); c=$(grep -cE "^- \[(x|X)\]" $f); echo "$(basename $f) total=$t checked=$c unchecked=$((t-c))"; done
requirements.md total=16 checked=16 unchecked=0
[exit 0]
```

```console
$ git rev-parse --git-dir; ls Dockerfile* .eslintrc* eslint.config.* .prettierrc* .npmrc package.json *.tf 2>&1 | head; grep -nE "__pycache__|\*\.py\[cod\]|\.venv|venv/|dist/|egg-info|\.DS_Store|Thumbs.db|\.env" .gitignore; cat .dockerignore; grep -n -i docker specs/002-idempotent-duplicate-save/plan.md
/home/claude/bookmarks-api/.git/worktrees/forward-r1
ls: cannot access 'Dockerfile*': No such file or directory
ls: cannot access '.eslintrc*': No such file or directory
ls: cannot access 'eslint.config.*': No such file or directory
ls: cannot access '.prettierrc*': No such file or directory
ls: cannot access '.npmrc': No such file or directory
ls: cannot access 'package.json': No such file or directory
ls: cannot access '*.tf': No such file or directory
2:.env
3:.env.*
4:!.env.example
7:__pycache__/
8:*.py[cod]
9:*.egg-info/
10:.venv/
11:venv/
13:dist/
25:.DS_Store
26:Thumbs.db
.git/
.venv/
__pycache__/
*.pyc
.pytest_cache/
.env
.env.*
!.env.example
*.log
[exit 1]
```

| Checklist | Total | Checked | Unchecked | Status |
|-----------|-------|---------|-----------|--------|
| requirements.md | 16 | 16 | 0 | ✓ PASS |

All checklists passed; proceeding. Ignore files: repo is git; `.gitignore` already has the Python and universal patterns; `.dockerignore` exists (docker-compose present) with essential patterns; no other tool configs. No changes needed.

### Baseline (before any change)

```console
$ set -a; . ./.env; set +a; uv run --python 3.13 pytest -q 2>&1 | tail -5
      Built bookmarks-api @ file:///home/claude/runs/forward-r1
Installed 29 packages in 22ms
........................................................................ [ 73%]
..........................                                               [100%]
98 passed in 2.95s
[exit 0]
```

### Tests written first (T001–T005, T009) — expected to fail

```console
$ set -a; . ./.env; set +a; uv run --python 3.13 pytest -q 2>&1 | tail -15
            assert operation["requestBody"]["content"]["application/json"]["schema"]["$ref"].endswith(
                "/BookmarkCreate"
            )
>           assert "409" not in operation["responses"]  # specs/002 FR-007
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E           AssertionError: assert '409' not in {'201': {'description': 'Successful Response', 'content': {'application/json': {'schema': {'$ref': '#/components/schem...e request is not valid.', 'content': {'application/json': {'schema': {'$ref': '#/components/schemas/ErrorResponse'}}}}}

tests/integration/test_errors.py:85: AssertionError
=========================== short test summary info ============================
FAILED tests/integration/test_create_bookmark.py::test_equivalent_link_returns_existing_bookmark_with_200
FAILED tests/integration/test_create_bookmark.py::test_duplicate_save_ignores_title_and_tags_and_changes_nothing
FAILED tests/integration/test_create_bookmark.py::test_concurrent_saves_of_the_same_link_leave_one_bookmark
FAILED tests/integration/test_errors.py::test_duplicate_save_is_not_an_error
FAILED tests/integration/test_errors.py::test_openapi_documents_every_operation[/bookmarks-post]
5 failed, 98 passed in 2.80s
[exit 0]
```

### After T006–T008 (repository, routes, errors)

```console
$ set -a; . ./.env; set +a; uv run --python 3.13 pytest -q 2>&1 | tail -15
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
........................................................................ [ 69%]
...............................                                          [100%]
103 passed in 2.83s
[exit 0]
```

### Race test repeated 30 times (flakiness check)

```console
$ set -a; . ./.env; set +a; for i in $(seq 30); do uv run --python 3.13 pytest -q -p no:cacheprovider "tests/integration/test_create_bookmark.py::test_concurrent_saves_of_the_same_link_leave_one_bookmark" 2>&1 | tail -1; done | sort | uniq -c
      5 1 passed in 0.14s
      7 1 passed in 0.15s
      4 1 passed in 0.16s
      7 1 passed in 0.17s
      1 1 passed in 0.18s
      3 1 passed in 0.19s
      1 1 passed in 0.20s
      2 1 passed in 0.21s
[exit 0]
```

### T011 README + T012 grep

```console
$ grep -n "POST /bookmarks" README.md; grep -rn "DuplicateUrlError\|duplicate_url\|409" src tests
100:| `POST /bookmarks` | Save `{"url", "title", "tags"}`; 201 for a new link; 200 with the existing bookmark, unchanged, if the link is already saved |
src/bookmarks_api/errors.py:35:STATUS_CODES = {400: "bad_request", 404: "not_found", 405: "method_not_allowed", 409: "conflict"}
tests/integration/test_errors.py:85:        assert "409" not in operation["responses"]  # specs/002 FR-007
grep: tests/integration/__pycache__/test_errors.cpython-313-pytest-9.1.1.pyc: binary file matches
[exit 0]
```

### T013 full suite on 3.11 / 3.12 / 3.13

```console
$ set -a; . ./.env; set +a; uv run --python 3.11 pytest -q 2>&1 | tail -3
........................................................................ [ 69%]
...............................                                          [100%]
103 passed in 3.24s
[exit 0]
```

```console
$ set -a; . ./.env; set +a; uv run --python 3.12 pytest -q 2>&1 | tail -3
........................................................................ [ 69%]
...............................                                          [100%]
103 passed in 2.85s
[exit 0]
```

```console
$ set -a; . ./.env; set +a; uv run --python 3.13 pytest -q 2>&1 | tail -3
........................................................................ [ 69%]
...............................                                          [100%]
103 passed in 3.07s
[exit 0]
```

### T014 quickstart manual validation (server on port 18731, DATABASE_URL set to this run's own test database; the dev database in .env is shared, so it was not used)

```console
$ bash /tmp/claude-0/-home-claude/2f87c0d2-82af-5dcb-b1b6-181ed3dee423/scratchpad/forward-r1-only/qs.sh
step1:
{"id":1,"url":"https://fastapi.tiangolo.com/","title":"FastAPI docs","tags":["api"],"created_at":"2026-10-24T11:48:21.129398Z"} HTTP 201
step2:
{"id":1,"url":"https://fastapi.tiangolo.com/","title":"FastAPI docs","tags":["api"],"created_at":"2026-10-24T11:48:21.129398Z"} HTTP 200
step3:
{"items":[{"id":1,"url":"https://fastapi.tiangolo.com/","title":"FastAPI docs","tags":["api"],"created_at":"2026-10-24T11:48:21.129398Z"}],"total":1,"limit":20,"next_cursor":null} HTTP 200
step4:
{"error":{"code":"validation_error","message":"The request is not valid.","details":[{"field":"tags","message":"Tag 'no spaces' is not valid: use 1 to 30 letters, digits or hyphens."}]}} HTTP 422
step5:
['200', '201', '422']
[exit 143]
```

Note: `[exit 143]` above is the uvicorn process being killed by the script (SIGTERM via `wait`); all five steps produced the expected output.

### Tasks marked [X]

```console
$ grep -cE "^- \[X\] T0" specs/002-idempotent-duplicate-save/tasks.md; grep -cE "^- \[ \] T0" specs/002-idempotent-duplicate-save/tasks.md
14
0
[exit 1]
```

## Review: code diff

```console
$ git diff ep03-forward-r1-tasks -- src README.md
diff --git a/README.md b/README.md
index 5c4557f..63eba18 100644
--- a/README.md
+++ b/README.md
@@ -97,7 +97,7 @@ uv run pytest                                          # tests, against the book
 
 | Endpoint | What it does |
 | --- | --- |
-| `POST /bookmarks` | Save `{"url", "title", "tags"}`; 409 if the link is already saved |
+| `POST /bookmarks` | Save `{"url", "title", "tags"}`; 201 for a new link; 200 with the existing bookmark, unchanged, if the link is already saved |
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
index f93517e..8cfafdc 100644
--- a/src/bookmarks_api/repository.py
+++ b/src/bookmarks_api/repository.py
@@ -6,16 +6,25 @@ from sqlalchemy import delete, func, select, tuple_
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
+    is already saved, the existing row is returned unchanged with ``created=False``; the title and
+    tags in ``data`` are ignored (specs/002-idempotent-duplicate-save, FR-002/FR-003).
+
+    ON CONFLICT DO NOTHING relies on the unique index, so two concurrent saves of the same new link
+    store one row: one caller gets ``created=True``, the other the same row with ``created=False``.
+    If the conflicting row is deleted before it can be read, the insert is retried.
     """
     normalized = normalize_url(data.url)
     statement = (
@@ -24,15 +33,19 @@ def create_bookmark(session: Session, data: BookmarkCreate) -> BookmarkRow:
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
+        session.rollback()  # read-only transaction; nothing to keep
+        if existing is not None:
+            return existing, False
+    raise RuntimeError("Could not save or find the bookmark after repeated conflicts.")
 
 
 def list_bookmarks(
diff --git a/src/bookmarks_api/routes.py b/src/bookmarks_api/routes.py
index cc51123..5b360fb 100644
--- a/src/bookmarks_api/routes.py
+++ b/src/bookmarks_api/routes.py
@@ -40,13 +40,25 @@ def _reject_offset(value: str | None) -> None:
     status_code=status.HTTP_201_CREATED,
     response_model=Bookmark,
     summary="Save a bookmark",
+    description=(
+        "201 with the new bookmark when the link is not saved yet; 200 with the existing "
+        "bookmark, unchanged, when the link (after normalization) is already saved. "
+        "The title and tags of a duplicate save are ignored."
+    ),
     responses={
-        409: {"model": ErrorResponse, "description": "This link is already bookmarked."},
+        200: {
+            "model": Bookmark,
+            "description": "This link was already saved; the existing bookmark is returned unchanged.",
+        },
+        201: {"description": "Bookmark saved."},
         **ERROR_422,
     },
 )
-def create_bookmark(data: BookmarkCreate, session: SessionDep) -> Bookmark:
-    return Bookmark.model_validate(repository.create_bookmark(session, data))
+def create_bookmark(data: BookmarkCreate, session: SessionDep, response: Response) -> Bookmark:
+    row, created = repository.create_bookmark(session, data)
+    if not created:
+        response.status_code = status.HTTP_200_OK
+    return Bookmark.model_validate(row)
 
 
 @router.get(
[exit 0]
```

## Review: test diff (stat)

```console
$ git diff --stat ep03-forward-r1-tasks -- tests; git diff ep03-forward-r1-tasks -- tests/integration/test_errors.py
 tests/integration/test_create_bookmark.py | 95 ++++++++++++++++++++++++++-----
 tests/integration/test_errors.py          | 20 ++++---
 2 files changed, 91 insertions(+), 24 deletions(-)
diff --git a/tests/integration/test_errors.py b/tests/integration/test_errors.py
index 1f473e0..08cdc8c 100644
--- a/tests/integration/test_errors.py
+++ b/tests/integration/test_errors.py
@@ -22,14 +22,14 @@ def test_validation_error_envelope(client: TestClient) -> None:
     assert fields == {"url", "title"}
 
 
-def test_duplicate_error_envelope(client: TestClient) -> None:
+def test_duplicate_save_is_not_an_error(client: TestClient) -> None:
+    """specs/002 FR-002: a duplicate save returns 200 with a bookmark, not an error envelope."""
     client.post("/bookmarks", json={"url": "https://example.com", "title": "A"})
+    response = client.post("/bookmarks", json={"url": "https://example.com/", "title": "B"})
 
-    assert_envelope(
-        client.post("/bookmarks", json={"url": "https://example.com/", "title": "B"}),
-        409,
-        "duplicate_url",
-    )
+    assert response.status_code == 200
+    assert "error" not in response.json()
+    assert set(response.json()) == {"id", "url", "title", "tags", "created_at"}
 
 
 def test_not_found_error_envelope(client: TestClient) -> None:
@@ -74,7 +74,7 @@ def test_openapi_documents_every_operation(client: TestClient, path: str, method
     operation = spec["paths"][path][method]
 
     assert operation["summary"]
-    error_codes = {"post": {"409", "422"}, "get": {"422"}, "delete": {"404", "422"}}[method]
+    error_codes = {"post": {"422"}, "get": {"422"}, "delete": {"404", "422"}}[method]
     for code in error_codes:
         schema = operation["responses"][code]["content"]["application/json"]["schema"]
         assert schema["$ref"].endswith("/ErrorResponse")
@@ -82,8 +82,10 @@ def test_openapi_documents_every_operation(client: TestClient, path: str, method
         assert operation["requestBody"]["content"]["application/json"]["schema"]["$ref"].endswith(
             "/BookmarkCreate"
         )
-        success = operation["responses"]["201"]["content"]["application/json"]["schema"]
-        assert success["$ref"].endswith("/Bookmark")
+        assert "409" not in operation["responses"]  # specs/002 FR-007
+        for status in ("200", "201"):
+            success = operation["responses"][status]["content"]["application/json"]["schema"]
+            assert success["$ref"].endswith("/Bookmark")
     if method == "get":
         success = operation["responses"]["200"]["content"]["application/json"]["schema"]
         assert success["$ref"].endswith("/BookmarkPage")
[exit 0]
```

## Review: artifact diffs

```console
$ git diff --stat ep03-start -- specs; git diff ep03-start -- specs/001-bookmarks-api | wc -l
 .../checklists/requirements.md                     |  43 +++++
 .../contracts/openapi.yaml                         |  80 ++++++++++
 specs/002-idempotent-duplicate-save/data-model.md  |  23 +++
 specs/002-idempotent-duplicate-save/plan.md        | 102 ++++++++++++
 specs/002-idempotent-duplicate-save/quickstart.md  |  31 ++++
 specs/002-idempotent-duplicate-save/research.md    |  59 +++++++
 specs/002-idempotent-duplicate-save/spec.md        | 143 +++++++++++++++++
 specs/002-idempotent-duplicate-save/tasks.md       | 175 +++++++++++++++++++++
 8 files changed, 656 insertions(+)
0
[exit 0]
```

## Review finding R1: second rollback expires the returned row

Hypothesis: `session.rollback()` expires every loaded instance, so the duplicate path returns an expired row and serialization issues an extra SELECT (and a 500 `ObjectDeletedError` if the row is deleted in between).

```console
$ set -a; . ./.env; set +a; uv run --python 3.13 python /tmp/claude-0/-home-claude/2f87c0d2-82af-5dcb-b1b6-181ed3dee423/scratchpad/forward-r1-only/expire_check.py
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
unknown PostgreSQL timezone: 'ASIA0'; will use UTC
created: False expired attrs after return: ['created_at', 'id', 'tags', 'title', 'url', 'url_normalized']
[exit 0]
```

Fix: replaced the second `session.rollback()` with `session.commit()` in `src/bookmarks_api/repository.py` (session factories use `expire_on_commit=False`).

```console
$ set -a; . ./.env; set +a; uv run --python 3.13 python /tmp/claude-0/-home-claude/2f87c0d2-82af-5dcb-b1b6-181ed3dee423/scratchpad/forward-r1-only/expire_check.py 2>&1 | grep created; git diff -- src/bookmarks_api/repository.py
created: False expired attrs after return: []
diff --git a/src/bookmarks_api/repository.py b/src/bookmarks_api/repository.py
index f93517e..2202c35 100644
--- a/src/bookmarks_api/repository.py
+++ b/src/bookmarks_api/repository.py
@@ -6,16 +6,25 @@ from sqlalchemy import delete, func, select, tuple_
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
+    is already saved, the existing row is returned unchanged with ``created=False``; the title and
+    tags in ``data`` are ignored (specs/002-idempotent-duplicate-save, FR-002/FR-003).
+
+    ON CONFLICT DO NOTHING relies on the unique index, so two concurrent saves of the same new link
+    store one row: one caller gets ``created=True``, the other the same row with ``created=False``.
+    If the conflicting row is deleted before it can be read, the insert is retried.
     """
     normalized = normalize_url(data.url)
     statement = (
@@ -24,15 +33,21 @@ def create_bookmark(session: Session, data: BookmarkCreate) -> BookmarkRow:
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
+        # End the read-only transaction with commit, not rollback: rollback expires the loaded
+        # row, which would reload it lazily (or fail if it was deleted meanwhile).
+        session.commit()
+        if existing is not None:
+            return existing, False
+    raise RuntimeError("Could not save or find the bookmark after repeated conflicts.")
 
 
 def list_bookmarks(
[exit 0]
```

```console
$ set -a; . ./.env; set +a; uv run --python 3.11 pytest -q 2>&1 | tail -1
103 passed in 2.86s
[exit 0]
```

```console
$ set -a; . ./.env; set +a; uv run --python 3.12 pytest -q 2>&1 | tail -1
103 passed in 3.33s
[exit 0]
```

```console
$ set -a; . ./.env; set +a; uv run --python 3.13 pytest -q 2>&1 | tail -1
103 passed in 3.29s
[exit 0]
```

Other output seen: `unknown PostgreSQL timezone: 'ASIA0'; will use UTC` is printed by psycopg when the standalone script connects (environment noise; not seen inside pytest output, no effect on results).

## Review: artifact diffs (findings)

- `specs/001-bookmarks-api/` unchanged (`git diff ep03-start -- specs/001-bookmarks-api | wc -l` = 0).
- specs/002 artifacts are consistent with the implementation: spec FR-002/FR-003/FR-005/FR-007, plan, research (ON CONFLICT DO NOTHING + lookup, 201/200 via `Response`), contract delta (200/201/422, no 409) match the generated `/openapi.json` (quickstart step 5: `['200', '201', '422']`).
- Stale-by-design: specs/001 still describes the 409 duplicate rule in spec.md (Clarifications, US1 AC3, Edge Cases, FR-004), plan.md (Constitution III row), research.md ("Preventing duplicate links"), quickstart.md (manual step 2), tasks.md (T008/T012/T015/T016/T026), contracts/openapi.yaml (409 response, `duplicate_url` in the code enum). The flow-forward rule forbids editing them; specs/002 states it supersedes these.
- Review finding R1 (code): fixed above (rollback expired the returned row → commit instead). research.md's description ("end the transaction and SELECT") still matches.
- Not covered by a test: the bounded retry branch when the conflicting row is deleted between the conflict and the lookup (hard to trigger deterministically through the API).

## Spec Kit implement — completion report

- All 14 tasks in `specs/002-idempotent-duplicate-save/tasks.md` completed and marked `[X]`.
- Phase 3 (US1): tests T001–T005 written first (5 failed against the 409 code as expected; T004's two new tests passed already), then T006 repository `(row, created)`, T007 route 201/200 + OpenAPI 200/201/422, T008 removed `DuplicateUrlError` and its 409 handler.
- Phase 4 (US2): T009 parametrized invalid re-save test (passes; validation precedes duplicate check); T010 no code change needed.
- Phase 5: T011 README endpoint row; T012 grep — only the generic `409: "conflict"` map remains in `errors.py`; T013 full suite 103 passed on 3.11, 3.12, 3.13 (re-run after fix R1: 103/103 each); T014 quickstart steps 1–5 as expected.
- Race test run 30× in isolation: 30/30 passed.
- Checklist gate: requirements.md 16/16 PASS.
- Hooks: none.

End: 2026-10-24T11:49:26Z
