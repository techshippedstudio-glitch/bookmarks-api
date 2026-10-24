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
