# 02-artifacts

Step start: 2026-10-24T11:42:51Z

## Flow-back decisions (per docs/guides/evolving-specs.md "Flow-Back", as summarized in the run brief)

Note: docs/guides/evolving-specs.md is not in the worktree or installed on disk (`find / -name evolving-specs.md` returned nothing), so the guide's steps are applied as stated in the run brief.

1. **Record the discovery in the artifact closest to the work.** The closest artifact to the code change is `tasks.md`, which names the exact functions and tests. Recorded first: a new "Phase 10: Flow-back" section with the discovery and tasks T037-T042 (marked [X], since the code was done in step 1), plus a note in Phase 3 that T008/T012/T015/T016/T026 built the old rule and are kept as history (same pattern as the existing Phase 4 note for constitution v1.1.0).
2. **Classify the change.** It changes *behavior* (spec FR-004, US1 scenario 3, edge cases, FR-005 wording), *strategy* (research "Preventing duplicate links" and "Error envelope", plan Summary and Constitution Check III), and the *contract* (openapi.yaml: 409 removed, 200 added, `duplicate_url` removed from the error code enum). Task breakdown: new Phase 10 tasks. Data model: no schema change; only the notes on `url_normalized` and the unique index.
3. **Update every conflicting artifact.** spec.md, plan.md, tasks.md, research.md, contracts/openapi.yaml, data-model.md, quickstart.md, README.md. Not changed: `.specify/memory/constitution.md` (Principle III lists 409 as the status for conflicts in general; it does not require a duplicate to be a conflict, so it does not conflict); `checklists/requirements.md` (a historical record of spec quality at specify time; line 35 says the Edge Cases section *listed* open questions, still true); the spec's quoted **Input** line (verbatim original user description); README intro "with no duplicate URLs" (still true).

## Command: find all references in artifacts and README

