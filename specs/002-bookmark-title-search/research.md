# Research: Search Bookmarks by Title

No NEEDS CLARIFICATION remained in the Technical Context: the stack is fixed by the plan input
(existing FastAPI, SQLAlchemy 2, Alembic, PostgreSQL; no new runtime dependency) and the spec's
clarifications settle the behavior. Each decision records what was chosen, why, and what else was
considered. Measurements were taken on PostgreSQL 16.15 (C.UTF-8) inside a transaction that was
rolled back.

## Endpoint shape

- **Decision**: A new `GET /bookmarks/search` with query parameters `q` (required), `tag`,
  `limit`, `cursor`; response `BookmarkPage` (the list's page model).
- **Rationale**: Clarification Q1: search is its own request that requires words, and the list is
  unchanged (FR-001, FR-011). Under `/bookmarks` it reads as a view of the same collection, and
  sharing the page model makes "pages the same way the bookmark list does" literal. The path does
  not clash with `DELETE /bookmarks/{bookmark_id}` (different method; `search` is not an int).
- **Alternatives considered**: `GET /bookmarks?q=` (rejected by Q1: a missing `q` must be an error,
  not the full list); `POST /bookmarks/search` with a JSON body (a read should be a cacheable GET,
  and the list already uses query parameters).

## What a word is, and case

- **Decision**: Lowercase, then split on every run of characters that are not letters or digits;
  drop empty pieces. In SQL: `array_remove(regexp_split_to_array(lower(title), '[^[:alnum:]]+'), '')`.
  In Python, for the search: `re.findall(r"[^\W_]+", q.lower())`, de-duplicated.
- **Rationale**: Clarification Q2 (letters of any alphabet and digits; everything else separates)
  and FR-002 (ignore case). `lower()` and `[[:alnum:]]` follow the database's character type, so
  "Ünï" and "ΣΟΦΙΑ" lowercase and split correctly (verified: `' FastAPI: a tutorial — Spec-Kit_guide
  Python3 Ünï '` → `{fastapi,a,tutorial,spec,kit,guide,python3,ünï}`). `[^\W_]` is Python's
  "word character except underscore", the same set for letters and decimal digits.
- **Known difference**: Python counts a few numeric symbols (for example "½") as alphanumeric where
  PostgreSQL's `[[:alnum:]]` does not. Such a search word appears in no title's word list, so the
  search returns nothing; it can never widen a search. Accepted as a documented edge.
- **Alternatives considered**: PostgreSQL full-text search (`to_tsvector('simple', title)`): its
  parser keeps "spec-kit" as a hyphenated token plus parts and treats URLs, emails and numbers
  specially, which contradicts Q2's single rule; `ILIKE '%word%'` (matches inside words, violating
  FR-004, and needs `pg_trgm` for speed); `~* '\mword\M'` regex (whole-word, but one regex per word,
  needs escaping, and no index).

## Matching: all words, whole words

- **Decision**: `title_words(title) @> ARRAY[:w1, :w2, ...]` (array containment).
- **Rationale**: Containment is exactly "the title has every search word, in any order" (FR-003,
  Q1 of specify) with whole-word equality (FR-004). Repeated search words are harmless; Python
  de-duplicates them anyway.
- **Alternatives considered**: `&&` (overlap, means "any word": rejected by FR-003); a phrase match
  (rejected by the specify answer).

## Index and performance (SC-004)

- **Decision**: GIN expression index `ix_bookmarks_title_words` on the same `title_words(title)`
  expression, created in Alembic revision `0002` and declared in `models.py`. The query must use
  the identical expression with literal (not bound) pattern constants so the planner matches the
  index.
- **Rationale**: All functions in the expression are IMMUTABLE (`lower`, `regexp_split_to_array`,
  `array_remove`), so PostgreSQL accepts the expression index. Measured with 100,000 bookmarks
  (1,000 matching): first page (`LIMIT 21`, two words) 6.5 ms via Bitmap Index Scan + top-N sort;
  `count(*)` 4.1 ms. Well under SC-004's one second.
- **Alternatives considered**: a stored generated `title_words` column (duplicates data, larger
  migration, same index); no index (sequential scan with a regex per row; fine at 1k rows, risky at
  100k).

## Request model and validation

- **Decision**: `BookmarkSearchQuery(BookmarkListQuery)` adds `q: str` with `min_length=1`,
  `max_length=200` and a validator that requires at least one word (FR-008). It inherits `limit`
  (1-100, default 20), `cursor` (validated by `decode_cursor`) and `tag` (normalized by
  `normalize_tag`), so FR-009's "same errors" holds by construction. The route also takes the
  existing `reject_offset` dependency.
- **Rationale**: Constitution I (explicit request model) and the existing pattern (T037 in 001
  introduced `BookmarkListQuery` bound with `Query()`). Inheritance keeps one definition of each
  shared rule.
- **Alternatives considered**: separate `Query(...)` parameters on the route (no request model;
  duplicates the list's rules).

## Repository

- **Decision**: Give `repository.list_bookmarks` an optional keyword `words: Sequence[str] | None =
  None`; when given, add the containment condition to both the count and the page query.
- **Rationale**: Search is the list with one more condition: same order, keyset, `limit + 1`
  look-ahead and `total`. One function keeps them from drifting; the default `None` leaves the list
  exactly as it is (FR-011), which the existing tests prove.
- **Alternatives considered**: a separate `search_bookmarks` function (duplicates the keyset and
  count logic).

## Paging, total and cursor reuse

- **Decision**: Same keyset `(created_at, id) < cursor` and opaque cursor from `cursor.py`; `total`
  is `COUNT(*)` with the search and tag conditions. A cursor from one search used with another is
  accepted as a position (clarification Q3).
- **Rationale**: Constitution VI; FR-007; matches the list's behavior exactly.
- **Alternatives considered**: a cursor that embeds the search and tag and rejects mismatches
  (rejected by Q3).

## Errors

- **Decision**: No new error codes. Every invalid input is a 422 `validation_error` through the
  existing `RequestValidationError` handler, with `details[].field` such as `query.q`.
- **Rationale**: Constitution III; FR-010.

## Dependencies (Constitution IV)

No change to `pyproject.toml` or `uv.lock`. The search uses the standard library `re` module and
built-in PostgreSQL functions.
