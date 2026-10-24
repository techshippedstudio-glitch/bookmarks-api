# Step 02 — artifacts (flowback-r2)

Start: 2026-10-24T11:59:25Z

```console
$ grep -rn -i -E '409|duplicate|conflict|already|existing_id|DuplicateUrl|on_conflict|201' specs README.md .specify/memory
specs/001-bookmarks-api/checklists/requirements.md:35:- The Edge Cases section lists open behavior questions (duplicate handling, link equivalence, tag
specs/001-bookmarks-api/quickstart.md:38:| 1 | `POST /bookmarks` `{"url": "https://fastapi.tiangolo.com/", "title": "FastAPI docs", "tags": ["Python", "api"]}` | 201, tags `["api", "python"]` |
specs/001-bookmarks-api/quickstart.md:39:| 2 | `POST /bookmarks` `{"url": "HTTPS://FastAPI.tiangolo.com", "title": "Again"}` | 409 `duplicate_url`, `details.existing_id` = id from step 1 |
specs/001-bookmarks-api/tasks.md:44:- [X] T008 [P] Create `src/bookmarks_api/errors.py`: Pydantic models `ErrorBody {code, message, details}` and `ErrorResponse {error: ErrorBody}`; domain exceptions `NotFoundError` and `DuplicateUrlError(existing_id)`; exception handlers producing the envelope for `RequestValidationError` (422 `validation_error`, field errors in `details`), `StarletteHTTPException` (status-mapped code), `NotFoundError` (404 `not_found`), `DuplicateUrlError` (409 `duplicate_url`, `details.existing_id`) and any other exception (500 `internal_error`, no internals) (Constitution III)
specs/001-bookmarks-api/tasks.md:54:**Goal**: A user can save a link with a title and optional tags; duplicates are rejected.
specs/001-bookmarks-api/tasks.md:56:**Independent Test**: `POST /bookmarks` returns 201 with the saved bookmark; saving an equivalent
specs/001-bookmarks-api/tasks.md:57:link returns 409 with `details.existing_id`.
specs/001-bookmarks-api/tasks.md:63:- [X] T011 [P] [US1] Unit tests in `tests/unit/test_normalize.py` for link normalization (lowercase scheme and host, default ports 80/443 removed, trailing path slashes removed, fragment removed, query kept; examples `HTTPS://Example.com:443/docs/#intro` → `https://example.com/docs`, `https://example.com/search?q=FastAPI` keeps `?q=FastAPI`; non-http(s) and host-less links rejected) and tag normalization (trim, lowercase, de-duplicate, sort; must match `^[a-z0-9-]{1,30}$`)
specs/001-bookmarks-api/tasks.md:64:- [X] T012 [P] [US1] Integration tests in `tests/integration/test_create_bookmark.py` for User Story 1 scenarios 1 to 4: save with no tags (201, `tags == []`, `created_at` present); tags `["Python", " api ", "python"]` → `["api", "python"]`; `https://example.com/docs` then `HTTPS://Example.com/docs/#intro` → 409 `duplicate_url` with `details.existing_id`, still one row; missing url, missing title, `ftp://` link, url over 2048 characters, title over 200 characters, 11 tags, and invalid tag `"no spaces"` each → 422 `validation_error` and nothing saved; two concurrent saves of equivalent links (two threads) → exactly one 201 and one 409, one row (FR-004)
specs/001-bookmarks-api/tasks.md:70:- [X] T015 [US1] Implement `create_bookmark(session, data)` in `src/bookmarks_api/repository.py` using `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`, raising `DuplicateUrlError(existing_id)` when nothing is inserted (research.md, "Preventing duplicate links")
specs/001-bookmarks-api/tasks.md:71:- [X] T016 [US1] Implement `POST /bookmarks` in `src/bookmarks_api/routes.py` returning 201 with `Bookmark`, with 409 and 422 responses declared using `ErrorResponse`
specs/001-bookmarks-api/tasks.md:129:- [X] T023 [P] [US4] Integration tests in `tests/integration/test_delete_bookmark.py` for User Story 4 scenarios 1 to 3: delete → 204 and absent from list and tag filter; unknown id → 404 `not_found`; delete then save the same link again → 201 new bookmark
specs/001-bookmarks-api/tasks.md:144:- [X] T026 [P] Integration tests in `tests/integration/test_errors.py` asserting every error class (422, 404, 409, and an unknown route 404) uses the envelope `{"error": {"code", "message", "details"}}` (SC-005), and that `/openapi.json` lists all three operations with request and response schemas (Constitution I)
specs/001-bookmarks-api/tasks.md:187:2. Complete Phase 3 (save with duplicate protection)
specs/001-bookmarks-api/tasks.md:209:- [X] T035 Rewrite the paging tests in `tests/integration/test_list_bookmarks.py` and `tests/integration/test_filter_by_tag.py` for cursors, and add a test that pages through all results while bookmarks are saved between requests and finds no duplicates and no gaps, per US2/AC3-AC5 and the Constitution VI quality gate (missing)
specs/001-bookmarks-api/spec.md:9:**Input**: User description: "Build a bookmarks API. A user can save a link with a title and optional tags, list their bookmarks newest first, filter by tag, and delete a bookmark. Saving the same URL twice must not create a duplicate."
specs/001-bookmarks-api/spec.md:15:- Q: When someone saves a link that is already bookmarked, what should happen? → A: Reject it with a conflict error that includes the existing bookmark's identifier; the existing bookmark is left unchanged.
specs/001-bookmarks-api/spec.md:17:- Q: How should tags be cleaned up and limited? → A: Trim spaces, lowercase, drop duplicates; 1 to 30 characters of letters, digits and hyphens; at most 10 tags per bookmark.
specs/001-bookmarks-api/spec.md:46:   a conflict error that includes the existing bookmark's identifier.
specs/001-bookmarks-api/spec.md:125:- Saving a link that is already bookmarked, even with a different title or tags, is rejected with
specs/001-bookmarks-api/spec.md:126:  a conflict error that includes the existing bookmark's identifier; the existing bookmark is not
specs/001-bookmarks-api/spec.md:154:  fragment removed, query kept). A save of an existing link MUST be rejected with a conflict error
specs/001-bookmarks-api/spec.md:170:- **FR-011**: System MUST normalize tags by trimming spaces, lowercasing and removing duplicates,
specs/001-bookmarks-api/data-model.md:13:| `url_normalized` | `varchar(2048)` | not null, **unique** | Normalized link used for duplicate detection (FR-004) |
specs/001-bookmarks-api/data-model.md:15:| `tags` | `text[]` | not null, default `'{}'`, `cardinality(tags) <= 10` | Normalized, de-duplicated, sorted |
specs/001-bookmarks-api/data-model.md:23:| `uq_bookmarks_url_normalized` | `UNIQUE (url_normalized)` | No duplicate links, even under concurrent saves (FR-004) |
specs/001-bookmarks-api/data-model.md:33:| `tags` | Optional list; each trimmed and lowercased; must match `^[a-z0-9-]{1,30}$`; duplicates removed; at most 10 after de-duplication | FR-011, FR-001 |
specs/001-bookmarks-api/plan.md:12:with no duplicate links after normalization. Built as a FastAPI service with Pydantic request and
specs/001-bookmarks-api/plan.md:52:| III. Consistent Error Shape | One envelope `{"error": {"code", "message", "details"}}` for validation (422), not found (404) and duplicate (409), installed as global exception handlers | Pass |
specs/001-bookmarks-api/research.md:36:## Preventing duplicate links
specs/001-bookmarks-api/research.md:39:  unique index. Insert with `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING ...`; if
specs/001-bookmarks-api/research.md:40:  nothing is returned, look up the existing row and raise a duplicate error carrying its id.
specs/001-bookmarks-api/research.md:42:  `ON CONFLICT` avoids relying on catching exceptions mid-transaction.
specs/001-bookmarks-api/research.md:55:  trailing slash to bare hosts, which conflicts with storing the link as given and with our
specs/001-bookmarks-api/research.md:87:  `validation_error` (422), `not_found` (404), `duplicate_url` (409, `details.existing_id`).
specs/001-bookmarks-api/contracts/openapi.yaml:20:        '201':
specs/001-bookmarks-api/contracts/openapi.yaml:25:        '409':
specs/001-bookmarks-api/contracts/openapi.yaml:26:          description: The normalized link is already bookmarked; details.existing_id names it
specs/001-bookmarks-api/contracts/openapi.yaml:129:              enum: [validation_error, not_found, duplicate_url, internal_error]
specs/001-bookmarks-api/contracts/openapi.yaml:132:              description: Extra information, e.g. field errors or existing_id
README.md:7:A small REST API where you can save a link with a title and optional tags, list bookmarks newest first, filter by tag, and delete a bookmark, with no duplicate URLs. It is built with FastAPI and PostgreSQL, but none of the application code was written by hand: it was driven by a constitution and a spec through the Spec Kit flow.
README.md:65:   /speckit-specify Build a bookmarks API. A user can save a link with a title and optional tags, list their bookmarks newest first, filter by tag, and delete a bookmark. Saving the same URL twice must not create a duplicate.
README.md:100:| `POST /bookmarks` | Save `{"url", "title", "tags"}`; 409 if the link is already saved |
.specify/memory/.constitution-template.json:2:  "sha256": "ce7549540fa45543cca797a150201d868e64495fdff39dc38246fb17bd4024b3",
.specify/memory/constitution.md:26:Every error response, including validation errors, not-found and conflicts, MUST use one JSON
.specify/memory/constitution.md:28:`details`. HTTP status codes MUST match the error class (400/422 invalid input, 404 not found, 409
.specify/memory/constitution.md:29:conflict). Internal details such as stack traces or SQL MUST NOT appear in responses.
.specify/memory/constitution.md:58:duplicates or miss items, and deep offsets make the database read and discard every skipped row.
.specify/memory/constitution.md:68:  requests, and sees no duplicates and no gaps (Principle VI).
[exit 0]
```

## 2a. Record in the closest artifact (tasks.md) and classify

Classification: changes **behavior** (FR-004 duplicate rule); strategy (unique index + ON CONFLICT DO NOTHING) unchanged; task breakdown: one flow-back task T037 added, conflicting done tasks rewritten.

```console
$ git diff specs/001-bookmarks-api/tasks.md
diff --git a/specs/001-bookmarks-api/tasks.md b/specs/001-bookmarks-api/tasks.md
index eca6021..66e26f1 100644
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
 
