# Research: Idempotent Duplicate Save

Feature: [spec.md](spec.md). Prior decisions this builds on:
[specs/001-bookmarks-api/research.md](../001-bookmarks-api/research.md), "Preventing duplicate
links" (unique index on `url_normalized` + `INSERT ... ON CONFLICT DO NOTHING RETURNING`).

No `NEEDS CLARIFICATION` items were left in the Technical Context. The decisions below cover the
design choices the change request leaves open.

## 1. How to return the existing bookmark race-safely

- **Decision**: Keep the single statement
  `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING *`. If it returns a row, commit and
  report `created=True` (201). If it returns nothing, end the transaction and `SELECT` the row by
  `url_normalized`, reporting `created=False` (200). If that `SELECT` finds nothing (the
  conflicting row was deleted between the two statements), retry the insert; at most 3 attempts.
- **Rationale**: Under PostgreSQL's default READ COMMITTED isolation, a concurrent insert of the
  same key makes the second `INSERT ... ON CONFLICT` wait for the first transaction; once the first
  commits, the second does nothing, and a fresh `SELECT` (new snapshot) sees the committed row. So
  of two concurrent saves exactly one inserts (201) and the other reads the same row (200). The
  unique index remains the only guard, so FR-001 holds without locks.
- **Alternatives considered**:
  - `ON CONFLICT DO UPDATE SET url_normalized = EXCLUDED.url_normalized RETURNING *, (xmax = 0)
    AS inserted`: returns the row in one statement, but performs a write (new row version) on every
    duplicate save, which conflicts in spirit with "the stored bookmark is not modified", and relies
    on the undocumented `xmax` trick. Rejected.
  - `SELECT` first, then `INSERT`: racy without extra locking; two concurrent saves can both miss
    the `SELECT`. Rejected.
  - `SERIALIZABLE` transaction or advisory lock: more moving parts for no gain over the unique
    index. Rejected.

## 2. How the route chooses 201 vs 200

- **Decision**: `repository.create_bookmark` returns `(BookmarkRow, created: bool)`. The route keeps
  `status_code=201` as its default and sets `response.status_code = 200` (FastAPI's injected
  `Response`) when `created` is false. The 200 response is declared in the route's `responses` with
  `model=Bookmark` so the generated OpenAPI documents both.
- **Rationale**: Same response model for both outcomes (Constitution I), status code carries the
  difference (spec Assumption 1). Minimal change to the existing route.
- **Alternatives considered**: returning `JSONResponse` manually (bypasses the response model);
  a separate endpoint (out of scope). Rejected.

## 3. What happens to `DuplicateUrlError` and `duplicate_url`

- **Decision**: Remove `DuplicateUrlError`, its 409 exception handler, the 409 entry on
  `POST /bookmarks`, and `duplicate_url` from the contract's error-code enum. The generic
  `409 -> "conflict"` mapping for framework `HTTPException`s in `STATUS_CODES` stays (it is not tied
  to duplicates).
- **Rationale**: Nothing raises it any more (spec SC-004: no save ever returns a conflict). Dead
  code and a documented-but-impossible response would make the contract lie (Constitution I).
- **Alternatives considered**: keep the class "just in case": rejected as dead code.

## 4. Validation before the duplicate check

- **Decision**: Unchanged request validation (`BookmarkCreate`) runs before the repository is called,
  so an invalid duplicate request still gets 422.
- **Rationale**: Spec FR-006 / Assumption 2; it is also what the existing FastAPI flow already does.
- **Alternatives considered**: skip validation of title/tags for duplicates: contradicts FR-006.
