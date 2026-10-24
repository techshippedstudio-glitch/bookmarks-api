# Feature Specification: Idempotent Duplicate Save

**Feature Branch**: `002-idempotent-duplicate-save`

**Created**: 2026-10-24

**Status**: Draft

**Input**: User description: "Saving a link that is already bookmarked must no longer be rejected. If the link (after the existing normalization rules) is already saved, return the existing bookmark unchanged with HTTP 200 OK instead of the current 409 conflict. The title and tags sent in the new request are ignored; the stored bookmark is not modified. Saving a new link still returns 201 Created. Two concurrent saves of the same new link must still store only one bookmark (one gets 201, the other gets 200 with the same bookmark). This replaces the duplicate rule in FR-004 of specs/001-bookmarks-api."

## Relationship to Earlier Specifications

- **Builds on**: [specs/001-bookmarks-api](../001-bookmarks-api/spec.md) (Bookmarks API). That
  feature directory is a finished historical record and is not edited.
- **Supersedes**: the duplicate rule in **FR-004** of `specs/001-bookmarks-api` — the sentence "A
  save of an existing link MUST be rejected with a conflict error that includes the existing
  bookmark's identifier" — together with the parts of 001 that restate it (User Story 1 acceptance
  scenario 3, the first Edge Case bullet, and the first Clarification of Session 2026-10-21). Those
  are replaced by FR-001 to FR-003 below.
- **Unchanged from 001**: the rest of FR-004 still applies — the system MUST NOT store two
  bookmarks for the same link, links are compared after the existing normalization rules (scheme
  and host lowercased, default port removed, trailing path slash removed, fragment removed, query
  kept), and the guarantee holds when two saves happen at the same moment. All other 001
  requirements (FR-001 to FR-003 and FR-005 to FR-011) are unchanged.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Saving an already-saved link returns the existing bookmark (Priority: P1)

A user (or a tool acting for them) saves a link without first checking whether it is already
bookmarked. Instead of an error, they get back the bookmark they already have, untouched, and can
tell from the response that nothing new was created.

**Why this priority**: This is the whole change. Clients that retry saves or import links in bulk
no longer have to treat "already saved" as a failure and parse an error to find the existing
bookmark.

**Independent Test**: Save a link, then save an equivalent form of it with a different title and
tags; confirm the second response is a success that returns the first bookmark exactly as stored,
signals "existing" rather than "created", and that only one bookmark exists.

**Acceptance Scenarios**:

1. **Given** a bookmark for `https://example.com/docs` exists with title "Docs" and tag "python",
   **When** the user saves `HTTPS://Example.com/docs/#intro` with title "Other" and tag "misc",
   **Then** the response is 200 OK and contains the existing bookmark (same identifier, link,
   title "Docs", tag "python" and saved time), and the list still holds exactly one bookmark for
   that link, unchanged.
2. **Given** a bookmark for `https://example.com/docs` exists, **When** the user saves
   `https://example.com/docs` again with the identical title and tags, **Then** the response is
   200 OK with the existing bookmark and no second bookmark is created.
3. **Given** no bookmark exists for a link, **When** the user saves it, **Then** the response is
   201 Created with the new bookmark (unchanged from 001).
4. **Given** a bookmark for `https://example.com/docs?a=1` exists, **When** the user saves
   `https://example.com/docs?a=2`, **Then** it is treated as a new link and the response is 201
   Created (query strings still distinguish links).

---

### User Story 2 - Concurrent saves of the same new link store one bookmark (Priority: P2)

Two clients save the same, not-yet-saved link at the same moment. Exactly one bookmark is stored;
one client is told it was created and the other receives that same bookmark as an existing one.

**Why this priority**: The duplicate guarantee from 001 must survive the change; without it the
new behavior could silently create duplicates under load.

**Independent Test**: Fire two saves of the same new link at the same moment; confirm one response
is 201 Created, the other is 200 OK, both carry the same bookmark identifier, and exactly one
bookmark is stored.

**Acceptance Scenarios**:

1. **Given** no bookmark exists for a link, **When** two saves of that link (in equivalent forms)
   arrive at the same moment, **Then** exactly one bookmark is stored, one response is 201 Created
   and the other is 200 OK, and both responses contain the same bookmark.

---

### Edge Cases

- A duplicate save whose title or tags would be invalid on their own (for example a title over 200
  characters or an invalid tag) is still rejected with a validation error: input is validated
  before the duplicate check, as in 001, so the request is never silently accepted with bad input.
- A duplicate save with different title or tags never changes the stored bookmark; its title,
  tags and saved time stay exactly as they were.
- After a bookmark is deleted, saving the same link again creates a new bookmark (201 Created), as
  in 001.
- A duplicate save does not move the existing bookmark in the newest-first list: its saved time is
  not changed.
- The duplicate case no longer produces any error response; the conflict error described in 001
  is no longer returned for duplicate links.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: When a user saves a link whose normalized form matches an existing bookmark (using
  the normalization rules of 001 FR-004), the system MUST return the existing bookmark with a
  200 OK success response instead of rejecting the save. This supersedes the duplicate rule in
  FR-004 of `specs/001-bookmarks-api`.
- **FR-002**: On such a duplicate save the system MUST ignore the title and tags sent in the
  request and MUST NOT modify the stored bookmark in any way (identifier, link, title, tags and
  saved time stay the same).
- **FR-003**: Saving a link that is not already bookmarked MUST continue to store a new bookmark
  and return it with a 201 Created response.
- **FR-004**: The system MUST continue to store at most one bookmark per normalized link, even when
  saves of the same new link happen at the same moment; in that case exactly one save MUST receive
  201 Created and every other MUST receive 200 OK with the same bookmark.
- **FR-005**: Request validation (link, title and tag rules of 001 FR-002 and FR-011) MUST still be
  applied to every save, including a save of a link that is already bookmarked.
- **FR-006**: The published API description MUST document both success outcomes of a save (201 for
  a new bookmark, 200 for an existing one) and MUST no longer list a conflict error for the save
  operation.

### Key Entities

- **Bookmark**: Unchanged from 001. The normalized link remains unique across all bookmarks; this
  feature only changes what a save of an existing normalized link returns.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Saving the same link any number of times, in any of its equivalent forms, always
  leaves exactly one bookmark for it, and every save after the first succeeds.
- **SC-002**: In 100% of tested duplicate saves the returned bookmark is identical to the stored
  one, and the stored bookmark is unchanged afterwards.
- **SC-003**: In 100% of tested concurrent double saves of a new link, exactly one bookmark is
  stored and the two responses are one "created" and one "existing" carrying the same bookmark.
- **SC-004**: No save request for a valid link returns a conflict error.
- **SC-005**: Every acceptance scenario above is covered by an automated test that passes, and the
  existing 001 test suite (updated only where it asserted the old conflict behavior) still passes.

## Assumptions

- Clients distinguish "created" from "existing" by the response status (201 vs 200); the response
  body has the same bookmark shape in both cases.
- Validation still runs before the duplicate check, so an invalid request for an already-saved link
  receives a validation error, not the existing bookmark (the change request does not say
  otherwise, and 001 validated first).
- No data migration is needed: the stored data and its uniqueness rule are unchanged.
- Single-user scope, no editing of bookmarks, and all other 001 assumptions still hold.
