# Feature Specification: Bookmarks API

**Feature Branch**: `001-bookmarks-api`

**Created**: 2026-10-21

**Status**: Draft

**Input**: User description: "Build a bookmarks API. A user can save a link with a title and optional tags, list their bookmarks newest first, filter by tag, and delete a bookmark. Saving the same URL twice must not create a duplicate."

## Clarifications

### Session 2026-10-21

- Q: When someone saves a link that is already bookmarked, what should happen? → A: ~~Reject it with a conflict error that includes the existing bookmark's identifier; the existing bookmark is left unchanged.~~ Superseded on 2026-10-24 (see "Change request 2026-10-24" below).
- Q: Which links count as "the same link"? → A: Links that match after normalization: scheme and host lowercased, default port removed, trailing slash on the path removed, fragment (#...) removed; the query string is kept as is.
- Q: How should tags be cleaned up and limited? → A: Trim spaces, lowercase, drop duplicates; 1 to 30 characters of letters, digits and hyphens; at most 10 tags per bookmark.
- Q: How should the list behave when there are many bookmarks? → A: Return pages: 20 per page by default, up to 100 per page, using a limit and an offset, plus the total count.
- Q: How long can a title and a link be? → A: Title 1 to 200 characters; link at most 2048 characters.

### Session 2026-10-21 (constitution v1.1.0)

- Q: Principle VI forbids offset pagination. How does a client ask for the next page? → A: Each page returns an opaque next-page token (none on the last page); the client passes it back to get the next page. The offset option is removed, and a request that still sends it gets a validation error that points to the token.

### Change request 2026-10-24

- Q: Saving a link that is already bookmarked must no longer be rejected. What should happen instead? → A: If the link (after normalization) is already saved, the existing bookmark is returned unchanged with a success response (200 OK) instead of a conflict error. The title and tags sent in the new request are ignored and the stored bookmark is not modified. Saving a new link still returns 201 Created. Two concurrent saves of the same new link still store only one bookmark: one gets 201, the other gets 200 with the same bookmark. This replaces the duplicate rule in FR-004.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Save a bookmark (Priority: P1)

A user saves a link they want to come back to, giving it a title and, optionally, a few tags
that describe it.

**Why this priority**: Saving is the core of the product. Without it there is nothing to list,
filter or delete.

**Independent Test**: Can be fully tested by saving a bookmark and confirming the response
contains the saved link, title, tags and the time it was saved.

**Acceptance Scenarios**:

1. **Given** no bookmarks exist, **When** the user saves a link with a title, **Then** the bookmark
   is stored and returned with its link, title, an empty tag list and its saved time.
2. **Given** no bookmarks exist, **When** the user saves a link with a title and the tags "Python",
   " api " and "python", **Then** the bookmark is returned with the tags "api" and "python".
3. **Given** a bookmark for `https://example.com/docs` exists, **When** the user saves
   `HTTPS://Example.com/docs/#intro` with a different title and tags, **Then** no second bookmark
   is created and the user receives the existing bookmark, unchanged, with a 200 OK success
   response (not 201 Created).
4. **Given** any state, **When** the user tries to save a bookmark without a link or without a
   title, with a link that is not a valid http or https address, with a title over 200 characters,
   with more than 10 tags, or with an invalid tag, **Then** nothing is saved and the user receives
   an error explaining what is wrong.

---

### User Story 2 - List bookmarks, newest first (Priority: P2)

A user looks through what they have saved, with the most recently saved bookmarks at the top.

**Why this priority**: Saved links are only useful if the user can find them again; recent items
are the ones most often revisited.

**Independent Test**: Can be tested by saving several bookmarks at different times and confirming
the list returns all of them, most recently saved first.

**Acceptance Scenarios**:

1. **Given** three bookmarks saved one after another, **When** the user lists bookmarks, **Then**
   all three are returned, the most recently saved first, with a total count of 3.
2. **Given** no bookmarks exist, **When** the user lists bookmarks, **Then** an empty list with a
   total count of 0 is returned, not an error.
3. **Given** 25 bookmarks exist, **When** the user lists without paging options, **Then** the 20
   newest are returned with a total count of 25 and a next-page token; **When** the user asks for
   the next page with that token, **Then** the remaining 5 are returned with no next-page token.
4. **Given** any state, **When** the user asks for more than 100 per page, or sends a next-page
   token that is malformed, **Then** the user receives an error explaining what is allowed.
5. **Given** 25 bookmarks exist and the user has fetched the first page, **When** a new bookmark is
   saved and the user asks for the next page with the token, **Then** the next page holds exactly
   the 5 older bookmarks, with none repeated and none skipped.

---

### User Story 3 - Filter bookmarks by tag (Priority: P3)

A user narrows the list to bookmarks with a particular tag, for example everything tagged
"postgres".

**Why this priority**: Filtering makes a growing collection usable, but listing works without it.

**Independent Test**: Can be tested by saving bookmarks with different tags and confirming that a
tag filter returns only the matching bookmarks, still newest first.

**Acceptance Scenarios**:

1. **Given** bookmarks tagged "python", "postgres" and both, **When** the user filters by
   "postgres", **Then** only the bookmarks carrying that tag are returned, newest first.
2. **Given** a bookmark tagged "postgres", **When** the user filters by "Postgres", **Then** the
   bookmark is returned (the filter is normalized like tags are).
3. **Given** bookmarks exist, **When** the user filters by a tag no bookmark has, **Then** an empty
   list is returned.

---

### User Story 4 - Delete a bookmark (Priority: P4)

A user removes a bookmark they no longer need.

**Why this priority**: Deleting keeps the collection tidy, but the product is useful before it
exists.

**Independent Test**: Can be tested by saving a bookmark, deleting it, and confirming it no longer
appears in the list.

**Acceptance Scenarios**:

1. **Given** a saved bookmark, **When** the user deletes it, **Then** it no longer appears in the
   list or in tag filters.
2. **Given** a bookmark that does not exist, **When** the user tries to delete it, **Then** the user
   receives a not-found error.
3. **Given** a bookmark was deleted, **When** the user saves the same link again, **Then** it is
   saved as a new bookmark.

---

### Edge Cases

- Saving a link that is already bookmarked, even with a different title or tags, is not an error:
  the existing bookmark is returned unchanged with 200 OK; the title and tags in the request are
  ignored and the stored bookmark is not modified.
- Links that differ only in scheme or host letter case, a default port (`:80` for http, `:443`
  for https), a trailing slash on the path, or a fragment are the same link. Links with different
  query strings are different links.
- Tags are trimmed and lowercased before saving or filtering; repeated tags on one bookmark are
  kept once.
- A tag that is empty after trimming, longer than 30 characters, or contains characters other
  than letters, digits and hyphens is rejected.
- Two saves of the same new link at the same moment still leave exactly one bookmark: one save
  gets 201 Created, the other gets 200 OK with the same bookmark.
- A malformed next-page token (one that does not decode to a position in the list) is rejected with
  a validation error.
- A request that sends the removed offset option is rejected with a validation error that names the
  next-page token instead.
- Bookmarks saved or deleted between page requests never cause a bookmark to be repeated or skipped.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow a user to save a bookmark consisting of a link, a title and zero to
  10 tags.
- **FR-002**: System MUST reject a bookmark that has no link, no title, a link that is not a valid
  http or https address, a link longer than 2048 characters, or a title longer than 200
  characters, and MUST explain the problem to the user.
- **FR-003**: System MUST record the time each bookmark was saved.
- **FR-004**: System MUST NOT store two bookmarks for the same link, where links are compared after
  normalization (scheme and host lowercased, default port removed, trailing path slash removed,
  fragment removed, query kept). A save of a link that is already saved MUST NOT be rejected: it
  MUST return the existing bookmark unchanged with 200 OK, ignoring the title and tags in the
  request and leaving the stored bookmark unmodified. A save of a new link MUST return 201
  Created. This MUST hold even when two saves of the same new link happen at the same moment:
  exactly one bookmark is stored, one save gets 201 and the other gets 200 with the same
  bookmark.
- **FR-005**: System MUST return the saved bookmark (or, for an already-saved link, the existing
  bookmark), including an identifier the user can use to delete it.
- **FR-006**: System MUST list bookmarks ordered by saved time, most recent first, in pages of 20
  by default and at most 100, and MUST include the total number of matching bookmarks. Each page
  MUST return an opaque next-page token (none on the last page), and paging with it MUST NOT repeat
  or skip bookmarks when bookmarks are saved or deleted between requests (Constitution VI).
- **FR-007**: System MUST allow the user to filter the list to bookmarks carrying a given tag,
  keeping the newest-first order and paging; the filter value is normalized the same way as tags.
- **FR-008**: System MUST allow the user to delete a bookmark by its identifier.
- **FR-009**: System MUST return a not-found error when the user deletes a bookmark that does not
  exist.
- **FR-010**: System MUST report every error in one consistent format with a machine-readable code
  and a human-readable message.
- **FR-011**: System MUST normalize tags by trimming spaces, lowercasing and removing duplicates,
  and MUST reject tags that are empty, longer than 30 characters, or contain characters other than
  letters, digits and hyphens.

### Key Entities

- **Bookmark**: A link the user saved. Has an identifier, a link (web address, at most 2048
  characters) as the user gave it, the normalized form of that link (unique across all
  bookmarks), a title (1 to 200 characters), the time it was saved, and up to 10 tags.
- **Tag**: A short label (1 to 30 lowercase letters, digits or hyphens) describing a bookmark. A
  bookmark can have several tags, and a tag can be shared by many bookmarks.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can save a bookmark and see it at the top of their list in a single save
  followed by a single list request.
- **SC-002**: Saving the same link any number of times, in any of its equivalent forms, always
  leaves exactly one bookmark for it.
- **SC-003**: Filtering by a tag returns only bookmarks with that tag in 100% of tested cases.
- **SC-004**: Every acceptance scenario above is covered by an automated test that passes.
- **SC-005**: Every error a user can trigger returns the same error format.

## Assumptions

- This version serves a single user: there are no accounts, sign-in or per-user separation. All
  bookmarks belong to that one user. Multi-user support is out of scope.
- Editing an existing bookmark's title or tags is out of scope for this version.
- The API is used by developers and tools, not directly through a user interface.
- Bookmarks are kept until the user deletes them; there is no automatic expiry.
