# Step 02 — plan (Spec Kit plan command, existing feature)

Start: 2026-10-24T11:59:22Z

Arguments passed to the command: the change request verbatim (see coordinator brief).

```console
$ test -f .specify/extensions.yml && cat .specify/extensions.yml || echo 'no .specify/extensions.yml (pre-plan hooks skipped)'
no .specify/extensions.yml (pre-plan hooks skipped)
[exit 0]
```

```console
$ .specify/scripts/bash/setup-plan.sh --json
Plan already exists at /home/claude/runs/living-r2/specs/001-bookmarks-api/plan.md, skipping template copy
{"FEATURE_SPEC":"/home/claude/runs/living-r2/specs/001-bookmarks-api/spec.md","IMPL_PLAN":"/home/claude/runs/living-r2/specs/001-bookmarks-api/plan.md","FEATURE_DIR":"/home/claude/runs/living-r2/specs/001-bookmarks-api","BRANCH":"001-bookmarks-api"}
[exit 0]
```

```console
$ uv run --python 3.13 python -c "import yaml,sys; d=yaml.safe_load(open('specs/001-bookmarks-api/contracts/openapi.yaml')); print(sorted(d['paths']['/bookmarks']['post']['responses']))" 2>&1 || python3 -c "import yaml; d=yaml.safe_load(open('specs/001-bookmarks-api/contracts/openapi.yaml')); print(sorted(d['paths']['/bookmarks']['post']['responses']))"
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
Using CPython 3.13.17 interpreter at: /usr/local/bin/python3.13
Creating virtual environment at: .venv
   Building bookmarks-api @ file:///home/claude/runs/living-r2
      Built bookmarks-api @ file:///home/claude/runs/living-r2
Installed 29 packages in 17ms
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import yaml,sys; d=yaml.safe_load(open('specs/001-bookmarks-api/contracts/openapi.yaml')); print(sorted(d['paths']['/bookmarks']['post']['responses']))
    ^^^^^^^^^^^^^^^
ModuleNotFoundError: No module named 'yaml'
['200', '201', '422']
[exit 0]
```

```console
$ git diff -- specs/
diff --git a/specs/001-bookmarks-api/contracts/openapi.yaml b/specs/001-bookmarks-api/contracts/openapi.yaml
index ccb008e..b4e8451 100644
--- a/specs/001-bookmarks-api/contracts/openapi.yaml
+++ b/specs/001-bookmarks-api/contracts/openapi.yaml
@@ -1,7 +1,7 @@
 openapi: 3.1.0
 info:
   title: Bookmarks API
-  version: 0.1.0
+  version: 0.2.0
   description: >
     Save, list, filter and delete bookmarks. Single user, no authentication.
     The running service generates its own OpenAPI document at /openapi.json from the
@@ -9,24 +9,30 @@ info:
 paths:
   /bookmarks:
     post:
-      summary: Save a bookmark
+      summary: Save a bookmark, or return the existing one for an already saved link
       operationId: createBookmark
+      description: >
+        Idempotent per normalized link (FR-004). A new link is stored and returned with 201.
+        If the normalized link is already saved, the existing bookmark is returned unchanged
+        with 200; the title and tags in the request are ignored and nothing is modified. Two
+        concurrent saves of the same new link store one bookmark: one gets 201, the other 200
+        with the same bookmark.
       requestBody:
         required: true
         content:
           application/json:
             schema: { $ref: '#/components/schemas/BookmarkCreate' }
       responses:
-        '201':
-          description: Bookmark saved
+        '200':
+          description: The normalized link was already saved; the existing bookmark, unchanged
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
@@ -126,8 +132,8 @@ components:
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
index 7f7c730..b4b305d 100644
--- a/specs/001-bookmarks-api/data-model.md
+++ b/specs/001-bookmarks-api/data-model.md
@@ -10,7 +10,7 @@ bookmark's "link" is the `url` field in the API and the database.
 | --- | --- | --- | --- |
 | `id` | `bigint` | primary key, generated always as identity | Identifier returned to the user and used for delete |
 | `url` | `varchar(2048)` | not null | The link exactly as the user gave it |
-| `url_normalized` | `varchar(2048)` | not null, **unique** | Normalized link used for duplicate detection (FR-004) |
+| `url_normalized` | `varchar(2048)` | not null, **unique** | Normalized link used for duplicate detection; a save whose normalized link exists returns the existing row (FR-004) |
 | `title` | `varchar(200)` | not null, `char_length(title) >= 1` | Trimmed before saving |
 | `tags` | `text[]` | not null, default `'{}'`, `cardinality(tags) <= 10` | Normalized, de-duplicated, sorted |
 | `created_at` | `timestamptz` | not null, default `now()` | The saved time (FR-003) |
@@ -55,5 +55,8 @@ Examples: `HTTPS://Example.com:443/docs/#intro` → `https://example.com/docs`;
 ## Lifecycle
 
 A bookmark is created by a save and removed by a delete; there is no update in this version.
