# Data Model: Bookmarks API

One table holds everything the feature needs. Tags are stored on the bookmark as a normalized
array (see [research.md](research.md), "Tags storage and filtering"). What the spec calls the
bookmark's "link" is the `url` field in the API and the database.

## Table `bookmarks`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigint` | primary key, generated always as identity | Identifier returned to the user and used for delete |
| `url` | `varchar(2048)` | not null | The link exactly as the user gave it |
| `url_normalized` | `varchar(2048)` | not null, **unique** | Normalized link used for duplicate detection; a save whose normalized link exists returns the existing row (FR-004) |
| `title` | `varchar(200)` | not null, `char_length(title) >= 1` | Trimmed before saving |
| `tags` | `text[]` | not null, default `'{}'`, `cardinality(tags) <= 10` | Normalized, de-duplicated, sorted |
| `created_at` | `timestamptz` | not null, default `now()` | The saved time (FR-003) |

### Indexes

| Name | Definition | Serves |
| --- | --- | --- |
| `bookmarks_pkey` | `PRIMARY KEY (id)` | Delete by id |
| `uq_bookmarks_url_normalized` | `UNIQUE (url_normalized)` | No duplicate links, even under concurrent saves (FR-004) |
| `ix_bookmarks_created_at_id` | `(created_at DESC, id DESC)` | Newest-first listing and paging (FR-006) |
| `ix_bookmarks_tags` | `GIN (tags)` | Tag filter `tags @> ARRAY[:tag]` (FR-007) |

## Validation rules (applied in the API before the database)

| Field | Rule | Source |
| --- | --- | --- |
| `url` | Required; http or https scheme with a host; at most 2048 characters | FR-002 |
| `title` | Required; 1 to 200 characters after trimming | FR-002 |
| `tags` | Optional list; each trimmed and lowercased; must match `^[a-z0-9-]{1,30}$`; duplicates removed; at most 10 after de-duplication | FR-011, FR-001 |
| `limit` | Integer 1 to 100, default 20 | FR-006 |
| `cursor` | Optional opaque token from a previous page's `next_cursor`; must decode to a timestamp and an id | FR-006 |
| `offset` | Not accepted (Constitution VI); sending it returns 422 | FR-006 |
| `tag` (filter) | Normalized like a tag; must be a valid tag | FR-007 |

The database constraints (`varchar` lengths, unique index, cardinality check) are a second line of
defense; the API rejects invalid input with a 422 before it reaches the database.

## Link normalization

`url_normalized` is derived from `url`:

1. Lowercase the scheme and the host.
2. Remove the port if it is the default for the scheme (80 for http, 443 for https).
3. Remove trailing slashes from the path.
4. Remove the fragment (`#...`).
5. Keep the query string exactly as given.

Examples: `HTTPS://Example.com:443/docs/#intro` → `https://example.com/docs`;
`https://example.com/search?q=FastAPI` keeps `?q=FastAPI`.

## Lifecycle

A bookmark is created by a save and removed by a delete; there is no update in this version.
Saving a link whose normalized form already exists does not create or change a row: the existing
row is returned as it is, with 200 OK instead of 201 Created, and the request's title and tags are
ignored (FR-004, revised 2026-10-24). No schema change is needed for this rule.
Deleting a bookmark frees its normalized link, so the same link can be saved again (User Story 4,
scenario 3).
