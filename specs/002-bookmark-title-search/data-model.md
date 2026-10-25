# Data Model: Bookmark Title Search

Search stores nothing. It reads the existing `bookmarks` table, defined in
[../001-bookmarks-api/data-model.md](../001-bookmarks-api/data-model.md), which this feature does
not change (no new column, index or migration; see [research.md](research.md), "Index and
performance").

## Entities

### Bookmark (existing, read only)

| Field used | Column | How search uses it |
| --- | --- | --- |
| `title` | `title varchar(200)` | Matched against every search word, case-insensitively, as a substring |
| `tags` | `tags text[]` | Optional tag filter `tags @> ARRAY[:tag]` (unchanged) |
| `created_at`, `id` | `created_at timestamptz`, `id bigint` | Order `created_at DESC, id DESC` and the keyset cursor (unchanged) |

Results are returned with every `Bookmark` field (`id`, `url`, `title`, `tags`, `created_at`), the
same as the list (FR-010).

### Search request (`BookmarkSearchQuery`, not stored)

Extends the list's request model `BookmarkListQuery`.

| Field | Type | Rule | Source |
| --- | --- | --- | --- |
| `q` | string, required | 1 to 200 characters; must contain a non-space character; split on whitespace into words, empty pieces and repeated words dropped; no minimum word length | FR-001, FR-003, FR-004, Clarifications |
| `tag` | string, optional | Normalized and validated exactly like the list's tag filter | FR-006 |
| `limit` | integer, optional | 1 to 100, default 20 | FR-007 |
| `cursor` | string, optional | A `next_cursor` from a previous page; must decode to a time and an id | FR-007 |
| `offset` | — | Not accepted; sending it returns 422 pointing to `cursor` | FR-007, Constitution VI |

### Search words (derived, not stored)

`search_words(q)` returns the list of distinct words in the order they first appear. Example:
`"  Postgres   guide postgres "` → `["Postgres", "guide"]`. Case is left as typed; the comparison
itself ignores case, so `"Postgres"` and `"postgres"` count as the same word for de-duplication.

## Matching rule

A bookmark matches when, for every search word `w`, `lower(title)` contains `lower(w)` as a
substring, with every character of `w` taken literally (`%`, `_` and `/` are escaped). The tag
filter, when given, is ANDed. `total` counts all matching bookmarks; the page holds up to `limit` of
them after the cursor position.

## Lifecycle

No state changes: a search never creates, changes or deletes a bookmark (FR-011).
