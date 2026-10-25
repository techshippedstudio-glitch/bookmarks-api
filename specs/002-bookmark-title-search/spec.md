# Feature Specification: Search Bookmarks by Title

**Feature Branch**: `002-bookmark-title-search`

**Created**: 2026-10-25

**Status**: Draft

**Input**: User description: "Let users search their bookmarks by words in the title. A search returns matching bookmarks newest first, can be combined with the tag filter, and pages the same way the bookmark list does. Search ignores letter case."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Search bookmarks by title words (Priority: P1)

A user remembers a word or two from the title of something they saved and types them in to find
it, instead of scrolling through every bookmark.

**Why this priority**: Finding a saved link by what it was called is the whole point of the
feature; the other stories refine it.

**Independent Test**: Can be fully tested by saving bookmarks with different titles, searching for
a word that appears in some of them, and confirming only those bookmarks come back, newest first.

**Acceptance Scenarios**:

1. **Given** bookmarks titled "Postgres indexing guide", "FastAPI tutorial" and "Postgres backups",
   saved in that order, **When** the user searches for "postgres", **Then** "Postgres backups" and
   "Postgres indexing guide" are returned, in that order, with a total count of 2.
2. **Given** a bookmark titled "Learning PostgreSQL", **When** the user searches for "postgresql",
   "POSTGRESQL" or "PostgreSQL", **Then** the bookmark is returned each time (letter case is
   ignored).
3. **Given** bookmarks exist, **When** the user searches for a word no title contains, **Then** an
   empty list with a total count of 0 is returned, not an error.
4. **Given** a bookmark titled "Postgres indexing guide", **When** the user searches for
   "indexing postgres", **Then** the bookmark is returned (every word must appear, in any order);
   **When** the user searches for "postgres backups", **Then** it is not returned.
5. **Given** any state, **When** the user sends a search that is empty, contains only spaces or
   punctuation, or is longer than 200 characters, **Then** nothing is searched and the user
   receives an error explaining what is allowed.

---

### User Story 2 - Combine search with the tag filter (Priority: P2)

A user narrows a search to one tag, for example bookmarks tagged "python" whose title mentions
"testing".

**Why this priority**: Combining the two filters makes a large collection manageable, but search
is already useful on its own.

**Independent Test**: Can be tested by saving bookmarks with overlapping titles and tags and
confirming that a search plus a tag returns only bookmarks that match both.

**Acceptance Scenarios**:

1. **Given** bookmarks "Testing in Python" tagged "python", "Testing in Go" tagged "go" and
   "Python packaging" tagged "python", **When** the user searches for "testing" with the tag
   "python", **Then** only "Testing in Python" is returned, with a total count of 1.
2. **Given** a bookmark titled "Testing in Python" tagged "python", **When** the user searches for
   "testing" with the tag "Python", **Then** the bookmark is returned (the tag is normalized the
   same way as in the bookmark list).
3. **Given** bookmarks exist, **When** the user searches for a word that matches titles but with a
   tag none of those bookmarks carry, **Then** an empty list with a total count of 0 is returned.
4. **Given** any state, **When** the user searches with an invalid tag, **Then** the user receives
   the same error the bookmark list gives for that tag.

---

### User Story 3 - Page through search results (Priority: P3)

A user whose search matches many bookmarks reads the results a page at a time, exactly as they
page through the bookmark list.

**Why this priority**: Most searches match a handful of bookmarks; paging matters only for broad
searches in large collections.

**Independent Test**: Can be tested by saving more matching bookmarks than fit on one page and
following the next-page token until it runs out, confirming every match is seen exactly once.

**Acceptance Scenarios**:

1. **Given** 25 bookmarks whose titles contain "guide" and 5 that do not, **When** the user searches
   for "guide" without paging options, **Then** the 20 newest matches are returned with a total
   count of 25 and a next-page token; **When** the user asks for the next page with that token,
   **Then** the remaining 5 matches are returned with no next-page token.
2. **Given** matching bookmarks exist, **When** the user asks for a page size between 1 and 100,
   **Then** at most that many matches are returned per page.
3. **Given** 25 matching bookmarks and the user has fetched the first page, **When** a new matching
   bookmark is saved and the user asks for the next page with the token, **Then** the next page
   holds exactly the 5 older matches, with none repeated and none skipped.
