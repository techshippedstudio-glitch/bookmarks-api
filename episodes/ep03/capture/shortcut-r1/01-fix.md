# shortcut-r1 step 01: fix

Model: Opus 5.5 (claude-opus-5-5)

```console
$ date -u +%Y-%m-%dT%H:%M:%SZ
2026-10-24T11:41:40Z
[exit 0]
```

```console
$ git ls-files src tests specs | head -80
specs/001-bookmarks-api/checklists/requirements.md
specs/001-bookmarks-api/contracts/openapi.yaml
specs/001-bookmarks-api/data-model.md
specs/001-bookmarks-api/plan.md
specs/001-bookmarks-api/quickstart.md
specs/001-bookmarks-api/research.md
specs/001-bookmarks-api/spec.md
specs/001-bookmarks-api/tasks.md
src/bookmarks_api/__init__.py
src/bookmarks_api/config.py
src/bookmarks_api/cursor.py
src/bookmarks_api/db.py
src/bookmarks_api/errors.py
src/bookmarks_api/main.py
src/bookmarks_api/models.py
src/bookmarks_api/normalize.py
src/bookmarks_api/repository.py
src/bookmarks_api/routes.py
src/bookmarks_api/schemas.py
tests/__init__.py
tests/conftest.py
tests/integration/conftest.py
tests/integration/test_create_bookmark.py
tests/integration/test_delete_bookmark.py
tests/integration/test_errors.py
tests/integration/test_filter_by_tag.py
tests/integration/test_list_bookmarks.py
tests/unit/test_cursor.py
tests/unit/test_normalize.py
[exit 0]
```

```console
$ grep -rn "409\|conflict\|Conflict\|duplicate\|Duplicate" src tests | head -60
grep: src/bookmarks_api/__pycache__/repository.cpython-313.pyc: binary file matches
grep: src/bookmarks_api/__pycache__/errors.cpython-313.pyc: binary file matches
grep: src/bookmarks_api/__pycache__/normalize.cpython-313.pyc: binary file matches
grep: tests/integration/__pycache__/test_list_bookmarks.cpython-313-pytest-9.1.1.pyc: binary file matches
grep: tests/integration/__pycache__/test_errors.cpython-313-pytest-9.1.1.pyc: binary file matches
grep: tests/integration/__pycache__/test_create_bookmark.cpython-313-pytest-9.1.1.pyc: binary file matches
src/bookmarks_api/errors.py:35:class DuplicateUrlError(Exception):
src/bookmarks_api/errors.py:42:STATUS_CODES = {400: "bad_request", 404: "not_found", 405: "method_not_allowed", 409: "conflict"}
src/bookmarks_api/errors.py:78:    @app.exception_handler(DuplicateUrlError)
src/bookmarks_api/errors.py:79:    async def handle_duplicate(_: Request, exc: DuplicateUrlError) -> JSONResponse:
src/bookmarks_api/errors.py:80:        return error_response(409, "duplicate_url", exc.message, {"existing_id": exc.existing_id})
src/bookmarks_api/normalize.py:16:    """Return the normalized form of a link used to detect duplicates.
src/bookmarks_api/normalize.py:59:    """Normalize each tag, drop duplicates and return them sorted."""
src/bookmarks_api/repository.py:9:from bookmarks_api.errors import DuplicateUrlError, NotFoundError
src/bookmarks_api/repository.py:16:    """Insert a bookmark, or raise DuplicateUrlError if its normalized link already exists.
src/bookmarks_api/repository.py:24:        .on_conflict_do_nothing(index_elements=[BookmarkRow.url_normalized])
src/bookmarks_api/repository.py:33:        raise DuplicateUrlError(existing_id)
src/bookmarks_api/routes.py:44:        409: {"model": ErrorResponse, "description": "This link is already bookmarked."},
tests/integration/test_create_bookmark.py:23:def test_tags_are_trimmed_lowercased_and_deduplicated(client: TestClient) -> None:
tests/integration/test_create_bookmark.py:40:def test_equivalent_link_is_rejected_as_duplicate(client: TestClient, row_count) -> None:
tests/integration/test_create_bookmark.py:47:    assert second.status_code == 409
tests/integration/test_create_bookmark.py:49:    assert error["code"] == "duplicate_url"
tests/integration/test_create_bookmark.py:54:def test_duplicate_leaves_the_existing_bookmark_unchanged(client: TestClient, engine) -> None:
tests/integration/test_create_bookmark.py:80:    assert sorted(statuses) == [201, 409]
tests/integration/test_list_bookmarks.py:70:def test_saves_between_pages_cause_no_duplicates_or_gaps(client: TestClient) -> None:
tests/integration/test_errors.py:25:def test_duplicate_error_envelope(client: TestClient) -> None:
tests/integration/test_errors.py:30:        409,
tests/integration/test_errors.py:31:        "duplicate_url",
tests/integration/test_errors.py:77:    error_codes = {"post": {"409", "422"}, "get": {"422"}, "delete": {"404", "422"}}[method]
[exit 0]
```

