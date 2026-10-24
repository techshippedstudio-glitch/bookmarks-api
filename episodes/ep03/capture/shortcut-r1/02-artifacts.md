# shortcut-r1 step 02: artifacts

Model: Opus 5.5 (claude-opus-5-5)

```console
$ date -u +%Y-%m-%dT%H:%M:%SZ
2026-10-24T11:42:50Z
[exit 0]
```

```console
$ grep -n -i "409\|duplicate\|conflict\|already\|FR-004\|existing_id" specs/001-bookmarks-api/spec.md specs/001-bookmarks-api/plan.md specs/001-bookmarks-api/tasks.md
specs/001-bookmarks-api/spec.md:9:**Input**: User description: "Build a bookmarks API. A user can save a link with a title and optional tags, list their bookmarks newest first, filter by tag, and delete a bookmark. Saving the same URL twice must not create a duplicate."
specs/001-bookmarks-api/spec.md:15:- Q: When someone saves a link that is already bookmarked, what should happen? → A: Reject it with a conflict error that includes the existing bookmark's identifier; the existing bookmark is left unchanged.
specs/001-bookmarks-api/spec.md:17:- Q: How should tags be cleaned up and limited? → A: Trim spaces, lowercase, drop duplicates; 1 to 30 characters of letters, digits and hyphens; at most 10 tags per bookmark.
specs/001-bookmarks-api/spec.md:46:   a conflict error that includes the existing bookmark's identifier.
specs/001-bookmarks-api/spec.md:125:- Saving a link that is already bookmarked, even with a different title or tags, is rejected with
specs/001-bookmarks-api/spec.md:126:  a conflict error that includes the existing bookmark's identifier; the existing bookmark is not
specs/001-bookmarks-api/spec.md:152:- **FR-004**: System MUST NOT store two bookmarks for the same link, where links are compared after
specs/001-bookmarks-api/spec.md:154:  fragment removed, query kept). A save of an existing link MUST be rejected with a conflict error
specs/001-bookmarks-api/spec.md:170:- **FR-011**: System MUST normalize tags by trimming spaces, lowercasing and removing duplicates,
specs/001-bookmarks-api/plan.md:12:with no duplicate links after normalization. Built as a FastAPI service with Pydantic request and
specs/001-bookmarks-api/plan.md:52:| III. Consistent Error Shape | One envelope `{"error": {"code", "message", "details"}}` for validation (422), not found (404) and duplicate (409), installed as global exception handlers | Pass |
specs/001-bookmarks-api/tasks.md:44:- [X] T008 [P] Create `src/bookmarks_api/errors.py`: Pydantic models `ErrorBody {code, message, details}` and `ErrorResponse {error: ErrorBody}`; domain exceptions `NotFoundError` and `DuplicateUrlError(existing_id)`; exception handlers producing the envelope for `RequestValidationError` (422 `validation_error`, field errors in `details`), `StarletteHTTPException` (status-mapped code), `NotFoundError` (404 `not_found`), `DuplicateUrlError` (409 `duplicate_url`, `details.existing_id`) and any other exception (500 `internal_error`, no internals) (Constitution III)
specs/001-bookmarks-api/tasks.md:54:**Goal**: A user can save a link with a title and optional tags; duplicates are rejected.
specs/001-bookmarks-api/tasks.md:57:link returns 409 with `details.existing_id`.
specs/001-bookmarks-api/tasks.md:63:- [X] T011 [P] [US1] Unit tests in `tests/unit/test_normalize.py` for link normalization (lowercase scheme and host, default ports 80/443 removed, trailing path slashes removed, fragment removed, query kept; examples `HTTPS://Example.com:443/docs/#intro` → `https://example.com/docs`, `https://example.com/search?q=FastAPI` keeps `?q=FastAPI`; non-http(s) and host-less links rejected) and tag normalization (trim, lowercase, de-duplicate, sort; must match `^[a-z0-9-]{1,30}$`)
specs/001-bookmarks-api/tasks.md:64:- [X] T012 [P] [US1] Integration tests in `tests/integration/test_create_bookmark.py` for User Story 1 scenarios 1 to 4: save with no tags (201, `tags == []`, `created_at` present); tags `["Python", " api ", "python"]` → `["api", "python"]`; `https://example.com/docs` then `HTTPS://Example.com/docs/#intro` → 409 `duplicate_url` with `details.existing_id`, still one row; missing url, missing title, `ftp://` link, url over 2048 characters, title over 200 characters, 11 tags, and invalid tag `"no spaces"` each → 422 `validation_error` and nothing saved; two concurrent saves of equivalent links (two threads) → exactly one 201 and one 409, one row (FR-004)
specs/001-bookmarks-api/tasks.md:70:- [X] T015 [US1] Implement `create_bookmark(session, data)` in `src/bookmarks_api/repository.py` using `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`, raising `DuplicateUrlError(existing_id)` when nothing is inserted (research.md, "Preventing duplicate links")
specs/001-bookmarks-api/tasks.md:71:- [X] T016 [US1] Implement `POST /bookmarks` in `src/bookmarks_api/routes.py` returning 201 with `Bookmark`, with 409 and 422 responses declared using `ErrorResponse`
specs/001-bookmarks-api/tasks.md:144:- [X] T026 [P] Integration tests in `tests/integration/test_errors.py` asserting every error class (422, 404, 409, and an unknown route 404) uses the envelope `{"error": {"code", "message", "details"}}` (SC-005), and that `/openapi.json` lists all three operations with request and response schemas (Constitution I)
specs/001-bookmarks-api/tasks.md:187:2. Complete Phase 3 (save with duplicate protection)
specs/001-bookmarks-api/tasks.md:209:- [X] T035 Rewrite the paging tests in `tests/integration/test_list_bookmarks.py` and `tests/integration/test_filter_by_tag.py` for cursors, and add a test that pages through all results while bookmarks are saved between requests and finds no duplicates and no gaps, per US2/AC3-AC5 and the Constitution VI quality gate (missing)
[exit 0]
```

```console
$ sed -n "40,50p;122,130p;150,158p" specs/001-bookmarks-api/spec.md
1. **Given** no bookmarks exist, **When** the user saves a link with a title, **Then** the bookmark
   is stored and returned with its link, title, an empty tag list and its saved time.
