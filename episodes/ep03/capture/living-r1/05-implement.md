# Step 05: implement (Spec Kit implement command), then code + artifact diff review

Start: 2026-10-24T11:51:03Z

Arguments: the change request (verbatim). Pre/post hooks: no .specify/extensions.yml; skipped.

Checklist gate: checklists/requirements.md 16 total, 16 checked, 0 unchecked -> PASS, proceeded automatically.

| Checklist | Total | Checked | Unchecked | Status |
|-----------|-------|---------|-----------|--------|
| requirements.md | 16 | 16 | 0 | PASS |

Ignore files: git repo detected; .gitignore already has the Python patterns (__pycache__/, *.py[cod], .venv/, venv/, dist/, *.egg-info/) and universal ones; .dockerignore exists (Docker named in plan) with .git/, .venv/, __pycache__/, *.pyc, .env*, *.log. No Dockerfile, eslint, prettier, npm or terraform files. Nothing appended.

## Commands and full output (in order)

```
$ .specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
{"FEATURE_DIR":"/home/claude/runs/living-r1/specs/001-bookmarks-api","AVAILABLE_DOCS":["research.md","data-model.md","contracts/","quickstart.md","tasks.md"]}
exit=0
$ grep -cE '^- \[( |X|x)\]' specs/001-bookmarks-api/checklists/requirements.md; grep -cE '^- \[(X|x)\]' specs/001-bookmarks-api/checklists/requirements.md; grep -cE '^- \[ \]' specs/001-bookmarks-api/checklists/requirements.md
16
16
0
exit=1
$ git rev-parse --git-dir; cat .gitignore; ls Dockerfile* 2>&1; cat .dockerignore; ls .eslintrc* eslint.config.* .prettierrc* .npmrc package.json *.tf 2>&1
/home/claude/bookmarks-api/.git/worktrees/living-r1
# Environment and secrets
.env
.env.*
!.env.example

# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/
build/
dist/

# Tooling caches
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/

# Editors and OS
.vscode/
.idea/
.DS_Store
Thumbs.db

# Agent folder: Claude Code can keep local settings and tokens in .claude/.
# Only the Spec Kit skills are tracked, so viewers can see what Spec Kit generated.
.claude/*
!.claude/skills/

# Note: .specify/ is intentionally tracked (constitution, templates, scripts).
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
exit=2
$ set -a; . ./.env; set +a; uv run --python 3.13 pytest -q   # baseline before changes
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
........................................................................ [ 73%]
..........................                                               [100%]
98 passed in 3.10s
exit=0
$ uv run --python 3.13 pytest -q tests/integration/test_create_bookmark.py   # T012 written, expect failures before T015/T016
                 ~~~~~~~~~~~~~~~^^^^^^
  KeyError: 'id'
  
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.
    warnings.warn(pytest.PytestUnhandledThreadExceptionWarning(msg))

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/integration/test_create_bookmark.py::test_equivalent_link_returns_the_existing_bookmark
FAILED tests/integration/test_create_bookmark.py::test_repeat_save_leaves_the_stored_bookmark_unchanged
FAILED tests/integration/test_create_bookmark.py::test_saving_the_same_link_many_times_leaves_one_bookmark
FAILED tests/integration/test_create_bookmark.py::test_existing_bookmark_deleted_before_lookup_is_saved_again
FAILED tests/integration/test_create_bookmark.py::test_concurrent_saves_of_the_same_link_leave_one_bookmark
5 failed, 15 passed, 1 warning in 0.73s
exit=1
$ uv run --python 3.13 pytest -q   # after T015, T016, T008
___________ test_openapi_documents_every_operation[/bookmarks-post] ____________

client = <starlette.testclient.TestClient object at 0x7f4cbb3cd150>
path = '/bookmarks', method = 'post'

    @pytest.mark.parametrize(
        ("path", "method"),
        [("/bookmarks", "post"), ("/bookmarks", "get"), ("/bookmarks/{bookmark_id}", "delete")],
    )
    def test_openapi_documents_every_operation(client: TestClient, path: str, method: str) -> None:
        spec = client.get("/openapi.json").json()
        operation = spec["paths"][path][method]
    
        assert operation["summary"]
        error_codes = {"post": {"409", "422"}, "get": {"422"}, "delete": {"404", "422"}}[method]
        for code in error_codes:
>           schema = operation["responses"][code]["content"]["application/json"]["schema"]
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E           KeyError: '409'

tests/integration/test_errors.py:79: KeyError
=========================== short test summary info ============================
FAILED tests/integration/test_errors.py::test_duplicate_error_envelope - asse...
FAILED tests/integration/test_errors.py::test_openapi_documents_every_operation[/bookmarks-post]
2 failed, 98 passed in 2.86s
exit=1
$ uv run --python 3.13 pytest -q   # T030
........................................................................ [ 72%]
...........................                                              [100%]
99 passed in 2.68s
exit=0
$ uv run --python 3.12 pytest -q   # T030
Installed 29 packages in 17ms
........................................................................ [ 72%]
...........................                                              [100%]
99 passed in 3.45s
exit=0
$ uv run --python 3.11 pytest -q   # T030
Installed 29 packages in 41ms
........................................................................ [ 72%]
...........................                                              [100%]
99 passed in 3.11s
exit=0
$ # T030 quickstart manual checks (server: uvicorn on port 18431, DATABASE_URL set to this run's own test database, emptied first)
$ 1 POST /bookmarks fastapi docs
{"id":1,"url":"https://fastapi.tiangolo.com/","title":"FastAPI docs","tags":["api","python"],"created_at":"2026-10-24T11:53:26.216962Z"} HTTP 201
$ 2 POST /bookmarks same link, other title and tags
{"id":1,"url":"https://fastapi.tiangolo.com/","title":"FastAPI docs","tags":["api","python"],"created_at":"2026-10-24T11:53:26.216962Z"} HTTP 200
$ 3 GET /bookmarks
{"items":[{"id":1,"url":"https://fastapi.tiangolo.com/","title":"FastAPI docs","tags":["api","python"],"created_at":"2026-10-24T11:53:26.216962Z"}],"total":1,"limit":20,"next_cursor":null} HTTP 200
$ 4 GET /bookmarks?tag=PYTHON
{"items":[{"id":1,"url":"https://fastapi.tiangolo.com/","title":"FastAPI docs","tags":["api","python"],"created_at":"2026-10-24T11:53:26.216962Z"}],"total":1,"limit":20,"next_cursor":null} HTTP 200
$ 5 GET /bookmarks?limit=500
{"error":{"code":"validation_error","message":"The request is not valid.","details":[{"field":"query.limit","message":"Input should be less than or equal to 100"}]}} HTTP 422
$ 6 DELETE /bookmarks/1
 HTTP 204
$ 7 DELETE /bookmarks/1 again
{"error":{"code":"not_found","message":"No bookmark with id 1.","details":null}} HTTP 404
$ 8 POST ftp link
{"error":{"code":"validation_error","message":"The request is not valid.","details":[{"field":"url","message":"The link must start with http:// or https://."}]}} HTTP 422
$ openapi POST responses
{'201': 'Bookmark saved.', '200': 'The link is already bookmarked; the existing bookmark, unchanged.', '422': 'The request is not valid.'}

server stopped
```