+Saving a link whose normalized form already exists does not create or change a row: the existing
+row is returned as it is, with 200 OK instead of 201 Created, and the request's title and tags are
+ignored (FR-004, revised 2026-10-24). No schema change is needed for this rule.
 Deleting a bookmark frees its normalized link, so the same link can be saved again (User Story 4,
 scenario 3).
diff --git a/specs/001-bookmarks-api/plan.md b/specs/001-bookmarks-api/plan.md
index 4806bc5..7703d1f 100644
--- a/specs/001-bookmarks-api/plan.md
+++ b/specs/001-bookmarks-api/plan.md
@@ -1,6 +1,6 @@
 # Implementation Plan: Bookmarks API
 
-**Branch**: `001-bookmarks-api` | **Date**: 2026-10-21 | **Spec**: [spec.md](spec.md)
+**Branch**: `001-bookmarks-api` | **Date**: 2026-10-21 (revised 2026-10-24: duplicate saves return the existing bookmark) | **Spec**: [spec.md](spec.md)
 
 **Input**: Feature specification from `/specs/001-bookmarks-api/spec.md`
 
@@ -13,7 +13,16 @@ with no duplicate links after normalization. Built as a FastAPI service with Pyd
 response models, PostgreSQL storage through SQLAlchemy 2.0 (sync, psycopg 3), and Alembic
 migrations. Uniqueness is enforced by a unique index on the normalized link, so it holds under
 concurrent saves; tags are a normalized `text[]` column with a GIN index for filtering. All errors
