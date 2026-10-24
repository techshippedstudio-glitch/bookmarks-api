# Step 05 — implement (Spec Kit implement command) and joint review of code and artifact diffs

Start: 2026-10-24T12:05:44Z

```console
$ test -f .specify/extensions.yml && cat .specify/extensions.yml || echo 'no .specify/extensions.yml (before_implement hooks skipped)'
no .specify/extensions.yml (before_implement hooks skipped)
[exit 0]
```

```console
$ .specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
{"FEATURE_DIR":"/home/claude/runs/living-r2/specs/001-bookmarks-api","AVAILABLE_DOCS":["research.md","data-model.md","contracts/","quickstart.md","tasks.md"]}
[exit 0]
```

```console
$ for f in specs/001-bookmarks-api/checklists/*.md; do t=$(grep -c -E '^- \[( |x|X)\]' $f); c=$(grep -c -E '^- \[(x|X)\]' $f); echo "$(basename $f) total=$t checked=$c unchecked=$((t-c))"; done
requirements.md total=16 checked=16 unchecked=0
[exit 0]
```

```console
$ git rev-parse --git-dir; ls Dockerfile* 2>/dev/null; grep -n -i docker specs/001-bookmarks-api/plan.md | head -3; cat .dockerignore; grep -n -E '__pycache__|\.pyc|\.venv|venv/|dist/|egg-info|\.env|DS_Store|Thumbs' .gitignore
/home/claude/bookmarks-api/.git/worktrees/living-r2
17:existing `docker-compose.yml`.
35:**Storage**: PostgreSQL (18 via the repo's `docker-compose.yml`); databases `bookmarks` (dev) and
.git/
.venv/
__pycache__/
*.pyc
.pytest_cache/
.env
.env.*
!.env.example
*.log
2:.env
3:.env.*
4:!.env.example
7:__pycache__/
9:*.egg-info/
10:.venv/
11:venv/
13:dist/
25:.DS_Store
26:Thumbs.db
[exit 0]
```

Checklist gate:

| Checklist | Total | Checked | Unchecked | Status |
|-----------|-------|---------|-----------|--------|
| requirements.md | 16 | 16 | 0 | ✓ PASS |

All checklists pass → proceed automatically.

