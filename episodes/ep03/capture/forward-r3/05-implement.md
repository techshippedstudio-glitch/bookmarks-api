# Step 05 — implement (forward-r3)

Start: 2026-10-24T12:40:42Z

## Commands

```console
$ .specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
{"FEATURE_DIR":"/home/claude/runs/forward-r3/specs/002-idempotent-duplicate-save","AVAILABLE_DOCS":["research.md","data-model.md","contracts/","quickstart.md","tasks.md"]}
[exit 0]
```

```console
$ for f in specs/002-idempotent-duplicate-save/checklists/*.md; do t=$(grep -cE "^- \[( |x|X)\]" $f); c=$(grep -cE "^- \[(x|X)\]" $f); echo "$(basename $f) total=$t checked=$c unchecked=$((t-c))"; done
requirements.md total=16 checked=16 unchecked=0
[exit 0]
```

```console
$ git rev-parse --git-dir; ls Dockerfile* .eslintrc* eslint.config.* .prettierrc* .npmrc package.json 2>&1 | head; grep -nE "__pycache__|\*\.py\[cod\]|\.venv|venv/|dist/|egg-info|\.DS_Store|Thumbs.db|\.env" .gitignore; grep -n -i docker specs/002-idempotent-duplicate-save/plan.md || echo "no Docker in 002 plan"
/home/claude/bookmarks-api/.git/worktrees/forward-r3
ls: cannot access 'Dockerfile*': No such file or directory
ls: cannot access '.eslintrc*': No such file or directory
ls: cannot access 'eslint.config.*': No such file or directory
ls: cannot access '.prettierrc*': No such file or directory
ls: cannot access '.npmrc': No such file or directory
ls: cannot access 'package.json': No such file or directory
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
no Docker in 002 plan
[exit 0]
```

Checklist gate: requirements.md 16/16 checked — PASS, proceed. Ignore files: git repo → .gitignore already has Python + universal patterns; no Dockerfile/ESLint/Prettier/npm/terraform files → no other ignore files needed.

### T001 baseline

```console
$ set -a; . ./.env; set +a; echo "TEST_DATABASE_URL db=${TEST_DATABASE_URL##*/}"; uv run --python 3.13 pytest -q 2>&1 | tail -5
TEST_DATABASE_URL db=bookmarks_test_forward_r3
      Built bookmarks-api @ file:///home/claude/runs/forward-r3
Installed 29 packages in 16ms
........................................................................ [ 73%]
..........................                                               [100%]
98 passed in 3.17s
[exit 0]
```

### T002-T007, T011 tests written first (test_create_bookmark.py, test_errors.py); expect failures before implementation

```console
$ git diff --stat; set -a; . ./.env; set +a; uv run --python 3.13 pytest -q tests/integration/test_create_bookmark.py tests/integration/test_errors.py 2>&1 | grep -E "^(FAILED|ERROR)|passed|failed"
 tests/integration/test_create_bookmark.py | 116 ++++++++++++++++++++++++++----
 tests/integration/test_errors.py          |  18 ++---
 2 files changed, 108 insertions(+), 26 deletions(-)
FAILED tests/integration/test_create_bookmark.py::test_equivalent_link_returns_existing_bookmark
FAILED tests/integration/test_create_bookmark.py::test_duplicate_leaves_the_existing_bookmark_unchanged
FAILED tests/integration/test_create_bookmark.py::test_bookmark_deleted_mid_save_is_saved_as_new
FAILED tests/integration/test_create_bookmark.py::test_concurrent_saves_of_the_same_link_leave_one_bookmark
FAILED tests/integration/test_errors.py::test_openapi_documents_every_operation[/bookmarks-post]
5 failed, 26 passed in 1.09s
[exit 0]
```

### T008-T010 implemented (repository.py, routes.py, errors.py)

Note: first draft of T008 called `session.rollback()` after `_find_existing` returned the row; removed before the first test run because rollback expires loaded instances (forcing a lazy reload, and a possible ObjectDeletedError if the row vanished). Final code below.

