# 04 implement — forward-r2

Start: 2026-10-24T12:01:56Z

```console
$ ls .specify/extensions.yml
ls: cannot access '.specify/extensions.yml': No such file or directory
[exit 2]
```

```console
$ .specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
{"FEATURE_DIR":"/home/claude/runs/forward-r2/specs/002-idempotent-bookmark-save","AVAILABLE_DOCS":["research.md","data-model.md","contracts/","quickstart.md","tasks.md"]}
[exit 0]
```

```console
$ for f in specs/002-idempotent-bookmark-save/checklists/*.md; do t=$(grep -cE "^- \[( |x|X)\]" $f); c=$(grep -cE "^- \[(x|X)\]" $f); echo "$f total=$t checked=$c unchecked=$((t-c))"; done
specs/002-idempotent-bookmark-save/checklists/requirements.md total=16 checked=16 unchecked=0
[exit 0]
```

```console
$ git rev-parse --git-dir; ls Dockerfile* 2>&1; ls .eslintrc* eslint.config.* .prettierrc* .npmrc package.json *.tf 2>&1 | head; cat .dockerignore
/home/claude/bookmarks-api/.git/worktrees/forward-r2
ls: cannot access 'Dockerfile*': No such file or directory
ls: cannot access '.eslintrc*': No such file or directory
ls: cannot access 'eslint.config.*': No such file or directory
ls: cannot access '.prettierrc*': No such file or directory
ls: cannot access '.npmrc': No such file or directory
ls: cannot access 'package.json': No such file or directory
ls: cannot access '*.tf': No such file or directory
.git/
.venv/
__pycache__/
*.pyc
.pytest_cache/
.env
.env.*
!.env.example
*.log
[exit 0]
```

```console
$ set -a; . ./.env; set +a; uv run --python 3.13 pytest -q 2>&1 | tail -5
      Built bookmarks-api @ file:///home/claude/runs/forward-r2
Installed 29 packages in 14ms
........................................................................ [ 73%]
..........................                                               [100%]
98 passed in 3.38s
[exit 0]
```