@@ -51,24 +51,25 @@ its own.
 
 ## Phase 3: User Story 1 - Save a bookmark (Priority: P1) 🎯 MVP
 
-**Goal**: A user can save a link with a title and optional tags; duplicates are rejected.
+**Goal**: A user can save a link with a title and optional tags; saving a link that is already
+saved returns the existing bookmark instead of creating a duplicate.
 
 **Independent Test**: `POST /bookmarks` returns 201 with the saved bookmark; saving an equivalent
-link returns 409 with `details.existing_id`.
+link returns 200 with the existing bookmark, unchanged.
 
 ### Tests for User Story 1
 
 > Write these first and confirm they fail before implementing.
 
 - [X] T011 [P] [US1] Unit tests in `tests/unit/test_normalize.py` for link normalization (lowercase scheme and host, default ports 80/443 removed, trailing path slashes removed, fragment removed, query kept; examples `HTTPS://Example.com:443/docs/#intro` → `https://example.com/docs`, `https://example.com/search?q=FastAPI` keeps `?q=FastAPI`; non-http(s) and host-less links rejected) and tag normalization (trim, lowercase, de-duplicate, sort; must match `^[a-z0-9-]{1,30}$`)
-- [X] T012 [P] [US1] Integration tests in `tests/integration/test_create_bookmark.py` for User Story 1 scenarios 1 to 4: save with no tags (201, `tags == []`, `created_at` present); tags `["Python", " api ", "python"]` → `["api", "python"]`; `https://example.com/docs` then `HTTPS://Example.com/docs/#intro` → 409 `duplicate_url` with `details.existing_id`, still one row; missing url, missing title, `ftp://` link, url over 2048 characters, title over 200 characters, 11 tags, and invalid tag `"no spaces"` each → 422 `validation_error` and nothing saved; two concurrent saves of equivalent links (two threads) → exactly one 201 and one 409, one row (FR-004)
+- [X] T012 [P] [US1] Integration tests in `tests/integration/test_create_bookmark.py` for User Story 1 scenarios 1 to 4: save with no tags (201, `tags == []`, `created_at` present); tags `["Python", " api ", "python"]` → `["api", "python"]`; `https://example.com/docs` then `HTTPS://Example.com/docs/#intro` with a different title and tags → 200 with the existing bookmark unchanged (same id, url, title, tags, created_at), still one row; missing url, missing title, `ftp://` link, url over 2048 characters, title over 200 characters, 11 tags, and invalid tag `"no spaces"` each → 422 `validation_error` and nothing saved; two concurrent saves of equivalent links (two threads) → exactly one 201 and one 200 with the same bookmark, one row (FR-004)
 
 ### Implementation for User Story 1
 
 - [X] T013 [P] [US1] Implement `normalize_url(url) -> str` and `normalize_tags(tags) -> list[str]` in `src/bookmarks_api/normalize.py` using only the standard library, raising `ValueError` with a clear message on invalid input
 - [X] T014 [P] [US1] Create Pydantic models in `src/bookmarks_api/schemas.py`: `BookmarkCreate` (`url` str, max 2048, http/https with a host; `title` trimmed, 1 to 200 characters; `tags` list default `[]`, normalized via `normalize_tags`, at most 10 after de-duplication; extra fields forbidden) and `Bookmark` (`id`, `url`, `title`, `tags`, `created_at`)