```console
$ git diff src/
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
index f93517e..b81dab3 100644
--- a/src/bookmarks_api/repository.py
+++ b/src/bookmarks_api/repository.py
@@ -6,16 +6,31 @@ from sqlalchemy import delete, func, select, tuple_
 from sqlalchemy.dialects.postgresql import insert
 from sqlalchemy.orm import Session
 
-from bookmarks_api.errors import DuplicateUrlError, NotFoundError
+from bookmarks_api.errors import NotFoundError
 from bookmarks_api.models import BookmarkRow
 from bookmarks_api.normalize import normalize_url
 from bookmarks_api.schemas import BookmarkCreate
 
+MAX_SAVE_ATTEMPTS = 3
 
-def create_bookmark(session: Session, data: BookmarkCreate) -> BookmarkRow:
-    """Insert a bookmark, or raise DuplicateUrlError if its normalized link already exists.
 
-    ON CONFLICT DO NOTHING relies on the unique index, so this holds under concurrent saves.
+def _find_existing(session: Session, normalized: str) -> BookmarkRow | None:
+    """Return the bookmark stored for a normalized link, or None."""
+    return session.scalars(
+        select(BookmarkRow).where(BookmarkRow.url_normalized == normalized)
+    ).one_or_none()
+
+
+def create_bookmark(session: Session, data: BookmarkCreate) -> tuple[BookmarkRow, bool]:
+    """Save a bookmark and return ``(row, created)``.
+
+    If the normalized link is new, the row is inserted and ``created`` is True. If it is already
+    bookmarked, the existing row is returned unchanged and ``created`` is False; the request's
+    title and tags are ignored (specs/002-idempotent-duplicate-save FR-001, FR-002).
+
+    ON CONFLICT DO NOTHING relies on the unique index, so this holds under concurrent saves: the
+    losing insert waits for the winner, inserts nothing, then reads the committed row. If that row
+    is deleted before it can be read, the insert is retried.
     """
     normalized = normalize_url(data.url)
     statement = (
@@ -24,15 +39,20 @@ def create_bookmark(session: Session, data: BookmarkCreate) -> BookmarkRow:
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
+        existing = _find_existing(session, normalized)
+        if existing is not None:
+            # Nothing was written; the read-only transaction ends when the session closes.
+            # (A rollback here would expire the loaded row and force a reload.)
+            return existing, False
+    raise RuntimeError(
+        f"Could not save or find a bookmark for {normalized!r} after {MAX_SAVE_ATTEMPTS} attempts."
+    )
 
 
 def list_bookmarks(
diff --git a/src/bookmarks_api/routes.py b/src/bookmarks_api/routes.py
index cc51123..d0573af 100644
--- a/src/bookmarks_api/routes.py
+++ b/src/bookmarks_api/routes.py
@@ -41,12 +41,20 @@ def _reject_offset(value: str | None) -> None:
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
+    row, created = repository.create_bookmark(session, data)
+    if not created:
+        response.status_code = status.HTTP_200_OK
+    return Bookmark.model_validate(row)
 
 
 @router.get(
[exit 0]
```

```console
$ grep -rn --include=*.py "DuplicateUrlError\|duplicate_url" src tests || echo "no remaining references"
no remaining references
[exit 0]
```

```console
$ set -a; . ./.env; set +a; uv run --python 3.13 pytest -q 2>&1 | tail -4
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
........................................................................ [ 71%]
.............................                                            [100%]
101 passed in 3.49s
[exit 0]
```

### T012 concurrency verification (20 runs)

```console
$ set -a; . ./.env; set +a; ok=0; for i in $(seq 20); do uv run --python 3.13 pytest -q -k concurrent tests/integration/test_create_bookmark.py 2>&1 | grep -q "1 passed" && ok=$((ok+1)) || { echo "run $i FAILED"; break; }; done; echo "passed runs: $ok/20"
passed runs: 20/20
[exit 0]
```

### T013 README

```console
$ git diff README.md
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
 
[exit 0]
```

### T014 full suite on 3.11, 3.12, 3.13

```console
$ set -a; . ./.env; set +a; for v in 3.11 3.12 3.13; do echo "== Python $v"; uv run --python $v pytest -q 2>&1 | tail -1; done
== Python 3.11
101 passed in 3.12s
== Python 3.12
101 passed in 3.34s
== Python 3.13
101 passed in 2.95s
[exit 0]
```

