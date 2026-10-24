# Step 02: plan (Spec Kit plan command, existing feature)

Start: 2026-10-24T11:42:50Z

## Commands and output

```
$ cat .claude/skills/speckit-plan/SKILL.md   # read and followed
$ ls .specify/extensions.yml
ls: cannot access '.specify/extensions.yml': No such file or directory
$ export SPECIFY_FEATURE_DIRECTORY=specs/001-bookmarks-api && .specify/scripts/bash/setup-plan.sh --json
Plan already exists at /home/claude/runs/living-r1/specs/001-bookmarks-api/plan.md, skipping template copy
{"FEATURE_SPEC":"/home/claude/runs/living-r1/specs/001-bookmarks-api/spec.md","IMPL_PLAN":"/home/claude/runs/living-r1/specs/001-bookmarks-api/plan.md","FEATURE_DIR":"/home/claude/runs/living-r1/specs/001-bookmarks-api","BRANCH":"001-bookmarks-api"}
exit=0
```

Arguments passed to the command: the change request (verbatim from the brief).

Pre-execution hooks: `.specify/extensions.yml` does not exist, skipped silently.

Setup note: the script found the existing plan.md and skipped the template copy, so the plan
workflow revised the existing plan.md in place (keeping the rationale recorded in 01-spec.md) rather
than refilling an empty template.

Load context: read spec.md (as edited in step 1), .specify/memory/constitution.md, plan.md, research.md,
data-model.md, contracts/openapi.yaml, quickstart.md, and the current code (repository.py, routes.py,
errors.py, schemas.py) and tests (test_create_bookmark.py, test_errors.py) for Technical Context.

Technical Context: unchanged; no NEEDS CLARIFICATION.
Constitution Check (gate before Phase 0): all six principles Pass; row III reworded (no 409 produced any more).
Phase 0: research.md "Preventing duplicate links" decision revised (201 new / 200 existing; READ COMMITTED
reasoning for the concurrent case; delete-between-statements retry; DO UPDATE ... xmax=0 alternative rejected;
history of the 409 decision kept). Error envelope decision: duplicate_url removed.
Phase 1: data-model.md lifecycle note added; contracts/openapi.yaml POST gains a 200 response and a description,
409 removed, duplicate_url removed from the error code enum and existing_id from the details description;
quickstart.md manual step 2 now expects 200 with the unchanged step 1 bookmark.
Post-design Constitution re-check: Pass (recorded in plan.md).