## T002, T003 (Foundational) — edits made with a Python rewrite script (agent tool), diff below

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
index f93517e..48e59bd 100644
--- a/src/bookmarks_api/repository.py
+++ b/src/bookmarks_api/repository.py
@@ -6,16 +6,26 @@ from sqlalchemy import delete, func, select, tuple_
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
+    """Save a bookmark, or return the existing one if its normalized link is already saved.
+
+    Returns ``(row, created)``: ``created`` is True when this call inserted the bookmark and
+    False when the normalized link was already bookmarked; the existing row is then returned
+    unchanged and the request's title and tags are ignored (specs/002 FR-001, FR-002).
+
+    ON CONFLICT DO NOTHING relies on the unique index, so exactly one of several concurrent
+    saves of the same new link inserts it; the others wait for that insert to commit and then
+    read the committed row (specs/002 FR-004). If the conflicting bookmark is deleted between
+    the insert attempt and the lookup, the insert is retried.
     """
     normalized = normalize_url(data.url)
     statement = (
@@ -24,15 +34,19 @@ def create_bookmark(session: Session, data: BookmarkCreate) -> BookmarkRow:
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
+        if existing is not None:
+            session.commit()
+            return existing, False
+    raise RuntimeError(f"Could not save or find the bookmark after {MAX_SAVE_ATTEMPTS} attempts.")
 
 
 def list_bookmarks(
[exit 0]
```

## T004–T008 (US1 tests, written before T009) — diff below

```console
$ git diff tests/
diff --git a/tests/integration/test_create_bookmark.py b/tests/integration/test_create_bookmark.py
index bf537d3..c9868f4 100644
--- a/tests/integration/test_create_bookmark.py
+++ b/tests/integration/test_create_bookmark.py
@@ -37,27 +37,69 @@ def test_link_is_stored_as_given(client: TestClient) -> None:
     assert response.json()["url"] == "HTTPS://Example.com/Docs/"
 
 
-def test_equivalent_link_is_rejected_as_duplicate(client: TestClient, row_count) -> None:
+def test_equivalent_link_returns_existing_bookmark_with_200(client: TestClient, row_count) -> None:
+    """specs/002 US1 scenario 1 (supersedes specs/001 FR-004's 409 duplicate rule)."""
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
 
 
-def test_duplicate_leaves_the_existing_bookmark_unchanged(client: TestClient, engine) -> None:
-    client.post("/bookmarks", json={"url": "https://example.com/docs", "title": "Docs"})
-    client.post("/bookmarks", json={"url": "https://example.com/docs/", "title": "Changed"})
+def test_resave_ignores_title_and_tags_and_changes_nothing(client: TestClient) -> None:
+    """specs/002 US1 scenario 2, FR-002."""
+    first = client.post(
+        "/bookmarks",
+        json={"url": "https://example.com/docs", "title": "Docs", "tags": ["python"]},
+    )
+    second = client.post(
+        "/bookmarks",
+        json={"url": "https://example.com/docs", "title": "Other", "tags": ["api", "new"]},
+    )
+
+    assert second.status_code == 200
+    assert second.json()["title"] == "Docs"
+    assert second.json()["tags"] == ["python"]
+    listed = client.get("/bookmarks").json()
+    assert listed["total"] == 1
+    assert listed["items"] == [first.json()]
+
+
+def test_different_query_string_is_a_new_bookmark(client: TestClient, row_count) -> None:
+    """specs/002 US1 scenario 3."""
+    first = client.post("/bookmarks", json={"url": "https://example.com/docs", "title": "Docs"})
+    second = client.post(
+        "/bookmarks", json={"url": "https://example.com/docs?page=2", "title": "Page 2"}
+    )
+
+    assert second.status_code == 201
+    assert second.json()["id"] != first.json()["id"]
+    assert row_count() == 2
+
 
-    with engine.connect() as connection:
-        title = connection.exec_driver_sql("SELECT title FROM bookmarks").scalar_one()
-    assert title == "Docs"
+@pytest.mark.parametrize(
+    "payload",
+    [
+        pytest.param({"url": "https://example.com/docs", "title": ""}, id="empty-title"),
+        pytest.param(
+            {"url": "https://example.com/docs", "title": "T", "tags": [f"t{i}" for i in range(11)]},
+            id="eleven-tags",
+        ),
+    ],
+)
+def test_invalid_resave_is_still_rejected(client: TestClient, payload: dict) -> None:
+    """specs/002 FR-005: a re-save is validated like a new save."""
+    first = client.post("/bookmarks", json={"url": "https://example.com/docs", "title": "Docs"})
+    response = client.post("/bookmarks", json=payload)
+
+    assert response.status_code == 422
+    assert response.json()["error"]["code"] == "validation_error"
+    assert client.get("/bookmarks").json()["items"] == [first.json()]
 
 
 def test_concurrent_saves_of_the_same_link_leave_one_bookmark(client: TestClient, row_count) -> None:
diff --git a/tests/integration/test_errors.py b/tests/integration/test_errors.py
index 1f473e0..8d5f20b 100644
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
+        assert "409" not in operation["responses"]  # specs/002: re-saves are no longer errors
+        for success_code in ("201", "200"):
+            success = operation["responses"][success_code]["content"]["application/json"]["schema"]
+            assert success["$ref"].endswith("/Bookmark")
     if method == "get":
         success = operation["responses"]["200"]["content"]["application/json"]["schema"]
         assert success["$ref"].endswith("/BookmarkPage")
[exit 0]
```

```console
$ set -a; . ./.env; set +a; uv run --python 3.13 pytest -q 2>&1 | tail -25
FAILED tests/integration/test_create_bookmark.py::test_tags_are_trimmed_lowercased_and_deduplicated
FAILED tests/integration/test_create_bookmark.py::test_link_is_stored_as_given
FAILED tests/integration/test_create_bookmark.py::test_equivalent_link_returns_existing_bookmark_with_200
FAILED tests/integration/test_create_bookmark.py::test_resave_ignores_title_and_tags_and_changes_nothing
FAILED tests/integration/test_create_bookmark.py::test_different_query_string_is_a_new_bookmark
FAILED tests/integration/test_create_bookmark.py::test_invalid_resave_is_still_rejected[empty-title]
FAILED tests/integration/test_create_bookmark.py::test_invalid_resave_is_still_rejected[eleven-tags]
FAILED tests/integration/test_create_bookmark.py::test_concurrent_saves_of_the_same_link_leave_one_bookmark
FAILED tests/integration/test_create_bookmark.py::test_title_of_exactly_200_and_ten_tags_are_accepted
FAILED tests/integration/test_create_bookmark.py::test_eleven_tags_that_dedupe_to_ten_are_accepted
FAILED tests/integration/test_delete_bookmark.py::test_deleted_bookmark_disappears_from_list_and_filter
FAILED tests/integration/test_delete_bookmark.py::test_deleting_twice_returns_not_found_the_second_time
FAILED tests/integration/test_delete_bookmark.py::test_link_can_be_saved_again_after_delete
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
25 failed, 75 passed in 2.08s
[exit 0]
```

The run above (25 failed) is the TDD red state after T002–T008: the route still passed the new `(row, created)` tuple to `Bookmark.model_validate`, so every save failed.

## T009 (route) — diff below

```console
$ git diff src/bookmarks_api/routes.py
diff --git a/src/bookmarks_api/routes.py b/src/bookmarks_api/routes.py
index cc51123..fa79b73 100644
--- a/src/bookmarks_api/routes.py
+++ b/src/bookmarks_api/routes.py
@@ -40,13 +40,27 @@ def _reject_offset(value: str | None) -> None:
     status_code=status.HTTP_201_CREATED,
     response_model=Bookmark,
     summary="Save a bookmark",
+    description=(
+        "Idempotent per normalized link (specs/002-idempotent-bookmark-save). A new link is "
+        "stored and returned with 201. A link that is already bookmarked returns the existing "
+        "bookmark unchanged with 200; the title and tags in the request are ignored."
+    ),
     responses={
-        409: {"model": ErrorResponse, "description": "This link is already bookmarked."},
+        201: {"description": "Bookmark saved (the link was not bookmarked before)."},
+        200: {
+            "model": Bookmark,
+            "description": (
+                "This link was already bookmarked; the existing bookmark is returned unchanged."
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

Note: right after T009 the suite was first run outside the capture helper (same command as below); its output was "1 failed, 99 passed in 2.87s" with the single failure `test_concurrent_saves_of_the_same_link_leave_one_bookmark` (`At index 0 diff: 200 != 201` — the old test still asserts `[201, 409]`). Re-run through the capture helper:

```console
$ set -a; . ./.env; set +a; uv run --python 3.13 pytest -q 2>&1 | tail -15
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
    
>       assert sorted(statuses) == [201, 409]
E       assert [200, 201] == [201, 409]
E         
E         At index 0 diff: 200 != 201
E         Use -v to get more diff

tests/integration/test_create_bookmark.py:122: AssertionError
=========================== short test summary info ============================
FAILED tests/integration/test_create_bookmark.py::test_concurrent_saves_of_the_same_link_leave_one_bookmark
1 failed, 99 passed in 3.12s
[exit 0]
```

US1 checkpoint: T004–T008 tests all pass; the one failure is the US3 concurrency test (old 409 expectation), which T013 owns. Applied T013 next (before the US2 verification tasks, since US2 has no code change); order deviation noted.

## T013 (US3 test) — diff below

```console
$ git diff tests/integration/test_create_bookmark.py | sed -n "/def test_concurrent/,/row_count() == 1/p"
 def test_concurrent_saves_of_the_same_link_leave_one_bookmark(client: TestClient, row_count) -> None:
-    statuses: list[int] = []
+    """specs/002 US3 scenario 1, FR-004: one save gets 201, the other 200 with the same bookmark."""
+    results: list[tuple[int, dict]] = []
     barrier = threading.Barrier(2)
 
     def save(url: str) -> None:
         barrier.wait()
-        statuses.append(client.post("/bookmarks", json={"url": url, "title": "Race"}).status_code)
+        response = client.post("/bookmarks", json={"url": url, "title": "Race"})
+        results.append((response.status_code, response.json()))
 
     threads = [
         threading.Thread(target=save, args=("https://example.com/race",)),
@@ -77,7 +121,8 @@ def test_concurrent_saves_of_the_same_link_leave_one_bookmark(client: TestClient
     for thread in threads:
         thread.join()
 
-    assert sorted(statuses) == [201, 409]
+    assert sorted(status for status, _ in results) == [200, 201]
+    assert results[0][1]["id"] == results[1][1]["id"]
     assert row_count() == 1
[exit 0]
```

## T010–T012 (US2 verification)

```console
$ grep -n -A8 "def test_save_with_title_and_no_tags" tests/integration/test_create_bookmark.py | head -5; grep -n -A7 "def test_link_can_be_saved_again_after_delete" tests/integration/test_delete_bookmark.py
10:def test_save_with_title_and_no_tags(client: TestClient, row_count) -> None:
11-    response = client.post("/bookmarks", json={"url": "https://example.com/docs", "title": "Docs"})
12-
13-    assert response.status_code == 201
14-    body = response.json()
42:def test_link_can_be_saved_again_after_delete(client: TestClient) -> None:
43-    first = save(client, "https://example.com/a")
44-    client.delete(f"/bookmarks/{first}")
45-
46-    response = client.post("/bookmarks", json={"url": "https://EXAMPLE.com/a/", "title": "Again"})
47-
48-    assert response.status_code == 201
49-    assert response.json()["id"] != first
[exit 0]
```

```console
$ set -a; . ./.env; set +a; uv run --python 3.13 pytest -q tests/integration/test_create_bookmark.py tests/integration/test_delete_bookmark.py 2>&1 | tail -3
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
............................                                             [100%]
28 passed in 1.05s
[exit 0]
```

## T014 (US3 flakiness loop, 20 runs)

```console
$ set -a; . ./.env; set +a; ok=0; for i in $(seq 20); do uv run --python 3.13 pytest -q tests/integration/test_create_bookmark.py -k concurrent 2>&1 | tail -1 | grep -q "1 passed" && ok=$((ok+1)) || { echo "run $i failed"; }; done; echo "concurrent test passed $ok/20"
concurrent test passed 20/20
[exit 0]
```

## T015 (README) — edited the endpoint table row with the Edit tool; line 7 ("with no duplicate URLs") left as is (still true: one bookmark per link). Line 65 is the ep01 historical `/speckit-specify` prompt and was left unchanged.

```console
$ git diff README.md
diff --git a/README.md b/README.md
index 5c4557f..02e9c60 100644
--- a/README.md
+++ b/README.md
@@ -97,7 +97,7 @@ uv run pytest                                          # tests, against the book
 
 | Endpoint | What it does |
 | --- | --- |
-| `POST /bookmarks` | Save `{"url", "title", "tags"}`; 409 if the link is already saved |
+| `POST /bookmarks` | Save `{"url", "title", "tags"}`; 201 for a new link, 200 with the existing bookmark unchanged if the link is already saved ([specs/002-idempotent-bookmark-save](specs/002-idempotent-bookmark-save/spec.md)) |
 | `GET /bookmarks?tag=&limit=&cursor=` | List newest first, 20 per page by default, optional tag filter; pass `next_cursor` from one page as `cursor` to get the next |
 | `DELETE /bookmarks/{id}` | Delete a bookmark |
 
[exit 0]
```

## T016 (generated OpenAPI vs contracts/openapi.yaml)

```console
$ set -a; . ./.env; set +a; uv run --python 3.13 python -c "
import json
from bookmarks_api.main import create_app
spec = create_app().openapi()
post = spec[\"paths\"][\"/bookmarks\"][\"post\"]
print(\"responses:\", sorted(post[\"responses\"]))
for c, r in sorted(post[\"responses\"].items()):
    print(c, r.get(\"description\"), json.dumps(r.get(\"content\", {}).get(\"application/json\", {}).get(\"schema\")))
print(\"duplicate_url in spec:\", \"duplicate_url\" in json.dumps(spec))
"
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
responses: ['200', '201', '422']
200 This link was already bookmarked; the existing bookmark is returned unchanged. {"$ref": "#/components/schemas/Bookmark"}
201 Bookmark saved (the link was not bookmarked before). {"$ref": "#/components/schemas/Bookmark"}
422 The request is not valid. {"$ref": "#/components/schemas/ErrorResponse"}
duplicate_url in spec: False
[exit 0]
```

T016 result: generated POST /bookmarks responses = 200, 201, 422 (all `Bookmark`/`ErrorResponse` refs), no 409, no `duplicate_url` anywhere — matches contracts/openapi.yaml. Minor wording drift only: generated 422 description is the shared "The request is not valid." vs the contract's "Invalid link, title or tags (also on a re-save)"; left as is (shared constant, not a contract break).

## T018 (quickstart manual steps 1–7 via TestClient; helper script at /home/claude/scratch/forward-r2/quickstart_walk.py)

```console
$ set -a; . ./.env; set +a; uv run --python 3.13 python /home/claude/scratch/forward-r2/quickstart_walk.py 2>&1 | grep -v UV_NATIVE_TLS
unknown PostgreSQL timezone: 'ASIA0'; will use UTC
1 201 {'id': 1, 'url': 'https://fastapi.tiangolo.com/', 'title': 'FastAPI docs', 'tags': ['python'], 'created_at': '2026-10-24T12:04:22.505079Z'}
2 200 {'id': 1, 'url': 'https://fastapi.tiangolo.com/', 'title': 'FastAPI docs', 'tags': ['python'], 'created_at': '2026-10-24T12:04:22.505079Z'} identical: True
3 200 total 1 unchanged: True
4 201 new id 3
5 422 validation_error
6 204 201 new id 4 != 1
7 ['200', '201', '422']
[exit 0]
```

T018 observation: step 4 got id 3, not 2 — the re-save in step 2 consumed identity value 2 (`INSERT ... ON CONFLICT DO NOTHING` advances the sequence even when no row is inserted). Each re-save therefore burns one id. Not a spec violation (ids are only required to be unique), recorded as a surprise. The "unknown PostgreSQL timezone: 'ASIA0'" line is a psycopg warning from the environment's server timezone setting, not from this change.

## T017 (full suite on 3.11, 3.12, 3.13)

```console
$ set -a; . ./.env; set +a; uv run --python 3.11 pytest -q 2>&1 | grep -v UV_NATIVE_TLS | tail -4
Installed 29 packages in 31ms
........................................................................ [ 72%]
............................                                             [100%]
100 passed in 3.15s
[exit 0]
```

```console
$ set -a; . ./.env; set +a; uv run --python 3.12 pytest -q 2>&1 | grep -v UV_NATIVE_TLS | tail -4
Installed 29 packages in 17ms
........................................................................ [ 72%]
............................                                             [100%]
100 passed in 2.64s
[exit 0]
```

```console
$ set -a; . ./.env; set +a; uv run --python 3.13 pytest -q 2>&1 | grep -v UV_NATIVE_TLS | tail -4
Installed 29 packages in 24ms
........................................................................ [ 72%]
............................                                             [100%]
100 passed in 2.94s
[exit 0]
```

## Mark tasks complete

```console
$ grep -cE "^- \[X\] T0" specs/002-idempotent-bookmark-save/tasks.md; grep -cE "^- \[ \] T0" specs/002-idempotent-bookmark-save/tasks.md
18
0
[exit 1]
```

## Review: code and artifact diffs (ep03-forward-r2-tasks..working tree)

```console
$ git status --short; git diff --stat ep03-forward-r2-tasks
 M README.md
 M specs/002-idempotent-bookmark-save/tasks.md
 M src/bookmarks_api/errors.py
 M src/bookmarks_api/repository.py
 M src/bookmarks_api/routes.py
 M tests/integration/test_create_bookmark.py
 M tests/integration/test_errors.py
?? episodes/ep03/capture/forward-r2/04-implement.md
 README.md                                   |  2 +-
 specs/002-idempotent-bookmark-save/tasks.md | 36 +++++++-------
 src/bookmarks_api/errors.py                 | 11 -----
 src/bookmarks_api/repository.py             | 38 ++++++++++-----
 src/bookmarks_api/routes.py                 | 20 ++++++--
 tests/integration/test_create_bookmark.py   | 73 +++++++++++++++++++++++------
 tests/integration/test_errors.py            | 18 ++-----
 7 files changed, 126 insertions(+), 72 deletions(-)
[exit 0]
```

```console
$ git diff ep03-forward-r2-tasks -- src/
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
index f93517e..48e59bd 100644
--- a/src/bookmarks_api/repository.py
+++ b/src/bookmarks_api/repository.py
@@ -6,16 +6,26 @@ from sqlalchemy import delete, func, select, tuple_
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
+    """Save a bookmark, or return the existing one if its normalized link is already saved.
+
+    Returns ``(row, created)``: ``created`` is True when this call inserted the bookmark and
+    False when the normalized link was already bookmarked; the existing row is then returned
+    unchanged and the request's title and tags are ignored (specs/002 FR-001, FR-002).
+
+    ON CONFLICT DO NOTHING relies on the unique index, so exactly one of several concurrent
+    saves of the same new link inserts it; the others wait for that insert to commit and then
+    read the committed row (specs/002 FR-004). If the conflicting bookmark is deleted between
+    the insert attempt and the lookup, the insert is retried.
     """
     normalized = normalize_url(data.url)
     statement = (
@@ -24,15 +34,19 @@ def create_bookmark(session: Session, data: BookmarkCreate) -> BookmarkRow:
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
+        if existing is not None:
+            session.commit()
+            return existing, False
+    raise RuntimeError(f"Could not save or find the bookmark after {MAX_SAVE_ATTEMPTS} attempts.")
 
 
 def list_bookmarks(
diff --git a/src/bookmarks_api/routes.py b/src/bookmarks_api/routes.py
index cc51123..fa79b73 100644
--- a/src/bookmarks_api/routes.py
+++ b/src/bookmarks_api/routes.py
@@ -40,13 +40,27 @@ def _reject_offset(value: str | None) -> None:
     status_code=status.HTTP_201_CREATED,
     response_model=Bookmark,
     summary="Save a bookmark",
+    description=(
+        "Idempotent per normalized link (specs/002-idempotent-bookmark-save). A new link is "
+        "stored and returned with 201. A link that is already bookmarked returns the existing "
+        "bookmark unchanged with 200; the title and tags in the request are ignored."
+    ),
     responses={
-        409: {"model": ErrorResponse, "description": "This link is already bookmarked."},
+        201: {"description": "Bookmark saved (the link was not bookmarked before)."},
+        200: {
+            "model": Bookmark,
+            "description": (
+                "This link was already bookmarked; the existing bookmark is returned unchanged."
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
$ git diff --stat ep03-start -- specs/001-bookmarks-api; echo "specs/001 changed files: $(git diff --name-only ep03-start -- specs/001-bookmarks-api | wc -l)"
specs/001 changed files: 0
[exit 0]
```

```console
$ grep -rn -i "duplicate_url\|DuplicateUrlError\|409" src tests README.md specs/002-idempotent-bookmark-save | grep -v "^specs/002-idempotent-bookmark-save/tasks.md"
grep: tests/integration/__pycache__/test_create_bookmark.cpython-311-pytest-9.1.1.pyc: binary file matches
grep: tests/integration/__pycache__/test_errors.cpython-313-pytest-9.1.1.pyc: binary file matches
grep: tests/integration/__pycache__/test_create_bookmark.cpython-312-pytest-9.1.1.pyc: binary file matches
grep: tests/integration/__pycache__/test_errors.cpython-311-pytest-9.1.1.pyc: binary file matches
grep: tests/integration/__pycache__/test_errors.cpython-312-pytest-9.1.1.pyc: binary file matches
grep: tests/integration/__pycache__/test_create_bookmark.cpython-313-pytest-9.1.1.pyc: binary file matches
src/bookmarks_api/errors.py:35:STATUS_CODES = {400: "bad_request", 404: "not_found", 405: "method_not_allowed", 409: "conflict"}
tests/integration/test_create_bookmark.py:41:    """specs/002 US1 scenario 1 (supersedes specs/001 FR-004's 409 duplicate rule)."""
tests/integration/test_errors.py:75:        assert "409" not in operation["responses"]  # specs/002: re-saves are no longer errors
specs/002-idempotent-bookmark-save/quickstart.md:6:001's manual step 2 (which expected 409 `duplicate_url`).
specs/002-idempotent-bookmark-save/quickstart.md:34:| 7 | `GET /openapi.json` → `paths./bookmarks.post.responses` | has `200`, `201`, `422`; no `409` |
specs/002-idempotent-bookmark-save/spec.md:9:**Input**: User description: "Saving a link that is already bookmarked must no longer be rejected. If the link (after the existing normalization rules) is already saved, return the existing bookmark unchanged with HTTP 200 OK instead of the current 409 conflict. The title and tags sent in the new request are ignored; the stored bookmark is not modified. Saving a new link still returns 201 Created. Two concurrent saves of the same new link must still store only one bookmark (one gets 201, the other gets 200 with the same bookmark). This replaces the duplicate rule in FR-004 of specs/001-bookmarks-api."
specs/002-idempotent-bookmark-save/data-model.md:11:| `url_normalized` + `uq_bookmarks_url_normalized` | Duplicate detection; a second save of the same normalized link is rejected (409) | Identity of a saved link; a second save of the same normalized link **finds** the existing row and returns it (200). Still guarantees one row per normalized link under concurrent saves (spec FR-004) |
specs/002-idempotent-bookmark-save/plan.md:10:(409 `duplicate_url` on a re-save). `specs/001-bookmarks-api` stays as the historical record and is
specs/002-idempotent-bookmark-save/plan.md:11:not edited; where its plan, research, contract or quickstart describe the 409 duplicate response,
specs/002-idempotent-bookmark-save/plan.md:21:winner gets 201, the loser reads the committed row and gets 200. The `DuplicateUrlError` exception,
specs/002-idempotent-bookmark-save/plan.md:22:its 409 handler and the `duplicate_url` error code are removed. No schema change, no migration, no
specs/002-idempotent-bookmark-save/plan.md:56:| I. Typed API Contracts | `POST /bookmarks` keeps the `BookmarkCreate` request model and returns the `Bookmark` response model for both 201 and 200; the 200 response is declared on the route so it appears in the generated OpenAPI; the stale 409 entry is removed | Pass |
specs/002-idempotent-bookmark-save/plan.md:58:| III. Consistent Error Shape | No new error; the 409 `duplicate_url` error disappears because a re-save is no longer an error. Validation (422) still uses the envelope. The principle's "409 conflict" mapping simply has no remaining user on this endpoint | Pass |
specs/002-idempotent-bookmark-save/plan.md:60:| V. Tests Ship With Every Feature | Every acceptance scenario in spec.md maps to a test in the same change; tests asserting the superseded 409 behavior are replaced; full suite must pass on 3.11–3.13 | Pass |
specs/002-idempotent-bookmark-save/plan.md:87:├── repository.py        # create_bookmark → returns (row, created); no DuplicateUrlError
specs/002-idempotent-bookmark-save/plan.md:88:├── routes.py            # POST /bookmarks sets 201 or 200; responses declare 200, drop 409
specs/002-idempotent-bookmark-save/plan.md:89:└── errors.py            # remove DuplicateUrlError and its 409 handler
specs/002-idempotent-bookmark-save/plan.md:94:    └── test_errors.py            # drop 409 envelope test; OpenAPI check expects 200, not 409
specs/002-idempotent-bookmark-save/research.md:39:  unchanged") and no longer declare `409`. The response body is the same `Bookmark` shape for both.
specs/002-idempotent-bookmark-save/research.md:55:- **Decision**: Delete `DuplicateUrlError`, its exception handler, and the `duplicate_url` code. The
specs/002-idempotent-bookmark-save/research.md:56:  generic `409 → "conflict"` entry in the HTTP status-code map stays (it serves framework
specs/002-idempotent-bookmark-save/contracts/openapi.yaml:7:    operation of specs/001-bookmarks-api/contracts/openapi.yaml: the 409 duplicate_url response is
specs/002-idempotent-bookmark-save/contracts/openapi.yaml:48:        Same envelope as the 001 contract; the duplicate_url code no longer exists.
[exit 0]
```

## Review notes (agent)

- Code diff is limited to the three modules planned (repository.py, routes.py, errors.py); no migration, no dependency change. `ErrorResponse` is still imported in routes.py and still used (ERROR_422, DELETE 404).
- `specs/001-bookmarks-api`: 0 files changed since `ep03-start` (immutability rule held).
- Remaining `409` references in code: only the generic `409: "conflict"` entry in `STATUS_CODES` (errors.py:35), kept by design (research.md). Constitution III text still names "409 conflict" as an error class; no feature uses it any more. Not changed (constitution is out of scope).
- Artifacts that still describe the old 409 duplicate rule, by design of flow-forward and left untouched: `specs/001-bookmarks-api/spec.md` (FR-004, US1 scenario 3, Edge Cases bullet 1, Clarifications Q1), `specs/001-bookmarks-api/research.md` ("Preventing duplicate links", error codes), `specs/001-bookmarks-api/contracts/openapi.yaml` (409 response, `duplicate_url` enum), `specs/001-bookmarks-api/quickstart.md` (step 2 expects 409), `specs/001-bookmarks-api/data-model.md` ("duplicate detection (FR-004)"), `specs/001-bookmarks-api/tasks.md`. None of these carry a forward link to 002 (they cannot be edited); only 002 links back.
- The 001 quickstart step 2 will now fail if someone follows it (gets 200, expects 409). The 002 quickstart says it replaces that step.
- Surprise: each re-save consumes one identity value (seen in T018: ids 1, 3, 4).
- Ordering deviation: T013 (US3 test) was applied before T010–T012 (US2 verification) because the old concurrency test was the only failure after T009.

## Spec Kit completion report (verbatim)

Implementation complete for `specs/002-idempotent-bookmark-save`.

| Checklist | Total | Checked | Unchecked | Status |
|-----------|-------|---------|-----------|--------|
| requirements.md | 16 | 16 | 0 | ✓ PASS |

- Tasks: 18/18 marked [X] (T001–T018).
- Phase 1 Setup: baseline 98 passed (3.13).
- Phase 2 Foundational: `repository.create_bookmark` returns `(row, created)`; `DuplicateUrlError` + 409 handler removed.
- Phase 3 US1: re-save returns 200 with the existing bookmark unchanged; OpenAPI declares 200/201/422, no 409.
- Phase 4 US2: new-link saves still 201 (verified, no code change).
- Phase 5 US3: concurrent first saves → [200, 201], same id, one row; 20/20 loop runs passed.
- Phase 6 Polish: README endpoint row updated; generated OpenAPI matches contract; quickstart steps 1–7 pass; full suite 100 passed on 3.11, 3.12, 3.13.
- Extension hooks: none registered.

End: 2026-10-24T12:05:10Z
