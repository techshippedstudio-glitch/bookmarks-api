# Data Model: Search Bookmarks by Title

Search stores nothing new. It reads the existing `bookmarks` table defined in
[specs/001-bookmarks-api/data-model.md](../001-bookmarks-api/data-model.md) and adds one index.

## Bookmark (existing, unchanged columns)

| Field | Used by search for |
| --- | --- |
| `title` | The words matched against the search (FR-001) |
| `tags` | The optional tag filter (FR-006), as in the list |
| `created_at`, `id` | Newest-first order and the keyset cursor (FR-005, FR-007) |

## Title words (derived, not stored)

The words of a title, and of a search, are computed by one SQL expression, used identically in
the index, on the title side of the query and on the search side:

```text
title_words(x) = array_remove(regexp_split_to_array(lower(x), '[^[:alnum:]]+'), '')
```

- Lowercased (FR-002).
- Split on every run of characters that are not letters or digits (clarification Q2).
- Empty pieces from leading or trailing separators removed.

Examples: "FastAPI: a tutorial" → `{fastapi, a, tutorial}`; "Spec-Kit guide" →
`{spec, kit, guide}`; "Learning PostgreSQL" → `{learning, postgresql}`.

### New index

| Name | Table | Method | Expression | Migration |
| --- | --- | --- | --- | --- |
| `ix_bookmarks_title_words` | `bookmarks` | GIN | `title_words(title)` as above | `0002` (upgrade creates, downgrade drops) |

## Search (request value, not stored)

| Field | Rule | Error when broken |
| --- | --- | --- |
| `q` | Required; 1 to 200 characters as sent; at least one letter or decimal digit | 422 `validation_error`, field `query.q` |
| words | `title_words(q)`: the same expression as titles, computed in the database | (derived) |
| `tag` | Optional; normalized and validated as in the list (`normalize_tag`) | 422, field `query.tag` |
| `limit` | 1 to 100, default 20 | 422, field `query.limit` |
| `cursor` | Optional; a `next_cursor` from the list or a search | 422, field `query.cursor` |
| `offset` | Not accepted (Constitution VI) | 422, field `query.offset`, message names `cursor` |

## Matching rule

A bookmark matches when `title_words(title) @> title_words(q)` and `cardinality(title_words(q)) > 0`
(its title contains every search word, as a whole word, in any order; a search the database splits
into no words matches nothing) and, if `tag` is given, `tags @> ARRAY[tag]`. Results are ordered by
`created_at DESC, id DESC`; the next page starts strictly after the cursor's `(created_at, id)`.

## State transitions

None. Search is read-only; a deleted bookmark simply stops matching.