### T015 quickstart manual validation (script /home/claude/scratch/forward-r3/quickstart.sh: loads .env, sets DATABASE_URL to this run's TEST_DATABASE_URL, truncates, starts uvicorn on :8765, runs quickstart steps 1-5 with curl, stops the server)

```console
$ cat /home/claude/scratch/forward-r3/quickstart.sh; echo ----; bash /home/claude/scratch/forward-r3/quickstart.sh 2>&1 | grep -v UV_NATIVE_TLS
#!/usr/bin/env bash
# Manual quickstart validation for 002 against the run's own test database.
set -a; . ./.env; set +a
export DATABASE_URL="$TEST_DATABASE_URL"
uv run --python 3.13 python -c "
import os, sqlalchemy as sa
from bookmarks_api.config import sqlalchemy_url
e = sa.create_engine(sqlalchemy_url(os.environ['DATABASE_URL']))
with e.begin() as c: c.execute(sa.text('TRUNCATE bookmarks RESTART IDENTITY'))
print('truncated', os.environ['DATABASE_URL'].rsplit('/',1)[1])
"
uv run --python 3.13 uvicorn bookmarks_api.main:app --port 8765 --log-level warning &
PID=$!
for i in $(seq 50); do curl -s -o /dev/null http://127.0.0.1:8765/openapi.json && break; sleep 0.2; done
B=http://127.0.0.1:8765
post() { curl -s -w '  -> HTTP %{http_code}\n' -H 'Content-Type: application/json' -X POST "$B/bookmarks" -d "$1"; }
echo "Step 1:"; post '{"url": "https://fastapi.tiangolo.com/", "title": "FastAPI docs", "tags": ["python"]}'
echo "Step 2:"; post '{"url": "HTTPS://FastAPI.tiangolo.com#top", "title": "Again", "tags": ["other"]}'
echo "Step 3:"; curl -s -w '  -> HTTP %{http_code}\n' "$B/bookmarks"
echo "Step 4:"; post '{"url": "https://fastapi.tiangolo.com/", "title": "t", "tags": ["no spaces"]}'
echo "Step 5:"; curl -s "$B/openapi.json" | python3 -c "import json,sys; r=json.load(sys.stdin)['paths']['/bookmarks']['post']['responses']; print('post responses:', sorted(r), {k: v.get('content',{}).get('application/json',{}).get('schema') for k,v in r.items()})"
kill $PID; wait $PID 2>/dev/null
echo "server stopped"
----
truncated bookmarks_test_forward_r3
Step 1:
unknown PostgreSQL timezone: 'ASIA0'; will use UTC
{"id":1,"url":"https://fastapi.tiangolo.com/","title":"FastAPI docs","tags":["python"],"created_at":"2026-10-24T12:43:25.367419Z"}  -> HTTP 201
Step 2:
{"id":1,"url":"https://fastapi.tiangolo.com/","title":"FastAPI docs","tags":["python"],"created_at":"2026-10-24T12:43:25.367419Z"}  -> HTTP 200
Step 3:
{"items":[{"id":1,"url":"https://fastapi.tiangolo.com/","title":"FastAPI docs","tags":["python"],"created_at":"2026-10-24T12:43:25.367419Z"}],"total":1,"limit":20,"next_cursor":null}  -> HTTP 200
Step 4:
{"error":{"code":"validation_error","message":"The request is not valid.","details":[{"field":"tags","message":"Tag 'no spaces' is not valid: use 1 to 30 letters, digits or hyphens."}]}}  -> HTTP 422
Step 5:
post responses: ['200', '201', '422'] {'201': {'$ref': '#/components/schemas/Bookmark'}, '200': {'$ref': '#/components/schemas/Bookmark'}, '422': {'$ref': '#/components/schemas/ErrorResponse'}}
server stopped
[exit 0]
```

### Tasks marked [X]

## Review of code and artifact diffs

```console
$ git diff --stat ep03-analyze; git diff --quiet ep03-start -- specs/001-bookmarks-api && echo "specs/001-bookmarks-api: no changes since ep03-start"
fatal: ambiguous argument 'ep03-analyze': unknown revision or path not in the working tree.
Use '--' to separate paths from revisions, like this:
'git <command> [<revision>...] -- [<file>...]'
specs/001-bookmarks-api: no changes since ep03-start
[exit 0]
```