-- [X] T015 [US1] Implement `create_bookmark(session, data)` in `src/bookmarks_api/repository.py` using `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`, raising `DuplicateUrlError(existing_id)` when nothing is inserted (research.md, "Preventing duplicate links")
-- [X] T016 [US1] Implement `POST /bookmarks` in `src/bookmarks_api/routes.py` returning 201 with `Bookmark`, with 409 and 422 responses declared using `ErrorResponse`
+- [X] T015 [US1] Implement `create_bookmark(session, data)` in `src/bookmarks_api/repository.py` using `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`, returning `(row, created)`; when nothing is inserted, read the existing row by `url_normalized` and return it unchanged with `created = False` (research.md, "Preventing duplicate links")
+- [X] T016 [US1] Implement `POST /bookmarks` in `src/bookmarks_api/routes.py` returning 201 with `Bookmark` for a new link and 200 with the existing `Bookmark` for an already-saved link, with the 422 response declared using `ErrorResponse`
 
 **Checkpoint**: User Story 1 works and is tested on its own (MVP)
 
@@ -141,7 +142,7 @@ again returns 404.
 
 **Purpose**: Improvements that affect multiple user stories
 
-- [X] T026 [P] Integration tests in `tests/integration/test_errors.py` asserting every error class (422, 404, 409, and an unknown route 404) uses the envelope `{"error": {"code", "message", "details"}}` (SC-005), and that `/openapi.json` lists all three operations with request and response schemas (Constitution I)
+- [X] T026 [P] Integration tests in `tests/integration/test_errors.py` asserting every error class (422, 404, and an unknown route 404) uses the envelope `{"error": {"code", "message", "details"}}` (SC-005), and that `/openapi.json` lists all three operations with request and response schemas (Constitution I)
 - [X] T027 [P] Update `README.md` with run instructions: `uv sync`, `uv run alembic upgrade head`, `uv run uvicorn bookmarks_api.main:app --reload`, `uv run pytest`
 - [X] T028 Run the full test suite and the manual checks in `specs/001-bookmarks-api/quickstart.md`
 
@@ -184,7 +185,7 @@ Task: "BookmarkCreate / Bookmark in src/bookmarks_api/schemas.py"
 ### MVP First (User Story 1 only)
 
 1. Complete Phase 1 and Phase 2
-2. Complete Phase 3 (save with duplicate protection)
+2. Complete Phase 3 (save, returning the existing bookmark for a duplicate link)
 3. Stop and validate: run the US1 tests
 
 ### Incremental Delivery
@@ -208,3 +209,14 @@ Task: "BookmarkCreate / Bookmark in src/bookmarks_api/schemas.py"
 - [X] T034 Return 422 `validation_error` for a malformed `cursor` and for any request that sends `offset`, with a message that names `cursor`, per spec Edge Cases (missing)
 - [X] T035 Rewrite the paging tests in `tests/integration/test_list_bookmarks.py` and `tests/integration/test_filter_by_tag.py` for cursors, and add a test that pages through all results while bookmarks are saved between requests and finds no duplicates and no gaps, per US2/AC3-AC5 and the Constitution VI quality gate (missing)
 - [X] T036 Update the `GET /bookmarks` row in `README.md` to document `cursor` and `next_cursor` instead of `offset`, per contracts/openapi.yaml (partial)