-use one JSON envelope. Tests run with pytest against the real `bookmarks_test` database from the
+use one JSON envelope.
+
+Saving is idempotent per normalized link (FR-004, revised 2026-10-24): `POST /bookmarks` returns
+201 Created with the new bookmark when the link is new, and 200 OK with the existing bookmark,
+unchanged, when the normalized link is already saved (the request's title and tags are ignored).
+The same `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING` statement decides which:
+a returned row means 201; no row means the link exists, so the existing row is read and returned
+with 200. The unique index still guarantees one row when two saves of the same new link race; the
+loser of the race gets 200 with the winner's bookmark. Duplicates are no longer an error, so the
+409 `duplicate_url` response is removed. No schema change or migration is needed. Tests run with pytest against the real `bookmarks_test` database from the
 existing `docker-compose.yml`.
 
 ## Technical Context
@@ -47,16 +56,20 @@ under a second for 100k bookmarks (indexed queries)
 
 | Principle | How the plan complies | Status |
 | --- | --- | --- |
-| I. Typed API Contracts | Pydantic models for the create request, bookmark, page and error responses; FastAPI generates OpenAPI from them; no untyped dicts cross the boundary | Pass |
+| I. Typed API Contracts | Pydantic models for the create request, bookmark, page and error responses; FastAPI generates OpenAPI from them; no untyped dicts cross the boundary. `POST /bookmarks` declares both 201 and 200 with the same `Bookmark` model | Pass |
 | II. Real-Database Testing | Integration tests hit `bookmarks_test` on real PostgreSQL; schema created by running the Alembic migrations; tables truncated before each test; no database mocks | Pass |
-| III. Consistent Error Shape | One envelope `{"error": {"code", "message", "details"}}` for validation (422), not found (404) and duplicate (409), installed as global exception handlers | Pass |
+| III. Consistent Error Shape | One envelope `{"error": {"code", "message", "details"}}` for validation (422), not found (404) and unexpected (500), installed as global exception handlers. A duplicate save is no longer an error (revised FR-004: 200 with the existing bookmark), so the 409 `duplicate_url` error is removed; the generic 409 mapping for framework `HTTPException`s stays in the envelope | Pass |
 | IV. Minimal Dependencies | Six runtime/test dependencies, each justified in research.md; standard library used for link normalization and config | Pass |
-| V. Tests Ship With Every Feature | Each user story's tasks include tests for its acceptance scenarios; suite must pass before converge | Pass |
+| V. Tests Ship With Every Feature | Each user story's tasks include tests for its acceptance scenarios; suite must pass before converge. The revised US1 scenario 3 and the concurrent-save edge case (one 201, one 200, same bookmark, one row) get tests in the same change as the behavior | Pass |
 | VI. Cursor Pagination | `GET /bookmarks` uses keyset paging on `(created_at, id)` with an opaque `next_cursor`; no offset in the API or queries; a test pages through all results while bookmarks are added between requests | Pass |
 
 Post-design re-check (after Phase 1): Pass. The data model, contract and quickstart introduce no
 new dependencies or untyped interfaces.
 
+Post-design re-check (2026-10-24 revision): Pass. The revised duplicate rule changes only the
+save endpoint's success responses (201 or 200) and removes the 409 error; it adds no dependency,
+no table or index, and no untyped interface.
+
 ## Project Structure
 
 ### Documentation (this feature)
@@ -90,14 +103,16 @@ src/bookmarks_api/
 ├── models.py            # SQLAlchemy table mapping
 ├── schemas.py           # Pydantic request/response models
 ├── normalize.py         # link and tag normalization (pure functions)
+├── cursor.py            # opaque keyset cursor encode/decode (Constitution VI)
 ├── errors.py            # error envelope, domain exceptions and handlers
-├── repository.py        # queries: create, list/filter with total, delete
+├── repository.py        # queries: create-or-get existing, list/filter with total, delete
 └── routes.py            # /bookmarks endpoints
 
 tests/
 ├── conftest.py          # test database setup (migrations, truncate per test), API client
 ├── unit/
-│   └── test_normalize.py
+│   ├── test_normalize.py
+│   └── test_cursor.py
 └── integration/
     ├── test_create_bookmark.py
     ├── test_list_bookmarks.py
diff --git a/specs/001-bookmarks-api/quickstart.md b/specs/001-bookmarks-api/quickstart.md
index 6605e43..1232093 100644
--- a/specs/001-bookmarks-api/quickstart.md
+++ b/specs/001-bookmarks-api/quickstart.md
@@ -36,8 +36,8 @@ http://127.0.0.1:8000/docs, or use curl:
 | Step | Request | Expected |
 | --- | --- | --- |
 | 1 | `POST /bookmarks` `{"url": "https://fastapi.tiangolo.com/", "title": "FastAPI docs", "tags": ["Python", "api"]}` | 201, tags `["api", "python"]` |
-| 2 | `POST /bookmarks` `{"url": "HTTPS://FastAPI.tiangolo.com", "title": "Again"}` | 409 `duplicate_url`, `details.existing_id` = id from step 1 |
-| 3 | `GET /bookmarks` | 200, the step 1 bookmark first, `total` 1 |
+| 2 | `POST /bookmarks` `{"url": "HTTPS://FastAPI.tiangolo.com", "title": "Again", "tags": ["other"]}` | 200, the step 1 bookmark unchanged (same `id`, `url`, title "FastAPI docs", tags `["api", "python"]`, `created_at`) |
+| 3 | `GET /bookmarks` | 200, the step 1 bookmark first, `total` 1 (step 2 created nothing) |
 | 4 | `GET /bookmarks?tag=PYTHON` | 200, the step 1 bookmark |
 | 5 | `GET /bookmarks?limit=500` | 422 `validation_error` |
 | 6 | `DELETE /bookmarks/{id}` | 204 |
diff --git a/specs/001-bookmarks-api/research.md b/specs/001-bookmarks-api/research.md
index 5ae30cd..1a36f15 100644
--- a/specs/001-bookmarks-api/research.md
+++ b/specs/001-bookmarks-api/research.md
@@ -35,13 +35,30 @@ considered.
 
 ## Preventing duplicate links
 
-- **Decision**: Store the link as given (`url`) and a normalized form (`url_normalized`) with a
-  unique index. Insert with `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING ...`; if
-  nothing is returned, look up the existing row and raise a duplicate error carrying its id.
+- **Decision** (revised 2026-10-24 for the new FR-004): Store the link as given (`url`) and a
+  normalized form (`url_normalized`) with a unique index. Insert with
+  `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING ...`. If a row is returned, the
+  bookmark is new: return it with 201 Created. If nothing is returned, the normalized link already
+  exists: select the existing row by `url_normalized` and return it unchanged with 200 OK. The
+  request's title and tags are not written anywhere (no `DO UPDATE`). The repository returns the
+  row plus a `created` flag, and the route sets the status code from that flag.
 - **Rationale**: The database guarantees uniqueness even when two saves race (spec edge case);
-  `ON CONFLICT` avoids relying on catching exceptions mid-transaction.
+  `ON CONFLICT` avoids relying on catching exceptions mid-transaction. Under PostgreSQL's default
+  READ COMMITTED isolation, a concurrent insert of the same normalized link waits for the first
+  transaction; once it commits, the second insert does nothing, and the follow-up `SELECT` (a new
+  statement, so a new snapshot) sees the committed row. So the race yields one 201 and one 200
+  with the same bookmark, and exactly one row. If the existing row is deleted between the
+  conflicting insert and the select (the lookup finds nothing), the save retries the insert once
+  more, so the client never gets an error for a link that is no longer saved.
 - **Alternatives considered**: check-then-insert in application code (races under concurrency);
-  catching `IntegrityError` (works, but leaves the transaction aborted and is noisier).
+  catching `IntegrityError` (works, but leaves the transaction aborted and is noisier);
+  `ON CONFLICT DO UPDATE ... RETURNING` with a no-op update to get the row in one statement (it
+  would take a row lock and create a new row version on every repeat save, and the spec says the
+  stored bookmark is not modified); a 303 See Other redirect to the existing bookmark (there is no
+  `GET /bookmarks/{id}` to redirect to, and the change request specifies 200 with the bookmark).
+- **History**: the original decision (2026-10-21) raised a duplicate error carrying the existing
+  id, mapped to 409 `duplicate_url` with `details.existing_id`. Replaced by the change request of
+  2026-10-24; the insert-and-lookup mechanism is kept, only the outcome changes.
 
 ## Link normalization
 
@@ -84,7 +101,9 @@ considered.
 ## Error envelope
 
 - **Decision**: `{"error": {"code": str, "message": str, "details": object | null}}`. Codes:
-  `validation_error` (422), `not_found` (404), `duplicate_url` (409, `details.existing_id`).
+  `validation_error` (422), `not_found` (404), `internal_error` (500). The `duplicate_url` (409,
+  `details.existing_id`) code was removed on 2026-10-24 because a duplicate save now succeeds with
+  200 (revised FR-004); the `DuplicateUrlError` exception and its handler go with it.
   FastAPI's `RequestValidationError` and `HTTPException` handlers are replaced so framework errors
   use the same shape; unexpected errors return 500 `internal_error` without internals.
 - **Rationale**: Constitution III.
[exit 0]
```

```console
$ test -f .specify/extensions.yml && cat .specify/extensions.yml || echo 'no .specify/extensions.yml (after_plan hooks skipped)'
no .specify/extensions.yml (after_plan hooks skipped)
[exit 0]
```

Note: the YAML check first tried the project venv (no PyYAML there, by design: not a dependency),
then fell back to the system python3, which parsed the contract and shows POST responses
`['200', '201', '422']`. The `uv run` also created `.venv` in the worktree (git-ignored).

## How the plan command was carried out

- Pre-hooks: `.specify/extensions.yml` does not exist → skipped.
- Setup: `setup-plan.sh --json` found the existing plan.md and did not copy the template (output above).
- Loaded spec.md (revised in step 1) and `.specify/memory/constitution.md`.
- The plan already existed, so the workflow was executed as a revision of plan.md rather than a
  fresh template fill, preserving the rationale listed in step 1's capture (unique index,
  ON CONFLICT DO NOTHING, url + url_normalized, error envelope, keyset paging, Python versions).
- Technical Context: no unknowns; no NEEDS CLARIFICATION introduced by the change. Unchanged.
- Constitution Check: rows I, III and V updated for the new behavior; all six pass; no
  Complexity Tracking entries. Post-design re-check added for the 2026-10-24 revision.
- Phase 0 (research.md): "Preventing duplicate links" decision revised (201 new / 200 existing,
  concurrency reasoning under READ COMMITTED, retry when the existing row vanishes between insert
  and select, alternatives: DO UPDATE no-op, 303 redirect), with a History note; error envelope
  decision drops `duplicate_url`.
- Phase 1: data-model.md (url_normalized note + lifecycle note, no schema change),
  contracts/openapi.yaml (version 0.2.0; POST gets 200 and 201 with `Bookmark`; 409 removed;
  `duplicate_url` removed from the error-code enum), quickstart.md (manual step 2 now expects 200
  with the unchanged step 1 bookmark).
- Project Structure in plan.md also corrected to list `cursor.py` / `test_cursor.py`, which exist
  since ep02 but were missing from the tree (drift noticed while revising; outside the change
  request, recorded here).
- Post-hooks: none (no extensions.yml).

## Completion report

- Branch: `001-bookmarks-api` (script-reported; the git branch is `claude/ep03-living-r2`, the
  feature was pinned via `SPECIFY_FEATURE_DIRECTORY=specs/001-bookmarks-api`)
- IMPL_PLAN: `specs/001-bookmarks-api/plan.md`
- Artifacts updated: plan.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md
- No new feature folder created.

End: 2026-10-24T12:00:36Z