```console
$ git diff ep03-analyze -- tests/
fatal: bad revision 'ep03-analyze'
[exit 128]
```

```console
$ grep -rn --include=*.py --include=*.md --include=*.yaml -i "409\|duplicate_url\|conflict" src tests README.md specs/002-idempotent-duplicate-save | grep -v "^specs/002-idempotent-duplicate-save/spec.md:9:"
src/bookmarks_api/errors.py:35:STATUS_CODES = {400: "bad_request", 404: "not_found", 405: "method_not_allowed", 409: "conflict"}
src/bookmarks_api/repository.py:31:    ON CONFLICT DO NOTHING relies on the unique index, so this holds under concurrent saves: the
src/bookmarks_api/repository.py:39:        .on_conflict_do_nothing(index_elements=[BookmarkRow.url_normalized])
tests/integration/test_errors.py:75:        assert "409" not in operation["responses"]
specs/002-idempotent-duplicate-save/quickstart.md:37:| 5 | `GET /openapi.json` → `paths./bookmarks.post.responses` | has `200` and `201` (both `Bookmark`) and `422`; no `409` |
specs/002-idempotent-duplicate-save/tasks.md:19:(409 `duplicate_url` → 200 with the existing bookmark). `specs/001-bookmarks-api/` is not edited.
specs/002-idempotent-duplicate-save/tasks.md:68:- [X] T006 [US1] In `tests/integration/test_create_bookmark.py`, add `test_bookmark_deleted_mid_save_is_saved_as_new`: save `https://example.com/gone` (keep its `id`), then monkeypatch `repository._find_existing` with a wrapper that, on its first call only, deletes that row through a separate committed connection from the `engine` fixture and then calls the original; POST the same link again and assert 201, a new `id` different from the first, and `row_count() == 1`. The database stays real (Constitution II): only the timing of a real delete is forced (research.md, "Row deleted between the conflict and the lookup")
specs/002-idempotent-duplicate-save/tasks.md:69:- [X] T007 [P] [US1] In `tests/integration/test_errors.py`, delete `test_duplicate_error_envelope`, and change `test_openapi_documents_every_operation` so the `post` error codes are `{"422"}`, it asserts `"409" not in operation["responses"]` for `post`, and it asserts both `responses["201"]` and `responses["200"]` reference `/Bookmark` (spec FR-006, contracts/openapi.yaml)
specs/002-idempotent-duplicate-save/tasks.md:73:- [X] T008 [US1] In `src/bookmarks_api/repository.py`, change `create_bookmark(session, data)` to return `tuple[BookmarkRow, bool]` (row, created): keep `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`; on an inserted row commit and return `(row, True)`; when nothing is inserted roll back, look the row up by `url_normalized` through a module-level helper `_find_existing(session, normalized) -> BookmarkRow | None` and return `(row, False)` without writing; if the helper finds nothing (row deleted in between), retry the insert, at most 3 attempts in total, then raise `RuntimeError` (rendered as 500 `internal_error`). Remove the `DuplicateUrlError` import and update the docstring (research.md, "Returning the existing bookmark" and "Row deleted between the conflict and the lookup")
specs/002-idempotent-duplicate-save/tasks.md:74:- [X] T009 [US1] In `src/bookmarks_api/routes.py`, change `create_bookmark` to accept `response: Response`, unpack `(row, created)` from the repository, set `response.status_code = status.HTTP_200_OK` when not created (default stays 201), and replace the route's `responses` with `{200: {"model": Bookmark, "description": "This link is already bookmarked; the existing bookmark is returned unchanged."}, **ERROR_422}` — no 409 entry (research.md, "Response status and contract"; Constitution I)
specs/002-idempotent-duplicate-save/tasks.md:75:- [X] T010 [US1] In `src/bookmarks_api/errors.py`, delete the `DuplicateUrlError` class and its `handle_duplicate` 409 exception handler; keep the generic `409: "conflict"` entry in `STATUS_CODES` (research.md, "Removing the duplicate error")
specs/002-idempotent-duplicate-save/tasks.md:105:- [X] T013 [P] In `README.md`, change the endpoint table row for `POST /bookmarks` from "409 if the link is already saved" to "201 for a new link; 200 with the existing bookmark, unchanged, if the link is already saved"
specs/002-idempotent-duplicate-save/spec.md:16:  "A save of an existing link MUST be rejected with a conflict error that includes the existing
specs/002-idempotent-duplicate-save/spec.md:93:- The duplicate case no longer produces any error response; the conflict error described in 001
specs/002-idempotent-duplicate-save/spec.md:115:  a new bookmark, 200 for an existing one) and MUST no longer list a conflict error for the save
specs/002-idempotent-duplicate-save/spec.md:133:- **SC-004**: No save request for a valid link returns a conflict error.
specs/002-idempotent-duplicate-save/spec.md:135:  existing 001 test suite (updated only where it asserted the old conflict behavior) still passes.
specs/002-idempotent-duplicate-save/plan.md:12:existing bookmark, unchanged, with **200 OK** instead of the 409 `duplicate_url` error defined by
specs/002-idempotent-duplicate-save/plan.md:14:returns **201 Created**. The existing `INSERT ... ON CONFLICT (url_normalized) DO NOTHING
specs/002-idempotent-duplicate-save/plan.md:19:nothing, then reads the committed row and gets 200. The `DuplicateUrlError` exception, its 409
specs/002-idempotent-duplicate-save/plan.md:20:handler and the 409 entry in the OpenAPI responses are removed. No schema, migration or dependency
specs/002-idempotent-duplicate-save/plan.md:54:| I. Typed API Contracts | Both outcomes of `POST /bookmarks` use the existing `Bookmark` response model; the 200 response is declared on the route so the generated OpenAPI lists 200 and 201 with the `Bookmark` schema; the 409 entry is removed | Pass |
specs/002-idempotent-duplicate-save/plan.md:56:| III. Consistent Error Shape | Fewer error cases: the duplicate case is no longer an error. Remaining errors (422, 404, 405, 500) keep the envelope. The principle's mention of 409 lists an allowed class, it does not require one to exist | Pass |
specs/002-idempotent-duplicate-save/plan.md:58:| V. Tests Ship With Every Feature | Every acceptance scenario of spec US1 and US2 maps to a test in the same change; old 409 assertions in the create and concurrency tests are replaced by 200 assertions, and the duplicate-envelope test in `test_errors.py` is removed explicitly because that error no longer exists; the retry path for a bookmark deleted mid-save gets its own real-database test | Pass |
specs/002-idempotent-duplicate-save/plan.md:62:`Bookmark` schema, removes 409 and the `duplicate_url` error code; no new dependencies, models or
specs/002-idempotent-duplicate-save/plan.md:89:├── routes.py            # POST /bookmarks sets 201 or 200 from `created`; declares 200, drops 409
specs/002-idempotent-duplicate-save/plan.md:90:└── errors.py            # DuplicateUrlError and its 409 handler removed
specs/002-idempotent-duplicate-save/plan.md:94:└── test_errors.py           # duplicate-envelope test removed; OpenAPI check expects 200+201, no 409 for POST
specs/002-idempotent-duplicate-save/research.md:9:- **Decision**: Keep `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING *`. If a row is
specs/002-idempotent-duplicate-save/research.md:19:  - `ON CONFLICT DO UPDATE SET url_normalized = EXCLUDED.url_normalized RETURNING *, (xmax = 0)`
specs/002-idempotent-duplicate-save/research.md:26:## Row deleted between the conflict and the lookup
specs/002-idempotent-duplicate-save/research.md:28:- **Decision**: If the follow-up `SELECT` finds nothing (the conflicting bookmark was deleted in
specs/002-idempotent-duplicate-save/research.md:34:- **Alternatives considered**: Returning 409 or 404 in this window (reintroduces an error for a
specs/002-idempotent-duplicate-save/research.md:41:  route's `responses`, and remove the 409 entry, so `/openapi.json` documents both outcomes with the
specs/002-idempotent-duplicate-save/research.md:50:- **Decision**: Delete `DuplicateUrlError`, its 409 handler and the `duplicate_url` error code from
specs/002-idempotent-duplicate-save/research.md:51:  the contract. Keep the generic `409: "conflict"` entry in the HTTP-status code map (it only names
specs/002-idempotent-duplicate-save/contracts/openapi.yaml:11:    200 with the existing bookmark instead of 409); all other operations are unchanged.
[exit 0]
```

