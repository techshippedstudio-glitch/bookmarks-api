# Step 01 — spec (manual edit of spec.md)

Start: 2026-10-24T11:58:24Z


```console
$ git status --short && git rev-parse HEAD && git describe --tags
?? episodes/
c997fe2c9df70e0facd230eaf8dda37fcbca846c
ep03-start
[exit 0]
```

```console
$ grep -n -i -E 'duplicate|conflict|409|same link|already' specs/001-bookmarks-api/spec.md
9:**Input**: User description: "Build a bookmarks API. A user can save a link with a title and optional tags, list their bookmarks newest first, filter by tag, and delete a bookmark. Saving the same URL twice must not create a duplicate."
15:- Q: When someone saves a link that is already bookmarked, what should happen? → A: Reject it with a conflict error that includes the existing bookmark's identifier; the existing bookmark is left unchanged.
16:- Q: Which links count as "the same link"? → A: Links that match after normalization: scheme and host lowercased, default port removed, trailing slash on the path removed, fragment (#...) removed; the query string is kept as is.
17:- Q: How should tags be cleaned up and limited? → A: Trim spaces, lowercase, drop duplicates; 1 to 30 characters of letters, digits and hyphens; at most 10 tags per bookmark.
46:   a conflict error that includes the existing bookmark's identifier.
118:3. **Given** a bookmark was deleted, **When** the user saves the same link again, **Then** it is
125:- Saving a link that is already bookmarked, even with a different title or tags, is rejected with
126:  a conflict error that includes the existing bookmark's identifier; the existing bookmark is not
129:  for https), a trailing slash on the path, or a fragment are the same link. Links with different
135:- Two saves of the same link at the same moment still leave exactly one bookmark.
152:- **FR-004**: System MUST NOT store two bookmarks for the same link, where links are compared after
154:  fragment removed, query kept). A save of an existing link MUST be rejected with a conflict error
170:- **FR-011**: System MUST normalize tags by trimming spaces, lowercasing and removing duplicates,
188:- **SC-002**: Saving the same link any number of times, in any of its equivalent forms, always
[exit 0]
```

```console
$ git diff -- specs/001-bookmarks-api/spec.md
diff --git a/specs/001-bookmarks-api/spec.md b/specs/001-bookmarks-api/spec.md
index 3ed7b96..27a9a3d 100644
--- a/specs/001-bookmarks-api/spec.md
+++ b/specs/001-bookmarks-api/spec.md
@@ -12,7 +12,7 @@
 
 ### Session 2026-10-21
 
-- Q: When someone saves a link that is already bookmarked, what should happen? → A: Reject it with a conflict error that includes the existing bookmark's identifier; the existing bookmark is left unchanged.
+- Q: When someone saves a link that is already bookmarked, what should happen? → A: Reject it with a conflict error that includes the existing bookmark's identifier; the existing bookmark is left unchanged. *(Superseded 2026-10-24 by the change request below; see FR-004.)*
 - Q: Which links count as "the same link"? → A: Links that match after normalization: scheme and host lowercased, default port removed, trailing slash on the path removed, fragment (#...) removed; the query string is kept as is.
 - Q: How should tags be cleaned up and limited? → A: Trim spaces, lowercase, drop duplicates; 1 to 30 characters of letters, digits and hyphens; at most 10 tags per bookmark.
 - Q: How should the list behave when there are many bookmarks? → A: Return pages: 20 per page by default, up to 100 per page, using a limit and an offset, plus the total count.
@@ -22,6 +22,13 @@
 
 - Q: Principle VI forbids offset pagination. How does a client ask for the next page? → A: Each page returns an opaque next-page token (none on the last page); the client passes it back to get the next page. The offset option is removed, and a request that still sends it gets a validation error that points to the token.
 
+### Change request 2026-10-24 (duplicate saves)
+
+- Saving a link that is already bookmarked is no longer rejected. If the link (after the existing
+  normalization rules) is already saved, the existing bookmark is returned unchanged with HTTP 200
+  OK instead of a 409 conflict; the title and tags sent in the new request are ignored. Saving a
+  new link still returns 201 Created. This replaces the duplicate rule in FR-004.
+
 ## User Scenarios & Testing *(mandatory)*
 
 ### User Story 1 - Save a bookmark (Priority: P1)
@@ -42,8 +49,10 @@ contains the saved link, title, tags and the time it was saved.
 2. **Given** no bookmarks exist, **When** the user saves a link with a title and the tags "Python",
    " api " and "python", **Then** the bookmark is returned with the tags "api" and "python".
 3. **Given** a bookmark for `https://example.com/docs` exists, **When** the user saves