Task execution order and progress:
1. T012 (tests first): rewrote the duplicate tests in tests/integration/test_create_bookmark.py (200 + same body,
   stored row unchanged, many repeat saves -> one row, retry after delete-between-statements, concurrent 201 + 200
   with same id). Ran: 5 failed, 15 passed (expected failures). -> [X]
2. T015: repository.create_bookmark returns (row, created); _find_by_normalized_url helper; one retry. -> [X]
   Self-review during the task: the first draft ended the lookup transaction with session.rollback(), which expires
   loaded ORM instances; changed to session.commit() (expire_on_commit=False, nothing written) before running tests.
3. T016: POST /bookmarks sets 200 when not created; 200 response declared with Bookmark; 409 removed. -> [X]
4. T008: removed DuplicateUrlError and its 409 handler from errors.py. -> [X]
   Suite after T015/T016/T008: 2 failed (test_errors.py old 409 tests, owned by T028), 98 passed.
5. T028: removed the 409 envelope test; OpenAPI test now expects 201 and 200 with Bookmark, 422 ErrorResponse, no 409. -> [X]
6. T029: README POST row updated. -> [X]
7. T030: suite on 3.13, 3.12, 3.11: 99 passed each; quickstart manual steps 1-8 all as expected (step 2: HTTP 200
   with the unchanged step 1 bookmark). -> [X]