```
$ grep -rn -i "409\|duplicate\|conflict\|existing_id" specs README.md .specify/memory/constitution.md   # at tag ep03-flowback-r1-fix
.specify/memory/constitution.md:26:Every error response, including validation errors, not-found and conflicts, MUST use one JSON
.specify/memory/constitution.md:28:`details`. HTTP status codes MUST match the error class (400/422 invalid input, 404 not found, 409
.specify/memory/constitution.md:29:conflict). Internal details such as stack traces or SQL MUST NOT appear in responses.
.specify/memory/constitution.md:58:duplicates or miss items, and deep offsets make the database read and discard every skipped row.
.specify/memory/constitution.md:68:  requests, and sees no duplicates and no gaps (Principle VI).
README.md:7:A small REST API where you can save a link with a title and optional tags, list bookmarks newest first, filter by tag, and delete a bookmark, with no duplicate URLs. It is built with FastAPI and PostgreSQL, but none of the application code was written by hand: it was driven by a constitution and a spec through the Spec Kit flow.
README.md:65:   /speckit-specify Build a bookmarks API. A user can save a link with a title and optional tags, list their bookmarks newest first, filter by tag, and delete a bookmark. Saving the same URL twice must not create a duplicate.
README.md:100:| `POST /bookmarks` | Save `{"url", "title", "tags"}`; 409 if the link is already saved |
specs/001-bookmarks-api/checklists/requirements.md:35:- The Edge Cases section lists open behavior questions (duplicate handling, link equivalence, tag
specs/001-bookmarks-api/contracts/openapi.yaml:25:        '409':
specs/001-bookmarks-api/contracts/openapi.yaml:26:          description: The normalized link is already bookmarked; details.existing_id names it
specs/001-bookmarks-api/contracts/openapi.yaml:129:              enum: [validation_error, not_found, duplicate_url, internal_error]
specs/001-bookmarks-api/contracts/openapi.yaml:132:              description: Extra information, e.g. field errors or existing_id
specs/001-bookmarks-api/data-model.md:13:| `url_normalized` | `varchar(2048)` | not null, **unique** | Normalized link used for duplicate detection (FR-004) |
specs/001-bookmarks-api/data-model.md:15:| `tags` | `text[]` | not null, default `'{}'`, `cardinality(tags) <= 10` | Normalized, de-duplicated, sorted |
specs/001-bookmarks-api/data-model.md:23:| `uq_bookmarks_url_normalized` | `UNIQUE (url_normalized)` | No duplicate links, even under concurrent saves (FR-004) |
specs/001-bookmarks-api/data-model.md:33:| `tags` | Optional list; each trimmed and lowercased; must match `^[a-z0-9-]{1,30}$`; duplicates removed; at most 10 after de-duplication | FR-011, FR-001 |
specs/001-bookmarks-api/plan.md:12:with no duplicate links after normalization. Built as a FastAPI service with Pydantic request and
specs/001-bookmarks-api/plan.md:52:| III. Consistent Error Shape | One envelope `{"error": {"code", "message", "details"}}` for validation (422), not found (404) and duplicate (409), installed as global exception handlers | Pass |
specs/001-bookmarks-api/quickstart.md:39:| 2 | `POST /bookmarks` `{"url": "HTTPS://FastAPI.tiangolo.com", "title": "Again"}` | 409 `duplicate_url`, `details.existing_id` = id from step 1 |
specs/001-bookmarks-api/research.md:36:## Preventing duplicate links
specs/001-bookmarks-api/research.md:39:  unique index. Insert with `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING ...`; if
specs/001-bookmarks-api/research.md:40:  nothing is returned, look up the existing row and raise a duplicate error carrying its id.
specs/001-bookmarks-api/research.md:42:  `ON CONFLICT` avoids relying on catching exceptions mid-transaction.
specs/001-bookmarks-api/research.md:55:  trailing slash to bare hosts, which conflicts with storing the link as given and with our
specs/001-bookmarks-api/research.md:87:  `validation_error` (422), `not_found` (404), `duplicate_url` (409, `details.existing_id`).
specs/001-bookmarks-api/spec.md:9:**Input**: User description: "Build a bookmarks API. A user can save a link with a title and optional tags, list their bookmarks newest first, filter by tag, and delete a bookmark. Saving the same URL twice must not create a duplicate."
specs/001-bookmarks-api/spec.md:15:- Q: When someone saves a link that is already bookmarked, what should happen? → A: Reject it with a conflict error that includes the existing bookmark's identifier; the existing bookmark is left unchanged.
specs/001-bookmarks-api/spec.md:17:- Q: How should tags be cleaned up and limited? → A: Trim spaces, lowercase, drop duplicates; 1 to 30 characters of letters, digits and hyphens; at most 10 tags per bookmark.
specs/001-bookmarks-api/spec.md:46:   a conflict error that includes the existing bookmark's identifier.
specs/001-bookmarks-api/spec.md:126:  a conflict error that includes the existing bookmark's identifier; the existing bookmark is not
specs/001-bookmarks-api/spec.md:154:  fragment removed, query kept). A save of an existing link MUST be rejected with a conflict error
specs/001-bookmarks-api/spec.md:170:- **FR-011**: System MUST normalize tags by trimming spaces, lowercasing and removing duplicates,
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
```

## Command: validate the contract YAML

```
$ uv run --python 3.13 --with pyyaml python -c "import yaml;yaml.safe_load(open('specs/001-bookmarks-api/contracts/openapi.yaml'));print('yaml ok')"
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
yaml ok
```

## Command: references remaining after the update

