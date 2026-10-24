# Feature Specification: Idempotent Duplicate Save

**Feature Branch**: `002-idempotent-duplicate-save`

**Created**: 2026-10-24

**Status**: Draft

**Input**: User description: "Saving a link that is already bookmarked must no longer be rejected. If the link (after the existing normalization rules) is already saved, return the existing bookmark unchanged with HTTP 200 OK instead of the current 409 conflict. The title and tags sent in the new request are ignored; the stored bookmark is not modified. Saving a new link still returns 201 Created. Two concurrent saves of the same new link must still store only one bookmark (one gets 201, the other gets 200 with the same bookmark). This replaces the duplicate rule in FR-004 of specs/001-bookmarks-api."

**Supersedes**: the duplicate rule in **FR-004** of [`specs/001-bookmarks-api/spec.md`](../001-bookmarks-api/spec.md)
(and the matching Clarification "Q: When someone saves a link that is already bookmarked…",
User Story 1 Acceptance Scenario 3 and the first Edge Case of that spec). Everything else in
`specs/001-bookmarks-api` stays in force, including FR-004's normalization rules and its "never
store two bookmarks for the same link" guarantee. `specs/001-bookmarks-api` is a finished,
historical record and is not edited; where the two specs disagree about saving an
already-bookmarked link, this spec wins.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Saving an already-bookmarked link returns the existing bookmark (Priority: P1)

A user (or a tool acting for them) saves a link without knowing, or caring, whether it is already
bookmarked. Instead of receiving an error, they get back the bookmark that is already stored for
that link, so a "save" can be repeated safely.

**Why this priority**: This is the whole change. Clients no longer need special handling for the
"already saved" case; retrying a save is safe.

**Independent Test**: Save a link, then save the same link again (in an equivalent form, with a
different title and tags) and confirm the second response is a success that returns the first
bookmark exactly as stored, and that only one bookmark exists.

**Acceptance Scenarios**:

1. **Given** a bookmark for `https://example.com/docs` exists, **When** the user saves
   `HTTPS://Example.com/docs/#intro`, **Then** no second bookmark is created and the user receives
   a success response (HTTP 200 OK) containing the existing bookmark: same identifier, link,
   title, tags and saved time as before.
2. **Given** a bookmark for `https://example.com/docs` exists with title "Docs" and tags "api",
   **When** the user saves `https://example.com/docs` with title "Other" and tags "python" and
   "new", **Then** the response (HTTP 200 OK) returns title "Docs" and tags "api", and listing
   bookmarks afterwards still shows exactly one bookmark for that link with title "Docs" and tags
   "api".
3. **Given** no bookmark exists for a link, **When** the user saves it, **Then** it is stored and
   returned with HTTP 201 Created, as before.

---

### User Story 2 - Concurrent saves of the same new link still store one bookmark (Priority: P2)

Two saves of the same, not-yet-bookmarked link arrive at the same moment (for example a client
retrying while its first request is still in flight).

**Why this priority**: The "never two bookmarks for one link" guarantee from FR-004 of
specs/001-bookmarks-api must survive the change; only the response to the losing request changes.

**Independent Test**: Fire two saves of the same new link at the same time and confirm exactly one
gets HTTP 201 Created, the other gets HTTP 200 OK, both return the same bookmark identifier, and
exactly one bookmark is stored.

**Acceptance Scenarios**:

1. **Given** no bookmark exists for a link, **When** two saves of that link (possibly in different
   equivalent forms) happen at the same moment, **Then** exactly one bookmark is stored, one
   response is HTTP 201 Created and the other is HTTP 200 OK, and both responses carry the same
   bookmark.

---

### Edge Cases

- A save whose link matches an existing bookmark only after normalization (scheme/host case,
  default port, trailing path slash, fragment) returns the existing bookmark with HTTP 200 OK.
- A save whose link differs from an existing bookmark only in its query string is a new link and
  returns HTTP 201 Created.
- A duplicate save whose title or tags are invalid (for example a title over 200 characters, more
  than 10 tags, or an invalid tag) is still rejected with a validation error: input is validated
  before the duplicate check, exactly as for any other save. Valid but different title and tags are
  ignored.
- The returned existing bookmark shows the link as it was originally given, not the form sent in
  the duplicate request.
- After a bookmark is deleted, saving the same link again creates a new bookmark (HTTP 201
  Created), unchanged from specs/001-bookmarks-api.
- A duplicate save never produces a conflict error any more.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST NOT store two bookmarks for the same link, where links are compared
  after the normalization rules of FR-004 in specs/001-bookmarks-api (scheme and host lowercased,
  default port removed, trailing path slash removed, fragment removed, query kept). This MUST
  hold even when two saves happen at the same moment.
- **FR-002**: When a save's link (after normalization) matches an existing bookmark, the System
  MUST respond with success (HTTP 200 OK) and return the existing bookmark exactly as stored. It
  MUST NOT return a conflict error. *(Replaces the duplicate rule in FR-004 of
  specs/001-bookmarks-api, which required a conflict error.)*
- **FR-003**: When a save matches an existing bookmark, the System MUST ignore the title and tags
  sent in that save and MUST NOT modify the stored bookmark (identifier, link, title, tags and
  saved time all stay the same).
- **FR-004**: When a save's link does not match any existing bookmark, the System MUST store it
  and respond with HTTP 201 Created, as before.
- **FR-005**: When two saves of the same new link happen at the same moment, exactly one MUST
  receive HTTP 201 Created and the other MUST receive HTTP 200 OK, and both MUST return the same
  bookmark.
- **FR-006**: Save requests MUST still be validated (FR-002 and FR-011 of specs/001-bookmarks-api)
  before the duplicate check; an invalid request is rejected with a validation error whether or
  not its link is already saved.

### Key Entities

- **Bookmark**: Unchanged from specs/001-bookmarks-api. The normalized form of its link remains
  unique across all bookmarks.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Saving the same link any number of times, in any of its equivalent forms, always
  leaves exactly one bookmark for it, and every save after the first returns that bookmark with a
  success status.
- **SC-002**: In 100% of tested duplicate saves the returned bookmark is identical (identifier,
  link, title, tags, saved time) to the stored one, and the stored one is unchanged.
- **SC-003**: In repeated tests of two simultaneous saves of a new link, there is always exactly
  one "created" response, one "already exists" success response, and one stored bookmark.
- **SC-004**: No save request ever returns a conflict error.
- **SC-005**: Every acceptance scenario above is covered by an automated test that passes.

## Assumptions

- The response body for a duplicate save has the same shape as for a newly created bookmark; the
  status code (200 vs 201) is how a client tells them apart.
- Validation of the request happens before the duplicate check, so an invalid duplicate request is
  still a validation error (the change request only says title and tags are ignored, not that
  validation is skipped).
- The single-user scope, delete behavior, listing, paging and filtering of
  specs/001-bookmarks-api are unchanged.
- The `conflict` error code may no longer be produced by any endpoint; the consistent error format
  (Constitution III) is otherwise unchanged.
