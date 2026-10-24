# Step 03 — analyze (flowback-r2)

Start: 2026-10-24T12:02:00Z

Arguments passed to the analyze command: the change request text (verbatim from the run brief).

```console
$ ls .specify; test -f .specify/extensions.yml && cat .specify/extensions.yml || echo 'no .specify/extensions.yml'
init-options.json
integration.json
integrations
memory
scripts
templates
workflows
no .specify/extensions.yml
[exit 0]
```

```console
$ export SPECIFY_FEATURE_DIRECTORY=specs/001-bookmarks-api; .specify/scripts/bash/check-prerequisites.sh --json --require-spec --require-tasks --include-tasks
{"FEATURE_DIR":"/home/claude/runs/flowback-r2/specs/001-bookmarks-api","AVAILABLE_DOCS":["research.md","data-model.md","contracts/","quickstart.md","tasks.md"]}
[exit 0]
```

## Analyze report — BEFORE remediation (run 1, verbatim)

Artifacts loaded: spec.md, plan.md, tasks.md, .specify/memory/constitution.md. No extension hooks (`.specify/extensions.yml` absent). Read-only pass; no files modified during the analysis.

## Specification Analysis Report

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| U1 | Underspecification | MEDIUM | spec.md Edge Cases (L130-146); FR-004 (L158-165); tasks.md T015 (L71), T037 (L222) | The new rule "return the existing bookmark" assumes the existing row can always be read after the insert is skipped. The spec does not say what happens when a save of an already-saved link races a delete of that same bookmark (insert skipped because the row exists, row deleted before it is read). Under the old rule this still produced a conflict error (with a null id); under the new rule T015's "read the existing row and return it" has no row to return, so the outcome is undefined (in code, `.one()` would raise and produce a 500). | Add an edge case: if the bookmark is deleted while the save is in progress, the save is retried and the link is saved as a new bookmark (201). Update T015/add a task, implement the retry in `repository.create_bookmark`, and add a real-database test. |
| I1 | Inconsistency | MEDIUM | spec.md:18 | The 2026-10-21 clarification still says pages use "a limit and an offset"; it was replaced by the constitution v1.1.0 clarification (L23) and FR-006, but unlike the duplicate-rule clarification (L15) it is not marked as superseded. | Mark L18's offset answer as superseded by the v1.1.0 session. |
| I2 | Inconsistency | MEDIUM | tasks.md:82-83 | US2 Independent Test says `GET /bookmarks` returns `total`, `limit` and `offset`; FR-006 and T033 define `next_cursor` and forbid offset. | Change to `total`, `limit` and `next_cursor`. |
| I3 | Inconsistency | MEDIUM | tasks.md Phase 3 (L52-75) vs Phase 4 note (L85-86) | Two conventions for superseded completed tasks in one file: Phase 4 keeps the original offset tasks as history with a note pointing at the corrective tasks; Phase 3's T012/T015/T016 (and T008, T026) were rewritten in place with no local note, so a reader of Phase 3 cannot tell those tasks changed. | Add a note under Phase 3 (and the T008/T026 locations are covered by it) pointing to Phase 10/T037, matching the Phase 4 convention. |
| I4 | Inconsistency | LOW | plan.md:22; tasks.md T031 (L203) | Plan says "tested on 3.12 and 3.13"; T031 says "3.11 and 3.12"; the suite is in fact run on 3.11, 3.12 and 3.13. | Make plan.md say "tested on 3.11, 3.12 and 3.13". |
| T1 | Terminology | LOW | spec.md FR-004 (L158-165), US1/AC3 (L48-51), Edge Cases (L130-132, L140-141), Clarification (L27) | The rest of the spec uses technology-neutral outcomes ("conflict error", "not-found error", "validation error"); the new duplicate rule names HTTP codes (200 OK, 201 Created). The codes come verbatim from the change request and are the observable distinction between "created" and "already saved", but the drift is unexplained. | Keep the codes and state in Assumptions why this requirement names them. |
| D1 | Duplication | LOW | tasks.md T037 (L222) vs T012 (L65), T015 (L71), T016 (L72) | T037 restates in full the behavior, files and tests that the rewritten T012/T015/T016 already describe. | Shorten T037 to the flow-back record and reference T008/T012/T015/T016/T026 for the details. |