-   `HTTPS://Example.com/docs/#intro`, **Then** no second bookmark is created and the user receives
-   a conflict error that includes the existing bookmark's identifier.
+   `HTTPS://Example.com/docs/#intro` with a different title and tags, **Then** no second bookmark
+   is created, the stored bookmark is not modified, and the user receives the existing bookmark
+   unchanged (same identifier, link, title, tags and saved time) with HTTP 200 OK instead of
+   201 Created.
 4. **Given** any state, **When** the user tries to save a bookmark without a link or without a
    title, with a link that is not a valid http or https address, with a title over 200 characters,
    with more than 10 tags, or with an invalid tag, **Then** nothing is saved and the user receives
@@ -122,9 +131,10 @@ appears in the list.
 
 ### Edge Cases
 
-- Saving a link that is already bookmarked, even with a different title or tags, is rejected with
-  a conflict error that includes the existing bookmark's identifier; the existing bookmark is not
-  changed.
+- Saving a link that is already bookmarked, even with a different title or tags, is not an error:
+  the existing bookmark is returned unchanged with HTTP 200 OK; the title and tags in the new
+  request are ignored and the stored bookmark is not modified. Saving a new link returns
+  201 Created.
 - Links that differ only in scheme or host letter case, a default port (`:80` for http, `:443`
   for https), a trailing slash on the path, or a fragment are the same link. Links with different
   query strings are different links.
@@ -132,7 +142,8 @@ appears in the list.
   kept once.
 - A tag that is empty after trimming, longer than 30 characters, or contains characters other
   than letters, digits and hyphens is rejected.
-- Two saves of the same link at the same moment still leave exactly one bookmark.
+- Two saves of the same new link at the same moment still leave exactly one bookmark: one gets
+  201 Created and the other gets 200 OK with the same bookmark.
 - A malformed next-page token (one that does not decode to a position in the list) is rejected with
   a validation error.
 - A request that sends the removed offset option is rejected with a validation error that names the
@@ -151,9 +162,12 @@ appears in the list.
 - **FR-003**: System MUST record the time each bookmark was saved.
 - **FR-004**: System MUST NOT store two bookmarks for the same link, where links are compared after
   normalization (scheme and host lowercased, default port removed, trailing path slash removed,
-  fragment removed, query kept). A save of an existing link MUST be rejected with a conflict error
-  that includes the existing bookmark's identifier, and MUST hold even when two saves happen at
-  the same moment.
+  fragment removed, query kept). A save of a link that is already saved MUST NOT be rejected: it
+  MUST return the existing bookmark unchanged with HTTP 200 OK, ignoring the title and tags in the
+  request and leaving the stored bookmark unmodified. A save of a new link MUST return
+  201 Created. This MUST hold even when two saves of the same new link happen at the same moment:
+  exactly one bookmark is stored, one save gets 201 Created and the other gets 200 OK with the
+  same bookmark.
 - **FR-005**: System MUST return the saved bookmark, including an identifier the user can use to
   delete it.
 - **FR-006**: System MUST list bookmarks ordered by saved time, most recent first, in pages of 20
