# Feature Specification: Idempotent Duplicate Save

**Feature Branch**: `002-idempotent-duplicate-save`

**Created**: 2026-10-24

**Status**: Draft

**Input**: User description: "Saving a link that is already bookmarked must no longer be rejected. If the link (after the existing normalization rules) is already saved, return the existing bookmark unchanged with HTTP 200 OK instead of the current 409 conflict. The title and tags sent in the new request are ignored; the stored bookmark is not modified. Saving a new link still returns 201 Created. Two concurrent saves of the same new link must still store only one bookmark (one gets 201, the other gets 200 with the same bookmark). This replaces the duplicate rule in FR-004 of specs/001-bookmarks-api."

**Supersedes**: the duplicate rule in **FR-004** of [specs/001-bookmarks-api](../001-bookmarks-api/spec.md)
(and the matching parts of its User Story 1 acceptance scenario 3, its first Edge Case, and its
2026-10-21 clarification about saving an already bookmarked link). Everything else in
`specs/001-bookmarks-api` (link normalization rules, validation, listing, paging, tag filtering,
deletion, error format) still applies unchanged. `specs/001-bookmarks-api` is kept as a historical
record and is not edited; where the two disagree about saving an already bookmarked link, this
spec wins.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Re-saving a bookmarked link returns the existing bookmark (Priority: P1)

A user (typically a tool or script) saves a link without first checking whether it is already
bookmarked. If it is, the user gets the existing bookmark back as a normal success, instead of an
error they have to special-case.

**Why this priority**: This is the whole change. Clients that save links repeatedly (imports,
browser extensions, retries after a network failure) can treat "save" as safe to repeat.

**Independent Test**: Save a link, save it again (in an equivalent form, with a different title and
tags), and confirm the second save succeeds with an "already existed" success status and returns
the original bookmark unchanged, and that the list still holds exactly one bookmark for it.

**Acceptance Scenarios**:

1. **Given** a bookmark for `https://example.com/docs` exists, **When** the user saves
   `HTTPS://Example.com/docs/#intro`, **Then** no second bookmark is created and the user receives
   the existing bookmark (same identifier, link, title, tags and saved time) with an "OK" success
   status (HTTP 200), not a conflict error.
2. **Given** a bookmark for `https://example.com/docs` exists with title "Docs" and tag "ref",
   **When** the user saves `https://example.com/docs` with title "Other" and tags "x" and "y",
   **Then** the response is the existing bookmark with title "Docs" and tag "ref", and listing
   bookmarks afterwards shows the stored bookmark still has title "Docs" and tag "ref".
3. **Given** no bookmark for a link exists, **When** the user saves it, **Then** it is stored and
   returned with a "Created" success status (HTTP 201), exactly as before.
4. **Given** no bookmark for a link exists, **When** two saves of that link arrive at the same
   moment, **Then** exactly one bookmark is stored; one save receives "Created" (HTTP 201) and the
   other receives "OK" (HTTP 200), and both responses carry the same bookmark.

---

### User Story 2 - Invalid saves are still rejected (Priority: P2)

A user who sends an invalid save request still gets a clear error, even if the link happens to be
already bookmarked.

**Why this priority**: The change must not weaken input validation; returning the existing bookmark
only applies to otherwise valid requests.

**Independent Test**: With a bookmark for a link already stored, send a save for the same link with
an invalid title or invalid tags and confirm a validation error is returned and nothing changes.

**Acceptance Scenarios**:

1. **Given** a bookmark for `https://example.com/docs` exists, **When** the user saves
   `https://example.com/docs` with a title over 200 characters, more than 10 tags, or an invalid
   tag, **Then** the user receives the usual validation error and the stored bookmark is unchanged.

---

### Edge Cases

- Saving a link that is already bookmarked, in any equivalent form (per the normalization rules of
  `specs/001-bookmarks-api`), with the same or a different title or tags, succeeds with HTTP 200 and
  returns the stored bookmark unchanged; the title and tags in the request are ignored.
- Links with different query strings are still different links; saving one when the other exists
  creates a new bookmark (HTTP 201).
- A request that is invalid (missing or invalid link, missing or too long title, too many or
  invalid tags) is rejected with a validation error before any duplicate check, whether or not the
  link is already saved.
- After a bookmark is deleted, saving the same link again creates a new bookmark (HTTP 201).
- Two saves of the same new link at the same moment leave exactly one bookmark: one gets HTTP 201,
  the other HTTP 200 with the same bookmark.
- Saving an already bookmarked link never produces a conflict (HTTP 409) error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST NOT store two bookmarks for the same link, where links are compared after
  the normalization rules defined in FR-004 of `specs/001-bookmarks-api` (scheme and host
  lowercased, default port removed, trailing path slash removed, fragment removed, query kept).
  This MUST hold even when two saves happen at the same moment. *(Replaces the duplicate rule in
  FR-004 of `specs/001-bookmarks-api`.)*
- **FR-002**: When a valid save request names a link that is already bookmarked, System MUST
  return the existing bookmark with HTTP 200 OK and MUST NOT return a conflict error.
- **FR-003**: When returning an existing bookmark for a duplicate save, System MUST ignore the
  title and tags in the request and MUST NOT modify the stored bookmark (link, title, tags and
  saved time all stay as they were).
- **FR-004**: When a valid save request names a link that is not yet bookmarked, System MUST store
  it and return it with HTTP 201 Created, as before.
- **FR-005**: When two saves of the same not-yet-bookmarked link happen at the same moment, System
  MUST store exactly one bookmark, answer one save with HTTP 201 and the other with HTTP 200, and
  return the same bookmark in both responses.
- **FR-006**: System MUST validate a save request with the existing rules of
  `specs/001-bookmarks-api` (FR-002, FR-011) before deciding whether the link is a duplicate; an
  invalid request MUST be rejected with the existing validation error even when the link is
  already saved.
- **FR-007**: The published API description MUST document both success outcomes of saving a
  bookmark (201 for a new bookmark, 200 for an existing one) and MUST no longer list a conflict
  outcome for saving.

### Key Entities

- **Bookmark**: Unchanged from `specs/001-bookmarks-api`. The normalized form of the link remains
  unique across all bookmarks; this feature only changes what a duplicate save returns.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Saving the same link any number of times, in any of its equivalent forms, always
  leaves exactly one bookmark for it, and every save after the first succeeds (0 conflict errors).
- **SC-002**: In 100% of tested duplicate saves, the returned bookmark is identical to the stored
  bookmark before the save (same identifier, link, title, tags and saved time).
- **SC-003**: In a test of two simultaneous saves of a new link, exactly one bookmark exists
  afterwards and the two responses are one "Created" and one "OK" carrying the same identifier.
- **SC-004**: Every acceptance scenario above is covered by an automated test that passes, and the
  full existing test suite still passes once the old conflict expectations are updated.

## Assumptions

- The normalization rules, validation rules and error format of `specs/001-bookmarks-api` are
  unchanged and reused as they are.
- Validation runs before the duplicate check, so an invalid request for an already saved link is
  still a validation error (the change request only covers valid saves).
- The response body for HTTP 200 has the same shape as the HTTP 201 body (a bookmark); the status
  code is how a client tells "created" from "already existed".
- The conflict error code previously used for duplicate saves is no longer produced by saving; it
  may remain in the shared error format for other uses.
- Updating a bookmark's title or tags remains out of scope, as in `specs/001-bookmarks-api`.
- `specs/001-bookmarks-api` is immutable and is not edited; this spec is the current source of
  truth for duplicate-save behavior.