All 30 tasks are [X].

## Review: code and artifact diffs together

- FR-004 (spec) <-> plan Summary <-> research "Preventing duplicate links" <-> repository.create_bookmark: same
  mechanism (ON CONFLICT DO NOTHING, then select in a new statement, return unchanged, one retry). Match.
- contracts/openapi.yaml POST responses {200 Bookmark, 201 Bookmark, 422 ErrorResponse} <-> generated
  /openapi.json POST responses {201, 200, 422} (printed above). Match; no 409 in either.
- Contract ErrorResponse.code enum [validation_error, not_found, method_not_allowed, internal_error] <-> codes
  the app emits: also "bad_request" (400), "conflict" (409) and "http_error" via STATUS_CODES for generic
  HTTPExceptions. Pre-existing (not touched by this change); nothing in the app raises 400/409 now. Noted, not changed.
- quickstart step 2 <-> manual run: match.
- tasks.md T012 retry test <-> test_existing_bookmark_deleted_before_lookup_is_saved_again: match (hooks
  repository._find_by_normalized_url, deletes through a separate connection on the real DB).
- Unreachable-in-practice path: if the retry also finds nothing (the row is deleted twice in a row between
  statements), create_bookmark raises RuntimeError -> 500 internal_error. Not covered by spec; noted.
- data-model.md: no schema change; no migration added (matches plan).

Completion report: 7 open tasks implemented and marked [X] (30/30). Tests: 99 passed on 3.11, 3.12, 3.13
(baseline before changes: 98 passed on 3.13; net +1 test: -2 removed/replaced duplicate tests, -1 409 envelope test,
+4 new US1 tests). Implementation matches spec, plan and contract.