4. **Given** any state, **When** the user asks for more than 100 per page, fewer than 1, sends a
   malformed next-page token, or sends the removed offset option, **Then** the user receives the
   same error the bookmark list gives.

---

### Edge Cases

- Letter case never affects whether a bookmark matches: "Postgres", "postgres" and "POSTGRES" find
  the same bookmarks.
- Leading, trailing and repeated spaces in the search are ignored; "  postgres   guide " is the same
  search as "postgres guide".
- Punctuation in the search or the title separates words: a title "FastAPI: a tutorial" contains
  the words "fastapi", "a" and "tutorial".
- A search word matches only a whole title word: "postgres" finds "Postgres backups", but "post"
  does not find "Postgres" and "gres" does not find "Postgres".
- A search with no words left after removing spaces and punctuation is rejected with a validation
  error, not treated as "match everything".
- A search for a word that appears in a bookmark's link or tags but not its title does not match
  that bookmark; only the title is searched.
- Bookmarks saved or deleted between page requests never cause a match to be repeated or skipped.
- A deleted bookmark no longer appears in search results.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST let a user search their bookmarks by one or more words, matching against
  the bookmark's title only.
- **FR-002**: Search MUST ignore letter case in both the search words and the titles.
- **FR-003**: System MUST split the search into words on spaces and punctuation, ignoring leading,
  trailing and repeated separators. When the search has several words, a bookmark MUST match only
  when its title contains all of the words, in any order.
- **FR-004**: A search word MUST match only a whole word of the title, never part of a longer word
  ("post" does not match "Postgres").
- **FR-005**: System MUST return search results ordered by saved time, most recent first.
- **FR-006**: System MUST let the user combine a search with the existing tag filter; a bookmark is
  returned only when it matches the search and carries the tag. The tag is normalized and
  validated exactly as for the bookmark list.
- **FR-007**: System MUST page search results the same way as the bookmark list: 20 per page by
  default, at most 100, the total number of matching bookmarks, and an opaque next-page token
  (none on the last page). Paging with the token MUST NOT repeat or skip bookmarks when bookmarks
  are saved or deleted between requests (Constitution VI).
- **FR-008**: System MUST reject a search that is missing, empty, has no words after removing
  spaces and punctuation, or is longer than 200 characters, and MUST explain what is allowed.
- **FR-009**: System MUST reject the same invalid paging and tag inputs the bookmark list rejects
  (page size outside 1 to 100, malformed next-page token, the removed offset option, invalid tag),
  with the same errors.
- **FR-010**: System MUST report every search error in the same consistent format as the rest of
  the API, with a machine-readable code and a human-readable message.
- **FR-011**: The existing bookmark list, tag filter, save and delete behavior MUST NOT change.

### Key Entities

- **Bookmark**: Unchanged from the bookmarks feature (specs/001-bookmarks-api). Search reads its
  title, tags and saved time.
- **Search**: What the user typed, up to 200 characters, reduced to a list of lowercase words. It
  is not stored.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can find a saved bookmark by one word of its title with a single search
  request, whatever letter case they type.
- **SC-002**: In 100% of tested cases, a search returns only bookmarks whose titles match, and
  every bookmark whose title matches.
- **SC-003**: Paging through all results of a search while bookmarks are saved between requests
  shows every match exactly once.
- **SC-004**: A search of a 100,000-bookmark collection returns its first page in under one second
  on a developer machine.
- **SC-005**: Every acceptance scenario above is covered by an automated test that passes, and the
  existing bookmark tests still pass.

## Assumptions

- This version serves a single user, as the bookmarks feature does; all bookmarks are searched.
- Only titles are searched. Searching links, tags or page contents is out of scope.
- Letters are compared without regard to case only; accents are not ignored ("cafe" does not find
  "Café"), and there is no stemming, spelling correction or ranking by relevance. Results are
  always newest first.
- A search is a read-only request; it does not change any bookmark and is not saved.
- The search limit of 200 characters matches the longest allowed title.
- The tag filter, page size, next-page token and their errors behave exactly as defined in
  specs/001-bookmarks-api/spec.md.
