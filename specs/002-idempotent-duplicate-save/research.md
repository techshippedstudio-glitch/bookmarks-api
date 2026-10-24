# Research: Idempotent Duplicate Save

Phase 0 for [plan.md](plan.md). The Technical Context has no `NEEDS CLARIFICATION` items; the
decisions below cover how to implement the spec's requirements in the existing code. They replace
the "Preventing duplicate links" decision in
[specs/001-bookmarks-api/research.md](../001-bookmarks-api/research.md) for what a duplicate save
returns; the uniqueness mechanism itself is kept.

## Returning the existing bookmark on a duplicate save

- **Decision**: Keep `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`. If a row is
  returned, commit and report `created=True`. If nothing is returned, end the transaction and
  `SELECT` the row by `url_normalized`, then report `created=False` with that row.
  `create_bookmark` returns `(row, created)`.
- **Rationale**: The unique index still guarantees one bookmark per normalized link under
  concurrency (spec FR-001, FR-005). `DO NOTHING` never touches the stored row, so title, tags and
  saved time stay unchanged (FR-003).
- **Alternatives considered**: `ON CONFLICT DO UPDATE SET url_normalized = EXCLUDED.url_normalized
  RETURNING *, (xmax = 0) AS inserted` returns the row in one statement but performs an UPDATE on
  every duplicate save (new row version, fires on any future trigger), which goes against "the
  stored bookmark is not modified"; rejected. Check-then-insert races; rejected.

## Concurrent saves of the same new link

- **Decision**: Rely on PostgreSQL's behavior under READ COMMITTED: when two inserts race on the
  same unique key, the second waits for the first to commit, then `DO NOTHING` returns no row; the
  follow-up `SELECT` runs as a new statement (new snapshot) and sees the committed row. Result: one
  201 and one 200 with the same bookmark.
- **Edge**: if the row disappears between the conflict and the lookup (a delete in between), the
  lookup returns nothing; the repository then retries the insert (bounded, 3 attempts) so the
  request still ends as 201 or 200.
- **Alternatives considered**: SERIALIZABLE isolation with retries (heavier, not needed);
  advisory locks (extra moving part).

## HTTP status selection and OpenAPI

- **Decision**: The route keeps `status_code=201` as its default and takes a FastAPI `Response`
  parameter; it sets `response.status_code = 200` when `created` is false. `responses=` declares
  `200: {"model": Bookmark, "description": "This link was already saved; the existing bookmark,
  unchanged."}` and the shared 422; the 409 entry is removed.
- **Rationale**: Same `Bookmark` model for both outcomes (Constitution I); the generated OpenAPI
  lists 200, 201 and 422 for `POST /bookmarks` (spec FR-007).
- **Alternatives considered**: returning `JSONResponse` directly (bypasses response-model
  serialization); a response header or body flag to mark "existing" (not requested; status code
  is enough).

## Removing the duplicate error

- **Decision**: Delete `DuplicateUrlError` and its exception handler; drop `duplicate_url` from
  the documented error codes for `POST /bookmarks`. Keep `409: "conflict"` in the generic
  status-to-code map of `errors.py`, which serves Starlette HTTP exceptions in general.
- **Rationale**: No code path raises it any more; dead error paths mislead readers. The spec only
  removes the conflict outcome for saving.
- **Alternatives considered**: keeping the exception "for later" (unused code; rejected).

## Validation order

- **Decision**: Unchanged: Pydantic validates the request body before the route runs, so an
  invalid request for an already saved link still returns 422 (spec FR-006).