[exit 0]
```

```console
$ grep -n -i -E 'duplicate|conflict|409|unique|concurren' specs/001-bookmarks-api/plan.md specs/001-bookmarks-api/research.md specs/001-bookmarks-api/data-model.md specs/001-bookmarks-api/quickstart.md specs/001-bookmarks-api/contracts/openapi.yaml
specs/001-bookmarks-api/plan.md:12:with no duplicate links after normalization. Built as a FastAPI service with Pydantic request and
specs/001-bookmarks-api/plan.md:14:migrations. Uniqueness is enforced by a unique index on the normalized link, so it holds under
specs/001-bookmarks-api/plan.md:15:concurrent saves; tags are a normalized `text[]` column with a GIN index for filtering. All errors
specs/001-bookmarks-api/plan.md:52:| III. Consistent Error Shape | One envelope `{"error": {"code", "message", "details"}}` for validation (422), not found (404) and duplicate (409), installed as global exception handlers | Pass |
specs/001-bookmarks-api/research.md:36:## Preventing duplicate links
specs/001-bookmarks-api/research.md:39:  unique index. Insert with `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING ...`; if
specs/001-bookmarks-api/research.md:40:  nothing is returned, look up the existing row and raise a duplicate error carrying its id.
specs/001-bookmarks-api/research.md:41:- **Rationale**: The database guarantees uniqueness even when two saves race (spec edge case);
specs/001-bookmarks-api/research.md:42:  `ON CONFLICT` avoids relying on catching exceptions mid-transaction.
specs/001-bookmarks-api/research.md:43:- **Alternatives considered**: check-then-insert in application code (races under concurrency);
specs/001-bookmarks-api/research.md:55:  trailing slash to bare hosts, which conflicts with storing the link as given and with our
specs/001-bookmarks-api/research.md:87:  `validation_error` (422), `not_found` (404), `duplicate_url` (409, `details.existing_id`).
specs/001-bookmarks-api/data-model.md:13:| `url_normalized` | `varchar(2048)` | not null, **unique** | Normalized link used for duplicate detection (FR-004) |
specs/001-bookmarks-api/data-model.md:15:| `tags` | `text[]` | not null, default `'{}'`, `cardinality(tags) <= 10` | Normalized, de-duplicated, sorted |
specs/001-bookmarks-api/data-model.md:23:| `uq_bookmarks_url_normalized` | `UNIQUE (url_normalized)` | No duplicate links, even under concurrent saves (FR-004) |
specs/001-bookmarks-api/data-model.md:33:| `tags` | Optional list; each trimmed and lowercased; must match `^[a-z0-9-]{1,30}$`; duplicates removed; at most 10 after de-duplication | FR-011, FR-001 |
specs/001-bookmarks-api/data-model.md:39:The database constraints (`varchar` lengths, unique index, cardinality check) are a second line of
specs/001-bookmarks-api/quickstart.md:39:| 2 | `POST /bookmarks` `{"url": "HTTPS://FastAPI.tiangolo.com", "title": "Again"}` | 409 `duplicate_url`, `details.existing_id` = id from step 1 |
specs/001-bookmarks-api/contracts/openapi.yaml:25:        '409':
specs/001-bookmarks-api/contracts/openapi.yaml:109:        tags: { type: array, items: { type: string }, description: Normalized, unique, sorted }
specs/001-bookmarks-api/contracts/openapi.yaml:129:              enum: [validation_error, not_found, duplicate_url, internal_error]
[exit 0]
```

## What changed in this step

Only `specs/001-bookmarks-api/spec.md` was edited (by hand, via a scripted exact-string replace):
the 2026-10-21 duplicate clarification was marked superseded (kept as history), a
"Change request 2026-10-24" note was added under Clarifications, and US1 acceptance scenario 3,
the duplicate edge case, the concurrent-save edge case and FR-004 were rewritten to the new
behavior. Nothing else was changed (plan, research, data model, contract, quickstart, tasks, code
and tests untouched in this step).

## Rationale in the current plan.md worth preserving (written before plan is rerun)

From plan.md (and the research.md decisions it points to):

1. **Uniqueness is enforced by the database, not the app**: "Uniqueness is enforced by a unique
   index on the normalized link, so it holds under concurrent saves" (plan Summary). This is
   still exactly what the new rule needs: two concurrent saves of the same new link must store
   one row. Keep `uq_bookmarks_url_normalized`.
2. **`INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING` then look up the existing row**
   (research.md, "Preventing duplicate links"), chosen over check-then-insert (races) and over
   catching `IntegrityError` (aborted transaction, noisier). The same mechanism gives 201 vs 200
   cleanly: rows returned → 201; nothing returned → select the existing row → 200. Only the last
   step changes (return the row instead of raising `DuplicateUrlError`).
3. **Store the link as given plus `url_normalized`** (Summary / data-model): needed so the 200
   response returns the existing bookmark's original `url`, not the new request's spelling.
4. **One error envelope for every error class** (Constitution III row): still applies to 422/404/500;
   the 409 `duplicate_url` entry no longer has a producer on `POST /bookmarks` and must be
   dropped from the Constitution Check row, the contract and the error-code enum (or explicitly
   kept as unused) — a decision for the plan step.
5. **Technical Context / dependency justification (Constitution IV)**: no new dependency is
   needed for this change; keep the existing table unchanged.
6. **Constitution VI keyset paging rationale** (unaffected; preserve verbatim).
7. **Tests run on Python 3.11, 3.12 and 3.13 against the real `bookmarks_test` database**
   (Technical Context says "tested on 3.12 and 3.13"; T031 added 3.11) — preserve.

End: 2026-10-24T11:59:18Z