(The two commands above that failed used the wrong tag name `ep03-analyze`; re-run with `ep03-forward-r3-analyze`.)

```console
$ git diff --stat ep03-forward-r3-analyze
 README.md                                    |   2 +-
 specs/002-idempotent-duplicate-save/tasks.md |  30 +++----
 src/bookmarks_api/errors.py                  |  11 ---
 src/bookmarks_api/repository.py              |  44 +++++++---
 src/bookmarks_api/routes.py                  |  14 +++-
 tests/integration/test_create_bookmark.py    | 116 ++++++++++++++++++++++++---
 tests/integration/test_errors.py             |  18 ++---
 7 files changed, 167 insertions(+), 68 deletions(-)
[exit 0]
```

```console
$ git diff ep03-forward-r3-analyze -- tests/
diff --git a/tests/integration/test_create_bookmark.py b/tests/integration/test_create_bookmark.py
index bf537d3..2125296 100644
--- a/tests/integration/test_create_bookmark.py
+++ b/tests/integration/test_create_bookmark.py
@@ -37,36 +37,125 @@ def test_link_is_stored_as_given(client: TestClient) -> None:
     assert response.json()["url"] == "HTTPS://Example.com/Docs/"
 
 
-def test_equivalent_link_is_rejected_as_duplicate(client: TestClient, row_count) -> None:
-    first = client.post("/bookmarks", json={"url": "https://example.com/docs", "title": "Docs"})
+def test_equivalent_link_returns_existing_bookmark(client: TestClient, row_count) -> None:
+    first = client.post(
+        "/bookmarks",
+        json={"url": "https://example.com/docs", "title": "Docs", "tags": ["python"]},
+    )
     second = client.post(
         "/bookmarks",
-        json={"url": "HTTPS://Example.com/docs/#intro", "title": "Other title", "tags": ["x"]},
+        json={"url": "HTTPS://Example.com/docs/#intro", "title": "Other", "tags": ["misc"]},
     )
 
-    assert second.status_code == 409
-    error = second.json()["error"]
-    assert error["code"] == "duplicate_url"
-    assert error["details"] == {"existing_id": first.json()["id"]}
+    assert first.status_code == 201
+    assert second.status_code == 200
+    assert second.json() == first.json()
+    body = second.json()
+    assert body["url"] == "https://example.com/docs"
+    assert body["title"] == "Docs"
+    assert body["tags"] == ["python"]
     assert row_count() == 1
 
 
 def test_duplicate_leaves_the_existing_bookmark_unchanged(client: TestClient, engine) -> None:
-    client.post("/bookmarks", json={"url": "https://example.com/docs", "title": "Docs"})
-    client.post("/bookmarks", json={"url": "https://example.com/docs/", "title": "Changed"})
+    payload = {"url": "https://example.com/docs", "title": "Docs", "tags": ["python"]}
+    original = client.post("/bookmarks", json=payload).json()
+    client.post("/bookmarks", json={"url": "https://example.com/newer", "title": "Newer"})
+    order_before = [item["id"] for item in client.get("/bookmarks").json()["items"]]
 
+    same = client.post("/bookmarks", json=payload)
+    changed = client.post(
+        "/bookmarks",
+        json={"url": "https://example.com/docs/", "title": "Changed", "tags": ["other"]},
+    )
+
+    assert same.status_code == 200
+    assert changed.status_code == 200
+    assert same.json() == original
+    assert changed.json() == original
     with engine.connect() as connection:
-        title = connection.exec_driver_sql("SELECT title FROM bookmarks").scalar_one()
+        title, tags, created_at = connection.exec_driver_sql(
+            "SELECT title, tags, created_at FROM bookmarks WHERE id = %s", (original["id"],)
+        ).one()
     assert title == "Docs"
+    assert tags == ["python"]
+    assert created_at == datetime.fromisoformat(original["created_at"])
+    order_after = [item["id"] for item in client.get("/bookmarks").json()["items"]]
+    assert order_before == order_after
+    assert order_after[-1] == original["id"]
+
+
+def test_different_query_string_is_a_new_bookmark(client: TestClient, row_count) -> None:
+    first = client.post("/bookmarks", json={"url": "https://example.com/docs?a=1", "title": "A"})
+    second = client.post("/bookmarks", json={"url": "https://example.com/docs?a=2", "title": "B"})
+
+    assert second.status_code == 201
+    assert second.json()["id"] != first.json()["id"]
+    assert row_count() == 2
+
+
+@pytest.mark.parametrize(
+    "changes",
+    [
+        pytest.param({"title": "t" * 201}, id="title-over-200"),
+        pytest.param({"tags": ["no spaces"]}, id="invalid-tag"),
+    ],
+)
+def test_invalid_duplicate_save_is_still_rejected(
+    client: TestClient, engine, row_count, changes: dict
+) -> None:
+    original = client.post(
+        "/bookmarks", json={"url": "https://example.com/docs", "title": "Docs"}
+    ).json()
+
+    response = client.post(
+        "/bookmarks", json={"url": "https://example.com/docs", "title": "Docs", **changes}
+    )
+
+    assert response.status_code == 422
+    assert response.json()["error"]["code"] == "validation_error"
+    assert row_count() == 1
+    with engine.connect() as connection:
+        title, tags = connection.exec_driver_sql(
+            "SELECT title, tags FROM bookmarks WHERE id = %s", (original["id"],)
+        ).one()
+    assert (title, tags) == ("Docs", [])
+
+
+def test_bookmark_deleted_mid_save_is_saved_as_new(
+    client: TestClient, engine, row_count, monkeypatch
+) -> None:
+    from bookmarks_api import repository
+
+    gone = client.post("/bookmarks", json={"url": "https://example.com/gone", "title": "Gone"})
+    gone_id = gone.json()["id"]
+    original_find = repository._find_existing
+    calls = {"count": 0}
+
+    def delete_then_find(session, normalized):
+        calls["count"] += 1
+        if calls["count"] == 1:
+            with engine.begin() as connection:
+                connection.exec_driver_sql("DELETE FROM bookmarks WHERE id = %s", (gone_id,))
+        return original_find(session, normalized)
+
+    monkeypatch.setattr(repository, "_find_existing", delete_then_find)
+    response = client.post("/bookmarks", json={"url": "https://example.com/gone", "title": "Again"})
+
+    assert response.status_code == 201
+    assert response.json()["id"] != gone_id
+    assert response.json()["title"] == "Again"
+    assert calls["count"] == 1
+    assert row_count() == 1
 
 
 def test_concurrent_saves_of_the_same_link_leave_one_bookmark(client: TestClient, row_count) -> None:
-    statuses: list[int] = []
+    responses: list = []
     barrier = threading.Barrier(2)
 
     def save(url: str) -> None:
         barrier.wait()
-        statuses.append(client.post("/bookmarks", json={"url": url, "title": "Race"}).status_code)
+        responses.append(client.post("/bookmarks", json={"url": url, "title": "Race"}))
 
     threads = [
         threading.Thread(target=save, args=("https://example.com/race",)),
@@ -77,7 +166,8 @@ def test_concurrent_saves_of_the_same_link_leave_one_bookmark(client: TestClient
     for thread in threads:
         thread.join()
 
-    assert sorted(statuses) == [201, 409]
+    assert sorted(response.status_code for response in responses) == [200, 201]
+    assert responses[0].json()["id"] == responses[1].json()["id"]
     assert row_count() == 1
 
 
diff --git a/tests/integration/test_errors.py b/tests/integration/test_errors.py
index 1f473e0..b57db3d 100644
--- a/tests/integration/test_errors.py
+++ b/tests/integration/test_errors.py
@@ -22,16 +22,6 @@ def test_validation_error_envelope(client: TestClient) -> None:
     assert fields == {"url", "title"}
 
 
-def test_duplicate_error_envelope(client: TestClient) -> None:
-    client.post("/bookmarks", json={"url": "https://example.com", "title": "A"})
-
-    assert_envelope(
-        client.post("/bookmarks", json={"url": "https://example.com/", "title": "B"}),
-        409,
-        "duplicate_url",
-    )
-
-
 def test_not_found_error_envelope(client: TestClient) -> None:
     assert_envelope(client.delete("/bookmarks/12345"), 404, "not_found")
 
@@ -74,7 +64,7 @@ def test_openapi_documents_every_operation(client: TestClient, path: str, method
     operation = spec["paths"][path][method]
 
     assert operation["summary"]
-    error_codes = {"post": {"409", "422"}, "get": {"422"}, "delete": {"404", "422"}}[method]
+    error_codes = {"post": {"422"}, "get": {"422"}, "delete": {"404", "422"}}[method]
     for code in error_codes:
         schema = operation["responses"][code]["content"]["application/json"]["schema"]
         assert schema["$ref"].endswith("/ErrorResponse")
@@ -82,8 +72,10 @@ def test_openapi_documents_every_operation(client: TestClient, path: str, method
         assert operation["requestBody"]["content"]["application/json"]["schema"]["$ref"].endswith(
             "/BookmarkCreate"
         )
-        success = operation["responses"]["201"]["content"]["application/json"]["schema"]
-        assert success["$ref"].endswith("/Bookmark")
+        assert "409" not in operation["responses"]
+        for status in ("201", "200"):
+            success = operation["responses"][status]["content"]["application/json"]["schema"]
+            assert success["$ref"].endswith("/Bookmark")
     if method == "get":
         success = operation["responses"]["200"]["content"]["application/json"]["schema"]
         assert success["$ref"].endswith("/BookmarkPage")
[exit 0]
```

