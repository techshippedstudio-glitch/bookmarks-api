# 02 plan — forward-r2

Start: 2026-10-24T11:59:16Z

```console
$ ls .specify/extensions.yml
ls: cannot access '.specify/extensions.yml': No such file or directory
[exit 2]
```

```console
$ .specify/scripts/bash/setup-plan.sh --json
Copied plan template to /home/claude/runs/forward-r2/specs/002-idempotent-bookmark-save/plan.md
{"FEATURE_SPEC":"/home/claude/runs/forward-r2/specs/002-idempotent-bookmark-save/spec.md","IMPL_PLAN":"/home/claude/runs/forward-r2/specs/002-idempotent-bookmark-save/plan.md","FEATURE_DIR":"/home/claude/runs/forward-r2/specs/002-idempotent-bookmark-save","BRANCH":"002-idempotent-bookmark-save"}
[exit 0]
```

## Agent actions (not shell commands)

- Read `.claude/skills/speckit-plan/SKILL.md`, the copied plan template, `specs/002-idempotent-bookmark-save/spec.md`, `.specify/memory/constitution.md`, and for context `specs/001-bookmarks-api/{plan,research,data-model,quickstart}.md`, `specs/001-bookmarks-api/contracts/openapi.yaml`, `src/bookmarks_api/{routes,repository,errors,schemas,models}.py`, `tests/integration/{test_create_bookmark,test_errors}.py`, `tests/conftest.py` (read only).
- No `.specify/extensions.yml` → no before/after plan hooks.
- Plan arguments: none beyond the change request (no extra planning guidance given).
- Wrote with the Write tool: `plan.md`, `research.md`, `data-model.md`, `contracts/openapi.yaml`, `quickstart.md` in `specs/002-idempotent-bookmark-save/`.
- Questions the command would ask: none (no NEEDS CLARIFICATION in Technical Context).
- Constitution Check: all six principles Pass, pre- and post-design. No Complexity Tracking entries.
- Design choice recorded in research.md: keep `ON CONFLICT DO NOTHING`, then SELECT existing row → 200; rejected `DO UPDATE ... (xmax = 0)` because it writes the row on every re-save.
- Note: `.specify/feature.json` (written in step 1) is ignored by `.specify/.gitignore` line 6 (`feature.json`), so it is not in the commits.

```console
$ cat specs/002-idempotent-bookmark-save/plan.md
# Implementation Plan: Idempotent Bookmark Save

**Branch**: `002-idempotent-bookmark-save` | **Date**: 2026-10-24 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-idempotent-bookmark-save/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

**Supersedes**: the duplicate rule of FR-004 in [specs/001-bookmarks-api](../001-bookmarks-api/spec.md)
(409 `duplicate_url` on a re-save). `specs/001-bookmarks-api` stays as the historical record and is
not edited; where its plan, research, contract or quickstart describe the 409 duplicate response,
this feature's artifacts take precedence.

## Summary

`POST /bookmarks` becomes idempotent per normalized link. A save of a link that is not yet
bookmarked still inserts and returns the bookmark with 201 Created. A save whose normalized link
already exists returns the stored bookmark, unchanged, with 200 OK; the request's title and tags
are ignored. The existing `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING` stays the
single point of truth for "who created it", so concurrent first saves still store one row: the
winner gets 201, the loser reads the committed row and gets 200. The `DuplicateUrlError` exception,
its 409 handler and the `duplicate_url` error code are removed. No schema change, no migration, no
new dependency.

## Technical Context

**Language/Version**: Python 3.11+ (suite run on 3.11, 3.12 and 3.13) — unchanged from 001

**Primary Dependencies**: FastAPI, Pydantic, SQLAlchemy 2.0, Alembic, psycopg 3; tests: pytest,
httpx — unchanged; no new dependency (Constitution IV)

**Storage**: PostgreSQL; existing `bookmarks` table and unique index `uq_bookmarks_url_normalized`
— unchanged, no migration

**Testing**: pytest integration tests through the HTTP API against the real test database
(Constitution II), including a two-thread concurrent first-save test

**Target Platform**: Linux server / developer machine — unchanged

**Project Type**: web-service (REST API)

**Performance Goals**: A re-save costs one insert attempt plus one indexed lookup by
`url_normalized`; no measurable change for interactive use

**Constraints**: The stored bookmark must not be modified by a re-save (no `DO UPDATE`); exactly
one row per normalized link under concurrency

**Scale/Scope**: One endpoint changes (`POST /bookmarks`); list, filter and delete are untouched

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | How the plan complies | Status |
| --- | --- | --- |
| I. Typed API Contracts | `POST /bookmarks` keeps the `BookmarkCreate` request model and returns the `Bookmark` response model for both 201 and 200; the 200 response is declared on the route so it appears in the generated OpenAPI; the stale 409 entry is removed | Pass |
| II. Real-Database Testing | Re-save, unchanged-bookmark and concurrent-first-save tests run against the real test database; no mocks | Pass |
| III. Consistent Error Shape | No new error; the 409 `duplicate_url` error disappears because a re-save is no longer an error. Validation (422) still uses the envelope. The principle's "409 conflict" mapping simply has no remaining user on this endpoint | Pass |
| IV. Minimal Dependencies | No new dependency | Pass |
| V. Tests Ship With Every Feature | Every acceptance scenario in spec.md maps to a test in the same change; tests asserting the superseded 409 behavior are replaced; full suite must pass on 3.11–3.13 | Pass |
| VI. Cursor Pagination | No list endpoint changes; a re-save does not change `created_at`, so keyset positions stay stable | Pass |

Post-design re-check (after Phase 1): Pass. The contract delta, data model note and quickstart add
no dependency, no untyped interface and no schema change.

## Project Structure

### Documentation (this feature)

```text
specs/002-idempotent-bookmark-save/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── openapi.yaml     # POST /bookmarks as changed by this feature
├── checklists/
│   └── requirements.md  # /speckit-specify quality checklist
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
src/bookmarks_api/
├── repository.py        # create_bookmark → returns (row, created); no DuplicateUrlError
├── routes.py            # POST /bookmarks sets 201 or 200; responses declare 200, drop 409
└── errors.py            # remove DuplicateUrlError and its 409 handler