```diff
$ git diff --stat; git diff
 README.md                                 |  2 +-
 specs/001-bookmarks-api/tasks.md          | 14 +++---
 src/bookmarks_api/errors.py               | 11 -----
 src/bookmarks_api/repository.py           | 42 +++++++++++-----
 src/bookmarks_api/routes.py               | 18 +++++--
 tests/integration/test_create_bookmark.py | 82 ++++++++++++++++++++++++++-----
 tests/integration/test_errors.py          | 18 ++-----
 7 files changed, 128 insertions(+), 59 deletions(-)
diff --git a/README.md b/README.md
index 5c4557f..b2b1bf4 100644
--- a/README.md
+++ b/README.md
@@ -97,7 +97,7 @@ uv run pytest                                          # tests, against the book
 
 | Endpoint | What it does |
 | --- | --- |
-| `POST /bookmarks` | Save `{"url", "title", "tags"}`; 409 if the link is already saved |
+| `POST /bookmarks` | Save `{"url", "title", "tags"}`; 201 for a new link, 200 with the existing bookmark (unchanged) if the link is already saved |
 | `GET /bookmarks?tag=&limit=&cursor=` | List newest first, 20 per page by default, optional tag filter; pass `next_cursor` from one page as `cursor` to get the next |
 | `DELETE /bookmarks/{id}` | Delete a bookmark |
 
diff --git a/specs/001-bookmarks-api/tasks.md b/specs/001-bookmarks-api/tasks.md
index a402094..61abec9 100644
--- a/specs/001-bookmarks-api/tasks.md
+++ b/specs/001-bookmarks-api/tasks.md
@@ -47,7 +47,7 @@ marked "changed 2026-10-24". The rationale and history of the previous task list
 - [X] T005 Create `src/bookmarks_api/models.py` mapping table `bookmarks` exactly as data-model.md: `id bigint` primary key generated always as identity; `url varchar(2048) not null`; `url_normalized varchar(2048) not null, unique`; `title varchar(200) not null, char_length(title) >= 1`; `tags text[] not null, default '{}', cardinality(tags) <= 10`; `created_at timestamptz not null, default now()`
 - [X] T006 Set up Alembic: `alembic.ini` and `migrations/env.py` reading the URL from `bookmarks_api.config` (overridable by `-x url=...` or the `sqlalchemy.url` option set by tests), with target metadata from `models.py`
 - [X] T007 Create migration `migrations/versions/0001_create_bookmarks.py` creating table `bookmarks` with the constraints in T005 and indexes `uq_bookmarks_url_normalized UNIQUE (url_normalized)`, `ix_bookmarks_created_at_id (created_at DESC, id DESC)`, `ix_bookmarks_tags GIN (tags)`; downgrade drops the table (no new migration for the 2026-10-24 change: the unique index already gives the guarantee, plan.md)
-- [ ] T008 (changed 2026-10-24) `src/bookmarks_api/errors.py`: Pydantic models `ErrorBody {code, message, details}` and `ErrorResponse {error: ErrorBody}`; domain exception `NotFoundError`; exception handlers producing the envelope for `RequestValidationError` (422 `validation_error`, field errors in `details`), `StarletteHTTPException` (status-mapped code), `NotFoundError` (404 `not_found`) and any other exception (500 `internal_error`, no internals) (Constitution III). Remove `DuplicateUrlError` and its 409 `duplicate_url` handler: a repeat save is no longer an error (FR-004, research.md "Error envelope")
+- [X] T008 (changed 2026-10-24) `src/bookmarks_api/errors.py`: Pydantic models `ErrorBody {code, message, details}` and `ErrorResponse {error: ErrorBody}`; domain exception `NotFoundError`; exception handlers producing the envelope for `RequestValidationError` (422 `validation_error`, field errors in `details`), `StarletteHTTPException` (status-mapped code), `NotFoundError` (404 `not_found`) and any other exception (500 `internal_error`, no internals) (Constitution III). Remove `DuplicateUrlError` and its 409 `duplicate_url` handler: a repeat save is no longer an error (FR-004, research.md "Error envelope")
 - [X] T009 Create `src/bookmarks_api/main.py` with `create_app()` registering the handlers from T008 and the router from `routes.py`, and module-level `app = create_app()`
 - [X] T010 Create `tests/conftest.py`: read `TEST_DATABASE_URL` (default `postgresql://bookmarks:bookmarks@localhost:5432/bookmarks_test`), run `alembic upgrade head` against it once per session, override `get_session` to use the test database, truncate `bookmarks` (restart identity) before every test, and provide a `client` fixture using FastAPI `TestClient` (Constitution II: no database mocks)
 
@@ -68,14 +68,14 @@ link returns 200 with the existing bookmark, unchanged, and still one row.
 > Write these first and confirm they fail before implementing.
 
 - [X] T011 [P] [US1] Unit tests in `tests/unit/test_normalize.py` for link normalization (lowercase scheme and host, default ports 80/443 removed, trailing path slashes removed, fragment removed, query kept; examples `HTTPS://Example.com:443/docs/#intro` → `https://example.com/docs`, `https://example.com/search?q=FastAPI` keeps `?q=FastAPI`; non-http(s) and host-less links rejected) and tag normalization (trim, lowercase, de-duplicate, sort; must match `^[a-z0-9-]{1,30}$`)