**Coverage Summary Table:**

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|
| FR-001 save link/title/0-10 tags | Yes | T005, T012, T014, T016 | |
| FR-002 reject invalid input | Yes | T012, T014 | |
| FR-003 record saved time | Yes | T005, T012 | |
| FR-004 no duplicates; existing link → existing bookmark 200; new → 201; concurrent → one 201 + one 200 | Yes | T007, T012, T015, T016, T037 | See U1 (save/delete race) |
| FR-005 return saved/existing bookmark with id | Yes | T014, T016, T037 | |
| FR-006 keyset paging, total, next token | Yes | T032-T035 | |
| FR-007 tag filter | Yes | T021, T022 | |
| FR-008 delete by id | Yes | T023-T025, T029 | |
| FR-009 not-found on delete | Yes | T023, T024 | |
| FR-010 one error format | Yes | T008, T026 | |
| FR-011 tag normalization | Yes | T011, T013, T014, T030 | |
| SC-001 save then top of list | Yes | T012, T017/T035 | |
| SC-002 one bookmark per link | Yes | T007, T012, T037 | |
| SC-003 tag filter correctness | Yes | T021 | |
| SC-004 every scenario tested | Yes | T012, T017, T021, T023, T026, T035 | |
| SC-005 same error format | Yes | T026 | |

**Constitution Alignment Issues:** None. (Principle III lists "409 conflict" as an example error class; the feature no longer produces a conflict error, which does not violate the principle: every error the feature does produce uses the envelope.)

**Unmapped Tasks:** None (T001-T004, T006, T009, T010, T027, T028, T031, T036 are setup/polish tasks serving all stories).

**Metrics:**

- Total Requirements: 16 (11 FR + 5 SC)
- Total Tasks: 37
- Coverage %: 100%
- Ambiguity Count: 0
- Duplication Count: 1
- Critical Issues Count: 0
- Findings by severity: CRITICAL 0, HIGH 0, MEDIUM 4, LOW 3 (total 7)

**Next Actions:** No CRITICAL issues. MEDIUM U1 is a behavior gap introduced by the duplicate-rule change and should be resolved before calling the feature done; I1-I3, I4, T1, D1 are wording fixes.

**Offer remediation:** "Would you like me to suggest concrete remediation edits for the top N issues?" — Per the run brief ("Resolve every finding it raises by editing artifacts or code"), the answer is yes, all 7. Remediation applied below, outside the read-only analyze pass.

## Remediation

### U1 — confirm the gap with a real-database probe (scratch script, not committed)

```console
$ uv run --python 3.13 python /home/claude/scratch/flowback-r2/race_probe.py
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
unknown PostgreSQL timezone: 'ASIA0'; will use UTC
RAISED: NoResultFound No row was found when one was required
[exit 0]
```

### U1 — code fix (bounded retry in repository.create_bookmark, MAX_SAVE_ATTEMPTS = 3) and new real-database test `test_save_racing_a_delete_of_the_same_link_saves_a_new_bookmark`

```console
$ uv run --python 3.13 python /home/claude/scratch/flowback-r2/race_probe.py
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
unknown PostgreSQL timezone: 'ASIA0'; will use UTC
(<bookmarks_api.models.BookmarkRow object at 0x7f43b1135be0>, True)
[exit 0]
```

```console
$ uv run --python 3.13 pytest -q
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
........................................................................ [ 73%]
..........................                                               [100%]
98 passed in 2.17s
[exit 0]
```

### U1 — new test against the pre-fix repository.py (temporarily restored from HEAD, then put back)