2. **Given** no bookmarks exist, **When** the user saves a link with a title and the tags "Python",
   " api " and "python", **Then** the bookmark is returned with the tags "api" and "python".
3. **Given** a bookmark for `https://example.com/docs` exists, **When** the user saves
   `HTTPS://Example.com/docs/#intro`, **Then** no second bookmark is created and the user receives
   a conflict error that includes the existing bookmark's identifier.
4. **Given** any state, **When** the user tries to save a bookmark without a link or without a
   title, with a link that is not a valid http or https address, with a title over 200 characters,
   with more than 10 tags, or with an invalid tag, **Then** nothing is saved and the user receives
   an error explaining what is wrong.

### Edge Cases

- Saving a link that is already bookmarked, even with a different title or tags, is rejected with
  a conflict error that includes the existing bookmark's identifier; the existing bookmark is not
  changed.
- Links that differ only in scheme or host letter case, a default port (`:80` for http, `:443`
  for https), a trailing slash on the path, or a fragment are the same link. Links with different
  query strings are different links.
  characters, and MUST explain the problem to the user.
- **FR-003**: System MUST record the time each bookmark was saved.
- **FR-004**: System MUST NOT store two bookmarks for the same link, where links are compared after
  normalization (scheme and host lowercased, default port removed, trailing path slash removed,
  fragment removed, query kept). A save of an existing link MUST be rejected with a conflict error
  that includes the existing bookmark's identifier, and MUST hold even when two saves happen at
  the same moment.
- **FR-005**: System MUST return the saved bookmark, including an identifier the user can use to
  delete it.
[exit 0]
```

```console
$ sed -n "52,60p" specs/001-bookmarks-api/tasks.md
## Phase 3: User Story 1 - Save a bookmark (Priority: P1) 🎯 MVP

**Goal**: A user can save a link with a title and optional tags; duplicates are rejected.

**Independent Test**: `POST /bookmarks` returns 201 with the saved bookmark; saving an equivalent
link returns 409 with `details.existing_id`.

