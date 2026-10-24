# Step 01: spec (manual edit of specs/001-bookmarks-api/spec.md)

Start: 2026-10-24T11:41:24Z

## Commands and output

```
$ git status && git branch --show-current && git log --oneline -3 && git describe --tags
On branch claude/ep03-living-r1
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   specs/001-bookmarks-api/spec.md

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	episodes/

no changes added to commit (use "git add" and/or "git commit -a")
claude/ep03-living-r1
c997fe2 ep02: implement convergence tasks (keyset pagination)
b6b252a ep02: converge pass 1
65990f5 ep02: analyze remediation for Constitution VI
ep03-start
```

Read: specs/001-bookmarks-api/spec.md, plan.md, research.md, tasks.md, data-model.md, quickstart.md, .specify/memory/constitution.md (reads only, no output captured beyond what is quoted below).

Edits (hand edits with the editor tool, spec.md only): added a dated change note under Clarifications; rewrote US1 acceptance scenario 3; rewrote the duplicate edge case and the concurrent-save edge case; rewrote the duplicate rule in FR-004. Note: the first edit attempt on the Clarifications block failed ("String to replace not found in file") because the match string included a line break the file does not have at that spot; retried with a shorter match, which applied.

```diff
$ git diff
diff --git a/specs/001-bookmarks-api/spec.md b/specs/001-bookmarks-api/spec.md
index 3ed7b96..b94822e 100644
--- a/specs/001-bookmarks-api/spec.md
+++ b/specs/001-bookmarks-api/spec.md
@@ -22,6 +22,10 @@
 
 - Q: Principle VI forbids offset pagination. How does a client ask for the next page? → A: Each page returns an opaque next-page token (none on the last page); the client passes it back to get the next page. The offset option is removed, and a request that still sends it gets a validation error that points to the token.
 
+### Change 2026-10-24 (duplicate saves)
+
+- Change request: Saving a link that is already bookmarked must no longer be rejected. If the link (after the existing normalization rules) is already saved, the existing bookmark is returned unchanged with 200 OK instead of a conflict error; the title and tags sent in the new request are ignored and the stored bookmark is not modified. Saving a new link still returns 201 Created. Two concurrent saves of the same new link still store only one bookmark (one gets 201, the other gets 200 with the same bookmark). This supersedes the first answer of Session 2026-10-21 and replaces the duplicate rule in FR-004.
+
 ## User Scenarios & Testing *(mandatory)*
 
 ### User Story 1 - Save a bookmark (Priority: P1)
@@ -42,8 +46,10 @@ contains the saved link, title, tags and the time it was saved.
 2. **Given** no bookmarks exist, **When** the user saves a link with a title and the tags "Python",
    " api " and "python", **Then** the bookmark is returned with the tags "api" and "python".
 3. **Given** a bookmark for `https://example.com/docs` exists, **When** the user saves
-   `HTTPS://Example.com/docs/#intro`, **Then** no second bookmark is created and the user receives
-   a conflict error that includes the existing bookmark's identifier.
+   `HTTPS://Example.com/docs/#intro` with a different title and tags, **Then** no second bookmark
+   is created and the user receives the existing bookmark, unchanged (its original link, title,
+   tags and saved time), with a 200 OK success response instead of the 201 Created used for a new
+   bookmark.
 4. **Given** any state, **When** the user tries to save a bookmark without a link or without a
    title, with a link that is not a valid http or https address, with a title over 200 characters,
    with more than 10 tags, or with an invalid tag, **Then** nothing is saved and the user receives
@@ -122,9 +128,9 @@ appears in the list.
 
 ### Edge Cases
 
-- Saving a link that is already bookmarked, even with a different title or tags, is rejected with
-  a conflict error that includes the existing bookmark's identifier; the existing bookmark is not
-  changed.
+- Saving a link that is already bookmarked, even with a different title or tags, is not an error:
+  the existing bookmark is returned unchanged with 200 OK; the title and tags in the request are
+  ignored and the stored bookmark is not modified.
 - Links that differ only in scheme or host letter case, a default port (`:80` for http, `:443`
   for https), a trailing slash on the path, or a fragment are the same link. Links with different
   query strings are different links.