```console
$ uv run --python 3.13 pytest -q -k racing_a_delete
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
F                                                                        [100%]
=================================== FAILURES ===================================
_______ test_save_racing_a_delete_of_the_same_link_saves_a_new_bookmark ________

client = <starlette.testclient.TestClient object at 0x7f0c7af63a10>
engine = Engine(postgresql+psycopg://bookmarks:***@localhost:5432/bookmarks_test_flowback_r2)
row_count = <function row_count.<locals>.count at 0x7f0c7ab7cf40>

    def test_save_racing_a_delete_of_the_same_link_saves_a_new_bookmark(
        client: TestClient, engine, row_count
    ) -> None:
        """The existing bookmark is deleted after the insert is skipped but before it is read."""
        first = client.post("/bookmarks", json={"url": "https://example.com/gone", "title": "Old"})
        deleted: list[bool] = []
    
        def delete_existing(_session: Session) -> None:
            if not deleted:
                deleted.append(True)
                with engine.begin() as connection:
                    connection.execute(text("DELETE FROM bookmarks"))
    
        event.listen(Session, "after_rollback", delete_existing)
        try:
            response = client.post(
                "/bookmarks", json={"url": "https://EXAMPLE.com/gone/", "title": "New"}
            )
        finally:
            event.remove(Session, "after_rollback", delete_existing)
    
        assert deleted == [True]
>       assert response.status_code == 201
E       assert 500 == 201
E        +  where 500 = <Response [500 Internal Server Error]>.status_code

tests/integration/test_create_bookmark.py:121: AssertionError
------------------------------ Captured log call -------------------------------
WARNING  psycopg:_cursor_base.py:514 unknown PostgreSQL timezone: 'ASIA0'; will use UTC
ERROR    bookmarks_api.errors:errors.py:73 Unhandled error
Traceback (most recent call last):
  File "/home/claude/runs/flowback-r2/.venv/lib/python3.13/site-packages/starlette/middleware/errors.py", line 164, in __call__
    await self.app(scope, receive, _send)
  File "/home/claude/runs/flowback-r2/.venv/lib/python3.13/site-packages/fastapi/telemetry/_asgi.py", line 151, in __call__
    await self.app(scope, receive, send)
  File "/home/claude/runs/flowback-r2/.venv/lib/python3.13/site-packages/starlette/middleware/exceptions.py", line 63, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/home/claude/runs/flowback-r2/.venv/lib/python3.13/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/home/claude/runs/flowback-r2/.venv/lib/python3.13/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/home/claude/runs/flowback-r2/.venv/lib/python3.13/site-packages/fastapi/middleware/asyncexitstack.py", line 18, in __call__
    await self.app(scope, receive, send)
  File "/home/claude/runs/flowback-r2/.venv/lib/python3.13/site-packages/starlette/routing.py", line 678, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/home/claude/runs/flowback-r2/.venv/lib/python3.13/site-packages/fastapi/routing.py", line 2811, in app
    await route.handle(scope, receive, send)
  File "/home/claude/runs/flowback-r2/.venv/lib/python3.13/site-packages/fastapi/routing.py", line 1839, in handle
    await self.original_router.handle(scope, receive, send)
  File "/home/claude/runs/flowback-r2/.venv/lib/python3.13/site-packages/fastapi/routing.py", line 2894, in handle
    await included_router._handle_selected(scope, receive, send)
  File "/home/claude/runs/flowback-r2/.venv/lib/python3.13/site-packages/fastapi/routing.py", line 1865, in _handle_selected
    await original_route.handle(scope, receive, send)
  File "/home/claude/runs/flowback-r2/.venv/lib/python3.13/site-packages/fastapi/routing.py", line 1328, in handle
    await effective_context.app(scope, receive, send)
  File "/home/claude/runs/flowback-r2/.venv/lib/python3.13/site-packages/fastapi/routing.py", line 166, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/home/claude/runs/flowback-r2/.venv/lib/python3.13/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/home/claude/runs/flowback-r2/.venv/lib/python3.13/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/home/claude/runs/flowback-r2/.venv/lib/python3.13/site-packages/fastapi/routing.py", line 152, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/home/claude/runs/flowback-r2/.venv/lib/python3.13/site-packages/fastapi/routing.py", line 745, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<3 lines>...
    )
    ^
  File "/home/claude/runs/flowback-r2/.venv/lib/python3.13/site-packages/fastapi/routing.py", line 374, in run_endpoint_function
    return await run_in_threadpool(
           ^^^^^^^^^^^^^^^^^^^^^^^^
        _run_sync_endpoint, function=dependant.call, arguments=values
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/home/claude/runs/flowback-r2/.venv/lib/python3.13/site-packages/starlette/concurrency.py", line 34, in run_in_threadpool
    return await anyio.to_thread.run_sync(func)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/claude/runs/flowback-r2/.venv/lib/python3.13/site-packages/anyio/to_thread.py", line 65, in run_sync
    return await get_async_backend().run_sync_in_worker_thread(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        func, args, abandon_on_cancel=abandon_on_cancel, limiter=limiter
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/home/claude/runs/flowback-r2/.venv/lib/python3.13/site-packages/anyio/_backends/_asyncio.py", line 2706, in run_sync_in_worker_thread
    return await future
           ^^^^^^^^^^^^
  File "/home/claude/runs/flowback-r2/.venv/lib/python3.13/site-packages/anyio/_backends/_asyncio.py", line 1100, in run
    result = context.run(func, *args)
  File "/home/claude/runs/flowback-r2/.venv/lib/python3.13/site-packages/fastapi/telemetry/_api.py", line 244, in _run_sync_endpoint
    return function(**arguments)
  File "/home/claude/runs/flowback-r2/src/bookmarks_api/routes.py", line 54, in create_bookmark
    row, created = repository.create_bookmark(session, data)
                   ~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^
  File "/home/claude/runs/flowback-r2/src/bookmarks_api/repository.py", line 35, in create_bookmark
    ).one()
      ~~~^^
  File "/home/claude/runs/flowback-r2/.venv/lib/python3.13/site-packages/sqlalchemy/engine/result.py", line 1421, in one
    return self._only_one_row(
           ~~~~~~~~~~~~~~~~~~^
        raise_for_second_row=True, raise_for_none=True, scalar=False
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "lib/sqlalchemy/engine/_result_cy.py", line 539, in sqlalchemy.engine._result_cy.BaseResultInternal._only_one_row
sqlalchemy.exc.NoResultFound: No row was found when one was required
=========================== short test summary info ============================
FAILED tests/integration/test_create_bookmark.py::test_save_racing_a_delete_of_the_same_link_saves_a_new_bookmark
1 failed, 97 deselected in 0.22s
[exit 1]
```