### Tests for User Story 1
[exit 0]
```

Edits applied by hand in one pass (scripted exact-string replacement via python3 heredoc) to spec.md, plan.md, tasks.md. Resulting diff:

```console
$ git diff -- specs
diff --git a/specs/001-bookmarks-api/plan.md b/specs/001-bookmarks-api/plan.md
index 4806bc5..0ffcc65 100644
--- a/specs/001-bookmarks-api/plan.md
+++ b/specs/001-bookmarks-api/plan.md
@@ -49,7 +49,7 @@ under a second for 100k bookmarks (indexed queries)
 | --- | --- | --- |
 | I. Typed API Contracts | Pydantic models for the create request, bookmark, page and error responses; FastAPI generates OpenAPI from them; no untyped dicts cross the boundary | Pass |
 | II. Real-Database Testing | Integration tests hit `bookmarks_test` on real PostgreSQL; schema created by running the Alembic migrations; tables truncated before each test; no database mocks | Pass |
-| III. Consistent Error Shape | One envelope `{"error": {"code", "message", "details"}}` for validation (422), not found (404) and duplicate (409), installed as global exception handlers | Pass |
+| III. Consistent Error Shape | One envelope `{"error": {"code", "message", "details"}}` for validation (422) and not found (404), installed as global exception handlers | Pass |
 | IV. Minimal Dependencies | Six runtime/test dependencies, each justified in research.md; standard library used for link normalization and config | Pass |
 | V. Tests Ship With Every Feature | Each user story's tasks include tests for its acceptance scenarios; suite must pass before converge | Pass |
 | VI. Cursor Pagination | `GET /bookmarks` uses keyset paging on `(created_at, id)` with an opaque `next_cursor`; no offset in the API or queries; a test pages through all results while bookmarks are added between requests | Pass |
diff --git a/specs/001-bookmarks-api/spec.md b/specs/001-bookmarks-api/spec.md
index 3ed7b96..34d5fde 100644
--- a/specs/001-bookmarks-api/spec.md
+++ b/specs/001-bookmarks-api/spec.md
@@ -12,7 +12,7 @@
 
 ### Session 2026-10-21
 
-- Q: When someone saves a link that is already bookmarked, what should happen? → A: Reject it with a conflict error that includes the existing bookmark's identifier; the existing bookmark is left unchanged.
+- Q: When someone saves a link that is already bookmarked, what should happen? → A: Return the existing bookmark unchanged with 200 OK (no longer a conflict error); the title and tags sent are ignored.
 - Q: Which links count as "the same link"? → A: Links that match after normalization: scheme and host lowercased, default port removed, trailing slash on the path removed, fragment (#...) removed; the query string is kept as is.
 - Q: How should tags be cleaned up and limited? → A: Trim spaces, lowercase, drop duplicates; 1 to 30 characters of letters, digits and hyphens; at most 10 tags per bookmark.
 - Q: How should the list behave when there are many bookmarks? → A: Return pages: 20 per page by default, up to 100 per page, using a limit and an offset, plus the total count.
@@ -43,7 +43,7 @@ contains the saved link, title, tags and the time it was saved.
    " api " and "python", **Then** the bookmark is returned with the tags "api" and "python".
 3. **Given** a bookmark for `https://example.com/docs` exists, **When** the user saves
    `HTTPS://Example.com/docs/#intro`, **Then** no second bookmark is created and the user receives
-   a conflict error that includes the existing bookmark's identifier.
+   the existing bookmark, unchanged, with 200 OK.
 4. **Given** any state, **When** the user tries to save a bookmark without a link or without a
    title, with a link that is not a valid http or https address, with a title over 200 characters,
    with more than 10 tags, or with an invalid tag, **Then** nothing is saved and the user receives
@@ -122,9 +122,9 @@ appears in the list.
 
 ### Edge Cases
 
-- Saving a link that is already bookmarked, even with a different title or tags, is rejected with
-  a conflict error that includes the existing bookmark's identifier; the existing bookmark is not
-  changed.
+- Saving a link that is already bookmarked, even with a different title or tags, returns the
+  existing bookmark with 200 OK; the title and tags sent are ignored and the existing bookmark is
+  not changed.
 - Links that differ only in scheme or host letter case, a default port (`:80` for http, `:443`
   for https), a trailing slash on the path, or a fragment are the same link. Links with different
   query strings are different links.
@@ -151,9 +151,10 @@ appears in the list.
 - **FR-003**: System MUST record the time each bookmark was saved.
 - **FR-004**: System MUST NOT store two bookmarks for the same link, where links are compared after
   normalization (scheme and host lowercased, default port removed, trailing path slash removed,
-  fragment removed, query kept). A save of an existing link MUST be rejected with a conflict error
-  that includes the existing bookmark's identifier, and MUST hold even when two saves happen at
-  the same moment.
+  fragment removed, query kept). A save of an existing link MUST return the existing bookmark
+  unchanged with 200 OK (the title and tags in the request are ignored); a save of a new link
+  returns 201 Created. This MUST hold even when two saves happen at the same moment (one gets 201,
+  the other gets 200 with the same bookmark).
 - **FR-005**: System MUST return the saved bookmark, including an identifier the user can use to
   delete it.
 - **FR-006**: System MUST list bookmarks ordered by saved time, most recent first, in pages of 20