-- [ ] T012 [P] [US1] (changed 2026-10-24) Integration tests in `tests/integration/test_create_bookmark.py` for User Story 1 scenarios 1 to 4: save with no tags (201, `tags == []`, `created_at` present); tags `["Python", " api ", "python"]` → `["api", "python"]`; `https://example.com/docs` (title "Docs", no tags) then `HTTPS://Example.com/docs/#intro` with title "Other title" and tags `["x"]` → 200 with a body equal to the first response (same `id`, `url` `https://example.com/docs`, `title` "Docs", `tags` `[]`, `created_at`), the stored row unchanged in the database, still one row; missing url, missing title, `ftp://` link, url over 2048 characters, title over 200 characters, 11 tags, and invalid tag `"no spaces"` each → 422 `validation_error` and nothing saved; two concurrent saves of equivalent new links (two threads) → exactly one 201 and one 200, both bodies carrying the same `id`, one row (FR-004); when the existing bookmark is deleted between the conflicting insert and the lookup (simulated by wrapping `repository._find_by_normalized_url` so its first call deletes the row through a separate connection to the real test database), the save retries the insert and returns 201 with a new bookmark (research.md, "Preventing duplicate links")
+- [X] T012 [P] [US1] (changed 2026-10-24) Integration tests in `tests/integration/test_create_bookmark.py` for User Story 1 scenarios 1 to 4: save with no tags (201, `tags == []`, `created_at` present); tags `["Python", " api ", "python"]` → `["api", "python"]`; `https://example.com/docs` (title "Docs", no tags) then `HTTPS://Example.com/docs/#intro` with title "Other title" and tags `["x"]` → 200 with a body equal to the first response (same `id`, `url` `https://example.com/docs`, `title` "Docs", `tags` `[]`, `created_at`), the stored row unchanged in the database, still one row; missing url, missing title, `ftp://` link, url over 2048 characters, title over 200 characters, 11 tags, and invalid tag `"no spaces"` each → 422 `validation_error` and nothing saved; two concurrent saves of equivalent new links (two threads) → exactly one 201 and one 200, both bodies carrying the same `id`, one row (FR-004); when the existing bookmark is deleted between the conflicting insert and the lookup (simulated by wrapping `repository._find_by_normalized_url` so its first call deletes the row through a separate connection to the real test database), the save retries the insert and returns 201 with a new bookmark (research.md, "Preventing duplicate links")
 
 ### Implementation for User Story 1
 
 - [X] T013 [P] [US1] Implement `normalize_url(url) -> str` and `normalize_tags(tags) -> list[str]` in `src/bookmarks_api/normalize.py` using only the standard library, raising `ValueError` with a clear message on invalid input
 - [X] T014 [P] [US1] Create Pydantic models in `src/bookmarks_api/schemas.py`: `BookmarkCreate` (`url` str, max 2048, http/https with a host; `title` trimmed, 1 to 200 characters; `tags` list default `[]`, normalized via `normalize_tags`, at most 10 after de-duplication; extra fields forbidden) and `Bookmark` (`id`, `url`, `title`, `tags`, `created_at`)
-- [ ] T015 [US1] (changed 2026-10-24) Implement `create_bookmark(session, data) -> tuple[BookmarkRow, bool]` in `src/bookmarks_api/repository.py` returning the row and whether it was inserted: `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`; on insert commit and return `(row, True)`; when nothing is inserted, end the transaction, select the existing row by `url_normalized` in a new statement through a helper `_find_by_normalized_url(session, normalized)` and return `(row, False)` without writing to it; if that select finds nothing (deleted in between), retry the insert once (research.md, "Preventing duplicate links")
-- [ ] T016 [US1] (changed 2026-10-24) Implement `POST /bookmarks` in `src/bookmarks_api/routes.py` returning 201 with `Bookmark` for a new bookmark and 200 with the existing `Bookmark` when the link is already saved; declare the 200 response with the `Bookmark` model and the 422 response with `ErrorResponse`; remove the 409 response (contracts/openapi.yaml)
+- [X] T015 [US1] (changed 2026-10-24) Implement `create_bookmark(session, data) -> tuple[BookmarkRow, bool]` in `src/bookmarks_api/repository.py` returning the row and whether it was inserted: `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`; on insert commit and return `(row, True)`; when nothing is inserted, end the transaction, select the existing row by `url_normalized` in a new statement through a helper `_find_by_normalized_url(session, normalized)` and return `(row, False)` without writing to it; if that select finds nothing (deleted in between), retry the insert once (research.md, "Preventing duplicate links")
+- [X] T016 [US1] (changed 2026-10-24) Implement `POST /bookmarks` in `src/bookmarks_api/routes.py` returning 201 with `Bookmark` for a new bookmark and 200 with the existing `Bookmark` when the link is already saved; declare the 200 response with the `Bookmark` model and the 422 response with `ErrorResponse`; remove the 409 response (contracts/openapi.yaml)
 
 **Checkpoint**: User Story 1 works and is tested on its own (MVP)
 