### Review notes (build-runner)

- Code matches plan/research: `INSERT ... ON CONFLICT DO NOTHING RETURNING` kept; `_find_existing` helper; bounded retry (3); route sets 200 when `created` is false; 409 response, `DuplicateUrlError` and its handler removed. No remaining references to `DuplicateUrlError`/`duplicate_url` in src or tests.
- Generated OpenAPI for `POST /bookmarks` lists `200`, `201` (both `Bookmark`) and `422` — matches `specs/002-idempotent-duplicate-save/contracts/openapi.yaml` (verified in T015 step 5 and by `test_openapi_documents_every_operation`).
- `specs/001-bookmarks-api/` unchanged since ep03-start (verified with `git diff --quiet`).
- Residual, not changed: `STATUS_CODES` in errors.py still maps 409 → "conflict" for framework HTTPExceptions (by design, research.md). The module docstring of `tests/integration/test_create_bookmark.py` still says "User Story 1 - Save a bookmark (spec.md, scenarios 1 to 4)", which points at 001's spec numbering; the duplicate tests in it now implement 002's US1/US2. Left as is (no task covers it).
- The concurrency test asserts outcomes only; it does not prove both requests reached the INSERT at the same instant (barrier before the HTTP call). 20/20 repeated runs passed.
- Environment noise: uvicorn printed `unknown PostgreSQL timezone: 'ASIA0'; will use UTC` during T015 (server/session timezone setting in this sandbox); responses unaffected.
- Note on process: T011's test edit (US2) was written together with US1's tests in the same pass over the same file, before T008, as allowed by the task list's dependency note.