@@ -132,7 +138,8 @@ appears in the list.
   kept once.
 - A tag that is empty after trimming, longer than 30 characters, or contains characters other
   than letters, digits and hyphens is rejected.
-- Two saves of the same link at the same moment still leave exactly one bookmark.
+- Two saves of the same new link at the same moment still leave exactly one bookmark: one save
+  gets 201 Created and the other gets 200 OK with the same bookmark.
 - A malformed next-page token (one that does not decode to a position in the list) is rejected with
   a validation error.
 - A request that sends the removed offset option is rejected with a validation error that names the
@@ -151,9 +158,11 @@ appears in the list.
 - **FR-003**: System MUST record the time each bookmark was saved.
 - **FR-004**: System MUST NOT store two bookmarks for the same link, where links are compared after
   normalization (scheme and host lowercased, default port removed, trailing path slash removed,
-  fragment removed, query kept). A save of an existing link MUST be rejected with a conflict error
-  that includes the existing bookmark's identifier, and MUST hold even when two saves happen at
-  the same moment.
+  fragment removed, query kept). A save of a link that is already saved MUST NOT be rejected: it
+  MUST return the existing bookmark unchanged with 200 OK, ignoring the title and tags in the
+  request and leaving the stored bookmark unmodified. A save of a new link MUST return 201 Created.
+  This MUST hold even when two saves of the same new link happen at the same moment: exactly one
+  bookmark is stored, one save gets 201 Created and the other gets 200 OK with the same bookmark.
 - **FR-005**: System MUST return the saved bookmark, including an identifier the user can use to
   delete it.
 - **FR-006**: System MUST list bookmarks ordered by saved time, most recent first, in pages of 20
```

## Rationale in the current plan.md (and its research.md) worth preserving before plan is rerun

From plan.md:
- Summary: "Uniqueness is enforced by a unique index on the normalized link, so it holds under concurrent saves" — still the mechanism for the new rule (one row under races).
- Technical Context choices and their reasons: FastAPI + Pydantic, SQLAlchemy 2.0 sync with psycopg 3 (binary), Alembic, pytest + httpx2 (current Starlette test client dependency; plain httpx deprecated there); tested on 3.11/3.12/3.13 (T031 history).
- Constitution Check rows: I typed contracts (no untyped dicts; OpenAPI generated from models); II real-DB tests (Alembic migrations run on bookmarks_test, truncate per test, no mocks); III one envelope for 422/404/409 as global handlers (409 duplicate row will change); IV six deps, each justified, stdlib for normalization and config; V tests per acceptance scenario; VI keyset paging on (created_at, id) with opaque next_cursor, no offset anywhere, page-while-inserting test.
- Project structure and the one-table design (data-model.md).
- Complexity Tracking: no violations.

From research.md ("Preventing duplicate links", the decision the change request touches):
- Store `url` as given plus `url_normalized` with a unique index; `INSERT ... ON CONFLICT (url_normalized) DO NOTHING RETURNING`; if nothing returned, look up the existing row.
- Rationale: the database guarantees uniqueness under races; ON CONFLICT avoids catching exceptions mid-transaction.
- Alternatives rejected: check-then-insert (races); catching IntegrityError (leaves the transaction aborted, noisier).
- Under the new rule the "look up the existing row" step now returns the row with 200 instead of raising DuplicateUrlError (409). Subtle point to keep: with ON CONFLICT DO NOTHING under READ COMMITTED, the conflicting row from a concurrent, just-committed insert is visible to the follow-up SELECT in a new statement, so the loser can return it.
- Error envelope decision: codes validation_error (422), not_found (404), duplicate_url (409, details.existing_id). The duplicate_url code becomes unused by the save endpoint.
- Paging decision (keyset, cursor JSON+base64url, offset -> 422) and the "Alternatives considered" history (offset was the original decision; violated Constitution VI v1.1.0).

End: 2026-10-24T11:42:45Z