```console
$ cat src/bookmarks_api/repository.py src/bookmarks_api/routes.py src/bookmarks_api/errors.py
"""Database queries for bookmarks."""

from datetime import datetime

from sqlalchemy import delete, func, select, tuple_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from bookmarks_api.errors import DuplicateUrlError, NotFoundError
from bookmarks_api.models import BookmarkRow
from bookmarks_api.normalize import normalize_url
from bookmarks_api.schemas import BookmarkCreate


def create_bookmark(session: Session, data: BookmarkCreate) -> BookmarkRow:
    """Insert a bookmark, or raise DuplicateUrlError if its normalized link already exists.

    ON CONFLICT DO NOTHING relies on the unique index, so this holds under concurrent saves.
    """
    normalized = normalize_url(data.url)
    statement = (
        insert(BookmarkRow)
        .values(url=data.url, url_normalized=normalized, title=data.title, tags=data.tags)
        .on_conflict_do_nothing(index_elements=[BookmarkRow.url_normalized])
        .returning(BookmarkRow)
    )
    row = session.scalars(statement).one_or_none()
    if row is None:
        session.rollback()
        existing_id = session.scalar(
            select(BookmarkRow.id).where(BookmarkRow.url_normalized == normalized)
        )
        raise DuplicateUrlError(existing_id)
    session.commit()
    return row


def list_bookmarks(
    session: Session,
    *,
    limit: int,
    after: tuple[datetime, int] | None = None,
    tag: str | None = None,
) -> tuple[list[BookmarkRow], int, bool]:
    """Return one page of bookmarks, newest first, the total matching the filter, and whether
    more pages follow.

    Keyset pagination (Constitution VI): the page starts strictly after the (created_at, id)
    position in ``after``, so saves and deletes between requests never shift the page. The
    row comparison matches the (created_at DESC, id DESC) index, so every page is a range scan.
    """
    conditions = [BookmarkRow.tags.contains([tag])] if tag else []
    total = session.scalar(select(func.count()).select_from(BookmarkRow).where(*conditions))
    page_conditions = list(conditions)
    if after is not None:
        page_conditions.append(tuple_(BookmarkRow.created_at, BookmarkRow.id) < tuple_(*after))
    rows = session.scalars(
        select(BookmarkRow)
        .where(*page_conditions)
        .order_by(BookmarkRow.created_at.desc(), BookmarkRow.id.desc())
        .limit(limit + 1)
    ).all()
    return list(rows[:limit]), total or 0, len(rows) > limit


def delete_bookmark(session: Session, bookmark_id: int) -> None:
    """Delete a bookmark by id, or raise NotFoundError if there is none."""
    result = session.execute(delete(BookmarkRow).where(BookmarkRow.id == bookmark_id))
    if result.rowcount == 0:
        session.rollback()
        raise NotFoundError(f"No bookmark with id {bookmark_id}.")
    session.commit()
"""HTTP endpoints for /bookmarks."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status
from pydantic import AfterValidator
from sqlalchemy.orm import Session

from bookmarks_api import repository
from bookmarks_api.cursor import decode_cursor, encode_cursor
from bookmarks_api.db import get_session
from bookmarks_api.errors import ErrorResponse
from bookmarks_api.normalize import normalize_tag
from bookmarks_api.schemas import Bookmark, BookmarkCreate, BookmarkPage

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])

SessionDep = Annotated[Session, Depends(get_session)]

ERROR_422 = {422: {"model": ErrorResponse, "description": "The request is not valid."}}

OFFSET_REMOVED = (
    "offset is not supported (Constitution VI); pass the previous page's next_cursor as cursor."
)


def _check_cursor(value: str | None) -> str | None:
    if value is not None:
        decode_cursor(value)  # raises ValueError for a malformed cursor
    return value


def _reject_offset(value: str | None) -> None:
    if value is not None:
        raise ValueError(OFFSET_REMOVED)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=Bookmark,
    summary="Save a bookmark",
    responses={
        409: {"model": ErrorResponse, "description": "This link is already bookmarked."},
        **ERROR_422,
    },
)
def create_bookmark(data: BookmarkCreate, session: SessionDep) -> Bookmark:
    return Bookmark.model_validate(repository.create_bookmark(session, data))


@router.get(
    "",
    response_model=BookmarkPage,
    summary="List bookmarks, newest first",
    responses=ERROR_422,
)
def list_bookmarks(
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=100, description="Page size, 1 to 100.")] = 20,
    cursor: Annotated[
        str | None,
        Query(description="The next_cursor from the previous page; omit for the first page."),
        AfterValidator(_check_cursor),
    ] = None,
    tag: Annotated[
        str | None,
        Query(description="Only bookmarks with this tag (normalized like tags)."),
        AfterValidator(lambda value: normalize_tag(value) if value is not None else None),
    ] = None,
    offset: Annotated[
        str | None, Query(include_in_schema=False), AfterValidator(_reject_offset)
    ] = None,
) -> BookmarkPage:
    after = decode_cursor(cursor) if cursor is not None else None
    rows, total, has_more = repository.list_bookmarks(session, limit=limit, after=after, tag=tag)
    next_cursor = encode_cursor(rows[-1].created_at, rows[-1].id) if has_more else None
    return BookmarkPage(
        items=[Bookmark.model_validate(row) for row in rows],
        total=total,
        limit=limit,
        next_cursor=next_cursor,
    )


@router.delete(
    "/{bookmark_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a bookmark",
    responses={404: {"model": ErrorResponse, "description": "No bookmark with this id."}, **ERROR_422},
)
def delete_bookmark(
    bookmark_id: Annotated[int, Path(ge=1, description="The bookmark's id.")], session: SessionDep
) -> Response:
    repository.delete_bookmark(session, bookmark_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
"""One error envelope for every error response (Constitution III).

    {"error": {"code": "...", "message": "...", "details": ...}}
"""

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class ErrorBody(BaseModel):
    code: str
    message: str
    details: Any = None


class ErrorResponse(BaseModel):
    error: ErrorBody


class NotFoundError(Exception):
    def __init__(self, message: str = "Bookmark not found.") -> None:
        super().__init__(message)
        self.message = message


class DuplicateUrlError(Exception):
    def __init__(self, existing_id: int) -> None:
        super().__init__(f"This link is already bookmarked (id {existing_id}).")
        self.existing_id = existing_id
        self.message = str(self)


STATUS_CODES = {400: "bad_request", 404: "not_found", 405: "method_not_allowed", 409: "conflict"}


def error_response(status: int, code: str, message: str, details: Any = None) -> JSONResponse:
    body = ErrorResponse(error=ErrorBody(code=code, message=message, details=details))
    return JSONResponse(status_code=status, content=jsonable_encoder(body))


def _validation_details(exc: RequestValidationError) -> list[dict[str, Any]]:
    details = []
    for err in exc.errors():
        details.append(
            {
                "field": ".".join(str(part) for part in err.get("loc", ()) if part != "body"),
                "message": err.get("msg", "Invalid value.").removeprefix("Value error, "),
            }
        )
    return details


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def handle_validation(_: Request, exc: RequestValidationError) -> JSONResponse:
        return error_response(
            422, "validation_error", "The request is not valid.", _validation_details(exc)
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = STATUS_CODES.get(exc.status_code, "http_error")
        return error_response(exc.status_code, code, str(exc.detail))

    @app.exception_handler(NotFoundError)
    async def handle_not_found(_: Request, exc: NotFoundError) -> JSONResponse:
        return error_response(404, "not_found", exc.message)

    @app.exception_handler(DuplicateUrlError)
    async def handle_duplicate(_: Request, exc: DuplicateUrlError) -> JSONResponse:
        return error_response(409, "duplicate_url", exc.message, {"existing_id": exc.existing_id})

    @app.exception_handler(Exception)
    async def handle_unexpected(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error", exc_info=exc)
        return error_response(500, "internal_error", "Something went wrong.")
[exit 0]
```