Project setup verification: git repo (worktree; `git rev-parse --git-dir` prints the shared
repo's worktree metadata path, which was not opened). `.gitignore` already has the Python and
universal patterns (`__pycache__/`, `*.py[cod]`, `.venv/`, `venv/`, `dist/`, `*.egg-info/`,
`.env*`, `.DS_Store`, `Thumbs.db`). Docker appears in plan.md (docker-compose) and `.dockerignore`
exists with `.git/`, `.venv/`, `__pycache__/`, `*.pyc`, `.env*`, `*.log`. No Dockerfile, ESLint,
Prettier, npm, Terraform or Helm files. No ignore-file changes needed.

Open tasks to execute (from tasks.md): T012 (tests first), T015, T016, T017, T028, T029, T030.

### Baseline test run before any change

```console
$ uv run --python 3.13 pytest -q 2>&1 | tail -5
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
........................................................................ [ 73%]
..........................                                               [100%]
98 passed in 2.67s
[exit 0]
```

### T012 — tests written first; run to confirm they fail

```console
$ git diff --stat; uv run --python 3.13 pytest -q tests/integration/test_create_bookmark.py 2>&1 | grep -v UV_NATIVE | tail -15
 tests/integration/test_create_bookmark.py | 79 ++++++++++++++++++++++++-------
 1 file changed, 63 insertions(+), 16 deletions(-)
        finally:
            event.remove(engine, "after_cursor_execute", delete_after_conflicting_insert)
    
        assert fired == [True]
>       assert response.status_code == 201
E       assert 409 == 201
E        +  where 409 = <Response [409 Conflict]>.status_code

tests/integration/test_create_bookmark.py:126: AssertionError
=========================== short test summary info ============================
FAILED tests/integration/test_create_bookmark.py::test_equivalent_link_returns_the_existing_bookmark_with_200
FAILED tests/integration/test_create_bookmark.py::test_repeat_save_leaves_the_stored_bookmark_unchanged
FAILED tests/integration/test_create_bookmark.py::test_concurrent_saves_of_the_same_new_link_give_201_and_200
FAILED tests/integration/test_create_bookmark.py::test_save_retries_when_the_existing_bookmark_is_deleted_mid_save
4 failed, 15 passed in 0.76s
[exit 0]
```

### T015, T016, T017 — repository, route, error removal; US1 tests

```console
$ uv run --python 3.13 pytest -q tests/integration/test_create_bookmark.py 2>&1 | grep -v UV_NATIVE | tail -5
...................                                                      [100%]
19 passed in 0.65s
[exit 0]
```

### T028, T029 — test_errors.py and README; full suite on 3.13

```console
$ uv run --python 3.13 pytest -q 2>&1 | grep -v UV_NATIVE | tail -5
........................................................................ [ 73%]
..........................                                               [100%]
98 passed in 2.85s
[exit 0]
```

### T030 — full suite on 3.11, 3.12, 3.13

```console
$ uv run --python 3.11 pytest -q 2>&1 | grep -v UV_NATIVE | tail -3
........................................................................ [ 73%]
..........................                                               [100%]
98 passed in 2.59s
[exit 0]
```

```console
$ uv run --python 3.12 pytest -q 2>&1 | grep -v UV_NATIVE | tail -3
........................................................................ [ 73%]
..........................                                               [100%]
98 passed in 3.22s
[exit 0]
```

```console
$ uv run --python 3.13 pytest -q 2>&1 | grep -v UV_NATIVE | tail -3
........................................................................ [ 73%]
..........................                                               [100%]
98 passed in 3.26s
[exit 0]
```

### T030 — quickstart manual checks (server pointed at this run's own database bookmarks_test_living_r2, because the dev DATABASE_URL may be shared with other runs)

Script: /home/claude/scratch/living-r2/quickstart.sh (truncate own DB, start uvicorn on :8765, run the 8 quickstart requests, stop).

```console
$ /home/claude/scratch/living-r2/quickstart.sh
truncated bookmarks in bookmarks_test_living_r2
--- POST /bookmarks {"url": "https://fastapi.tiangolo.com/", "title": "FastAPI docs", "tags": ["Python", "api"]}
{"id":1,"url":"https://fastapi.tiangolo.com/","title":"FastAPI docs","tags":["api","python"],"created_at":"2026-10-24T12:07:39.671163Z"}
HTTP 201
--- POST /bookmarks {"url": "HTTPS://FastAPI.tiangolo.com", "title": "Again", "tags": ["other"]}
{"id":1,"url":"https://fastapi.tiangolo.com/","title":"FastAPI docs","tags":["api","python"],"created_at":"2026-10-24T12:07:39.671163Z"}
HTTP 200
--- GET /bookmarks 
{"items":[{"id":1,"url":"https://fastapi.tiangolo.com/","title":"FastAPI docs","tags":["api","python"],"created_at":"2026-10-24T12:07:39.671163Z"}],"total":1,"limit":20,"next_cursor":null}
HTTP 200
--- GET /bookmarks?tag=PYTHON 
{"items":[{"id":1,"url":"https://fastapi.tiangolo.com/","title":"FastAPI docs","tags":["api","python"],"created_at":"2026-10-24T12:07:39.671163Z"}],"total":1,"limit":20,"next_cursor":null}
HTTP 200
--- GET /bookmarks?limit=500 
{"error":{"code":"validation_error","message":"The request is not valid.","details":[{"field":"query.limit","message":"Input should be less than or equal to 100"}]}}
HTTP 422
--- DELETE /bookmarks/1 

HTTP 204
--- DELETE /bookmarks/1 
{"error":{"code":"not_found","message":"No bookmark with id 1.","details":null}}
HTTP 404
--- POST /bookmarks {"url": "ftp://example.com", "title": "x"}
{"error":{"code":"validation_error","message":"The request is not valid.","details":[{"field":"url","message":"The link must start with http:// or https://."}]}}
HTTP 422
[exit 143]
```

Note: exit 143 is the script's own `kill` of uvicorn propagating through `wait`; all 8 requests returned the expected statuses (201, 200 unchanged, 200 total 1, 200, 422, 204, 404, 422).

## Joint review: code and artifact diffs since the analyze tag

```console
$ git diff --stat ep03-living-r2-analyze; git status --short
 README.md                                 |  2 +-
 specs/001-bookmarks-api/tasks.md          | 14 +++---
 src/bookmarks_api/errors.py               | 11 -----
 src/bookmarks_api/repository.py           | 34 ++++++++-----
 src/bookmarks_api/routes.py               | 15 ++++--
 tests/integration/test_create_bookmark.py | 79 ++++++++++++++++++++++++-------
 tests/integration/test_errors.py          | 18 ++-----
 7 files changed, 109 insertions(+), 64 deletions(-)
 M README.md
 M specs/001-bookmarks-api/tasks.md
 M src/bookmarks_api/errors.py
 M src/bookmarks_api/repository.py
 M src/bookmarks_api/routes.py
 M tests/integration/test_create_bookmark.py
 M tests/integration/test_errors.py
?? episodes/ep03/capture/living-r2/05-implement.md
[exit 0]
```

```console
$ git diff ep03-living-r2-analyze -- src README.md specs
diff --git a/README.md b/README.md
index 5c4557f..9e1ddba 100644
--- a/README.md
+++ b/README.md
@@ -97,7 +97,7 @@ uv run pytest                                          # tests, against the book
 
 | Endpoint | What it does |
 | --- | --- |
-| `POST /bookmarks` | Save `{"url", "title", "tags"}`; 409 if the link is already saved |
+| `POST /bookmarks` | Save `{"url", "title", "tags"}`; 201 for a new link; if the link is already saved, 200 with the existing bookmark unchanged (the title and tags sent are ignored) |
 | `GET /bookmarks?tag=&limit=&cursor=` | List newest first, 20 per page by default, optional tag filter; pass `next_cursor` from one page as `cursor` to get the next |
 | `DELETE /bookmarks/{id}` | Delete a bookmark |
 
diff --git a/specs/001-bookmarks-api/tasks.md b/specs/001-bookmarks-api/tasks.md
index 98206cd..ad7d7fd 100644
--- a/specs/001-bookmarks-api/tasks.md
+++ b/specs/001-bookmarks-api/tasks.md
@@ -69,15 +69,15 @@ still one row.
 > Write these first and confirm they fail before implementing.
 
 - [X] T011 [P] [US1] Unit tests in `tests/unit/test_normalize.py` for link normalization (lowercase scheme and host, default ports 80/443 removed, trailing path slashes removed, fragment removed, query kept; examples `HTTPS://Example.com:443/docs/#intro` → `https://example.com/docs`, `https://example.com/search?q=FastAPI` keeps `?q=FastAPI`; non-http(s) and host-less links rejected) and tag normalization (trim, lowercase, de-duplicate, sort; must match `^[a-z0-9-]{1,30}$`)
-- [ ] T012 [P] [US1] Update integration tests in `tests/integration/test_create_bookmark.py` for the revised User Story 1 scenario 3 and FR-004: save `https://example.com/docs` (title "Docs", tags `["a"]`) then `HTTPS://Example.com/docs/#intro` with title "Other" and tags `["b"]` → second response is 200 (not 201, not 409) and its body equals the first response body exactly (same `id`, `url` as first given, `title` "Docs", `tags` `["a"]`, `created_at`); the stored row's `url`, `title`, `tags` and `created_at` are unchanged when read back from the database; still exactly one row. Replace the concurrency test: two concurrent saves (two threads) of the same new link → status codes sorted are `[200, 201]`, both bodies carry the same `id`, exactly one row. Add a test for the retry path (research.md, "Preventing duplicate links"): with a bookmark saved, a SQLAlchemy `after_cursor_execute` listener on the test engine deletes that row through a separate real connection right after the conflicting `INSERT` of a repeat save (once only), so the existing-row lookup finds nothing; the save must then insert and return 201 with exactly one row (real test database, no mocks, Constitution II). Keep the scenario 1, 2 and 4 tests as they are; remove every assertion on 409 or `duplicate_url`
+- [X] T012 [P] [US1] Update integration tests in `tests/integration/test_create_bookmark.py` for the revised User Story 1 scenario 3 and FR-004: save `https://example.com/docs` (title "Docs", tags `["a"]`) then `HTTPS://Example.com/docs/#intro` with title "Other" and tags `["b"]` → second response is 200 (not 201, not 409) and its body equals the first response body exactly (same `id`, `url` as first given, `title` "Docs", `tags` `["a"]`, `created_at`); the stored row's `url`, `title`, `tags` and `created_at` are unchanged when read back from the database; still exactly one row. Replace the concurrency test: two concurrent saves (two threads) of the same new link → status codes sorted are `[200, 201]`, both bodies carry the same `id`, exactly one row. Add a test for the retry path (research.md, "Preventing duplicate links"): with a bookmark saved, a SQLAlchemy `after_cursor_execute` listener on the test engine deletes that row through a separate real connection right after the conflicting `INSERT` of a repeat save (once only), so the existing-row lookup finds nothing; the save must then insert and return 201 with exactly one row (real test database, no mocks, Constitution II). Keep the scenario 1, 2 and 4 tests as they are; remove every assertion on 409 or `duplicate_url`
 - [X] T013 [P] [US1] Implement `normalize_url(url) -> str` and `normalize_tags(tags) -> list[str]` in `src/bookmarks_api/normalize.py` using only the standard library, raising `ValueError` with a clear message on invalid input
 - [X] T014 [P] [US1] Create Pydantic models in `src/bookmarks_api/schemas.py`: `BookmarkCreate` (`url` str, max 2048, http/https with a host; `title` trimmed, 1 to 200 characters; `tags` list default `[]`, normalized via `normalize_tags`, at most 10 after de-duplication; extra fields forbidden) and `Bookmark` (`id`, `url`, `title`, `tags`, `created_at`)
 
 ### Implementation for User Story 1
 
-- [ ] T015 [US1] Change `create_bookmark(session, data)` in `src/bookmarks_api/repository.py` to return `(row, created: bool)`: keep `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`; a returned row → commit and return `(row, True)`; no row → end the insert transaction, select the existing row by `url_normalized` and return `(existing_row, False)` without writing the request's title or tags (no `DO UPDATE`); if that select finds nothing (the row was deleted in between), retry the insert once (research.md, "Preventing duplicate links", revised 2026-10-24)
-- [ ] T016 [US1] Update `POST /bookmarks` in `src/bookmarks_api/routes.py` to set the status code from the `created` flag (201 Created for a new link, 200 OK for an already saved link), both with the `Bookmark` response model; declare the 200 response in `responses` (description "The link was already saved; the existing bookmark, unchanged") and remove the 409 response, per contracts/openapi.yaml
-- [ ] T017 [US1] Remove `DuplicateUrlError` and its 409 `duplicate_url` handler from `src/bookmarks_api/errors.py` and its import from `src/bookmarks_api/repository.py`; keep the generic `409: "conflict"` entry in `STATUS_CODES` for framework `HTTPException`s (plan.md, Constitution Check III)
+- [X] T015 [US1] Change `create_bookmark(session, data)` in `src/bookmarks_api/repository.py` to return `(row, created: bool)`: keep `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`; a returned row → commit and return `(row, True)`; no row → end the insert transaction, select the existing row by `url_normalized` and return `(existing_row, False)` without writing the request's title or tags (no `DO UPDATE`); if that select finds nothing (the row was deleted in between), retry the insert once (research.md, "Preventing duplicate links", revised 2026-10-24)
+- [X] T016 [US1] Update `POST /bookmarks` in `src/bookmarks_api/routes.py` to set the status code from the `created` flag (201 Created for a new link, 200 OK for an already saved link), both with the `Bookmark` response model; declare the 200 response in `responses` (description "The link was already saved; the existing bookmark, unchanged") and remove the 409 response, per contracts/openapi.yaml
+- [X] T017 [US1] Remove `DuplicateUrlError` and its 409 `duplicate_url` handler from `src/bookmarks_api/errors.py` and its import from `src/bookmarks_api/repository.py`; keep the generic `409: "conflict"` entry in `STATUS_CODES` for framework `HTTPException`s (plan.md, Constitution Check III)
 
 **Checkpoint**: User Story 1 works and is tested on its own (MVP)
 
@@ -148,9 +148,9 @@ again returns 404.
 
 **Purpose**: Improvements that affect multiple user stories
 
-- [ ] T028 [P] Update `tests/integration/test_errors.py`: every error class (422, 404, and an unknown route 404) uses the envelope `{"error": {"code", "message", "details"}}` (SC-005); remove the duplicate 409 envelope test (a duplicate save is no longer an error); the `/openapi.json` check expects `POST /bookmarks` to declare 200, 201 and 422 and no 409, alongside the GET and DELETE operations with request and response schemas (Constitution I, contracts/openapi.yaml)
-- [ ] T029 [P] Update the `POST /bookmarks` row in `README.md`: a new link returns 201; an already saved link returns 200 with the existing bookmark unchanged (title and tags in the request ignored), instead of 409
-- [ ] T030 Run the full test suite on Python 3.11, 3.12 and 3.13 and the manual checks in `specs/001-bookmarks-api/quickstart.md` (step 2 now expects 200 with the step 1 bookmark unchanged)
+- [X] T028 [P] Update `tests/integration/test_errors.py`: every error class (422, 404, and an unknown route 404) uses the envelope `{"error": {"code", "message", "details"}}` (SC-005); remove the duplicate 409 envelope test (a duplicate save is no longer an error); the `/openapi.json` check expects `POST /bookmarks` to declare 200, 201 and 422 and no 409, alongside the GET and DELETE operations with request and response schemas (Constitution I, contracts/openapi.yaml)
+- [X] T029 [P] Update the `POST /bookmarks` row in `README.md`: a new link returns 201; an already saved link returns 200 with the existing bookmark unchanged (title and tags in the request ignored), instead of 409
+- [X] T030 Run the full test suite on Python 3.11, 3.12 and 3.13 and the manual checks in `specs/001-bookmarks-api/quickstart.md` (step 2 now expects 200 with the step 1 bookmark unchanged)
 
 ---
 
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
index f93517e..90285d2 100644
--- a/src/bookmarks_api/repository.py
+++ b/src/bookmarks_api/repository.py
@@ -6,16 +6,22 @@ from sqlalchemy import delete, func, select, tuple_
 from sqlalchemy.dialects.postgresql import insert
 from sqlalchemy.orm import Session
 
-from bookmarks_api.errors import DuplicateUrlError, NotFoundError
+from bookmarks_api.errors import NotFoundError
 from bookmarks_api.models import BookmarkRow
 from bookmarks_api.normalize import normalize_url
 from bookmarks_api.schemas import BookmarkCreate
 
 
-def create_bookmark(session: Session, data: BookmarkCreate) -> BookmarkRow:
-    """Insert a bookmark, or raise DuplicateUrlError if its normalized link already exists.
+def create_bookmark(session: Session, data: BookmarkCreate) -> tuple[BookmarkRow, bool]:
+    """Save a bookmark, or return the existing one if its normalized link is already saved.
 
-    ON CONFLICT DO NOTHING relies on the unique index, so this holds under concurrent saves.
+    Returns ``(row, created)``: ``created`` is True for a new bookmark (201) and False when the
+    link was already saved (200, FR-004). The existing bookmark is never modified, so the
+    request's title and tags are ignored for a repeat save.
+
+    ON CONFLICT DO NOTHING relies on the unique index, so this holds under concurrent saves: the
+    second of two racing saves inserts nothing and reads the row the first one committed. If that
+    row is deleted before it can be read, the insert is tried once more.
     """
     normalized = normalize_url(data.url)
     statement = (
@@ -24,15 +30,19 @@ def create_bookmark(session: Session, data: BookmarkCreate) -> BookmarkRow:
         .on_conflict_do_nothing(index_elements=[BookmarkRow.url_normalized])
         .returning(BookmarkRow)
     )
-    row = session.scalars(statement).one_or_none()
-    if row is None:
+    for _ in range(2):
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
+        session.commit()
+        if existing is not None:
+            return existing, False
+    raise RuntimeError("The link was saved and deleted repeatedly while saving; try again.")
 
 
 def list_bookmarks(
diff --git a/src/bookmarks_api/routes.py b/src/bookmarks_api/routes.py
index cc51123..fc39599 100644
--- a/src/bookmarks_api/routes.py
+++ b/src/bookmarks_api/routes.py
@@ -39,14 +39,21 @@ def _reject_offset(value: str | None) -> None:
     "",
     status_code=status.HTTP_201_CREATED,
     response_model=Bookmark,
-    summary="Save a bookmark",
+    summary="Save a bookmark, or return the existing one for an already saved link",
     responses={
-        409: {"model": ErrorResponse, "description": "This link is already bookmarked."},
+        200: {
+            "model": Bookmark,
+            "description": "The link was already saved; the existing bookmark, unchanged",
+        },
+        201: {"description": "Bookmark saved (new link)"},
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
$ uv run --python 3.13 python -c "
import json; from bookmarks_api.main import app
op=app.openapi()['paths']['/bookmarks']['post']
print(op['summary']); print(json.dumps({k:(v.get('description'), v.get('content',{}).get('application/json',{}).get('schema')) for k,v in op['responses'].items()}, indent=1))
print('error code enum present in generated spec?', 'duplicate_url' in json.dumps(app.openapi()))
" 2>&1 | grep -v UV_NATIVE
Save a bookmark, or return the existing one for an already saved link
{
 "201": [
  "Bookmark saved (new link)",
  {
   "$ref": "#/components/schemas/Bookmark"
  }
 ],
 "200": [
  "The link was already saved; the existing bookmark, unchanged",
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
error code enum present in generated spec? False
[exit 0]
```

```console
$ grep -rn -i -E 'duplicate_url|DuplicateUrlError|existing_id|409' src tests README.md
src/bookmarks_api/errors.py:35:STATUS_CODES = {400: "bad_request", 404: "not_found", 405: "method_not_allowed", 409: "conflict"}
tests/integration/test_errors.py:75:        assert set(operation["responses"]) == {"200", "201", "422"}  # no 409: FR-004
[exit 0]
```

### Review notes (code + artifacts read together)

- spec FR-004 / US1-AS3 / edge cases ↔ code: `create_bookmark` returns `(row, created)`; route sets
  200 when not created, 201 otherwise; no write path for title/tags on repeat (no DO UPDATE). Tests:
  200 body equals first 201 body; DB row identical before/after (id, url, url_normalized, title,
  tags, created_at); concurrent → [200, 201] with the same id, one row; retry path → 201, one row.
- plan/research ↔ code: ON CONFLICT DO NOTHING kept; lookup after rollback; one retry when the
  row vanished. Matches research.md "Preventing duplicate links" (revised).
- contract ↔ generated OpenAPI: POST declares 200 and 201 (both `Bookmark`) and 422; no 409;
  `duplicate_url` appears nowhere in the generated spec. Matches contracts/openapi.yaml 0.2.0.
- quickstart ↔ live server: all 8 manual steps as written (step 2: 200, step 1 bookmark unchanged).
- README ↔ contract: POST row updated.
- Observations not acted on (left for converge to judge, per the step order):
  1. If the retry also fails (link saved and deleted again within the same request), the code
     raises `RuntimeError`, which the global handler turns into 500 `internal_error`. The spec does
     not cover this double race; research.md only describes "retries the insert once".
  2. Pre-existing (not introduced here): contracts/openapi.yaml lists the error-code enum as
     `[validation_error, not_found, internal_error]`, but `errors.py` `STATUS_CODES` also produces
     `bad_request`, `method_not_allowed`, `conflict` and `http_error` for framework errors, and
     `test_wrong_method_uses_the_envelope` asserts `method_not_allowed`. Before this change the enum
     had `duplicate_url` but was equally incomplete for these framework codes.
- `uv run` created `.venv/` and `__pycache__/` (both git-ignored); no ignore-file change needed.

## Completion report (implement command)

- Tasks executed: T012 (tests first; 4 failing confirmed), T015, T016, T017, T028, T029, T030 —
  all marked `[X]`; tasks.md has 0 open tasks (30/30 complete).
- Tests: 98 passed on Python 3.11, 3.12 and 3.13 (same count as baseline: 4 duplicate tests were
  replaced by 4 new ones in test_create_bookmark.py; test_errors.py lost the 409 envelope test and
  the OpenAPI test gained 200/201 assertions — net 98 because the removed envelope test is offset
  by... see count note below).
- Quickstart manual checks: all pass.
- Extension hooks after implement: none (no `.specify/extensions.yml`).

```console
$ git stash -q && uv run --python 3.13 pytest -q --collect-only 2>/dev/null | tail -1; git stash pop -q && uv run --python 3.13 pytest -q --collect-only 2>/dev/null | tail -1; git status --short
98 tests collected in 0.04s
98 tests collected in 0.05s
 M README.md
 M specs/001-bookmarks-api/tasks.md
 M src/bookmarks_api/errors.py
 M src/bookmarks_api/repository.py
 M src/bookmarks_api/routes.py
 M tests/integration/test_create_bookmark.py
 M tests/integration/test_errors.py
?? episodes/ep03/capture/living-r2/05-implement.md
[exit 0]
```

Count note (correcting the unfinished sentence above): the stash check shows 98 tests collected
both at the analyze tag and after implement. test_create_bookmark.py: 3 old duplicate tests
(rejected-as-duplicate 409, duplicate-leaves-unchanged, concurrent [201, 409]) replaced by 4 new
ones (+1); test_errors.py: duplicate 409 envelope test removed (−1). Net 0 → 98.

End: 2026-10-24T12:08:21Z