## Spec Kit completion report (verbatim)

Implementation complete for `specs/002-idempotent-duplicate-save`.

| Checklist | Total | Checked | Unchecked | Status |
|-----------|-------|---------|-----------|--------|
| requirements.md | 16 | 16 | 0 | ✓ PASS |

- Tasks: 15/15 completed and marked `[X]` (Setup 1, US1 9, US2 2, Polish 3).
- Tests written first: 5 failed before implementation (T002, T003, T006, T011, T007-post), T004/T005 already passed (behavior unchanged by design).
- Files changed: `src/bookmarks_api/repository.py`, `src/bookmarks_api/routes.py`, `src/bookmarks_api/errors.py`, `tests/integration/test_create_bookmark.py`, `tests/integration/test_errors.py`, `README.md`, `specs/002-idempotent-duplicate-save/tasks.md`.
- Test results: 101 passed on Python 3.11, 3.12 and 3.13 (baseline before the change: 98 passed on 3.13). Concurrency test 20/20 runs.
- Quickstart: steps 1-5 all match expected (201; 200 identical body; list total 1 unchanged; 422 on invalid duplicate; OpenAPI POST responses 200/201/422, no 409).
- Extension hooks: `.specify/extensions.yml` does not exist — after_implement skipped.
End: 2026-10-24T12:43:59Z