diff --git a/specs/001-bookmarks-api/tasks.md b/specs/001-bookmarks-api/tasks.md
index eca6021..485e9f8 100644
--- a/specs/001-bookmarks-api/tasks.md
+++ b/specs/001-bookmarks-api/tasks.md
@@ -41,7 +41,7 @@ its own.
 - [X] T005 Create `src/bookmarks_api/models.py` mapping table `bookmarks` exactly as data-model.md: `id bigint` primary key generated always as identity; `url varchar(2048) not null`; `url_normalized varchar(2048) not null, unique`; `title varchar(200) not null, char_length(title) >= 1`; `tags text[] not null, default '{}', cardinality(tags) <= 10`; `created_at timestamptz not null, default now()`
 - [X] T006 Set up Alembic: `alembic.ini` and `migrations/env.py` reading the URL from `bookmarks_api.config` (overridable by `-x url=...` or the `sqlalchemy.url` option set by tests), with target metadata from `models.py`
 - [X] T007 Create migration `migrations/versions/0001_create_bookmarks.py` creating table `bookmarks` with the constraints in T005 and indexes `uq_bookmarks_url_normalized UNIQUE (url_normalized)`, `ix_bookmarks_created_at_id (created_at DESC, id DESC)`, `ix_bookmarks_tags GIN (tags)`; downgrade drops the table
-- [X] T008 [P] Create `src/bookmarks_api/errors.py`: Pydantic models `ErrorBody {code, message, details}` and `ErrorResponse {error: ErrorBody}`; domain exceptions `NotFoundError` and `DuplicateUrlError(existing_id)`; exception handlers producing the envelope for `RequestValidationError` (422 `validation_error`, field errors in `details`), `StarletteHTTPException` (status-mapped code), `NotFoundError` (404 `not_found`), `DuplicateUrlError` (409 `duplicate_url`, `details.existing_id`) and any other exception (500 `internal_error`, no internals) (Constitution III)
+- [X] T008 [P] Create `src/bookmarks_api/errors.py`: Pydantic models `ErrorBody {code, message, details}` and `ErrorResponse {error: ErrorBody}`; domain exception `NotFoundError`; exception handlers producing the envelope for `RequestValidationError` (422 `validation_error`, field errors in `details`), `StarletteHTTPException` (status-mapped code), `NotFoundError` (404 `not_found`) and any other exception (500 `internal_error`, no internals) (Constitution III)
 - [X] T009 Create `src/bookmarks_api/main.py` with `create_app()` registering the handlers from T008 and the router from `routes.py`, and module-level `app = create_app()`
 - [X] T010 Create `tests/conftest.py`: read `TEST_DATABASE_URL` (default `postgresql://bookmarks:bookmarks@localhost:5432/bookmarks_test`), run `alembic upgrade head` against it once per session, override `get_session` to use the test database, truncate `bookmarks` (restart identity) before every test, and provide a `client` fixture using FastAPI `TestClient` (Constitution II: no database mocks)
 
@@ -51,24 +51,24 @@ its own.
 
 ## Phase 3: User Story 1 - Save a bookmark (Priority: P1) 🎯 MVP
 
