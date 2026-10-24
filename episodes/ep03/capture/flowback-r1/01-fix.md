# 01-fix

Step start: 2026-10-24T11:41:00Z

## Context

Worktree /home/claude/runs/flowback-r1, branch claude/ep03-flowback-r1, starting at tag ep03-start (git describe: `ep03-start`).

## Command: baseline tests

```
$ set -a; . ./.env; set +a; uv run --python 3.13 pytest -q
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
Using CPython 3.13.17 interpreter at: /usr/local/bin/python3.13
Creating virtual environment at: .venv
   Building bookmarks-api @ file:///home/claude/runs/flowback-r1
      Built bookmarks-api @ file:///home/claude/runs/flowback-r1
Installed 29 packages in 17ms
........................................................................ [ 73%]
..........................                                               [100%]
98 passed in 3.23s
```

## Command: locate the duplicate rule in code and tests

```
$ git grep -n -i "409\|duplicate\|conflict\|DuplicateUrl" ep03-start -- src tests   # (ep03-start prefix stripped; same content as the pre-change working tree)
src/bookmarks_api/errors.py:35:class DuplicateUrlError(Exception):
src/bookmarks_api/errors.py:42:STATUS_CODES = {400: "bad_request", 404: "not_found", 405: "method_not_allowed", 409: "conflict"}
src/bookmarks_api/errors.py:78:    @app.exception_handler(DuplicateUrlError)
src/bookmarks_api/errors.py:79:    async def handle_duplicate(_: Request, exc: DuplicateUrlError) -> JSONResponse:
src/bookmarks_api/errors.py:80:        return error_response(409, "duplicate_url", exc.message, {"existing_id": exc.existing_id})
src/bookmarks_api/normalize.py:16:    """Return the normalized form of a link used to detect duplicates.
src/bookmarks_api/normalize.py:59:    """Normalize each tag, drop duplicates and return them sorted."""
src/bookmarks_api/repository.py:9:from bookmarks_api.errors import DuplicateUrlError, NotFoundError
src/bookmarks_api/repository.py:16:    """Insert a bookmark, or raise DuplicateUrlError if its normalized link already exists.
src/bookmarks_api/repository.py:18:    ON CONFLICT DO NOTHING relies on the unique index, so this holds under concurrent saves.
src/bookmarks_api/repository.py:24:        .on_conflict_do_nothing(index_elements=[BookmarkRow.url_normalized])
src/bookmarks_api/repository.py:33:        raise DuplicateUrlError(existing_id)
src/bookmarks_api/routes.py:44:        409: {"model": ErrorResponse, "description": "This link is already bookmarked."},
tests/integration/test_create_bookmark.py:23:def test_tags_are_trimmed_lowercased_and_deduplicated(client: TestClient) -> None:
tests/integration/test_create_bookmark.py:40:def test_equivalent_link_is_rejected_as_duplicate(client: TestClient, row_count) -> None:
tests/integration/test_create_bookmark.py:47:    assert second.status_code == 409
tests/integration/test_create_bookmark.py:49:    assert error["code"] == "duplicate_url"
tests/integration/test_create_bookmark.py:54:def test_duplicate_leaves_the_existing_bookmark_unchanged(client: TestClient, engine) -> None:
tests/integration/test_create_bookmark.py:80:    assert sorted(statuses) == [201, 409]
tests/integration/test_errors.py:25:def test_duplicate_error_envelope(client: TestClient) -> None:
tests/integration/test_errors.py:30:        409,
tests/integration/test_errors.py:31:        "duplicate_url",
tests/integration/test_errors.py:77:    error_codes = {"post": {"409", "422"}, "get": {"422"}, "delete": {"404", "422"}}[method]
tests/integration/test_list_bookmarks.py:70:def test_saves_between_pages_cause_no_duplicates_or_gaps(client: TestClient) -> None:
```

## Change made (code first, per flow-back)

