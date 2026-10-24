# Data Model: Idempotent Duplicate Save

No change to stored data. The `bookmarks` table, its columns, constraints and indexes are as
defined in [specs/001-bookmarks-api/data-model.md](../001-bookmarks-api/data-model.md); no new
migration is needed.

## What this feature relies on

| Element | Role in this feature |
| --- | --- |
| `url_normalized` with `uq_bookmarks_url_normalized` (`UNIQUE`) | Still guarantees one bookmark per normalized link, including under concurrent saves (spec FR-001, FR-005). A save whose normalized link already exists is now answered with the existing row (200) instead of an error. |
| `id`, `url`, `title`, `tags`, `created_at` | Returned unchanged for a duplicate save; a duplicate save never writes to them (spec FR-003). |

## Save outcomes (replaces the duplicate rule of 001's FR-004)

| Request (valid) | Stored state afterwards | Response |
| --- | --- | --- |
| Normalized link not stored | One new row | 201 Created, the new bookmark |
| Normalized link already stored | Unchanged | 200 OK, the existing bookmark (request title and tags ignored) |
| Two concurrent saves, link not stored | Exactly one new row | One 201 and one 200, same bookmark |

Validation rules for link, title and tags are unchanged (001 data-model "Validation rules") and
run before the duplicate check.