tests/
└── integration/
    ├── test_create_bookmark.py   # re-save returns 200 + existing bookmark; concurrency 201/200
    └── test_errors.py            # drop 409 envelope test; OpenAPI check expects 200, not 409
```

**Structure Decision**: Single project, existing `src/` layout from 001. Only the three modules
and two test files above change; no new modules, no migration.

## Complexity Tracking

No constitution violations to justify.
[exit 0]
```

```console
$ cat specs/002-idempotent-bookmark-save/research.md
# Research: Idempotent Bookmark Save

Phase 0 for [plan.md](plan.md). The Technical Context has no NEEDS CLARIFICATION items; the
decisions below settle how to implement the spec on the existing stack from
[specs/001-bookmarks-api](../001-bookmarks-api/research.md). Where this file disagrees with 001's
"Preventing duplicate links" and "Error envelope" decisions, this file supersedes them.

## Detecting "already saved" and staying correct under concurrency

- **Decision**: Keep `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING *`. If a row is
  returned, this request created the bookmark (201). If nothing is returned, end the transaction
  and `SELECT` the existing row by `url_normalized` in a new statement, then return it (200).
- **Rationale**: The unique index decides the race. Under READ COMMITTED, `ON CONFLICT DO NOTHING`
  waits for a concurrent inserter of the same key to commit, so the follow-up `SELECT` sees the
  winner's committed row. Exactly one request observes a returned row, so exactly one gets 201
  (spec FR-004). It is the same mechanism 001 already relies on, with the error replaced by a
  lookup.
- **Alternatives considered**: `ON CONFLICT DO UPDATE SET url_normalized = EXCLUDED.url_normalized
  RETURNING *, (xmax = 0) AS inserted` (one round trip, but it writes the row on every re-save,
  creating a new row version and firing any future update triggers, which contradicts "the stored
  bookmark is not modified"); check-then-insert (races); catching `IntegrityError` (aborted
  transaction, noisier).

## Row deleted between the conflict and the lookup

- **Decision**: If the lookup finds nothing (the conflicting bookmark was deleted in between),
  retry the insert. Bound the loop to a few attempts.
- **Rationale**: Without a retry the request would have neither a created row nor an existing one.
  A retry gives the correct answer for the new state (the link is no longer saved, so it is
  created, 201). The window is tiny, so the bound is never reached in practice.
- **Alternatives considered**: Returning 500 (wrong: the request is valid); `SELECT ... FOR SHARE`
  inside the same transaction (more locking for a case that almost never happens).

## Response status and contract

- **Decision**: The route keeps `status_code=201` as its default and sets `response.status_code =
  200` when the bookmark already existed. The route's `responses` declare `200` with the
  `Bookmark` model ("This link was already bookmarked; the existing bookmark is returned
  unchanged") and no longer declare `409`. The response body is the same `Bookmark` shape for both.
- **Rationale**: Constitution I: the OpenAPI document is generated from the code, so both success
  codes must be declared on the route. One body shape means clients read one representation.
- **Alternatives considered**: A separate `existing: bool` field or a `Location`/header flag (not
  asked for; the status code alone distinguishes created from existing).

## Validation before lookup

- **Decision**: The request body is validated by `BookmarkCreate` exactly as before, so a re-save
  with an invalid title, link or tags still returns 422 before any database work.
- **Rationale**: Spec FR-005; it is also what the framework does by default, so no extra code.
- **Alternatives considered**: Validating only the link on a re-save (would let invalid requests
  succeed, and split the validation rules by database state).

## Removing the duplicate error

- **Decision**: Delete `DuplicateUrlError`, its exception handler, and the `duplicate_url` code. The
  generic `409 → "conflict"` entry in the HTTP status-code map stays (it serves framework
  `HTTPException`s, not this feature).
- **Rationale**: Nothing raises it any more; dead error paths mislead readers of the contract.
- **Alternatives considered**: Keeping the class unused (dead code).
[exit 0]
```

