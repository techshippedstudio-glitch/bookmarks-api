# Research: Bookmark Title Search

Technical Context had no NEEDS CLARIFICATION items: the stack is fixed by the plan input and the
spec's Clarifications session settled token reuse, the speed target and word length. Each decision
below records what was chosen, why, and what else was considered.

## Endpoint shape

- **Decision**: A new endpoint `GET /bookmarks/search` with a required `q` plus the list's `tag`,
  `limit` and `cursor`, returning the existing `BookmarkPage`.
- **Rationale**: The spec requires an empty or blank search to be an error, "not treated as no
  search"; a required `q` on its own endpoint says that in the contract. `GET /bookmarks` keeps
  working exactly as today (spec Assumptions). The route is declared before
  `DELETE /bookmarks/{bookmark_id}`; that route only accepts DELETE and an integer, so there is no
  path clash either way.
- **Alternatives considered**: an optional `q` on `GET /bookmarks` (one endpoint, but `q=` would
  have to mean "error" while a missing `q` means "list everything", and the list's contract
  changes); `POST /bookmarks/search` with a body (not cacheable, and unlike the list's query style).

## Matching rule

- **Decision**: Split `q` on whitespace into words, drop empty pieces and repeats; a bookmark
  matches when its title contains every word, compared without letter case. In SQL each word is
  `title ILIKE '%' || word || '%' ESCAPE '/'` with `%`, `_` and the escape character escaped,
  produced by SQLAlchemy `BookmarkRow.title.icontains(word, autoescape=True)`; the conditions are
  ANDed.
- **Rationale**: Implements FR-001 to FR-003 and FR-008 directly (substring match per Clarification
  answer "A" in specify, all words, any order, literal characters). `autoescape=True` makes `%`,
  `_` and `/` literal without hand-written escaping. PostgreSQL case folding follows the database's
  character type (`C.UTF-8` here), so accented capitals fold too ("ÉCOLE" matches "école"), while
  accents themselves are not ignored, as the spec assumes.
- **Alternatives considered**: PostgreSQL full-text search (`to_tsvector`/`plainto_tsquery`): it
  stems and drops stop words, so "post" would not find "Postgres" and results differ from the
  spec's substring rule; regular expressions (`~*`) need escaping of many more characters; Python
  side filtering (breaks paging and totals).

## Search input validation

- **Decision**: `q` is a string of at most 200 characters (checked on the raw value) that must
  contain at least one non-space character; there is no minimum word length (Clarification). The
  parser is a pure function `search_words(q) -> list[str]` in `normalize.py`, called from a
  `field_validator` on `BookmarkSearchQuery`, so a bad `q` is a `RequestValidationError` and comes
  out as the standard 422 `validation_error` with `details[0].field == "query.q"`.
- **Rationale**: Same pattern as the `tag` and `cursor` validators on `BookmarkListQuery`; the pure
  function gets fast unit tests (Constitution V).
- **Alternatives considered**: validating in the route (a second error path outside the model,
  against Constitution I's spirit); a regex-only Field constraint (cannot de-duplicate words).

## Ordering, paging and totals

- **Decision**: Reuse `repository.list_bookmarks` by adding a keyword argument `title_words:
  list[str] | None = None`. Its conditions (tag containment plus title words) feed both the
  `COUNT(*)` for `total` and the page query; the page query keeps
  `ORDER BY created_at DESC, id DESC`, `(created_at, id) < cursor` and `LIMIT limit + 1`. The route
  builds `next_cursor` with the existing `encode_cursor`, and `BookmarkListQuery`'s cursor
  validator rejects malformed tokens. `reject_offset` is attached to the new route.
- **Rationale**: FR-005 and FR-007 say "the same way the bookmark list does"; sharing the query
  makes that true by construction. Per the clarified token rule, the cursor is a position only and
  is not bound to `q` or `tag`, exactly like the list's cursor.
- **Alternatives considered**: a separate `search_bookmarks` repository function (duplicates the
  paging logic that would then have to be kept in step); binding the cursor to a hash of `q` and
  `tag` (rejected by the clarification).

## Index and performance

- **Decision**: No new index and no migration. The page query walks `ix_bookmarks_created_at_id`
  in order and filters titles; the count scans at most 10,000 short titles. A timing test seeds
  10,000 bookmarks and checks a search answers in under 1 second (SC-006).
- **Rationale**: A sequential scan of 10,000 rows with `ILIKE` on titles of at most 200 characters
  takes a few milliseconds on PostgreSQL 16; an index would add a migration and an extension for no
  measurable gain at this scale.
- **Alternatives considered**: a `pg_trgm` GIN index on `title` (`gin_trgm_ops`): speeds substring
  search on very large tables, but needs `CREATE EXTENSION pg_trgm` in a migration and helps little
  for one- and two-character words; revisit if the collection grows by orders of magnitude.

## Dependencies (Constitution IV)

No new dependency. `icontains(..., autoescape=True)` is part of SQLAlchemy 2.0, already a runtime
dependency; word splitting uses `str.split`.