+
+## Phase 10: Flow-back (2026-10-24 change request: duplicate saves return the existing bookmark)
+
+> Discovery recorded here first, in the artifact closest to the work. The change was made in code
+> and tests, then flowed back to spec.md (FR-004, US1 scenario 3, Edge Cases, Clarifications),
+> plan.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md and README.md.
+> Classification: behavior change (FR-004 duplicate rule replaced); the strategy (unique index plus
+> `INSERT ... ON CONFLICT DO NOTHING`) is unchanged. T008, T012, T015, T016 and T026 above are
+> rewritten to describe the accepted behavior.
+
+- [X] T037 [US1] Saving a link whose normalized form is already stored returns the existing bookmark unchanged with 200 OK instead of 409 `duplicate_url`; the request's title and tags are ignored; a new link still returns 201 Created; two concurrent saves of the same new link store one bookmark (one 201, one 200 with the same bookmark). `create_bookmark` in `src/bookmarks_api/repository.py` returns `(row, created)`; `POST /bookmarks` in `src/bookmarks_api/routes.py` sets 200 when not created and declares 200 and 201 (no 409); `DuplicateUrlError` and its handler are removed from `src/bookmarks_api/errors.py`; tests updated in `tests/integration/test_create_bookmark.py` and `tests/integration/test_errors.py` (FR-004)
[exit 0]
```

## 2b. Update every conflicting artifact

Edits applied with a Python replace script (exact-match, assert count==1). Two attempts of the script aborted on an assertion before writing spec.md (wrong anchor text for the end of the Clarifications section: the line ends "points to the token." not "next-page token instead."); no partial writes happened (git status showed only tasks.md modified). Third attempt inserted the clarification with the corrected anchor, fourth applied the remaining edits. A first draft also changed the ErrorResponse `code` enum to add `method_not_allowed`; that was out of scope for this change request and was reverted with sed, leaving the enum as `[validation_error, not_found, internal_error]`.

Not changed (deliberately): `.specify/memory/constitution.md` Principle III ("409 conflict" listed as an example error class; still true as a generic rule, the feature just no longer produces it); `specs/001-bookmarks-api/checklists/requirements.md` line 35 (historical note about the original open questions); README line 65 (quotes the original /speckit-specify prompt verbatim, "Saving the same URL twice must not create a duplicate", still true).

```console
$ grep -rn -i -E '409|duplicate_url|existing_id|conflict error' specs README.md
specs/001-bookmarks-api/tasks.md:222:- [X] T037 [US1] Saving a link whose normalized form is already stored returns the existing bookmark unchanged with 200 OK instead of 409 `duplicate_url`; the request's title and tags are ignored; a new link still returns 201 Created; two concurrent saves of the same new link store one bookmark (one 201, one 200 with the same bookmark). `create_bookmark` in `src/bookmarks_api/repository.py` returns `(row, created)`; `POST /bookmarks` in `src/bookmarks_api/routes.py` sets 200 when not created and declares 200 and 201 (no 409); `DuplicateUrlError` and its handler are removed from `src/bookmarks_api/errors.py`; tests updated in `tests/integration/test_create_bookmark.py` and `tests/integration/test_errors.py` (FR-004)
specs/001-bookmarks-api/spec.md:15:- Q: When someone saves a link that is already bookmarked, what should happen? → A: ~~Reject it with a conflict error that includes the existing bookmark's identifier; the existing bookmark is left unchanged.~~ Superseded on 2026-10-24 (see "Change request 2026-10-24" below).
specs/001-bookmarks-api/spec.md:27:- Q: Saving a link that is already bookmarked must no longer be rejected. What should happen instead? → A: If the link (after normalization) is already saved, the existing bookmark is returned unchanged with a success response (200 OK) instead of a conflict error. The title and tags sent in the new request are ignored and the stored bookmark is not modified. Saving a new link still returns 201 Created. Two concurrent saves of the same new link still store only one bookmark: one gets 201, the other gets 200 with the same bookmark. This replaces the duplicate rule in FR-004.
specs/001-bookmarks-api/research.md:42:  "raise a duplicate error carrying its id", which produced 409).
specs/001-bookmarks-api/research.md:92:  existing bookmark with 200, so the former `duplicate_url` (409) code is gone.)
[exit 0]
```

```console
$ git diff -- specs README.md
diff --git a/README.md b/README.md
index 5c4557f..ff90bbe 100644
--- a/README.md
+++ b/README.md
@@ -97,7 +97,7 @@ uv run pytest                                          # tests, against the book
 
 | Endpoint | What it does |
 | --- | --- |
-| `POST /bookmarks` | Save `{"url", "title", "tags"}`; 409 if the link is already saved |
+| `POST /bookmarks` | Save `{"url", "title", "tags"}`; 201 for a new link, or 200 with the existing bookmark (unchanged) if the link is already saved |
 | `GET /bookmarks?tag=&limit=&cursor=` | List newest first, 20 per page by default, optional tag filter; pass `next_cursor` from one page as `cursor` to get the next |
 | `DELETE /bookmarks/{id}` | Delete a bookmark |
 
diff --git a/specs/001-bookmarks-api/contracts/openapi.yaml b/specs/001-bookmarks-api/contracts/openapi.yaml
index ccb008e..b2374c7 100644
--- a/specs/001-bookmarks-api/contracts/openapi.yaml
+++ b/specs/001-bookmarks-api/contracts/openapi.yaml
@@ -17,16 +17,18 @@ paths:
           application/json:
             schema: { $ref: '#/components/schemas/BookmarkCreate' }
       responses:
-        '201':
-          description: Bookmark saved
+        '200':
+          description: >
+            The normalized link is already bookmarked; the existing bookmark is returned
+            unchanged (the request's title and tags are ignored) (FR-004)
           content:
             application/json:
               schema: { $ref: '#/components/schemas/Bookmark' }
-        '409':
-          description: The normalized link is already bookmarked; details.existing_id names it
+        '201':
+          description: Bookmark saved (new link)
           content:
             application/json:
-              schema: { $ref: '#/components/schemas/ErrorResponse' }
+              schema: { $ref: '#/components/schemas/Bookmark' }
         '422':
           description: Invalid link, title or tags
           content:
@@ -126,8 +128,8 @@ components:
           properties:
             code:
               type: string
-              enum: [validation_error, not_found, duplicate_url, internal_error]
+              enum: [validation_error, not_found, internal_error]
             message: { type: string }
             details:
-              description: Extra information, e.g. field errors or existing_id
+              description: Extra information, e.g. field errors
               type: [object, array, 'null']
diff --git a/specs/001-bookmarks-api/data-model.md b/specs/001-bookmarks-api/data-model.md
index 7f7c730..8ca7900 100644
--- a/specs/001-bookmarks-api/data-model.md
+++ b/specs/001-bookmarks-api/data-model.md
@@ -10,7 +10,7 @@ bookmark's "link" is the `url` field in the API and the database.
 | --- | --- | --- | --- |
 | `id` | `bigint` | primary key, generated always as identity | Identifier returned to the user and used for delete |
 | `url` | `varchar(2048)` | not null | The link exactly as the user gave it |
-| `url_normalized` | `varchar(2048)` | not null, **unique** | Normalized link used for duplicate detection (FR-004) |
+| `url_normalized` | `varchar(2048)` | not null, **unique** | Normalized link used for duplicate detection; a save of a link already stored returns that row unchanged (FR-004) |
 | `title` | `varchar(200)` | not null, `char_length(title) >= 1` | Trimmed before saving |
 | `tags` | `text[]` | not null, default `'{}'`, `cardinality(tags) <= 10` | Normalized, de-duplicated, sorted |
 | `created_at` | `timestamptz` | not null, default `now()` | The saved time (FR-003) |
@@ -54,6 +54,8 @@ Examples: `HTTPS://Example.com:443/docs/#intro` → `https://example.com/docs`;
 
 ## Lifecycle
 
-A bookmark is created by a save and removed by a delete; there is no update in this version.
+A bookmark is created by a save of a new link and removed by a delete; there is no update in this
+version. Saving a link that is already stored returns the existing row and does not modify it
+(FR-004).
 Deleting a bookmark frees its normalized link, so the same link can be saved again (User Story 4,
 scenario 3).
diff --git a/specs/001-bookmarks-api/plan.md b/specs/001-bookmarks-api/plan.md
index 4806bc5..3c5a682 100644
--- a/specs/001-bookmarks-api/plan.md
+++ b/specs/001-bookmarks-api/plan.md
@@ -9,7 +9,8 @@
 ## Summary
 
 A single-user REST API to save, list (newest first, paged), filter by tag and delete bookmarks,
-with no duplicate links after normalization. Built as a FastAPI service with Pydantic request and
+with no duplicate links after normalization (saving an already-saved link returns the existing
+bookmark with 200 OK instead of an error). Built as a FastAPI service with Pydantic request and
 response models, PostgreSQL storage through SQLAlchemy 2.0 (sync, psycopg 3), and Alembic
 migrations. Uniqueness is enforced by a unique index on the normalized link, so it holds under
 concurrent saves; tags are a normalized `text[]` column with a GIN index for filtering. All errors
@@ -49,7 +50,7 @@ under a second for 100k bookmarks (indexed queries)
 | --- | --- | --- |
 | I. Typed API Contracts | Pydantic models for the create request, bookmark, page and error responses; FastAPI generates OpenAPI from them; no untyped dicts cross the boundary | Pass |
 | II. Real-Database Testing | Integration tests hit `bookmarks_test` on real PostgreSQL; schema created by running the Alembic migrations; tables truncated before each test; no database mocks | Pass |
-| III. Consistent Error Shape | One envelope `{"error": {"code", "message", "details"}}` for validation (422), not found (404) and duplicate (409), installed as global exception handlers | Pass |
+| III. Consistent Error Shape | One envelope `{"error": {"code", "message", "details"}}` for validation (422) and not found (404), installed as global exception handlers | Pass |
 | IV. Minimal Dependencies | Six runtime/test dependencies, each justified in research.md; standard library used for link normalization and config | Pass |
 | V. Tests Ship With Every Feature | Each user story's tasks include tests for its acceptance scenarios; suite must pass before converge | Pass |
 | VI. Cursor Pagination | `GET /bookmarks` uses keyset paging on `(created_at, id)` with an opaque `next_cursor`; no offset in the API or queries; a test pages through all results while bookmarks are added between requests | Pass |
diff --git a/specs/001-bookmarks-api/quickstart.md b/specs/001-bookmarks-api/quickstart.md
index 6605e43..a975cc3 100644
--- a/specs/001-bookmarks-api/quickstart.md
+++ b/specs/001-bookmarks-api/quickstart.md
@@ -36,7 +36,7 @@ http://127.0.0.1:8000/docs, or use curl:
 | Step | Request | Expected |
 | --- | --- | --- |
 | 1 | `POST /bookmarks` `{"url": "https://fastapi.tiangolo.com/", "title": "FastAPI docs", "tags": ["Python", "api"]}` | 201, tags `["api", "python"]` |
-| 2 | `POST /bookmarks` `{"url": "HTTPS://FastAPI.tiangolo.com", "title": "Again"}` | 409 `duplicate_url`, `details.existing_id` = id from step 1 |
+| 2 | `POST /bookmarks` `{"url": "HTTPS://FastAPI.tiangolo.com", "title": "Again"}` | 200, the step 1 bookmark unchanged (same id, title "FastAPI docs", tags `["api", "python"]`) |
 | 3 | `GET /bookmarks` | 200, the step 1 bookmark first, `total` 1 |
 | 4 | `GET /bookmarks?tag=PYTHON` | 200, the step 1 bookmark |
 | 5 | `GET /bookmarks?limit=500` | 422 `validation_error` |
diff --git a/specs/001-bookmarks-api/research.md b/specs/001-bookmarks-api/research.md
index 5ae30cd..ff905ed 100644
--- a/specs/001-bookmarks-api/research.md
+++ b/specs/001-bookmarks-api/research.md
@@ -37,8 +37,12 @@ considered.
 
 - **Decision**: Store the link as given (`url`) and a normalized form (`url_normalized`) with a
   unique index. Insert with `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING ...`; if
-  nothing is returned, look up the existing row and raise a duplicate error carrying its id.
-- **Rationale**: The database guarantees uniqueness even when two saves race (spec edge case);
+  nothing is returned, look up the existing row and return it unchanged, and the endpoint answers
+  200 OK instead of 201 Created (FR-004, change request 2026-10-24; this replaced the original
+  "raise a duplicate error carrying its id", which produced 409).
+- **Rationale**: The database guarantees uniqueness even when two saves race (spec edge case):
+  the losing insert waits for the winner to commit, inserts nothing, and then reads the winner's
+  row, so one save gets 201 and the other 200 with the same bookmark;
   `ON CONFLICT` avoids relying on catching exceptions mid-transaction.
 - **Alternatives considered**: check-then-insert in application code (races under concurrency);
   catching `IntegrityError` (works, but leaves the transaction aborted and is noisier).
@@ -84,7 +88,8 @@ considered.
 ## Error envelope
 
 - **Decision**: `{"error": {"code": str, "message": str, "details": object | null}}`. Codes:
-  `validation_error` (422), `not_found` (404), `duplicate_url` (409, `details.existing_id`).
+  `validation_error` (422), `not_found` (404). (A duplicate save is not an error; it returns the
+  existing bookmark with 200, so the former `duplicate_url` (409) code is gone.)
   FastAPI's `RequestValidationError` and `HTTPException` handlers are replaced so framework errors
   use the same shape; unexpected errors return 500 `internal_error` without internals.
 - **Rationale**: Constitution III.
diff --git a/specs/001-bookmarks-api/spec.md b/specs/001-bookmarks-api/spec.md
index 3ed7b96..3f648fb 100644
--- a/specs/001-bookmarks-api/spec.md
+++ b/specs/001-bookmarks-api/spec.md
@@ -12,7 +12,7 @@
 
 ### Session 2026-10-21
 
-- Q: When someone saves a link that is already bookmarked, what should happen? → A: Reject it with a conflict error that includes the existing bookmark's identifier; the existing bookmark is left unchanged.
+- Q: When someone saves a link that is already bookmarked, what should happen? → A: ~~Reject it with a conflict error that includes the existing bookmark's identifier; the existing bookmark is left unchanged.~~ Superseded on 2026-10-24 (see "Change request 2026-10-24" below).
 - Q: Which links count as "the same link"? → A: Links that match after normalization: scheme and host lowercased, default port removed, trailing slash on the path removed, fragment (#...) removed; the query string is kept as is.
 - Q: How should tags be cleaned up and limited? → A: Trim spaces, lowercase, drop duplicates; 1 to 30 characters of letters, digits and hyphens; at most 10 tags per bookmark.
 - Q: How should the list behave when there are many bookmarks? → A: Return pages: 20 per page by default, up to 100 per page, using a limit and an offset, plus the total count.
@@ -22,6 +22,10 @@
 
 - Q: Principle VI forbids offset pagination. How does a client ask for the next page? → A: Each page returns an opaque next-page token (none on the last page); the client passes it back to get the next page. The offset option is removed, and a request that still sends it gets a validation error that points to the token.
 
+### Change request 2026-10-24
+
+- Q: Saving a link that is already bookmarked must no longer be rejected. What should happen instead? → A: If the link (after normalization) is already saved, the existing bookmark is returned unchanged with a success response (200 OK) instead of a conflict error. The title and tags sent in the new request are ignored and the stored bookmark is not modified. Saving a new link still returns 201 Created. Two concurrent saves of the same new link still store only one bookmark: one gets 201, the other gets 200 with the same bookmark. This replaces the duplicate rule in FR-004.
+
 ## User Scenarios & Testing *(mandatory)*
 
 ### User Story 1 - Save a bookmark (Priority: P1)
@@ -42,8 +46,9 @@ contains the saved link, title, tags and the time it was saved.
 2. **Given** no bookmarks exist, **When** the user saves a link with a title and the tags "Python",
    " api " and "python", **Then** the bookmark is returned with the tags "api" and "python".
 3. **Given** a bookmark for `https://example.com/docs` exists, **When** the user saves
-   `HTTPS://Example.com/docs/#intro`, **Then** no second bookmark is created and the user receives
-   a conflict error that includes the existing bookmark's identifier.
+   `HTTPS://Example.com/docs/#intro` with a different title and tags, **Then** no second bookmark
+   is created and the user receives the existing bookmark, unchanged, with a 200 OK success
+   response (not 201 Created).
 4. **Given** any state, **When** the user tries to save a bookmark without a link or without a
    title, with a link that is not a valid http or https address, with a title over 200 characters,
    with more than 10 tags, or with an invalid tag, **Then** nothing is saved and the user receives
@@ -122,9 +127,9 @@ appears in the list.
 
 ### Edge Cases
 
-- Saving a link that is already bookmarked, even with a different title or tags, is rejected with
-  a conflict error that includes the existing bookmark's identifier; the existing bookmark is not
-  changed.
+- Saving a link that is already bookmarked, even with a different title or tags, is not an error:
+  the existing bookmark is returned unchanged with 200 OK; the title and tags in the request are
+  ignored and the stored bookmark is not modified.
 - Links that differ only in scheme or host letter case, a default port (`:80` for http, `:443`
   for https), a trailing slash on the path, or a fragment are the same link. Links with different
   query strings are different links.
@@ -132,7 +137,8 @@ appears in the list.
   kept once.
 - A tag that is empty after trimming, longer than 30 characters, or contains characters other
   than letters, digits and hyphens is rejected.
-- Two saves of the same link at the same moment still leave exactly one bookmark.
+- Two saves of the same new link at the same moment still leave exactly one bookmark: one save
+  gets 201 Created, the other gets 200 OK with the same bookmark.
 - A malformed next-page token (one that does not decode to a position in the list) is rejected with
   a validation error.
 - A request that sends the removed offset option is rejected with a validation error that names the
@@ -151,11 +157,14 @@ appears in the list.
 - **FR-003**: System MUST record the time each bookmark was saved.
 - **FR-004**: System MUST NOT store two bookmarks for the same link, where links are compared after
   normalization (scheme and host lowercased, default port removed, trailing path slash removed,
-  fragment removed, query kept). A save of an existing link MUST be rejected with a conflict error
-  that includes the existing bookmark's identifier, and MUST hold even when two saves happen at
-  the same moment.
-- **FR-005**: System MUST return the saved bookmark, including an identifier the user can use to
-  delete it.
+  fragment removed, query kept). A save of a link that is already saved MUST NOT be rejected: it
+  MUST return the existing bookmark unchanged with 200 OK, ignoring the title and tags in the
+  request and leaving the stored bookmark unmodified. A save of a new link MUST return 201
+  Created. This MUST hold even when two saves of the same new link happen at the same moment:
+  exactly one bookmark is stored, one save gets 201 and the other gets 200 with the same
+  bookmark.
+- **FR-005**: System MUST return the saved bookmark (or, for an already-saved link, the existing
+  bookmark), including an identifier the user can use to delete it.
 - **FR-006**: System MUST list bookmarks ordered by saved time, most recent first, in pages of 20
   by default and at most 100, and MUST include the total number of matching bookmarks. Each page
   MUST return an opaque next-page token (none on the last page), and paging with it MUST NOT repeat
diff --git a/specs/001-bookmarks-api/tasks.md b/specs/001-bookmarks-api/tasks.md
index eca6021..66e26f1 100644
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
 
@@ -51,24 +51,25 @@ its own.
 
 ## Phase 3: User Story 1 - Save a bookmark (Priority: P1) 🎯 MVP
 
-**Goal**: A user can save a link with a title and optional tags; duplicates are rejected.
+**Goal**: A user can save a link with a title and optional tags; saving a link that is already
+saved returns the existing bookmark instead of creating a duplicate.
 
 **Independent Test**: `POST /bookmarks` returns 201 with the saved bookmark; saving an equivalent
-link returns 409 with `details.existing_id`.
+link returns 200 with the existing bookmark, unchanged.
 
 ### Tests for User Story 1
 
 > Write these first and confirm they fail before implementing.
 
 - [X] T011 [P] [US1] Unit tests in `tests/unit/test_normalize.py` for link normalization (lowercase scheme and host, default ports 80/443 removed, trailing path slashes removed, fragment removed, query kept; examples `HTTPS://Example.com:443/docs/#intro` → `https://example.com/docs`, `https://example.com/search?q=FastAPI` keeps `?q=FastAPI`; non-http(s) and host-less links rejected) and tag normalization (trim, lowercase, de-duplicate, sort; must match `^[a-z0-9-]{1,30}$`)
-- [X] T012 [P] [US1] Integration tests in `tests/integration/test_create_bookmark.py` for User Story 1 scenarios 1 to 4: save with no tags (201, `tags == []`, `created_at` present); tags `["Python", " api ", "python"]` → `["api", "python"]`; `https://example.com/docs` then `HTTPS://Example.com/docs/#intro` → 409 `duplicate_url` with `details.existing_id`, still one row; missing url, missing title, `ftp://` link, url over 2048 characters, title over 200 characters, 11 tags, and invalid tag `"no spaces"` each → 422 `validation_error` and nothing saved; two concurrent saves of equivalent links (two threads) → exactly one 201 and one 409, one row (FR-004)
+- [X] T012 [P] [US1] Integration tests in `tests/integration/test_create_bookmark.py` for User Story 1 scenarios 1 to 4: save with no tags (201, `tags == []`, `created_at` present); tags `["Python", " api ", "python"]` → `["api", "python"]`; `https://example.com/docs` then `HTTPS://Example.com/docs/#intro` with a different title and tags → 200 with the existing bookmark unchanged (same id, url, title, tags, created_at), still one row; missing url, missing title, `ftp://` link, url over 2048 characters, title over 200 characters, 11 tags, and invalid tag `"no spaces"` each → 422 `validation_error` and nothing saved; two concurrent saves of equivalent links (two threads) → exactly one 201 and one 200 with the same bookmark, one row (FR-004)
 
 ### Implementation for User Story 1
 
 - [X] T013 [P] [US1] Implement `normalize_url(url) -> str` and `normalize_tags(tags) -> list[str]` in `src/bookmarks_api/normalize.py` using only the standard library, raising `ValueError` with a clear message on invalid input
 - [X] T014 [P] [US1] Create Pydantic models in `src/bookmarks_api/schemas.py`: `BookmarkCreate` (`url` str, max 2048, http/https with a host; `title` trimmed, 1 to 200 characters; `tags` list default `[]`, normalized via `normalize_tags`, at most 10 after de-duplication; extra fields forbidden) and `Bookmark` (`id`, `url`, `title`, `tags`, `created_at`)
-- [X] T015 [US1] Implement `create_bookmark(session, data)` in `src/bookmarks_api/repository.py` using `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`, raising `DuplicateUrlError(existing_id)` when nothing is inserted (research.md, "Preventing duplicate links")
-- [X] T016 [US1] Implement `POST /bookmarks` in `src/bookmarks_api/routes.py` returning 201 with `Bookmark`, with 409 and 422 responses declared using `ErrorResponse`
+- [X] T015 [US1] Implement `create_bookmark(session, data)` in `src/bookmarks_api/repository.py` using `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`, returning `(row, created)`; when nothing is inserted, read the existing row by `url_normalized` and return it unchanged with `created = False` (research.md, "Preventing duplicate links")
+- [X] T016 [US1] Implement `POST /bookmarks` in `src/bookmarks_api/routes.py` returning 201 with `Bookmark` for a new link and 200 with the existing `Bookmark` for an already-saved link, with the 422 response declared using `ErrorResponse`
 
 **Checkpoint**: User Story 1 works and is tested on its own (MVP)
 
@@ -141,7 +142,7 @@ again returns 404.
 
 **Purpose**: Improvements that affect multiple user stories
 
-- [X] T026 [P] Integration tests in `tests/integration/test_errors.py` asserting every error class (422, 404, 409, and an unknown route 404) uses the envelope `{"error": {"code", "message", "details"}}` (SC-005), and that `/openapi.json` lists all three operations with request and response schemas (Constitution I)
+- [X] T026 [P] Integration tests in `tests/integration/test_errors.py` asserting every error class (422, 404, and an unknown route 404) uses the envelope `{"error": {"code", "message", "details"}}` (SC-005), and that `/openapi.json` lists all three operations with request and response schemas (Constitution I)
 - [X] T027 [P] Update `README.md` with run instructions: `uv sync`, `uv run alembic upgrade head`, `uv run uvicorn bookmarks_api.main:app --reload`, `uv run pytest`
 - [X] T028 Run the full test suite and the manual checks in `specs/001-bookmarks-api/quickstart.md`
 
@@ -184,7 +185,7 @@ Task: "BookmarkCreate / Bookmark in src/bookmarks_api/schemas.py"
 ### MVP First (User Story 1 only)
 
 1. Complete Phase 1 and Phase 2
-2. Complete Phase 3 (save with duplicate protection)
+2. Complete Phase 3 (save, returning the existing bookmark for a duplicate link)
 3. Stop and validate: run the US1 tests
 
 ### Incremental Delivery
@@ -208,3 +209,14 @@ Task: "BookmarkCreate / Bookmark in src/bookmarks_api/schemas.py"
 - [X] T034 Return 422 `validation_error` for a malformed `cursor` and for any request that sends `offset`, with a message that names `cursor`, per spec Edge Cases (missing)
 - [X] T035 Rewrite the paging tests in `tests/integration/test_list_bookmarks.py` and `tests/integration/test_filter_by_tag.py` for cursors, and add a test that pages through all results while bookmarks are saved between requests and finds no duplicates and no gaps, per US2/AC3-AC5 and the Constitution VI quality gate (missing)
 - [X] T036 Update the `GET /bookmarks` row in `README.md` to document `cursor` and `next_cursor` instead of `offset`, per contracts/openapi.yaml (partial)
+
+## Phase 10: Flow-back (2026-10-24 change request: duplicate saves return the existing bookmark)
+
+> Discovery recorded here first, in the artifact closest to the work. The change was made in code
+> and tests, then flowed back to spec.md (FR-004, US1 scenario 3, Edge Cases, Clarifications),
+> plan.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md and README.md.
+> Classification: behavior change (FR-004 duplicate rule replaced); the strategy (unique index plus
+> `INSERT ... ON CONFLICT DO NOTHING`) is unchanged. T008, T012, T015, T016 and T026 above are
+> rewritten to describe the accepted behavior.
+
+- [X] T037 [US1] Saving a link whose normalized form is already stored returns the existing bookmark unchanged with 200 OK instead of 409 `duplicate_url`; the request's title and tags are ignored; a new link still returns 201 Created; two concurrent saves of the same new link store one bookmark (one 201, one 200 with the same bookmark). `create_bookmark` in `src/bookmarks_api/repository.py` returns `(row, created)`; `POST /bookmarks` in `src/bookmarks_api/routes.py` sets 200 when not created and declares 200 and 201 (no 409); `DuplicateUrlError` and its handler are removed from `src/bookmarks_api/errors.py`; tests updated in `tests/integration/test_create_bookmark.py` and `tests/integration/test_errors.py` (FR-004)
[exit 0]
```

## Tests after artifact edits

```console
$ uv run --python 3.13 pytest -q
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
........................................................................ [ 74%]
.........................                                                [100%]
97 passed in 2.71s
[exit 0]
```

End: 2026-10-24T12:01:51Z