```
$ grep -rn -i "409\|duplicate_url\|conflict error\|existing_id" specs README.md
specs/001-bookmarks-api/tasks.md:44:- [X] T008 [P] Create `src/bookmarks_api/errors.py`: Pydantic models `ErrorBody {code, message, details}` and `ErrorResponse {error: ErrorBody}`; domain exceptions `NotFoundError` and `DuplicateUrlError(existing_id)`; exception handlers producing the envelope for `RequestValidationError` (422 `validation_error`, field errors in `details`), `StarletteHTTPException` (status-mapped code), `NotFoundError` (404 `not_found`), `DuplicateUrlError` (409 `duplicate_url`, `details.existing_id`) and any other exception (500 `internal_error`, no internals) (Constitution III)
specs/001-bookmarks-api/tasks.md:61:> duplicate rule (409 `duplicate_url` with `details.existing_id`), which FR-004 no longer specifies.
specs/001-bookmarks-api/tasks.md:69:- [X] T012 [P] [US1] Integration tests in `tests/integration/test_create_bookmark.py` for User Story 1 scenarios 1 to 4: save with no tags (201, `tags == []`, `created_at` present); tags `["Python", " api ", "python"]` → `["api", "python"]`; `https://example.com/docs` then `HTTPS://Example.com/docs/#intro` → 409 `duplicate_url` with `details.existing_id`, still one row; missing url, missing title, `ftp://` link, url over 2048 characters, title over 200 characters, 11 tags, and invalid tag `"no spaces"` each → 422 `validation_error` and nothing saved; two concurrent saves of equivalent links (two threads) → exactly one 201 and one 409, one row (FR-004)
specs/001-bookmarks-api/tasks.md:75:- [X] T015 [US1] Implement `create_bookmark(session, data)` in `src/bookmarks_api/repository.py` using `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`, raising `DuplicateUrlError(existing_id)` when nothing is inserted (research.md, "Preventing duplicate links")
specs/001-bookmarks-api/tasks.md:76:- [X] T016 [US1] Implement `POST /bookmarks` in `src/bookmarks_api/routes.py` returning 201 with `Bookmark`, with 409 and 422 responses declared using `ErrorResponse`
specs/001-bookmarks-api/tasks.md:149:- [X] T026 [P] Integration tests in `tests/integration/test_errors.py` asserting every error class (422, 404, 409, and an unknown route 404) uses the envelope `{"error": {"code", "message", "details"}}` (SC-005), and that `/openapi.json` lists all three operations with request and response schemas (Constitution I)
specs/001-bookmarks-api/tasks.md:219:**Discovery**: Rejecting a save of an already-saved link with 409 forced clients to treat a
specs/001-bookmarks-api/tasks.md:227:- [X] T038 [US1] Make `POST /bookmarks` in `src/bookmarks_api/routes.py` return 201 with `Bookmark` for a new link and 200 with the existing `Bookmark` otherwise; declare 201, 200 and 422 in OpenAPI and no 409, per contracts/openapi.yaml
specs/001-bookmarks-api/tasks.md:228:- [X] T039 [P] Remove `DuplicateUrlError` and its 409 `duplicate_url` handler from `src/bookmarks_api/errors.py` (no longer raised), per research.md "Error envelope"
specs/001-bookmarks-api/tasks.md:230:- [X] T041 [P] Update `tests/integration/test_errors.py`: drop the 409 envelope test and assert `/openapi.json` documents `POST /bookmarks` with 201 and 200 `Bookmark` responses, 422 `ErrorResponse`, and no 409 (SC-005, Constitution I)
specs/001-bookmarks-api/tasks.md:231:- [X] T042 [P] Update the `POST /bookmarks` row in `README.md` and step 2 of `specs/001-bookmarks-api/quickstart.md` to describe 200 with the existing bookmark instead of 409
specs/001-bookmarks-api/spec.md:15:- Q: When someone saves a link that is already bookmarked, what should happen? → A: Reject it with a conflict error that includes the existing bookmark's identifier; the existing bookmark is left unchanged. *(Superseded 2026-10-24; see the flow-back session below.)*
specs/001-bookmarks-api/spec.md:27:- Q: When someone saves a link that is already bookmarked, what should happen? → A: It is no longer rejected. The existing bookmark is returned unchanged with HTTP 200 OK instead of the 409 conflict; the title and tags sent in the new request are ignored and the stored bookmark is not modified. Saving a new link still returns 201 Created. Two concurrent saves of the same new link still store only one bookmark: one gets 201, the other gets 200 with the same bookmark. This replaces the earlier duplicate answer and the duplicate rule in FR-004.
specs/001-bookmarks-api/plan.md:53:| III. Consistent Error Shape | One envelope `{"error": {"code", "message", "details"}}` for validation (422) and not found (404), installed as global exception handlers; a duplicate save is not an error (200 with the existing bookmark, FR-004), so there is no 409 | Pass |
specs/001-bookmarks-api/research.md:52:  cannot tell 201 from 200 without extra tricks); rejecting with 409 `duplicate_url` (the original
specs/001-bookmarks-api/research.md:97:  (200 with the existing bookmark, FR-004), so there is no `duplicate_url` code.
```

(Remaining hits are the superseded clarification kept as history, the history notes, the old completed tasks kept as history, and research's "Alternatives considered" entry.)

## Command: diff

```diff
$ git diff
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
 
diff --git a/specs/001-bookmarks-api/contracts/openapi.yaml b/specs/001-bookmarks-api/contracts/openapi.yaml
index ccb008e..1d17d0e 100644
--- a/specs/001-bookmarks-api/contracts/openapi.yaml
+++ b/specs/001-bookmarks-api/contracts/openapi.yaml
@@ -10,6 +10,9 @@ paths:
   /bookmarks:
     post:
       summary: Save a bookmark
+      description: >
+        Saves a new link (201). If the link, after normalization, is already saved, returns the
+        existing bookmark unchanged (200); the title and tags in the request are ignored (FR-004).
       operationId: createBookmark
       requestBody:
         required: true
@@ -18,15 +21,15 @@ paths:
             schema: { $ref: '#/components/schemas/BookmarkCreate' }
       responses:
         '201':
-          description: Bookmark saved
+          description: New link; bookmark saved
           content:
             application/json:
               schema: { $ref: '#/components/schemas/Bookmark' }
-        '409':
-          description: The normalized link is already bookmarked; details.existing_id names it
+        '200':
+          description: The normalized link is already saved; the existing bookmark, unchanged
           content:
             application/json:
-              schema: { $ref: '#/components/schemas/ErrorResponse' }
+              schema: { $ref: '#/components/schemas/Bookmark' }
         '422':
           description: Invalid link, title or tags
           content:
@@ -126,8 +129,8 @@ components:
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
index 7f7c730..9a80fbd 100644
--- a/specs/001-bookmarks-api/data-model.md
+++ b/specs/001-bookmarks-api/data-model.md
@@ -10,7 +10,7 @@ bookmark's "link" is the `url` field in the API and the database.
 | --- | --- | --- | --- |
 | `id` | `bigint` | primary key, generated always as identity | Identifier returned to the user and used for delete |
 | `url` | `varchar(2048)` | not null | The link exactly as the user gave it |
-| `url_normalized` | `varchar(2048)` | not null, **unique** | Normalized link used for duplicate detection (FR-004) |
+| `url_normalized` | `varchar(2048)` | not null, **unique** | Normalized link used to find an already-saved bookmark; a save of an existing link returns that row unchanged (FR-004) |
 | `title` | `varchar(200)` | not null, `char_length(title) >= 1` | Trimmed before saving |
 | `tags` | `text[]` | not null, default `'{}'`, `cardinality(tags) <= 10` | Normalized, de-duplicated, sorted |
 | `created_at` | `timestamptz` | not null, default `now()` | The saved time (FR-003) |
@@ -20,7 +20,7 @@ bookmark's "link" is the `url` field in the API and the database.
 | Name | Definition | Serves |
 | --- | --- | --- |
 | `bookmarks_pkey` | `PRIMARY KEY (id)` | Delete by id |
-| `uq_bookmarks_url_normalized` | `UNIQUE (url_normalized)` | No duplicate links, even under concurrent saves (FR-004) |
+| `uq_bookmarks_url_normalized` | `UNIQUE (url_normalized)` | No duplicate links, even under concurrent saves; the losing save returns the existing row (FR-004) |
 | `ix_bookmarks_created_at_id` | `(created_at DESC, id DESC)` | Newest-first listing and paging (FR-006) |
 | `ix_bookmarks_tags` | `GIN (tags)` | Tag filter `tags @> ARRAY[:tag]` (FR-007) |
 
diff --git a/specs/001-bookmarks-api/plan.md b/specs/001-bookmarks-api/plan.md
index 4806bc5..306f9c1 100644
--- a/specs/001-bookmarks-api/plan.md
+++ b/specs/001-bookmarks-api/plan.md
@@ -9,10 +9,11 @@
 ## Summary
 
 A single-user REST API to save, list (newest first, paged), filter by tag and delete bookmarks,
-with no duplicate links after normalization. Built as a FastAPI service with Pydantic request and
+with no duplicate links after normalization: saving a link that is already saved returns the
+existing bookmark unchanged (200 OK) instead of an error, and a new link returns 201. Built as a FastAPI service with Pydantic request and
 response models, PostgreSQL storage through SQLAlchemy 2.0 (sync, psycopg 3), and Alembic
 migrations. Uniqueness is enforced by a unique index on the normalized link, so it holds under
-concurrent saves; tags are a normalized `text[]` column with a GIN index for filtering. All errors
+concurrent saves (one concurrent save creates the row, the other returns it); tags are a normalized `text[]` column with a GIN index for filtering. All errors
 use one JSON envelope. Tests run with pytest against the real `bookmarks_test` database from the
 existing `docker-compose.yml`.
 
@@ -49,7 +50,7 @@ under a second for 100k bookmarks (indexed queries)
 | --- | --- | --- |
 | I. Typed API Contracts | Pydantic models for the create request, bookmark, page and error responses; FastAPI generates OpenAPI from them; no untyped dicts cross the boundary | Pass |
 | II. Real-Database Testing | Integration tests hit `bookmarks_test` on real PostgreSQL; schema created by running the Alembic migrations; tables truncated before each test; no database mocks | Pass |
-| III. Consistent Error Shape | One envelope `{"error": {"code", "message", "details"}}` for validation (422), not found (404) and duplicate (409), installed as global exception handlers | Pass |
+| III. Consistent Error Shape | One envelope `{"error": {"code", "message", "details"}}` for validation (422) and not found (404), installed as global exception handlers; a duplicate save is not an error (200 with the existing bookmark, FR-004), so there is no 409 | Pass |
 | IV. Minimal Dependencies | Six runtime/test dependencies, each justified in research.md; standard library used for link normalization and config | Pass |
 | V. Tests Ship With Every Feature | Each user story's tasks include tests for its acceptance scenarios; suite must pass before converge | Pass |
 | VI. Cursor Pagination | `GET /bookmarks` uses keyset paging on `(created_at, id)` with an opaque `next_cursor`; no offset in the API or queries; a test pages through all results while bookmarks are added between requests | Pass |
@@ -91,7 +92,7 @@ src/bookmarks_api/
 ├── schemas.py           # Pydantic request/response models
 ├── normalize.py         # link and tag normalization (pure functions)
 ├── errors.py            # error envelope, domain exceptions and handlers
-├── repository.py        # queries: create, list/filter with total, delete
+├── repository.py        # queries: create (or return existing), list/filter with total, delete
 └── routes.py            # /bookmarks endpoints
 
 tests/
diff --git a/specs/001-bookmarks-api/quickstart.md b/specs/001-bookmarks-api/quickstart.md
index 6605e43..81e7b4a 100644
--- a/specs/001-bookmarks-api/quickstart.md
+++ b/specs/001-bookmarks-api/quickstart.md
@@ -36,7 +36,7 @@ http://127.0.0.1:8000/docs, or use curl:
 | Step | Request | Expected |
 | --- | --- | --- |
 | 1 | `POST /bookmarks` `{"url": "https://fastapi.tiangolo.com/", "title": "FastAPI docs", "tags": ["Python", "api"]}` | 201, tags `["api", "python"]` |
-| 2 | `POST /bookmarks` `{"url": "HTTPS://FastAPI.tiangolo.com", "title": "Again"}` | 409 `duplicate_url`, `details.existing_id` = id from step 1 |
+| 2 | `POST /bookmarks` `{"url": "HTTPS://FastAPI.tiangolo.com", "title": "Again"}` | 200, the step 1 bookmark unchanged (same `id`, title "FastAPI docs", tags `["api", "python"]`) |
 | 3 | `GET /bookmarks` | 200, the step 1 bookmark first, `total` 1 |
 | 4 | `GET /bookmarks?tag=PYTHON` | 200, the step 1 bookmark |
 | 5 | `GET /bookmarks?limit=500` | 422 `validation_error` |
diff --git a/specs/001-bookmarks-api/research.md b/specs/001-bookmarks-api/research.md
index 5ae30cd..1b473cc 100644
--- a/specs/001-bookmarks-api/research.md
+++ b/specs/001-bookmarks-api/research.md
@@ -35,13 +35,22 @@ considered.
 
 ## Preventing duplicate links
 
-- **Decision**: Store the link as given (`url`) and a normalized form (`url_normalized`) with a
-  unique index. Insert with `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING ...`; if
-  nothing is returned, look up the existing row and raise a duplicate error carrying its id.
-- **Rationale**: The database guarantees uniqueness even when two saves race (spec edge case);
-  `ON CONFLICT` avoids relying on catching exceptions mid-transaction.
+- **Decision** (revised 2026-10-24, flow-back; FR-004): Store the link as given (`url`) and a
+  normalized form (`url_normalized`) with a unique index. Insert with
+  `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING ...`; a returned row means the link
+  was new (201 Created). If nothing is returned, select the existing row by `url_normalized` and
+  return it unchanged (200 OK); the request's title and tags are ignored. If that select finds
+  nothing (the conflicting row was deleted in between), retry the insert.
+- **Rationale**: The database guarantees uniqueness even when two saves race (spec edge case): the
+  loser of the race gets no row back and returns the winner's row, so one save gets 201 and the
+  other 200 with the same bookmark. `ON CONFLICT DO NOTHING` never writes to the existing row, so
+  the stored bookmark is not modified, and avoids catching exceptions mid-transaction.
 - **Alternatives considered**: check-then-insert in application code (races under concurrency);
-  catching `IntegrityError` (works, but leaves the transaction aborted and is noisier).
+  catching `IntegrityError` (works, but leaves the transaction aborted and is noisier);
+  `ON CONFLICT DO UPDATE SET url_normalized = EXCLUDED.url_normalized RETURNING ...` (returns the
+  row in one statement, but writes a new row version of a bookmark that must not be modified and
+  cannot tell 201 from 200 without extra tricks); rejecting with 409 `duplicate_url` (the original
+  decision, replaced by the revised FR-004).
 
 ## Link normalization
 
@@ -84,7 +93,8 @@ considered.
 ## Error envelope
 
 - **Decision**: `{"error": {"code": str, "message": str, "details": object | null}}`. Codes:
-  `validation_error` (422), `not_found` (404), `duplicate_url` (409, `details.existing_id`).
+  `validation_error` (422), `not_found` (404). A save of an already-saved link is not an error
+  (200 with the existing bookmark, FR-004), so there is no `duplicate_url` code.
   FastAPI's `RequestValidationError` and `HTTPException` handlers are replaced so framework errors
   use the same shape; unexpected errors return 500 `internal_error` without internals.
 - **Rationale**: Constitution III.
diff --git a/specs/001-bookmarks-api/spec.md b/specs/001-bookmarks-api/spec.md
index 3ed7b96..9da5925 100644
--- a/specs/001-bookmarks-api/spec.md
+++ b/specs/001-bookmarks-api/spec.md
@@ -12,7 +12,7 @@
 
 ### Session 2026-10-21
 
-- Q: When someone saves a link that is already bookmarked, what should happen? → A: Reject it with a conflict error that includes the existing bookmark's identifier; the existing bookmark is left unchanged.
+- Q: When someone saves a link that is already bookmarked, what should happen? → A: Reject it with a conflict error that includes the existing bookmark's identifier; the existing bookmark is left unchanged. *(Superseded 2026-10-24; see the flow-back session below.)*
 - Q: Which links count as "the same link"? → A: Links that match after normalization: scheme and host lowercased, default port removed, trailing slash on the path removed, fragment (#...) removed; the query string is kept as is.
 - Q: How should tags be cleaned up and limited? → A: Trim spaces, lowercase, drop duplicates; 1 to 30 characters of letters, digits and hyphens; at most 10 tags per bookmark.
 - Q: How should the list behave when there are many bookmarks? → A: Return pages: 20 per page by default, up to 100 per page, using a limit and an offset, plus the total count.
@@ -22,6 +22,10 @@
 
 - Q: Principle VI forbids offset pagination. How does a client ask for the next page? → A: Each page returns an opaque next-page token (none on the last page); the client passes it back to get the next page. The offset option is removed, and a request that still sends it gets a validation error that points to the token.
 
+### Session 2026-10-24 (flow-back: duplicate saves)
+
+- Q: When someone saves a link that is already bookmarked, what should happen? → A: It is no longer rejected. The existing bookmark is returned unchanged with HTTP 200 OK instead of the 409 conflict; the title and tags sent in the new request are ignored and the stored bookmark is not modified. Saving a new link still returns 201 Created. Two concurrent saves of the same new link still store only one bookmark: one gets 201, the other gets 200 with the same bookmark. This replaces the earlier duplicate answer and the duplicate rule in FR-004.
+
 ## User Scenarios & Testing *(mandatory)*
 
 ### User Story 1 - Save a bookmark (Priority: P1)
@@ -42,8 +46,9 @@ contains the saved link, title, tags and the time it was saved.
 2. **Given** no bookmarks exist, **When** the user saves a link with a title and the tags "Python",
    " api " and "python", **Then** the bookmark is returned with the tags "api" and "python".
 3. **Given** a bookmark for `https://example.com/docs` exists, **When** the user saves
-   `HTTPS://Example.com/docs/#intro`, **Then** no second bookmark is created and the user receives
-   a conflict error that includes the existing bookmark's identifier.
+   `HTTPS://Example.com/docs/#intro` with a different title and tags, **Then** no second bookmark is
+   created, the existing bookmark is not modified, and the user receives the existing bookmark
+   unchanged with 200 OK (a new link returns 201 Created).
 4. **Given** any state, **When** the user tries to save a bookmark without a link or without a
    title, with a link that is not a valid http or https address, with a title over 200 characters,
    with more than 10 tags, or with an invalid tag, **Then** nothing is saved and the user receives
@@ -122,9 +127,9 @@ appears in the list.
 
 ### Edge Cases
 
-- Saving a link that is already bookmarked, even with a different title or tags, is rejected with
-  a conflict error that includes the existing bookmark's identifier; the existing bookmark is not
-  changed.
+- Saving a link that is already bookmarked, even with a different title or tags, is not an error:
+  the existing bookmark is returned unchanged with 200 OK; the title and tags in the new request are
+  ignored and the stored bookmark is not changed.
 - Links that differ only in scheme or host letter case, a default port (`:80` for http, `:443`
   for https), a trailing slash on the path, or a fragment are the same link. Links with different
   query strings are different links.
@@ -132,7 +137,8 @@ appears in the list.
   kept once.
 - A tag that is empty after trimming, longer than 30 characters, or contains characters other
   than letters, digits and hyphens is rejected.
-- Two saves of the same link at the same moment still leave exactly one bookmark.
+- Two saves of the same new link at the same moment still leave exactly one bookmark: one save gets
+  201 Created and the other gets 200 OK with that same bookmark.
 - A malformed next-page token (one that does not decode to a position in the list) is rejected with
   a validation error.
 - A request that sends the removed offset option is rejected with a validation error that names the
@@ -151,11 +157,13 @@ appears in the list.
 - **FR-003**: System MUST record the time each bookmark was saved.
 - **FR-004**: System MUST NOT store two bookmarks for the same link, where links are compared after
   normalization (scheme and host lowercased, default port removed, trailing path slash removed,
-  fragment removed, query kept). A save of an existing link MUST be rejected with a conflict error
-  that includes the existing bookmark's identifier, and MUST hold even when two saves happen at
-  the same moment.
-- **FR-005**: System MUST return the saved bookmark, including an identifier the user can use to
-  delete it.
+  fragment removed, query kept). A save of a link that is already saved MUST NOT be rejected: it
+  MUST return the existing bookmark unchanged with HTTP 200 OK, ignoring the title and tags in the
+  request and leaving the stored bookmark unmodified. A save of a new link MUST return 201 Created.
+  This MUST hold even when two saves of the same new link happen at the same moment: only one
+  bookmark is stored, one save gets 201 and the other gets 200 with the same bookmark.
+- **FR-005**: System MUST return the saved bookmark (or, for an already-saved link, the existing
+  bookmark), including an identifier the user can use to delete it.
 - **FR-006**: System MUST list bookmarks ordered by saved time, most recent first, in pages of 20
   by default and at most 100, and MUST include the total number of matching bookmarks. Each page
   MUST return an opaque next-page token (none on the last page), and paging with it MUST NOT repeat
diff --git a/specs/001-bookmarks-api/tasks.md b/specs/001-bookmarks-api/tasks.md
index eca6021..4a8cfda 100644
--- a/specs/001-bookmarks-api/tasks.md
+++ b/specs/001-bookmarks-api/tasks.md
@@ -51,10 +51,15 @@ its own.
 
 ## Phase 3: User Story 1 - Save a bookmark (Priority: P1) 🎯 MVP
 
-**Goal**: A user can save a link with a title and optional tags; duplicates are rejected.
+**Goal**: A user can save a link with a title and optional tags; saving a link that is already
+saved returns the existing bookmark instead of creating a duplicate.
 
 **Independent Test**: `POST /bookmarks` returns 201 with the saved bookmark; saving an equivalent
-link returns 409 with `details.existing_id`.
+link returns 200 with the existing bookmark, unchanged.
+
+> Note (flow-back 2026-10-24): T008, T012, T015, T016 and T026 built and tested the original
+> duplicate rule (409 `duplicate_url` with `details.existing_id`), which FR-004 no longer specifies.
+> The replacement work is recorded in Phase 10; these tasks are kept as history.
 
 ### Tests for User Story 1
 
@@ -208,3 +213,19 @@ Task: "BookmarkCreate / Bookmark in src/bookmarks_api/schemas.py"
 - [X] T034 Return 422 `validation_error` for a malformed `cursor` and for any request that sends `offset`, with a message that names `cursor`, per spec Edge Cases (missing)
 - [X] T035 Rewrite the paging tests in `tests/integration/test_list_bookmarks.py` and `tests/integration/test_filter_by_tag.py` for cursors, and add a test that pages through all results while bookmarks are saved between requests and finds no duplicates and no gaps, per US2/AC3-AC5 and the Constitution VI quality gate (missing)
 - [X] T036 Update the `GET /bookmarks` row in `README.md` to document `cursor` and `next_cursor` instead of `offset`, per contracts/openapi.yaml (partial)
+
+## Phase 10: Flow-back - duplicate saves return the existing bookmark (2026-10-24)
+
+**Discovery**: Rejecting a save of an already-saved link with 409 forced clients to treat a
+harmless repeat save as an error. FR-004 now says a save of an existing link (after normalization)
+returns the existing bookmark unchanged with 200 OK; the title and tags in the new request are
+ignored; a new link still returns 201 Created; concurrent saves of the same new link still store one
+bookmark (one 201, the other 200 with the same bookmark). This changes behavior (spec), the duplicate
+strategy (research, plan) and the contract; the change was made in code first and flowed back here.
+
+- [X] T037 [US1] Change `create_bookmark(session, data)` in `src/bookmarks_api/repository.py` to return `(row, created)`: keep `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`; when nothing is inserted, select and return the existing row with `created=False`, without modifying it; if that row was deleted between the insert and the select, retry the insert (FR-004, research.md "Preventing duplicate links")
+- [X] T038 [US1] Make `POST /bookmarks` in `src/bookmarks_api/routes.py` return 201 with `Bookmark` for a new link and 200 with the existing `Bookmark` otherwise; declare 201, 200 and 422 in OpenAPI and no 409, per contracts/openapi.yaml
+- [X] T039 [P] Remove `DuplicateUrlError` and its 409 `duplicate_url` handler from `src/bookmarks_api/errors.py` (no longer raised), per research.md "Error envelope"
+- [X] T040 [P] [US1] Update `tests/integration/test_create_bookmark.py` for User Story 1 scenario 3 and the concurrency edge case: an equivalent link sent with a different title and tags → 200 with a body equal to the first save, stored url, title and tags unchanged, still one row; two concurrent saves of equivalent links → one 201 and one 200 with the same body, one row (FR-004)
+- [X] T041 [P] Update `tests/integration/test_errors.py`: drop the 409 envelope test and assert `/openapi.json` documents `POST /bookmarks` with 201 and 200 `Bookmark` responses, 422 `ErrorResponse`, and no 409 (SC-005, Constitution I)
+- [X] T042 [P] Update the `POST /bookmarks` row in `README.md` and step 2 of `specs/001-bookmarks-api/quickstart.md` to describe 200 with the existing bookmark instead of 409
```

## Command: tests (no code changed in this step)

```
$ set -a; . ./.env; set +a; uv run --python 3.13 pytest -q
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
........................................................................ [ 74%]
.........................                                                [100%]
97 passed in 2.93s
```

Step end: 2026-10-24T11:45:03Z
