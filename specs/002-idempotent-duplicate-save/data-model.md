# Data Model: Idempotent Duplicate Save

No storage change. The `bookmarks` table, its columns, constraints and indexes are exactly as
defined in [specs/001-bookmarks-api/data-model.md](../001-bookmarks-api/data-model.md); no
migration is added.

## What this feature relies on

| Element (from 001) | Role in this feature |
| --- | --- |
| `url_normalized` with `UNIQUE (url_normalized)` (`uq_bookmarks_url_normalized`) | Decides "new or existing" for every save, including two saves at the same moment (spec FR-004) |
| `created_at` | Not touched by a duplicate save, so the bookmark keeps its place in the newest-first list (spec Edge Cases) |
| `title`, `tags`, `url` | Never written by a duplicate save; the request's title and tags are ignored (spec FR-002) |

## Save outcome (not stored)

| Outcome | Condition | HTTP status | Body |
| --- | --- | --- | --- |
| created | No row has the request's `url_normalized`; a new row is inserted | 201 Created | the new `Bookmark` |
| existing | A row with the same `url_normalized` already exists | 200 OK | the existing `Bookmark`, unchanged |

Validation rules for the request (link, title, tags) are unchanged from 001 and run before the
outcome is decided (spec FR-005).
