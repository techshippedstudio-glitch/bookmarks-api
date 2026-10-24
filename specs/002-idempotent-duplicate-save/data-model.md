# Data Model: Idempotent Duplicate Save

No schema change. The `bookmarks` table, its columns and indexes are exactly as defined in
[specs/001-bookmarks-api/data-model.md](../001-bookmarks-api/data-model.md). No migration is
added.

## What this feature relies on

| Element | Defined in | Role in this feature |
| --- | --- | --- |
| `url_normalized` column, `UNIQUE` index `uq_bookmarks_url_normalized` | 001 data-model | The only guard that keeps one bookmark per normalized link, including under concurrent saves (spec FR-001, FR-005) |
| `url`, `title`, `tags`, `created_at`, `id` | 001 data-model | Returned unchanged on a duplicate save (spec FR-002, FR-003) |

## Save outcome (behavior, not stored)

A save now has two success outcomes instead of a success and a conflict error:

| Outcome | Condition | Stored data | HTTP status | Body |
| --- | --- | --- | --- | --- |
| Created | No row with the request's normalized link | New row inserted | 201 Created | The new `Bookmark` |
| Existing | A row with the request's normalized link exists (or a concurrent save inserted it first) | Nothing written; existing row untouched | 200 OK | The existing `Bookmark`, as stored |

Request validation (link, title, tags) is unchanged and happens before either outcome; an invalid
request is rejected with 422 `validation_error` in both cases.

## Superseded rule

`specs/001-bookmarks-api/data-model.md` and that spec's FR-004 describe a save of an existing link
as rejected with 409 `duplicate_url` and `details.existing_id`. That rejection is replaced by the
"Existing" outcome above (spec FR-002). The uniqueness rule itself is unchanged.
