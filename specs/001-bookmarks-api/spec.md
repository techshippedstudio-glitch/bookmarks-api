# Feature Specification: Bookmarks API

**Feature Branch**: `001-bookmarks-api`

**Created**: 2026-10-21

**Status**: Draft

**Input**: User description: "Build a bookmarks API. A user can save a link with a title and optional tags, list their bookmarks newest first, filter by tag, and delete a bookmark. Saving the same URL twice must not create a duplicate."

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
2. **Given** no bookmarks exist, **When** the user saves a link with a title and the tags "python"
   and "api", **Then** the bookmark is returned with both tags.
3. **Given** a bookmark for a link already exists, **When** the user saves the same link again,
   **Then** no second bookmark is created.
4. **Given** any state, **When** the user tries to save a bookmark without a link or without a
   title, or with a link that is not a valid web address, **Then** nothing is saved and the user
   receives an error explaining what is wrong.

---

### User Story 2 - List bookmarks, newest first (Priority: P2)

A user looks through what they have saved, with the most recently saved bookmarks at the top.

**Why this priority**: Saved links are only useful if the user can find them again; recent items
are the ones most often revisited.

**Independent Test**: Can be tested by saving several bookmarks at different times and confirming
the list returns all of them, most recently saved first.

**Acceptance Scenarios**:

1. **Given** three bookmarks saved one after another, **When** the user lists bookmarks, **Then**
   all three are returned, the most recently saved first.
2. **Given** no bookmarks exist, **When** the user lists bookmarks, **Then** an empty list is
   returned, not an error.

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
2. **Given** bookmarks exist, **When** the user filters by a tag no bookmark has, **Then** an empty
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

- What happens when the same link is saved twice with a different title or different tags?
- What counts as "the same link": does trailing slash, letter case or a tracking parameter matter?
- How are tags handled when they differ only in letter case or surrounding spaces ("API" vs " api")?
- What happens when the same tag is given twice for one bookmark?
- How long can a title or a tag be, and how many tags can one bookmark have?
- What happens when a very large number of bookmarks exist and the user lists them?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow a user to save a bookmark consisting of a link, a title and zero or
  more tags.
- **FR-002**: System MUST reject a bookmark that has no link, no title, or a link that is not a
  valid web address (http or https), and MUST explain the problem to the user.
- **FR-003**: System MUST record the time each bookmark was saved.
- **FR-004**: System MUST NOT store two bookmarks for the same link.
- **FR-005**: System MUST return the saved bookmark, including an identifier the user can use to
  delete it.
- **FR-006**: System MUST list all bookmarks ordered by saved time, most recent first.
- **FR-007**: System MUST allow the user to filter the list to bookmarks carrying a given tag,
  keeping the newest-first order.
- **FR-008**: System MUST allow the user to delete a bookmark by its identifier.
- **FR-009**: System MUST return a not-found error when the user deletes a bookmark that does not
  exist.
- **FR-010**: System MUST report every error in one consistent format with a machine-readable code
  and a human-readable message.

### Key Entities

- **Bookmark**: A link the user saved. Has a link (web address), a title, the time it was saved,
  and a set of tags. Each link appears at most once.
- **Tag**: A short label describing a bookmark. A bookmark can have several tags, and a tag can be
  shared by many bookmarks.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can save a bookmark and see it at the top of their list in a single save
  followed by a single list request.
- **SC-002**: Saving the same link any number of times always leaves exactly one bookmark for it.
- **SC-003**: Filtering by a tag returns only bookmarks with that tag in 100% of tested cases.
- **SC-004**: Every acceptance scenario above is covered by an automated test that passes.
- **SC-005**: Every error a user can trigger returns the same error format.

## Assumptions

- This version serves a single user: there are no accounts, sign-in or per-user separation. All
  bookmarks belong to that one user. Multi-user support is out of scope.
- Editing an existing bookmark's title or tags is out of scope for this version.
- The API is used by developers and tools, not directly through a user interface.
- Bookmarks are kept until the user deletes them; there is no automatic expiry.