### Artifact remediation (spec.md, tasks.md, plan.md, research.md)

```console
$ git diff -- specs
diff --git a/specs/001-bookmarks-api/plan.md b/specs/001-bookmarks-api/plan.md
index 3c5a682..ced4908 100644
--- a/specs/001-bookmarks-api/plan.md
+++ b/specs/001-bookmarks-api/plan.md
@@ -19,7 +19,7 @@ existing `docker-compose.yml`.
 
 ## Technical Context
 
-**Language/Version**: Python 3.11+ (tested on 3.12 and 3.13)
+**Language/Version**: Python 3.11+ (tested on 3.11, 3.12 and 3.13)
 
 **Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Alembic, psycopg 3 (binary), Uvicorn; tests:
 pytest, httpx2. Each is justified in [research.md](research.md) (Constitution IV).
diff --git a/specs/001-bookmarks-api/research.md b/specs/001-bookmarks-api/research.md
index ff905ed..c2f4e77 100644
--- a/specs/001-bookmarks-api/research.md
+++ b/specs/001-bookmarks-api/research.md
@@ -42,7 +42,9 @@ considered.
   "raise a duplicate error carrying its id", which produced 409).
 - **Rationale**: The database guarantees uniqueness even when two saves race (spec edge case):
   the losing insert waits for the winner to commit, inserts nothing, and then reads the winner's
-  row, so one save gets 201 and the other 200 with the same bookmark;
+  row, so one save gets 201 and the other 200 with the same bookmark. If the existing row is
+  deleted between the skipped insert and the read, the insert is retried (at most 3 attempts) and
+  the link is saved as new (201);
   `ON CONFLICT` avoids relying on catching exceptions mid-transaction.
 - **Alternatives considered**: check-then-insert in application code (races under concurrency);
   catching `IntegrityError` (works, but leaves the transaction aborted and is noisier).
diff --git a/specs/001-bookmarks-api/spec.md b/specs/001-bookmarks-api/spec.md
index 3f648fb..a228ad2 100644
--- a/specs/001-bookmarks-api/spec.md
+++ b/specs/001-bookmarks-api/spec.md
@@ -15,7 +15,7 @@
 - Q: When someone saves a link that is already bookmarked, what should happen? → A: ~~Reject it with a conflict error that includes the existing bookmark's identifier; the existing bookmark is left unchanged.~~ Superseded on 2026-10-24 (see "Change request 2026-10-24" below).
 - Q: Which links count as "the same link"? → A: Links that match after normalization: scheme and host lowercased, default port removed, trailing slash on the path removed, fragment (#...) removed; the query string is kept as is.
 - Q: How should tags be cleaned up and limited? → A: Trim spaces, lowercase, drop duplicates; 1 to 30 characters of letters, digits and hyphens; at most 10 tags per bookmark.
-- Q: How should the list behave when there are many bookmarks? → A: Return pages: 20 per page by default, up to 100 per page, using a limit and an offset, plus the total count.
+- Q: How should the list behave when there are many bookmarks? → A: Return pages: 20 per page by default, up to 100 per page, ~~using a limit and an offset~~, plus the total count. (Offset superseded by the constitution v1.1.0 session below: pages use a next-page token.)
 - Q: How long can a title and a link be? → A: Title 1 to 200 characters; link at most 2048 characters.
 
 ### Session 2026-10-21 (constitution v1.1.0)
@@ -139,6 +139,8 @@ appears in the list.
   than letters, digits and hyphens is rejected.
 - Two saves of the same new link at the same moment still leave exactly one bookmark: one save
   gets 201 Created, the other gets 200 OK with the same bookmark.
+- If the existing bookmark is deleted while a save of the same link is in progress, so there is no
+  longer an existing bookmark to return, the link is saved as a new bookmark (201 Created).
 - A malformed next-page token (one that does not decode to a position in the list) is rejected with
   a validation error.
 - A request that sends the removed offset option is rejected with a validation error that names the
@@ -207,3 +209,6 @@ appears in the list.
 - Editing an existing bookmark's title or tags is out of scope for this version.
 - The API is used by developers and tools, not directly through a user interface.
 - Bookmarks are kept until the user deletes them; there is no automatic expiry.
+- FR-004 names HTTP status codes (200 OK, 201 Created) because the change request of 2026-10-24
+  defines the duplicate rule by them: they are the only observable difference between "saved now"
+  and "already saved", since both return the same bookmark.
diff --git a/specs/001-bookmarks-api/tasks.md b/specs/001-bookmarks-api/tasks.md
index 66e26f1..bd28463 100644
--- a/specs/001-bookmarks-api/tasks.md
+++ b/specs/001-bookmarks-api/tasks.md
@@ -68,9 +68,13 @@ link returns 200 with the existing bookmark, unchanged.
 
 - [X] T013 [P] [US1] Implement `normalize_url(url) -> str` and `normalize_tags(tags) -> list[str]` in `src/bookmarks_api/normalize.py` using only the standard library, raising `ValueError` with a clear message on invalid input
 - [X] T014 [P] [US1] Create Pydantic models in `src/bookmarks_api/schemas.py`: `BookmarkCreate` (`url` str, max 2048, http/https with a host; `title` trimmed, 1 to 200 characters; `tags` list default `[]`, normalized via `normalize_tags`, at most 10 after de-duplication; extra fields forbidden) and `Bookmark` (`id`, `url`, `title`, `tags`, `created_at`)
-- [X] T015 [US1] Implement `create_bookmark(session, data)` in `src/bookmarks_api/repository.py` using `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`, returning `(row, created)`; when nothing is inserted, read the existing row by `url_normalized` and return it unchanged with `created = False` (research.md, "Preventing duplicate links")
+- [X] T015 [US1] Implement `create_bookmark(session, data)` in `src/bookmarks_api/repository.py` using `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`, returning `(row, created)`; when nothing is inserted, read the existing row by `url_normalized` and return it unchanged with `created = False`; if that row was deleted before it could be read, retry the insert (bounded) so the link is saved as new (research.md, "Preventing duplicate links")
 - [X] T016 [US1] Implement `POST /bookmarks` in `src/bookmarks_api/routes.py` returning 201 with `Bookmark` for a new link and 200 with the existing `Bookmark` for an already-saved link, with the 422 response declared using `ErrorResponse`
 
+> Note (change request 2026-10-24): T008, T012, T015, T016 and T026 were rewritten in place to
+> the accepted duplicate-save behavior (existing bookmark returned with 200, no 409). The change
+> is recorded in Phase 10 (T037, T038).
+
 **Checkpoint**: User Story 1 works and is tested on its own (MVP)
 
 ---
@@ -80,7 +84,7 @@ link returns 200 with the existing bookmark, unchanged.
 **Goal**: A user can list bookmarks newest first, in pages, with a total count.
 
 **Independent Test**: `GET /bookmarks` returns saved bookmarks newest first with `total`, `limit`
-and `offset`.
+and `next_cursor`.
 
 > Note (constitution v1.1.0): T017-T020 built offset paging, which Principle VI now forbids. Corrective
 > tasks are appended by /speckit-converge; these tasks are kept as history.
@@ -219,4 +223,5 @@ Task: "BookmarkCreate / Bookmark in src/bookmarks_api/schemas.py"
 > `INSERT ... ON CONFLICT DO NOTHING`) is unchanged. T008, T012, T015, T016 and T026 above are
 > rewritten to describe the accepted behavior.
 
-- [X] T037 [US1] Saving a link whose normalized form is already stored returns the existing bookmark unchanged with 200 OK instead of 409 `duplicate_url`; the request's title and tags are ignored; a new link still returns 201 Created; two concurrent saves of the same new link store one bookmark (one 201, one 200 with the same bookmark). `create_bookmark` in `src/bookmarks_api/repository.py` returns `(row, created)`; `POST /bookmarks` in `src/bookmarks_api/routes.py` sets 200 when not created and declares 200 and 201 (no 409); `DuplicateUrlError` and its handler are removed from `src/bookmarks_api/errors.py`; tests updated in `tests/integration/test_create_bookmark.py` and `tests/integration/test_errors.py` (FR-004)
+- [X] T037 [US1] Flow-back record for FR-004: an already-saved link returns the existing bookmark unchanged with 200 instead of 409 `duplicate_url`; implemented and tested as now described in T008, T012, T015, T016 and T026 (`src/bookmarks_api/errors.py`, `repository.py`, `routes.py`; `tests/integration/test_create_bookmark.py`, `test_errors.py`)
+- [X] T038 [US1] Handle a save racing a delete of the same link (found by /speckit-analyze, finding U1): in `create_bookmark` in `src/bookmarks_api/repository.py`, when the conflicting row is gone before it is read, retry the insert (at most 3 attempts) so the link is saved as new with 201; real-database test `test_save_racing_a_delete_of_the_same_link_saves_a_new_bookmark` in `tests/integration/test_create_bookmark.py`, per spec Edge Cases
[exit 0]
```