-**Goal**: A user can save a link with a title and optional tags; duplicates are rejected.
+**Goal**: A user can save a link with a title and optional tags; saving a duplicate returns the existing bookmark.
 
 **Independent Test**: `POST /bookmarks` returns 201 with the saved bookmark; saving an equivalent
-link returns 409 with `details.existing_id`.
+link returns 200 with the existing bookmark unchanged.
 
 ### Tests for User Story 1
 
 > Write these first and confirm they fail before implementing.
 
 - [X] T011 [P] [US1] Unit tests in `tests/unit/test_normalize.py` for link normalization (lowercase scheme and host, default ports 80/443 removed, trailing path slashes removed, fragment removed, query kept; examples `HTTPS://Example.com:443/docs/#intro` → `https://example.com/docs`, `https://example.com/search?q=FastAPI` keeps `?q=FastAPI`; non-http(s) and host-less links rejected) and tag normalization (trim, lowercase, de-duplicate, sort; must match `^[a-z0-9-]{1,30}$`)
-- [X] T012 [P] [US1] Integration tests in `tests/integration/test_create_bookmark.py` for User Story 1 scenarios 1 to 4: save with no tags (201, `tags == []`, `created_at` present); tags `["Python", " api ", "python"]` → `["api", "python"]`; `https://example.com/docs` then `HTTPS://Example.com/docs/#intro` → 409 `duplicate_url` with `details.existing_id`, still one row; missing url, missing title, `ftp://` link, url over 2048 characters, title over 200 characters, 11 tags, and invalid tag `"no spaces"` each → 422 `validation_error` and nothing saved; two concurrent saves of equivalent links (two threads) → exactly one 201 and one 409, one row (FR-004)
+- [X] T012 [P] [US1] Integration tests in `tests/integration/test_create_bookmark.py` for User Story 1 scenarios 1 to 4: save with no tags (201, `tags == []`, `created_at` present); tags `["Python", " api ", "python"]` → `["api", "python"]`; `https://example.com/docs` then `HTTPS://Example.com/docs/#intro` → 200 with the existing bookmark unchanged, still one row; missing url, missing title, `ftp://` link, url over 2048 characters, title over 200 characters, 11 tags, and invalid tag `"no spaces"` each → 422 `validation_error` and nothing saved; two concurrent saves of equivalent links (two threads) → exactly one 201 and one 200 with the same bookmark, one row (FR-004)
 
 ### Implementation for User Story 1
 
 - [X] T013 [P] [US1] Implement `normalize_url(url) -> str` and `normalize_tags(tags) -> list[str]` in `src/bookmarks_api/normalize.py` using only the standard library, raising `ValueError` with a clear message on invalid input
 - [X] T014 [P] [US1] Create Pydantic models in `src/bookmarks_api/schemas.py`: `BookmarkCreate` (`url` str, max 2048, http/https with a host; `title` trimmed, 1 to 200 characters; `tags` list default `[]`, normalized via `normalize_tags`, at most 10 after de-duplication; extra fields forbidden) and `Bookmark` (`id`, `url`, `title`, `tags`, `created_at`)
-- [X] T015 [US1] Implement `create_bookmark(session, data)` in `src/bookmarks_api/repository.py` using `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`, raising `DuplicateUrlError(existing_id)` when nothing is inserted (research.md, "Preventing duplicate links")
-- [X] T016 [US1] Implement `POST /bookmarks` in `src/bookmarks_api/routes.py` returning 201 with `Bookmark`, with 409 and 422 responses declared using `ErrorResponse`
+- [X] T015 [US1] Implement `create_bookmark(session, data)` in `src/bookmarks_api/repository.py` using `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`, returning `(row, created)`; when nothing is inserted, select and return the existing row with `created=False` (research.md, "Preventing duplicate links")
+- [X] T016 [US1] Implement `POST /bookmarks` in `src/bookmarks_api/routes.py` returning 201 with `Bookmark` for a new link and 200 with the existing `Bookmark` for a duplicate, with the 422 response declared using `ErrorResponse`
 
 **Checkpoint**: User Story 1 works and is tested on its own (MVP)
 
@@ -141,7 +141,7 @@ again returns 404.
 
 **Purpose**: Improvements that affect multiple user stories
 