- `repository.create_bookmark` now returns `(row, created)`. On a normalized-link conflict it reads the existing row and returns it with `created=False` instead of raising. If the conflicting row was deleted between the insert and the lookup, it retries the insert.
- `POST /bookmarks` sets 200 OK when `created` is false, keeps 201 for new links, and documents 201 and 200 (both `Bookmark`) and 422 in OpenAPI; 409 is no longer declared.
- `DuplicateUrlError` and its 409 `duplicate_url` handler are removed from `errors.py` (no longer raised anywhere). The generic `409: conflict` entry in `STATUS_CODES` is left as is.
- Tests: duplicate save now asserts 200 and a body identical to the first save; the stored url/title/tags are unchanged when the duplicate sends a different title and tags; concurrent saves yield [200, 201] with identical bodies and one row; the 409 envelope test is removed; the OpenAPI test asserts POST has 201 and 200 `Bookmark` responses and no 409.

## Command: diff

```diff
$ git diff
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
index f93517e..01f0c2b 100644
--- a/src/bookmarks_api/repository.py
+++ b/src/bookmarks_api/repository.py
@@ -6,16 +6,19 @@ from sqlalchemy import delete, func, select, tuple_
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
+    """Save a bookmark and return ``(row, created)``.
 
-    ON CONFLICT DO NOTHING relies on the unique index, so this holds under concurrent saves.
+    If a bookmark with the same normalized link already exists, return it unchanged with
+    ``created=False``; the title and tags in ``data`` are ignored (FR-004). ON CONFLICT DO NOTHING
+    relies on the unique index, so concurrent saves of the same new link store exactly one row:
+    one caller gets ``created=True`` and the others get that same row with ``created=False``.
     """
     normalized = normalize_url(data.url)
     statement = (
@@ -24,15 +27,20 @@ def create_bookmark(session: Session, data: BookmarkCreate) -> BookmarkRow:
         .on_conflict_do_nothing(index_elements=[BookmarkRow.url_normalized])
         .returning(BookmarkRow)
     )
-    row = session.scalars(statement).one_or_none()
-    if row is None:
+    while True:
+        row = session.scalars(statement).one_or_none()
+        if row is not None:
+            session.commit()
+            return row, True
+        session.rollback()
+        existing = session.scalars(
+            select(BookmarkRow).where(BookmarkRow.url_normalized == normalized)
+        ).one_or_none()
+        if existing is not None:
+            session.commit()
+            return existing, False
+        # The conflicting bookmark was deleted between the insert and the lookup: try again.
         session.rollback()
-        existing_id = session.scalar(
-            select(BookmarkRow.id).where(BookmarkRow.url_normalized == normalized)
-        )
-        raise DuplicateUrlError(existing_id)
-    session.commit()
-    return row
 
 
 def list_bookmarks(
diff --git a/src/bookmarks_api/routes.py b/src/bookmarks_api/routes.py
index cc51123..7a40b14 100644
--- a/src/bookmarks_api/routes.py
+++ b/src/bookmarks_api/routes.py
@@ -40,13 +40,25 @@ def _reject_offset(value: str | None) -> None:
     status_code=status.HTTP_201_CREATED,
     response_model=Bookmark,
     summary="Save a bookmark",
+    description=(
+        "Saves a new link and returns 201 Created. If the link (after normalization) is already "
+        "saved, returns the existing bookmark unchanged with 200 OK; the title and tags in the "
+        "request are ignored."
+    ),
     responses={
-        409: {"model": ErrorResponse, "description": "This link is already bookmarked."},
+        201: {"description": "The link was saved as a new bookmark."},
+        200: {
+            "model": Bookmark,
+            "description": "The link was already saved; the existing bookmark, unchanged.",
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
diff --git a/tests/integration/test_create_bookmark.py b/tests/integration/test_create_bookmark.py
index bf537d3..204f234 100644
--- a/tests/integration/test_create_bookmark.py
+++ b/tests/integration/test_create_bookmark.py
@@ -37,36 +37,44 @@ def test_link_is_stored_as_given(client: TestClient) -> None:
     assert response.json()["url"] == "HTTPS://Example.com/Docs/"
 
 
-def test_equivalent_link_is_rejected_as_duplicate(client: TestClient, row_count) -> None:
-    first = client.post("/bookmarks", json={"url": "https://example.com/docs", "title": "Docs"})
+def test_equivalent_link_returns_the_existing_bookmark(client: TestClient, row_count) -> None:
+    first = client.post(
+        "/bookmarks", json={"url": "https://example.com/docs", "title": "Docs", "tags": ["a"]}
+    )
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
     assert row_count() == 1
 
 
 def test_duplicate_leaves_the_existing_bookmark_unchanged(client: TestClient, engine) -> None:
     client.post("/bookmarks", json={"url": "https://example.com/docs", "title": "Docs"})
-    client.post("/bookmarks", json={"url": "https://example.com/docs/", "title": "Changed"})
+    response = client.post(
+        "/bookmarks", json={"url": "https://example.com/docs/", "title": "Changed", "tags": ["new"]}
+    )
 
+    assert response.status_code == 200
+    assert response.json()["title"] == "Docs"
+    assert response.json()["tags"] == []
     with engine.connect() as connection:
-        title = connection.exec_driver_sql("SELECT title FROM bookmarks").scalar_one()
-    assert title == "Docs"
+        url, title, tags = connection.exec_driver_sql(
+            "SELECT url, title, tags FROM bookmarks"
+        ).one()
+    assert (url, title, tags) == ("https://example.com/docs", "Docs", [])
 
 
 def test_concurrent_saves_of_the_same_link_leave_one_bookmark(client: TestClient, row_count) -> None:
-    statuses: list[int] = []
+    responses = []
     barrier = threading.Barrier(2)
 
     def save(url: str) -> None:
         barrier.wait()
-        statuses.append(client.post("/bookmarks", json={"url": url, "title": "Race"}).status_code)
+        responses.append(client.post("/bookmarks", json={"url": url, "title": "Race"}))
 
     threads = [
         threading.Thread(target=save, args=("https://example.com/race",)),
@@ -77,7 +85,8 @@ def test_concurrent_saves_of_the_same_link_leave_one_bookmark(client: TestClient
     for thread in threads:
         thread.join()
 
-    assert sorted(statuses) == [201, 409]
+    assert sorted(response.status_code for response in responses) == [200, 201]
+    assert responses[0].json() == responses[1].json()
     assert row_count() == 1
 
 
diff --git a/tests/integration/test_errors.py b/tests/integration/test_errors.py
index 1f473e0..228aeb6 100644
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
+        for code in ("201", "200"):
+            success = operation["responses"][code]["content"]["application/json"]["schema"]
+            assert success["$ref"].endswith("/Bookmark")
     if method == "get":
         success = operation["responses"]["200"]["content"]["application/json"]["schema"]
         assert success["$ref"].endswith("/BookmarkPage")
```