```console
$ uv run --python 3.13 pytest -q
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
........................................................................ [ 73%]
..........................                                               [100%]
98 passed in 2.87s
[exit 0]
```

## Analyze — run 2 (after remediation)

```console
$ export SPECIFY_FEATURE_DIRECTORY=specs/001-bookmarks-api; .specify/scripts/bash/check-prerequisites.sh --json --require-spec --require-tasks --include-tasks
{"FEATURE_DIR":"/home/claude/runs/flowback-r2/specs/001-bookmarks-api","AVAILABLE_DOCS":["research.md","data-model.md","contracts/","quickstart.md","tasks.md"]}
[exit 0]
```

## Analyze report — AFTER remediation (run 2, verbatim)

Artifacts reloaded: spec.md, plan.md, tasks.md, constitution. No extension hooks. Read-only pass.

## Specification Analysis Report

No findings. Previous findings re-checked:

| ID | Previous severity | Status | Evidence |
|----|-------------------|--------|----------|
| U1 | MEDIUM | Resolved | spec.md Edge Cases now defines the save/delete race (saved as new, 201); T015 and new T038 cover it; code retries (MAX_SAVE_ATTEMPTS = 3) and `test_save_racing_a_delete_of_the_same_link_saves_a_new_bookmark` passes on the real database (it failed against the pre-fix code). |
| I1 | MEDIUM | Resolved | spec.md:18 offset answer struck through and pointed at the v1.1.0 session. |
| I2 | MEDIUM | Resolved | tasks.md US2 Independent Test says `next_cursor`. |
| I3 | MEDIUM | Resolved | Phase 3 note lists the in-place rewrites and points to Phase 10. |
| I4 | LOW | Resolved | plan.md: "tested on 3.11, 3.12 and 3.13". |
| T1 | LOW | Resolved | spec.md Assumptions explains why FR-004 names HTTP status codes. |
| D1 | LOW | Resolved | T037 shortened to a flow-back record referencing T008/T012/T015/T016/T026. |

Note (not raised as a finding): the retry in `create_bookmark` is bounded at 3 attempts; a save would only fail if the same link were re-created and deleted again on every attempt. research.md records the bound.

**Coverage Summary Table:** unchanged from run 1 except FR-004 → T007, T012, T015, T016, T037, T038 and SC-002 → T007, T012, T037, T038.

**Constitution Alignment Issues:** None.

**Unmapped Tasks:** None.

**Metrics:**

- Total Requirements: 16 (11 FR + 5 SC)
- Total Tasks: 38
- Coverage %: 100%
- Ambiguity Count: 0
- Duplication Count: 0
- Critical Issues Count: 0
- Findings by severity: CRITICAL 0, HIGH 0, MEDIUM 0, LOW 0

**Next Actions:** Proceed to /speckit-converge.

End: 2026-10-24T12:05:33Z
