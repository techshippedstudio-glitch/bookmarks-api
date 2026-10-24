# Research: Idempotent Duplicate Save

Phase 0 output for [plan.md](plan.md). The Technical Context has no NEEDS CLARIFICATION items; the
decisions below record how the change fits the design of
[specs/001-bookmarks-api](../001-bookmarks-api/research.md) ("Preventing duplicate links").

## Returning the existing bookmark on a duplicate save

- **Decision**: Keep `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING *`. If a row is
  returned, commit and return `(row, created=True)`. If nothing is returned, roll back the empty
  transaction, `SELECT` the row by `url_normalized` and return `(row, created=False)`. The route
  sets 201 or 200 from `created`.
- **Rationale**: The unique index remains the single arbiter of "new or existing", so the change
  cannot introduce duplicates. Under PostgreSQL's default READ COMMITTED isolation, a racing insert
  blocks on the index until the winner commits, then `DO NOTHING` returns no row, and the following
  `SELECT` (new snapshot) sees the winner's committed row. One request gets 201, the other 200 with
  the same row (spec FR-004, US2).
- **Alternatives considered**:
  - `ON CONFLICT DO UPDATE SET url_normalized = EXCLUDED.url_normalized RETURNING *, (xmax = 0)`
    to get the row in one statement: works, but writes a new row version on every duplicate save
    (the stored bookmark is "not modified" logically, but the row is rewritten) and relies on the
    `xmax` system column trick; rejected for clarity.
  - Check-then-insert (`SELECT` first): races under concurrency; rejected (same reason as 001).
  - Catch `IntegrityError`: aborts the transaction; rejected (same reason as 001).

## Row deleted between the conflict and the lookup

- **Decision**: If the follow-up `SELECT` finds nothing (the conflicting bookmark was deleted in
  between), retry the insert. Bound the loop to 3 attempts; on exhaustion raise an internal error
  (500 envelope).
- **Rationale**: Without a retry the endpoint could crash on `None`; with it the save simply
  becomes a new bookmark (201), matching 001 US4 scenario 3 ("save after delete creates a new
  bookmark"). Three attempts is far beyond any realistic interleaving for a single user.
- **Alternatives considered**: Returning 409 or 404 in this window (reintroduces an error for a
  valid save); unbounded loop (no termination guarantee).

## Response status and contract

- **Decision**: Declare `status_code=201` as the route default, inject `Response` and set
  `response.status_code = 200` when `created` is false. Declare `200: {"model": Bookmark}` in the
  route's `responses`, and remove the 409 entry, so `/openapi.json` documents both outcomes with the
  `Bookmark` schema (Constitution I).
- **Rationale**: Same body model in both cases; status distinguishes created from existing (spec
  Assumptions). FastAPI keeps typed serialization through `response_model=Bookmark`.
- **Alternatives considered**: Returning a `JSONResponse` manually (bypasses the response model);
  adding a `created: bool` body field (changes the `Bookmark` shape, not asked for).

## Removing the duplicate error

- **Decision**: Delete `DuplicateUrlError`, its 409 handler and the `duplicate_url` error code from
  the contract. Keep the generic `409: "conflict"` entry in the HTTP-status code map (it only names
  framework `HTTPException`s and costs nothing).
- **Rationale**: Dead code would suggest a behavior that no longer exists; the spec says the
  duplicate case no longer produces any error (spec Edge Cases, SC-004).
- **Alternatives considered**: Keeping the exception "for later" (unused code, misleading).

## Validation before the duplicate check

- **Decision**: Unchanged: `BookmarkCreate` validation runs in FastAPI before the handler, so an
  invalid title or tags on a duplicate save still returns 422 (spec FR-005).
- **Rationale**: Matches 001 and the spec assumption; the request is never silently accepted with
  bad input.

## Contract file for this feature

- **Decision**: `contracts/openapi.yaml` in this folder is a complete copy of the API contract with
  the `POST /bookmarks` changes applied, and states that it supersedes
  `specs/001-bookmarks-api/contracts/openapi.yaml` for that operation.
- **Rationale**: Flow-forward keeps 001 as a historical record; a full contract here gives one
  readable current design contract instead of a partial delta that must be mentally merged.
- **Alternatives considered**: A delta contract with only `POST /bookmarks` (smaller, but readers
  must combine two files to know the current API).