@@ -147,9 +147,9 @@ again returns 404.
 
 **Purpose**: Improvements that affect multiple user stories
 
-- [ ] T028 [P] (changed 2026-10-24) Integration tests in `tests/integration/test_errors.py` asserting every error class (422, 404, 405, 500, and an unknown route 404) uses the envelope `{"error": {"code", "message", "details"}}` (SC-005), with the 409 `duplicate_url` envelope test removed; and that `/openapi.json` lists all three operations with request and response schemas (Constitution I): `POST /bookmarks` declares 201 and 200 with `Bookmark`, 422 with `ErrorResponse`, and no 409
-- [ ] T029 [P] (changed 2026-10-24) Update the `POST /bookmarks` row in `README.md`: 201 for a new link, 200 with the existing bookmark (unchanged) if the link is already saved, instead of "409 if the link is already saved"
-- [ ] T030 Run the full test suite on Python 3.11, 3.12 and 3.13 and the manual checks in `specs/001-bookmarks-api/quickstart.md` (step 2 now expects 200 with the unchanged step 1 bookmark)
+- [X] T028 [P] (changed 2026-10-24) Integration tests in `tests/integration/test_errors.py` asserting every error class (422, 404, 405, 500, and an unknown route 404) uses the envelope `{"error": {"code", "message", "details"}}` (SC-005), with the 409 `duplicate_url` envelope test removed; and that `/openapi.json` lists all three operations with request and response schemas (Constitution I): `POST /bookmarks` declares 201 and 200 with `Bookmark`, 422 with `ErrorResponse`, and no 409
+- [X] T029 [P] (changed 2026-10-24) Update the `POST /bookmarks` row in `README.md`: 201 for a new link, 200 with the existing bookmark (unchanged) if the link is already saved, instead of "409 if the link is already saved"
+- [X] T030 Run the full test suite on Python 3.11, 3.12 and 3.13 and the manual checks in `specs/001-bookmarks-api/quickstart.md` (step 2 now expects 200 with the unchanged step 1 bookmark)
 
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
index f93517e..58e01aa 100644
--- a/src/bookmarks_api/repository.py
+++ b/src/bookmarks_api/repository.py
@@ -6,16 +6,30 @@ from sqlalchemy import delete, func, select, tuple_
 from sqlalchemy.dialects.postgresql import insert
 from sqlalchemy.orm import Session
 
-from bookmarks_api.errors import DuplicateUrlError, NotFoundError
+from bookmarks_api.errors import NotFoundError
 from bookmarks_api.models import BookmarkRow
 from bookmarks_api.normalize import normalize_url
 from bookmarks_api.schemas import BookmarkCreate
 
+# One retry covers the case where the existing bookmark is deleted between the conflicting
+# insert and the lookup; the retry then either inserts or finds a row saved meanwhile.
+_INSERT_ATTEMPTS = 2
 