```console
$ cat specs/002-idempotent-bookmark-save/data-model.md
# Data Model: Idempotent Bookmark Save

No schema change. The `bookmarks` table, its columns, constraints and indexes are exactly as
defined in [specs/001-bookmarks-api/data-model.md](../001-bookmarks-api/data-model.md); no
migration is added.

## What changes in how the model is used

| Element | 001 meaning | Meaning after this feature |
| --- | --- | --- |
| `url_normalized` + `uq_bookmarks_url_normalized` | Duplicate detection; a second save of the same normalized link is rejected (409) | Identity of a saved link; a second save of the same normalized link **finds** the existing row and returns it (200). Still guarantees one row per normalized link under concurrent saves (spec FR-004) |
| `title`, `tags` | Set on insert | Set on insert only; a re-save never updates them (spec FR-002) |
| `created_at` | Saved time | Unchanged by a re-save, so the bookmark keeps its place in the newest-first list |

## Save outcome (per request)

```text
validate request ──invalid──▶ 422 validation_error (nothing stored)
      │ valid
      ▼
insert ON CONFLICT DO NOTHING ──row returned──▶ 201 Created, new bookmark
      │ no row (normalized link exists)
      ▼
select by url_normalized ──found──▶ 200 OK, existing bookmark unchanged
      │ not found (deleted meanwhile)
      └──▶ retry insert (bounded)
```

## Validation rules

Unchanged from 001 (`url`, `title`, `tags`), and applied to re-saves too (spec FR-005).
[exit 0]
```

```console
$ cat specs/002-idempotent-bookmark-save/contracts/openapi.yaml
openapi: 3.1.0
info:
  title: Bookmarks API — idempotent save (feature 002)
  version: 0.2.0
  description: >
    Contract delta for specs/002-idempotent-bookmark-save. It supersedes the POST /bookmarks
    operation of specs/001-bookmarks-api/contracts/openapi.yaml: the 409 duplicate_url response is
    removed and a 200 response returns the existing bookmark unchanged. All other operations and
    schemas are unchanged and remain defined in the 001 contract, which is referenced here.
    The running service generates its own OpenAPI document at /openapi.json from the Pydantic
    models; this file is the design contract those models must match.
paths:
  /bookmarks:
    post:
      summary: Save a bookmark
      description: >
        Idempotent per normalized link. A link that is not yet bookmarked is stored and returned
        with 201. A link whose normalized form is already bookmarked returns the existing bookmark,
        unchanged, with 200; the title and tags in the request are ignored. Concurrent first saves
        of the same link store one bookmark: one request gets 201, the other 200 with the same
        bookmark. The request is validated in both cases.
      operationId: createBookmark
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: '../../001-bookmarks-api/contracts/openapi.yaml#/components/schemas/BookmarkCreate' }
      responses:
        '201':
          description: Bookmark saved (the link was not bookmarked before)
          content:
            application/json:
              schema: { $ref: '../../001-bookmarks-api/contracts/openapi.yaml#/components/schemas/Bookmark' }
        '200':
          description: This link was already bookmarked; the existing bookmark is returned unchanged
          content:
            application/json:
              schema: { $ref: '../../001-bookmarks-api/contracts/openapi.yaml#/components/schemas/Bookmark' }
        '422':
          description: Invalid link, title or tags (also on a re-save)
          content:
            application/json:
              schema: { $ref: '#/components/schemas/ErrorResponse' }
components:
  schemas:
    ErrorResponse:
      description: >
        Same envelope as the 001 contract; the duplicate_url code no longer exists.
      type: object
      required: [error]
      properties:
        error:
          type: object
          required: [code, message]
          properties:
            code:
              type: string
              enum: [validation_error, not_found, internal_error]
            message: { type: string }
            details:
              description: Extra information, e.g. field errors
              type: [object, array, 'null']
[exit 0]
```