## Command: tests after the change

```
$ set -a; . ./.env; set +a; uv run --python 3.13 pytest -q
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
........................................................................ [ 74%]
.........................                                                [100%]
97 passed in 2.77s
```

```
$ uv run --python 3.13 pytest -q tests/integration/test_create_bookmark.py tests/integration/test_errors.py -v
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
============================= test session starts ==============================
platform linux -- Python 3.13.17, pytest-9.1.1, pluggy-1.7.0
rootdir: /home/claude/runs/flowback-r1
configfile: pyproject.toml
plugins: anyio-4.15.1
collected 27 items

tests/integration/test_create_bookmark.py ..................             [ 66%]
tests/integration/test_errors.py .........                               [100%]

============================== 27 passed in 0.90s ==============================
```

## Command: generated OpenAPI for POST /bookmarks

```
$ uv run --python 3.13 python -c "import json; from bookmarks_api.main import create_app; print(json.dumps(create_app().openapi()['paths']['/bookmarks']['post']['responses'], indent=1))"
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
{
 "201": {
  "description": "The link was saved as a new bookmark.",
  "content": {
   "application/json": {
    "schema": {
     "$ref": "#/components/schemas/Bookmark"
    }
   }
  }
 },
 "200": {
  "description": "The link was already saved; the existing bookmark, unchanged.",
  "content": {
   "application/json": {
    "schema": {
     "$ref": "#/components/schemas/Bookmark"
    }
   }
  }
 },
 "422": {
  "description": "The request is not valid.",
  "content": {
   "application/json": {
    "schema": {
     "$ref": "#/components/schemas/ErrorResponse"
    }
   }
  }
 }
}
```

## Note

`uvx ruff check src tests` reports one pre-existing I001 import-order finding in `src/bookmarks_api/models.py` (file untouched in this step; ruff is not a project dependency). Not acted on.

Step end: 2026-10-24T11:42:47Z