-def create_bookmark(session: Session, data: BookmarkCreate) -> BookmarkRow:
-    """Insert a bookmark, or raise DuplicateUrlError if its normalized link already exists.
 
-    ON CONFLICT DO NOTHING relies on the unique index, so this holds under concurrent saves.
+def _find_by_normalized_url(session: Session, normalized: str) -> BookmarkRow | None:
+    return session.scalars(
+        select(BookmarkRow).where(BookmarkRow.url_normalized == normalized)
+    ).one_or_none()
+
+
+def create_bookmark(session: Session, data: BookmarkCreate) -> tuple[BookmarkRow, bool]:
+    """Save a bookmark and return ``(row, created)``.
+
+    A new normalized link is inserted and returned with ``created=True``. A link that is already
+    saved returns the existing row unchanged with ``created=False``; the request's title and tags
+    are ignored (FR-004). ON CONFLICT DO NOTHING relies on the unique index, so two concurrent
+    saves of a new link store one row: under READ COMMITTED the loser's insert waits for the
+    winner to commit, and its follow-up select (a new statement) sees the winner's row.
     """
     normalized = normalize_url(data.url)
     statement = (
@@ -24,15 +38,19 @@ def create_bookmark(session: Session, data: BookmarkCreate) -> BookmarkRow:
         .on_conflict_do_nothing(index_elements=[BookmarkRow.url_normalized])
         .returning(BookmarkRow)
     )
-    row = session.scalars(statement).one_or_none()
-    if row is None:
+    for _ in range(_INSERT_ATTEMPTS):
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
+        existing = _find_by_normalized_url(session, normalized)
+        # End the read-only transaction without expiring the loaded row (rollback would expire
+        # it; the sessions use expire_on_commit=False). Nothing was written, so commit is a no-op.
+        session.commit()
+        if existing is not None:
+            return existing, False
+    raise RuntimeError("Could not save or find the bookmark after a concurrent delete.")
 
 
 def list_bookmarks(
diff --git a/src/bookmarks_api/routes.py b/src/bookmarks_api/routes.py
index cc51123..5a1ced8 100644
--- a/src/bookmarks_api/routes.py
+++ b/src/bookmarks_api/routes.py
@@ -40,13 +40,25 @@ def _reject_offset(value: str | None) -> None:
     status_code=status.HTTP_201_CREATED,
     response_model=Bookmark,
     summary="Save a bookmark",
+    description=(
+        "Saves a new link and returns 201. If the link, after normalization, is already "
+        "bookmarked, nothing is stored or changed: the existing bookmark is returned unchanged "
+        "with 200, and the title and tags in the request are ignored."
+    ),
     responses={
-        409: {"model": ErrorResponse, "description": "This link is already bookmarked."},
+        200: {
+            "model": Bookmark,
+            "description": "The link is already bookmarked; the existing bookmark, unchanged.",
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
diff --git a/tests/integration/test_create_bookmark.py b/tests/integration/test_create_bookmark.py
index bf537d3..882e620 100644
--- a/tests/integration/test_create_bookmark.py
+++ b/tests/integration/test_create_bookmark.py
@@ -37,36 +37,93 @@ def test_link_is_stored_as_given(client: TestClient) -> None:
     assert response.json()["url"] == "HTTPS://Example.com/Docs/"
 
 
-def test_equivalent_link_is_rejected_as_duplicate(client: TestClient, row_count) -> None:
+def test_equivalent_link_returns_the_existing_bookmark(client: TestClient, row_count) -> None:
     first = client.post("/bookmarks", json={"url": "https://example.com/docs", "title": "Docs"})
     second = client.post(
         "/bookmarks",
         json={"url": "HTTPS://Example.com/docs/#intro", "title": "Other title", "tags": ["x"]},
     )
 
-    assert second.status_code == 409
-    error = second.json()["error"]
-    assert error["code"] == "duplicate_url"
-    assert error["details"] == {"existing_id": first.json()["id"]}
+    assert first.status_code == 201
+    assert second.status_code == 200
+    assert second.json() == first.json()
+    assert second.json()["url"] == "https://example.com/docs"
+    assert second.json()["title"] == "Docs"
+    assert second.json()["tags"] == []
     assert row_count() == 1
 
 
-def test_duplicate_leaves_the_existing_bookmark_unchanged(client: TestClient, engine) -> None:
-    client.post("/bookmarks", json={"url": "https://example.com/docs", "title": "Docs"})
-    client.post("/bookmarks", json={"url": "https://example.com/docs/", "title": "Changed"})
+def test_repeat_save_leaves_the_stored_bookmark_unchanged(client: TestClient, engine) -> None:
+    client.post(
+        "/bookmarks", json={"url": "https://example.com/docs", "title": "Docs", "tags": ["a"]}
+    )
+    with engine.connect() as connection:
+        before = connection.exec_driver_sql("SELECT * FROM bookmarks").one()
+
+    response = client.post(
+        "/bookmarks",
+        json={"url": "https://example.com/docs/", "title": "Changed", "tags": ["b", "c"]},
+    )
 
+    assert response.status_code == 200
     with engine.connect() as connection:
-        title = connection.exec_driver_sql("SELECT title FROM bookmarks").scalar_one()
-    assert title == "Docs"
+        after = connection.exec_driver_sql("SELECT * FROM bookmarks").one()
+    assert after == before
+    assert after.title == "Docs"
+    assert after.tags == ["a"]
+
+
+def test_saving_the_same_link_many_times_leaves_one_bookmark(client: TestClient, row_count) -> None:
+    first = client.post("/bookmarks", json={"url": "https://example.com/a", "title": "A"})
+    repeats = [
+        client.post("/bookmarks", json={"url": url, "title": "Again"})
+        for url in ("https://example.com/a/", "HTTPS://EXAMPLE.COM:443/a", "https://example.com/a#x")
+    ]
+
+    assert first.status_code == 201
+    assert [response.status_code for response in repeats] == [200, 200, 200]
+    assert {response.json()["id"] for response in repeats} == {first.json()["id"]}
+    assert row_count() == 1
+
+
+def test_existing_bookmark_deleted_before_lookup_is_saved_again(
+    client: TestClient, engine, row_count, monkeypatch
+) -> None:
+    """The insert conflicts, then the row is deleted before the lookup: the save retries and
+    stores a new bookmark (research.md, "Preventing duplicate links")."""
+    from bookmarks_api import repository
+
+    first = client.post("/bookmarks", json={"url": "https://example.com/gone", "title": "Old"})
+    original_find = repository._find_by_normalized_url
+    calls = 0
+
+    def delete_then_find(session, normalized):
+        nonlocal calls
+        calls += 1
+        if calls == 1:
+            with engine.begin() as connection:
+                connection.exec_driver_sql("DELETE FROM bookmarks")
+        return original_find(session, normalized)
+
+    monkeypatch.setattr(repository, "_find_by_normalized_url", delete_then_find)
+    response = client.post("/bookmarks", json={"url": "https://example.com/gone/", "title": "New"})
+
+    assert response.status_code == 201
+    assert response.json()["title"] == "New"
+    assert response.json()["id"] != first.json()["id"]
+    assert row_count() == 1
 
 
 def test_concurrent_saves_of_the_same_link_leave_one_bookmark(client: TestClient, row_count) -> None:
     statuses: list[int] = []
+    ids: list[int] = []
     barrier = threading.Barrier(2)
 
     def save(url: str) -> None:
         barrier.wait()
-        statuses.append(client.post("/bookmarks", json={"url": url, "title": "Race"}).status_code)
+        response = client.post("/bookmarks", json={"url": url, "title": "Race"})
+        statuses.append(response.status_code)
+        ids.append(response.json()["id"])
 
     threads = [
         threading.Thread(target=save, args=("https://example.com/race",)),
@@ -77,7 +134,8 @@ def test_concurrent_saves_of_the_same_link_leave_one_bookmark(client: TestClient
     for thread in threads:
         thread.join()
 
-    assert sorted(statuses) == [201, 409]
+    assert sorted(statuses) == [200, 201]
+    assert len(set(ids)) == 1
     assert row_count() == 1
 
 
diff --git a/tests/integration/test_errors.py b/tests/integration/test_errors.py
index 1f473e0..6ed5e61 100644
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
+        for code in ("201", "200"):
+            success = operation["responses"][code]["content"]["application/json"]["schema"]
+            assert success["$ref"].endswith("/Bookmark")
+        assert "409" not in operation["responses"]
     if method == "get":
         success = operation["responses"]["200"]["content"]["application/json"]["schema"]
         assert success["$ref"].endswith("/BookmarkPage")
```

End: 2026-10-24T11:53:57Z