```console
$ cat specs/002-idempotent-bookmark-save/quickstart.md
# Quickstart: validate idempotent bookmark save

Runnable checks that prove feature 002 works end to end. The changed operation is defined in
[contracts/openapi.yaml](contracts/openapi.yaml); everything else, including setup, is as in
[specs/001-bookmarks-api/quickstart.md](../001-bookmarks-api/quickstart.md). This guide replaces
001's manual step 2 (which expected 409 `duplicate_url`).

## Prerequisites and setup

As in 001: Postgres running, `uv sync`, `uv run alembic upgrade head`. No new migration.

## Automated validation

```bash
set -a; . ./.env; set +a
uv run pytest -q
```

Expected: all tests pass, including the re-save and concurrent-save tests in
`tests/integration/test_create_bookmark.py`.

## Manual validation

Start the API: `uv run uvicorn bookmarks_api.main:app --reload`, then:

| Step | Request | Expected |
| --- | --- | --- |
| 1 | `POST /bookmarks` `{"url": "https://fastapi.tiangolo.com/", "title": "FastAPI docs", "tags": ["python"]}` | 201, new bookmark, note its `id` |
| 2 | `POST /bookmarks` `{"url": "HTTPS://FastAPI.tiangolo.com#top", "title": "Again", "tags": ["other"]}` | 200, same `id`, title `FastAPI docs`, tags `["python"]`, same `created_at` |
| 3 | `GET /bookmarks` | 200, `total` 1, the step 1 bookmark unchanged |
| 4 | `POST /bookmarks` `{"url": "https://fastapi.tiangolo.com/?q=1", "title": "Query"}` | 201 (different query string → different link) |
| 5 | `POST /bookmarks` `{"url": "https://fastapi.tiangolo.com", "title": ""}` | 422 `validation_error` (re-saves are validated too) |
| 6 | `DELETE /bookmarks/{id from step 1}`, then repeat step 1 | 204, then 201 with a new `id` |
| 7 | `GET /openapi.json` → `paths./bookmarks.post.responses` | has `200`, `201`, `422`; no `409` |
[exit 0]
```

## Spec Kit completion report (verbatim)

- **Branch**: `002-idempotent-bookmark-save` (as reported by setup-plan.sh from `.specify/feature.json`; the git branch is `claude/ep03-forward-r2`)
- **IMPL_PLAN**: `specs/002-idempotent-bookmark-save/plan.md`
- **Generated artifacts**: `research.md` (Phase 0), `data-model.md`, `contracts/openapi.yaml`, `quickstart.md` (Phase 1)
- Constitution Check: Pass (pre-research and post-design). No gate errors, no unresolved clarifications.
- Extension hooks: none registered.
- Next: `/speckit-tasks`.

End: 2026-10-24T12:00:42Z

```console
$ git status --short
?? episodes/ep03/capture/forward-r2/02-plan.md
?? specs/002-idempotent-bookmark-save/contracts/
?? specs/002-idempotent-bookmark-save/data-model.md
?? specs/002-idempotent-bookmark-save/plan.md
?? specs/002-idempotent-bookmark-save/quickstart.md
?? specs/002-idempotent-bookmark-save/research.md
[exit 0]
```