```console
$ cat tests/integration/test_create_bookmark.py tests/integration/test_errors.py
"""User Story 1 - Save a bookmark (spec.md, scenarios 1 to 4)."""

import threading
from datetime import datetime

import pytest
from fastapi.testclient import TestClient


def test_save_with_title_and_no_tags(client: TestClient, row_count) -> None:
    response = client.post("/bookmarks", json={"url": "https://example.com/docs", "title": "Docs"})

    assert response.status_code == 201
    body = response.json()
    assert body["url"] == "https://example.com/docs"
    assert body["title"] == "Docs"
    assert body["tags"] == []
    assert isinstance(body["id"], int)
    datetime.fromisoformat(body["created_at"])
    assert row_count() == 1


def test_tags_are_trimmed_lowercased_and_deduplicated(client: TestClient) -> None:
    response = client.post(
        "/bookmarks",
        json={"url": "https://example.com", "title": "Ex", "tags": ["Python", " api ", "python"]},
    )

    assert response.status_code == 201
    assert response.json()["tags"] == ["api", "python"]


def test_link_is_stored_as_given(client: TestClient) -> None:
    response = client.post("/bookmarks", json={"url": "HTTPS://Example.com/Docs/", "title": "X"})

    assert response.status_code == 201
    assert response.json()["url"] == "HTTPS://Example.com/Docs/"


def test_equivalent_link_is_rejected_as_duplicate(client: TestClient, row_count) -> None:
    first = client.post("/bookmarks", json={"url": "https://example.com/docs", "title": "Docs"})
    second = client.post(
        "/bookmarks",
        json={"url": "HTTPS://Example.com/docs/#intro", "title": "Other title", "tags": ["x"]},
    )

    assert second.status_code == 409
    error = second.json()["error"]
    assert error["code"] == "duplicate_url"
    assert error["details"] == {"existing_id": first.json()["id"]}
    assert row_count() == 1


def test_duplicate_leaves_the_existing_bookmark_unchanged(client: TestClient, engine) -> None:
    client.post("/bookmarks", json={"url": "https://example.com/docs", "title": "Docs"})
    client.post("/bookmarks", json={"url": "https://example.com/docs/", "title": "Changed"})

    with engine.connect() as connection:
        title = connection.exec_driver_sql("SELECT title FROM bookmarks").scalar_one()
    assert title == "Docs"


def test_concurrent_saves_of_the_same_link_leave_one_bookmark(client: TestClient, row_count) -> None:
    statuses: list[int] = []
    barrier = threading.Barrier(2)

    def save(url: str) -> None:
        barrier.wait()
        statuses.append(client.post("/bookmarks", json={"url": url, "title": "Race"}).status_code)

    threads = [
        threading.Thread(target=save, args=("https://example.com/race",)),
        threading.Thread(target=save, args=("https://EXAMPLE.com/race/",)),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sorted(statuses) == [201, 409]
    assert row_count() == 1


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({"title": "No link"}, id="missing-url"),
        pytest.param({"url": "https://example.com"}, id="missing-title"),
        pytest.param({"url": "https://example.com", "title": "   "}, id="blank-title"),
        pytest.param({"url": "ftp://example.com", "title": "FTP"}, id="ftp-link"),
        pytest.param({"url": "example.com", "title": "No scheme"}, id="no-scheme"),
        pytest.param(
            {"url": "https://example.com/" + "a" * 2048, "title": "Long"}, id="url-over-2048"
        ),
        pytest.param({"url": "https://example.com", "title": "t" * 201}, id="title-over-200"),
        pytest.param(
            {"url": "https://example.com", "title": "Many", "tags": [f"t{i}" for i in range(11)]},
            id="eleven-tags",
        ),
        pytest.param(
            {"url": "https://example.com", "title": "Bad tag", "tags": ["no spaces"]},
            id="invalid-tag",
        ),
        pytest.param(
            {"url": "https://example.com", "title": "Extra", "rating": 5}, id="unknown-field"
        ),
    ],
)
def test_invalid_input_is_rejected_and_nothing_saved(
    client: TestClient, row_count, payload: dict
) -> None:
    response = client.post("/bookmarks", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert row_count() == 0


def test_title_of_exactly_200_and_ten_tags_are_accepted(client: TestClient) -> None:
    response = client.post(
        "/bookmarks",
        json={
            "url": "https://example.com",
            "title": "t" * 200,
            "tags": [f"t{i}" for i in range(10)],
        },
    )

    assert response.status_code == 201


def test_eleven_tags_that_dedupe_to_ten_are_accepted(client: TestClient) -> None:
    tags = [f"t{i}" for i in range(10)] + ["T0"]
    response = client.post(
        "/bookmarks", json={"url": "https://example.com", "title": "Dupes", "tags": tags}
    )

    assert response.status_code == 201
    assert len(response.json()["tags"]) == 10
"""Cross-cutting checks: one error envelope everywhere (SC-005) and a complete OpenAPI contract
(Constitution I)."""

import pytest
from fastapi.testclient import TestClient


def assert_envelope(response, status: int, code: str) -> None:
    assert response.status_code == status
    body = response.json()
    assert set(body) == {"error"}
    assert set(body["error"]) == {"code", "message", "details"}
    assert body["error"]["code"] == code
    assert isinstance(body["error"]["message"], str) and body["error"]["message"]


def test_validation_error_envelope(client: TestClient) -> None:
    response = client.post("/bookmarks", json={"url": "ftp://x", "title": ""})

    assert_envelope(response, 422, "validation_error")
    fields = {detail["field"] for detail in response.json()["error"]["details"]}
    assert fields == {"url", "title"}


def test_duplicate_error_envelope(client: TestClient) -> None:
    client.post("/bookmarks", json={"url": "https://example.com", "title": "A"})

    assert_envelope(
        client.post("/bookmarks", json={"url": "https://example.com/", "title": "B"}),
        409,
        "duplicate_url",
    )


def test_not_found_error_envelope(client: TestClient) -> None:
    assert_envelope(client.delete("/bookmarks/12345"), 404, "not_found")


def test_unknown_route_uses_the_envelope(client: TestClient) -> None:
    assert_envelope(client.get("/nothing-here"), 404, "not_found")


def test_wrong_method_uses_the_envelope(client: TestClient) -> None:
    assert_envelope(client.put("/bookmarks"), 405, "method_not_allowed")


def test_malformed_json_uses_the_envelope(client: TestClient) -> None:
    response = client.post(
        "/bookmarks", content="{not json", headers={"Content-Type": "application/json"}
    )

    assert_envelope(response, 422, "validation_error")


def test_unexpected_errors_hide_internals(client: TestClient, monkeypatch) -> None:
    from bookmarks_api import repository

    def broken(*_args, **_kwargs):
        raise RuntimeError("SELECT secret FROM somewhere")

    monkeypatch.setattr(repository, "list_bookmarks", broken)
    response = client.get("/bookmarks")

    assert_envelope(response, 500, "internal_error")
    assert "secret" not in response.text


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
        schema = operation["responses"][code]["content"]["application/json"]["schema"]
        assert schema["$ref"].endswith("/ErrorResponse")
    if method == "post":
        assert operation["requestBody"]["content"]["application/json"]["schema"]["$ref"].endswith(
            "/BookmarkCreate"
        )
        success = operation["responses"]["201"]["content"]["application/json"]["schema"]
        assert success["$ref"].endswith("/Bookmark")
    if method == "get":
        success = operation["responses"]["200"]["content"]["application/json"]["schema"]
        assert success["$ref"].endswith("/BookmarkPage")
[exit 0]
```

