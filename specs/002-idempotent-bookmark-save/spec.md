# Feature Specification: Idempotent Bookmark Save

**Feature Branch**: `claude/ep03-forward-r2`

**Created**: 2026-10-24

**Status**: Draft

**Input**: User description: "Saving a link that is already bookmarked must no longer be rejected. If the link (after the existing normalization rules) is already saved, return the existing bookmark unchanged with HTTP 200 OK instead of the current 409 conflict. The title and tags sent in the new request are ignored; the stored bookmark is not modified. Saving a new link still returns 201 Created. Two concurrent saves of the same new link must still store only one bookmark (one gets 201, the other gets 200 with the same bookmark). This replaces the duplicate rule in FR-004 of specs/001-bookmarks-api."

## Relationship to Earlier Specifications

- **Builds on**: [specs/001-bookmarks-api](../001-bookmarks-api/spec.md) (Bookmarks API). That
  feature directory is a finished historical record and is not edited.
- **Supersedes**: the duplicate rule in **FR-004** of `specs/001-bookmarks-api` — the sentence "A
  save of an existing link MUST be rejected with a conflict error that includes the existing
  bookmark's identifier" — together with the parts of 001 that restate it (User Story 1
  acceptance scenario 3 and the first Edge Case bullet). Those are replaced by FR-001 to FR-004
  below.
- **Unchanged from 001**: everything else, including the link normalization rules in FR-004 (scheme
  and host lowercased, default port removed, trailing path slash removed, fragment removed, query
  kept), the rule that only one bookmark may exist per normalized link, input validation (FR-002,
  FR-011), listing, filtering, deleting and the error format.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Re-saving a saved link returns the existing bookmark (Priority: P1)

A user (or a tool acting for them) saves a link without first checking whether it is already
bookmarked. If it is, they get the bookmark they already have, as a success, instead of an error
they must handle.

**Why this priority**: This is the whole change. Clients can save links "fire and forget", and
retrying a save after a network failure becomes safe.

**Independent Test**: Save a link, save it again (in the same or an equivalent form, with a
different title and tags), and confirm the second response is a success that returns the original
bookmark unchanged, and that only one bookmark exists.

**Acceptance Scenarios**:

1. **Given** a bookmark for `https://example.com/docs` exists, **When** the user saves
   `HTTPS://Example.com/docs/#intro`, **Then** no second bookmark is created and the user receives
   a success response (200 OK, not 201 Created) containing the existing bookmark: same identifier,
   link, title, tags and saved time.
2. **Given** a bookmark for `https://example.com/docs` exists with title "Docs" and tag "python",
   **When** the user saves `https://example.com/docs` with title "Other" and tags "api" and "new",
   **Then** the response contains title "Docs" and tag "python", and listing bookmarks afterwards
   still shows the bookmark with title "Docs" and tag "python" only.
3. **Given** a bookmark for `https://example.com/docs` exists, **When** the user saves
   `https://example.com/docs?page=2`, **Then** it is a different link: a new bookmark is created
   and returned with 201 Created.

---

### User Story 2 - Saving a new link is unchanged (Priority: P2)

A user saves a link that is not bookmarked yet and gets it back as newly created, exactly as
before.

**Why this priority**: Existing behavior that must not regress; clients rely on 201 to tell a new
bookmark from an existing one.

**Independent Test**: Save a link that does not exist and confirm it is stored and returned with
201 Created.

**Acceptance Scenarios**:

1. **Given** no bookmark for a link exists, **When** the user saves it, **Then** it is stored and
   returned with 201 Created.
2. **Given** a bookmark was deleted, **When** the user saves the same link again, **Then** it is
   stored as a new bookmark and returned with 201 Created.

---

### User Story 3 - Concurrent saves of the same new link (Priority: P3)

Two saves of the same link that is not bookmarked yet arrive at the same moment.

**Why this priority**: Correctness under concurrency; rarer than the other paths but must never
create a duplicate.

**Independent Test**: Send two saves of the same new link at the same time and confirm exactly one
bookmark is stored, one response is 201 Created, the other is 200 OK, and both return the same
bookmark.

**Acceptance Scenarios**:

1. **Given** no bookmark for a link exists, **When** two saves of that link (possibly in different
   equivalent forms) happen at the same moment, **Then** exactly one bookmark is stored, one
   response is 201 Created and the other is 200 OK, and both responses carry the same bookmark
   identifier.

---

### Edge Cases

- Saving a link that is already bookmarked, in any equivalent form and with any title or tags,
  returns the existing bookmark unchanged with 200 OK; it is never rejected as a conflict.
- The title and tags of a re-save are ignored for storage, but the request is still validated first:
  a re-save with a missing or too-long title, an invalid link, more than 10 tags, or an invalid tag
  is rejected with a validation error, exactly as for a new link.
- Two saves of the same new link at the same moment leave exactly one bookmark (one 201, one 200).
- A re-save does not change the bookmark's saved time, so it does not move the bookmark to the top
  of the newest-first list.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: When a user saves a link whose normalized form (normalization rules unchanged from
  `specs/001-bookmarks-api` FR-004) matches an existing bookmark, the system MUST return that
  existing bookmark with 200 OK and MUST NOT return a conflict error. *(Supersedes the duplicate
  rule of 001 FR-004.)*
- **FR-002**: On such a re-save the system MUST NOT modify the stored bookmark: its identifier,
  link, title, tags and saved time stay as they were, and the title and tags in the request are
  ignored.
- **FR-003**: When a user saves a link that is not already bookmarked, the system MUST store it
  and return it with 201 Created (unchanged from 001).
- **FR-004**: The system MUST NOT store two bookmarks for the same normalized link, even when two
  saves of the same new link happen at the same moment; in that case one save MUST receive 201
  Created and the other 200 OK, and both MUST return the same bookmark.
- **FR-005**: A re-save request MUST pass the same input validation as a new save (001 FR-002 and
  FR-011) before the duplicate check; invalid requests are rejected with the existing error format.

### Key Entities

- **Bookmark**: unchanged from `specs/001-bookmarks-api`. The normalized link remains unique across
  all bookmarks.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Saving the same link any number of times, in any equivalent form, always leaves
  exactly one bookmark and every save after the first is reported as a success.
- **SC-002**: In 100% of tested re-saves the returned bookmark is identical to the stored one and
  the stored bookmark is unchanged.
- **SC-003**: In 100% of tested concurrent first saves of one link, exactly one bookmark exists
  afterwards, with exactly one "created" and one "already existed" response.
- **SC-004**: No save of a valid link ever results in a conflict error.
- **SC-005**: Every acceptance scenario above is covered by an automated test that passes.

## Assumptions

- The 200 OK response body for a re-save has the same shape as the 201 Created body for a new
  save, so clients read one bookmark representation.
- Validation runs before the duplicate check (FR-005); a client cannot use an invalid request to
  look up an existing bookmark.
- Updating a bookmark's title or tags remains out of scope, as in 001.
- No other behavior of `specs/001-bookmarks-api` changes.