-- [X] T026 [P] Integration tests in `tests/integration/test_errors.py` asserting every error class (422, 404, 409, and an unknown route 404) uses the envelope `{"error": {"code", "message", "details"}}` (SC-005), and that `/openapi.json` lists all three operations with request and response schemas (Constitution I)
+- [X] T026 [P] Integration tests in `tests/integration/test_errors.py` asserting every error class (422, 404, and an unknown route 404) uses the envelope `{"error": {"code", "message", "details"}}` (SC-005), and that `/openapi.json` lists all three operations with request and response schemas (Constitution I)
 - [X] T027 [P] Update `README.md` with run instructions: `uv sync`, `uv run alembic upgrade head`, `uv run uvicorn bookmarks_api.main:app --reload`, `uv run pytest`
 - [X] T028 Run the full test suite and the manual checks in `specs/001-bookmarks-api/quickstart.md`
 
[exit 0]
```

```console
$ git status --short
 M specs/001-bookmarks-api/plan.md
 M specs/001-bookmarks-api/spec.md
 M specs/001-bookmarks-api/tasks.md
?? episodes/ep03/capture/shortcut-r1/02-artifacts.md
[exit 0]
```

```console
$ set -a; . ./.env; set +a; uv run --python 3.11 pytest -q 2>&1 | tail -5
Creating virtual environment at: .venv
Installed 29 packages in 47ms
........................................................................ [ 74%]
.........................                                                [100%]
97 passed in 3.05s
[exit 0]
```

```console
$ set -a; . ./.env; set +a; uv run --python 3.12 pytest -q 2>&1 | tail -5
Creating virtual environment at: .venv
Installed 29 packages in 22ms
........................................................................ [ 74%]
.........................                                                [100%]
97 passed in 2.94s
[exit 0]
```

```console
$ set -a; . ./.env; set +a; uv run --python 3.13 pytest -q 2>&1 | tail -5
Creating virtual environment at: .venv
Installed 29 packages in 19ms
........................................................................ [ 74%]
.........................                                                [100%]
97 passed in 3.30s
[exit 0]
```

```console
$ grep -rn -i "409\|duplicate_url\|DuplicateUrl\|existing_id\|conflict error" specs src README.md --include=*.md --include=*.yaml --include=*.py
specs/001-bookmarks-api/quickstart.md:39:| 2 | `POST /bookmarks` `{"url": "HTTPS://FastAPI.tiangolo.com", "title": "Again"}` | 409 `duplicate_url`, `details.existing_id` = id from step 1 |
specs/001-bookmarks-api/spec.md:15:- Q: When someone saves a link that is already bookmarked, what should happen? → A: Return the existing bookmark unchanged with 200 OK (no longer a conflict error); the title and tags sent are ignored.
specs/001-bookmarks-api/research.md:87:  `validation_error` (422), `not_found` (404), `duplicate_url` (409, `details.existing_id`).
specs/001-bookmarks-api/contracts/openapi.yaml:25:        '409':
specs/001-bookmarks-api/contracts/openapi.yaml:26:          description: The normalized link is already bookmarked; details.existing_id names it
specs/001-bookmarks-api/contracts/openapi.yaml:129:              enum: [validation_error, not_found, duplicate_url, internal_error]
specs/001-bookmarks-api/contracts/openapi.yaml:132:              description: Extra information, e.g. field errors or existing_id
src/bookmarks_api/errors.py:35:STATUS_CODES = {400: "bad_request", 404: "not_found", 405: "method_not_allowed", 409: "conflict"}
README.md:100:| `POST /bookmarks` | Save `{"url", "title", "tags"}`; 409 if the link is already saved |
[exit 0]
```

Note: stale 409/duplicate_url references remain in quickstart.md, research.md, contracts/openapi.yaml and README.md. Per the run rules (edit only spec.md, plan.md, tasks.md) they were left as is.

```console
$ git status --short
 M specs/001-bookmarks-api/plan.md
 M specs/001-bookmarks-api/spec.md
 M specs/001-bookmarks-api/tasks.md
?? episodes/ep03/capture/shortcut-r1/02-artifacts.md
[exit 0]
```

```console
$ date -u +%Y-%m-%dT%H:%M:%SZ
2026-10-24T11:43:59Z
[exit 0]
```

