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