Attempt log for the edits: the first scripted edit attempt aborted on an assertion before writing any file
(the plan's source tree uses "└── routes.py", not "├── routes.py"); `git status --short` showed no changes; the
corrected script then applied all edits. A first draft of the contract enum also replaced duplicate_url with
method_not_allowed; reverted to just removing duplicate_url to keep the change scoped.

Post-execution hooks: none registered (no extensions.yml).

```
$ python3 -c "import yaml; yaml.safe_load(open(\"specs/001-bookmarks-api/contracts/openapi.yaml\")); print(\"yaml ok\")"
yaml ok
```

## Completion report

- Branch: 001-bookmarks-api (git branch claude/ep03-living-r1)
- IMPL_PLAN: specs/001-bookmarks-api/plan.md (revised)
- Artifacts regenerated/revised: research.md, data-model.md, contracts/openapi.yaml, quickstart.md
- Gates: Constitution Check Pass before and after design; no NEEDS CLARIFICATION.

```diff
$ git diff
diff --git a/specs/001-bookmarks-api/contracts/openapi.yaml b/specs/001-bookmarks-api/contracts/openapi.yaml
index ccb008e..46f2ed8 100644
--- a/specs/001-bookmarks-api/contracts/openapi.yaml
+++ b/specs/001-bookmarks-api/contracts/openapi.yaml
@@ -11,22 +11,26 @@ paths:
     post:
       summary: Save a bookmark
       operationId: createBookmark
+      description: >
+        Saves a new link and returns 201. If the link, after normalization, is already bookmarked,
+        nothing is stored or changed: the existing bookmark is returned unchanged with 200, and the
+        title and tags in the request are ignored.
       requestBody:
         required: true
         content:
           application/json:
             schema: { $ref: '#/components/schemas/BookmarkCreate' }
       responses:
-        '201':
-          description: Bookmark saved
+        '200':
+          description: The normalized link is already bookmarked; the existing bookmark is returned unchanged
           content:
             application/json:
               schema: { $ref: '#/components/schemas/Bookmark' }
-        '409':
-          description: The normalized link is already bookmarked; details.existing_id names it
+        '201':
+          description: Bookmark saved
           content:
             application/json:
-              schema: { $ref: '#/components/schemas/ErrorResponse' }
+              schema: { $ref: '#/components/schemas/Bookmark' }
         '422':
           description: Invalid link, title or tags
           content:
@@ -126,8 +130,8 @@ components:
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
index 7f7c730..f484473 100644
--- a/specs/001-bookmarks-api/data-model.md
+++ b/specs/001-bookmarks-api/data-model.md
@@ -55,5 +55,8 @@ Examples: `HTTPS://Example.com:443/docs/#intro` → `https://example.com/docs`;
 ## Lifecycle
 
 A bookmark is created by a save and removed by a delete; there is no update in this version.
+Saving a link whose normalized form is already stored does not create or change anything: the
+existing row is returned as it is (FR-004), so its title, tags and `created_at` never change after
+the first save.
 Deleting a bookmark frees its normalized link, so the same link can be saved again (User Story 4,
 scenario 3).
diff --git a/specs/001-bookmarks-api/plan.md b/specs/001-bookmarks-api/plan.md
index 4806bc5..7e3b1dd 100644
--- a/specs/001-bookmarks-api/plan.md
+++ b/specs/001-bookmarks-api/plan.md
@@ -1,6 +1,6 @@
 # Implementation Plan: Bookmarks API
 
-**Branch**: `001-bookmarks-api` | **Date**: 2026-10-21 | **Spec**: [spec.md](spec.md)
+**Branch**: `001-bookmarks-api` | **Date**: 2026-10-21 (revised 2026-10-24: duplicate saves) | **Spec**: [spec.md](spec.md)
 
 **Input**: Feature specification from `/specs/001-bookmarks-api/spec.md`
 
@@ -13,7 +13,15 @@ with no duplicate links after normalization. Built as a FastAPI service with Pyd
 response models, PostgreSQL storage through SQLAlchemy 2.0 (sync, psycopg 3), and Alembic
 migrations. Uniqueness is enforced by a unique index on the normalized link, so it holds under
 concurrent saves; tags are a normalized `text[]` column with a GIN index for filtering. All errors
-use one JSON envelope. Tests run with pytest against the real `bookmarks_test` database from the
+use one JSON envelope.
+
+Saving a link that is already bookmarked is not an error (spec FR-004, change of 2026-10-24):
+`POST /bookmarks` returns 201 Created with the new bookmark when it inserts a row, and 200 OK with
+the existing bookmark, unchanged, when the normalized link is already stored; the request's title
+and tags are ignored in that case. The insert still uses `ON CONFLICT (url_normalized) DO NOTHING`,
+so two concurrent saves of the same new link store one row: one caller gets 201, the other reads
+the winner's row and gets 200 with the same bookmark (research.md, "Preventing duplicate links").
+The 409 `duplicate_url` response is removed from the contract and the code. Tests run with pytest against the real `bookmarks_test` database from the
 existing `docker-compose.yml`.
 
 ## Technical Context
@@ -49,7 +57,7 @@ under a second for 100k bookmarks (indexed queries)
 | --- | --- | --- |
 | I. Typed API Contracts | Pydantic models for the create request, bookmark, page and error responses; FastAPI generates OpenAPI from them; no untyped dicts cross the boundary | Pass |
 | II. Real-Database Testing | Integration tests hit `bookmarks_test` on real PostgreSQL; schema created by running the Alembic migrations; tables truncated before each test; no database mocks | Pass |
-| III. Consistent Error Shape | One envelope `{"error": {"code", "message", "details"}}` for validation (422), not found (404) and duplicate (409), installed as global exception handlers | Pass |
+| III. Consistent Error Shape | One envelope `{"error": {"code", "message", "details"}}` for validation (422), not found (404) and other HTTP errors, installed as global exception handlers. A repeat save is now a success (200 with the existing bookmark), so the endpoints no longer produce a 409; the principle's status mapping still holds for every error that remains | Pass |
 | IV. Minimal Dependencies | Six runtime/test dependencies, each justified in research.md; standard library used for link normalization and config | Pass |
 | V. Tests Ship With Every Feature | Each user story's tasks include tests for its acceptance scenarios; suite must pass before converge | Pass |
 | VI. Cursor Pagination | `GET /bookmarks` uses keyset paging on `(created_at, id)` with an opaque `next_cursor`; no offset in the API or queries; a test pages through all results while bookmarks are added between requests | Pass |
@@ -57,6 +65,12 @@ under a second for 100k bookmarks (indexed queries)
 Post-design re-check (after Phase 1): Pass. The data model, contract and quickstart introduce no
 new dependencies or untyped interfaces.
 
+Re-check for the duplicate-save change (2026-10-24): Pass. No new dependency (IV); the 200 response
+reuses the typed `Bookmark` model and is declared in the contract and the generated OpenAPI (I);
+the remaining errors keep the envelope (III); the repeat-save and concurrent-save behavior is
+verified against the real test database (II, V); paging is untouched (VI). No schema migration is
+needed: the unique index on `url_normalized` already provides the guarantee.
+
 ## Project Structure
 
 ### Documentation (this feature)
@@ -90,9 +104,9 @@ src/bookmarks_api/
 ├── models.py            # SQLAlchemy table mapping
 ├── schemas.py           # Pydantic request/response models
 ├── normalize.py         # link and tag normalization (pure functions)
-├── errors.py            # error envelope, domain exceptions and handlers
-├── repository.py        # queries: create, list/filter with total, delete
-└── routes.py            # /bookmarks endpoints
+├── errors.py            # error envelope, domain exceptions (not found) and handlers
+├── repository.py        # queries: create-or-get-existing, list/filter with total, delete
+└── routes.py            # /bookmarks endpoints (POST: 201 new, 200 existing)
 
 tests/
 ├── conftest.py          # test database setup (migrations, truncate per test), API client
diff --git a/specs/001-bookmarks-api/quickstart.md b/specs/001-bookmarks-api/quickstart.md
index 6605e43..66c38ff 100644
--- a/specs/001-bookmarks-api/quickstart.md
+++ b/specs/001-bookmarks-api/quickstart.md
@@ -36,7 +36,7 @@ http://127.0.0.1:8000/docs, or use curl:
 | Step | Request | Expected |
 | --- | --- | --- |
 | 1 | `POST /bookmarks` `{"url": "https://fastapi.tiangolo.com/", "title": "FastAPI docs", "tags": ["Python", "api"]}` | 201, tags `["api", "python"]` |
-| 2 | `POST /bookmarks` `{"url": "HTTPS://FastAPI.tiangolo.com", "title": "Again"}` | 409 `duplicate_url`, `details.existing_id` = id from step 1 |
+| 2 | `POST /bookmarks` `{"url": "HTTPS://FastAPI.tiangolo.com", "title": "Again", "tags": ["other"]}` | 200, the step 1 bookmark unchanged: same `id`, title `FastAPI docs`, tags `["api", "python"]` |
 | 3 | `GET /bookmarks` | 200, the step 1 bookmark first, `total` 1 |
 | 4 | `GET /bookmarks?tag=PYTHON` | 200, the step 1 bookmark |
 | 5 | `GET /bookmarks?limit=500` | 422 `validation_error` |
diff --git a/specs/001-bookmarks-api/research.md b/specs/001-bookmarks-api/research.md
index 5ae30cd..56803a2 100644
--- a/specs/001-bookmarks-api/research.md
+++ b/specs/001-bookmarks-api/research.md
@@ -35,13 +35,32 @@ considered.
 
 ## Preventing duplicate links
 
-- **Decision**: Store the link as given (`url`) and a normalized form (`url_normalized`) with a
-  unique index. Insert with `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING ...`; if
-  nothing is returned, look up the existing row and raise a duplicate error carrying its id.
+- **Decision** (revised 2026-10-24 for the duplicate-save change in FR-004): Store the link as
+  given (`url`) and a normalized form (`url_normalized`) with a unique index. Insert with
+  `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING ...`. If a row is returned, it is a
+  new bookmark: commit and respond 201 Created. If nothing is returned, the link is already saved:
+  end the transaction, select the existing row by `url_normalized` in a new statement and return it
+  unchanged with 200 OK; the request's title and tags are discarded. If that select finds nothing
+  (the existing bookmark was deleted between the two statements), retry the insert once; the retry
+  either inserts (201) or finds the row (200).
 - **Rationale**: The database guarantees uniqueness even when two saves race (spec edge case);
-  `ON CONFLICT` avoids relying on catching exceptions mid-transaction.
+  `ON CONFLICT` avoids relying on catching exceptions mid-transaction. Under PostgreSQL's default
+  READ COMMITTED isolation, an `ON CONFLICT DO NOTHING` insert that hits a row being inserted by a
+  concurrent, uncommitted transaction waits for that transaction to finish; once the winner
+  commits, the loser's follow-up select (a new statement, so a new snapshot) sees the winner's row.
+  So two concurrent saves of a new link give exactly one row, one 201 and one 200 carrying the same
+  bookmark. The stored row is never written on a repeat save, so its title, tags and saved time
+  stay as they were.
 - **Alternatives considered**: check-then-insert in application code (races under concurrency);
-  catching `IntegrityError` (works, but leaves the transaction aborted and is noisier).
+  catching `IntegrityError` (works, but leaves the transaction aborted and is noisier);
+  `ON CONFLICT DO UPDATE SET url_normalized = EXCLUDED.url_normalized RETURNING *, (xmax = 0)` to
+  get the row and the inserted flag in one statement (rejected: it rewrites the existing row on
+  every repeat save, taking a row lock and leaving a dead tuple even though no value changes, and
+  `xmax = 0` relies on an undocumented system column); a dedicated "get or create" endpoint
+  (rejected: the change request keeps `POST /bookmarks`).
+- **History**: The original decision (2026-10-21) raised a duplicate error carrying the existing
+  id, returned as 409 `duplicate_url` with `details.existing_id`. The 2026-10-24 change replaces
+  that with 200 and the existing bookmark.
 
 ## Link normalization
 
@@ -84,7 +103,8 @@ considered.
 ## Error envelope
 
 - **Decision**: `{"error": {"code": str, "message": str, "details": object | null}}`. Codes:
-  `validation_error` (422), `not_found` (404), `duplicate_url` (409, `details.existing_id`).
+  `validation_error` (422), `not_found` (404). (`duplicate_url` (409, `details.existing_id`) was
+  removed on 2026-10-24: a repeat save now succeeds with 200; see "Preventing duplicate links".)
   FastAPI's `RequestValidationError` and `HTTPException` handlers are replaced so framework errors
   use the same shape; unexpected errors return 500 `internal_error` without internals.
 - **Rationale**: Constitution III.
```

End: 2026-10-24T11:45:05Z