Edits applied via scripted string replacement (python3 heredoc) to repository.py, routes.py, errors.py, test_create_bookmark.py, test_errors.py. Resulting diff:

```console
$ git diff -- src tests
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
index f93517e..a7cc975 100644
--- a/src/bookmarks_api/repository.py
+++ b/src/bookmarks_api/repository.py
@@ -6,14 +6,15 @@ from sqlalchemy import delete, func, select, tuple_
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
+    """Insert a bookmark and return (row, True), or return (existing row, False) if its
+    normalized link is already saved. The existing bookmark is not modified.
 
     ON CONFLICT DO NOTHING relies on the unique index, so this holds under concurrent saves.
     """
@@ -27,12 +28,12 @@ def create_bookmark(session: Session, data: BookmarkCreate) -> BookmarkRow:
     row = session.scalars(statement).one_or_none()
     if row is None:
         session.rollback()
-        existing_id = session.scalar(
-            select(BookmarkRow.id).where(BookmarkRow.url_normalized == normalized)
-        )
-        raise DuplicateUrlError(existing_id)
+        existing = session.scalars(
+            select(BookmarkRow).where(BookmarkRow.url_normalized == normalized)
+        ).one()
+        return existing, False
     session.commit()
-    return row
+    return row, True
 
 
 def list_bookmarks(
diff --git a/src/bookmarks_api/routes.py b/src/bookmarks_api/routes.py
index cc51123..f641b28 100644
--- a/src/bookmarks_api/routes.py
+++ b/src/bookmarks_api/routes.py
@@ -41,12 +41,18 @@ def _reject_offset(value: str | None) -> None:
     response_model=Bookmark,
     summary="Save a bookmark",
     responses={
-        409: {"model": ErrorResponse, "description": "This link is already bookmarked."},
+        200: {
+            "model": Bookmark,
+            "description": "Already bookmarked; the existing bookmark is returned unchanged.",
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
index bf537d3..19ad0ce 100644
--- a/tests/integration/test_create_bookmark.py
+++ b/tests/integration/test_create_bookmark.py
@@ -37,17 +37,16 @@ def test_link_is_stored_as_given(client: TestClient) -> None:
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
     assert row_count() == 1
 
 
@@ -61,12 +60,12 @@ def test_duplicate_leaves_the_existing_bookmark_unchanged(client: TestClient, en
 
 
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
@@ -77,7 +76,8 @@ def test_concurrent_saves_of_the_same_link_leave_one_bookmark(client: TestClient
     for thread in threads:
         thread.join()
 
-    assert sorted(statuses) == [201, 409]
+    assert sorted(r.status_code for r in responses) == [200, 201]
+    assert responses[0].json() == responses[1].json()
     assert row_count() == 1
 
 
diff --git a/tests/integration/test_errors.py b/tests/integration/test_errors.py
index 1f473e0..4c37f26 100644
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
@@ -82,8 +72,9 @@ def test_openapi_documents_every_operation(client: TestClient, path: str, method
         assert operation["requestBody"]["content"]["application/json"]["schema"]["$ref"].endswith(
             "/BookmarkCreate"
         )
-        success = operation["responses"]["201"]["content"]["application/json"]["schema"]
-        assert success["$ref"].endswith("/Bookmark")
+        for code in ("200", "201"):
+            success = operation["responses"][code]["content"]["application/json"]["schema"]
+            assert success["$ref"].endswith("/Bookmark")
     if method == "get":
         success = operation["responses"]["200"]["content"]["application/json"]["schema"]
         assert success["$ref"].endswith("/BookmarkPage")
[exit 0]
```

```console
$ set -a; . ./.env; set +a; uv run --python 3.13 pytest -q 2>&1 | tail -30
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
........................................................................ [ 74%]
.........................                                                [100%]
97 passed in 2.85s
[exit 0]
```

```console
$ git status --short
 M src/bookmarks_api/errors.py
 M src/bookmarks_api/repository.py
 M src/bookmarks_api/routes.py
 M tests/integration/test_create_bookmark.py
 M tests/integration/test_errors.py
?? episodes/
[exit 0]
```

```console
$ date -u +%Y-%m-%dT%H:%M:%SZ
2026-10-24T11:42:36Z
[exit 0]
```

