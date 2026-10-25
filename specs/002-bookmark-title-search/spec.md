# Feature Specification: Bookmark Title Search

**Feature Branch**: none (no `before_specify` hook ran, so no branch was created; spec directory is `specs/002-bookmark-title-search`)

**Created**: 2026-10-25

**Status**: Draft

**Input**: User description: "Let users search their bookmarks by words in the title. A search returns matching bookmarks newest first, can be combined with the tag filter, and pages the same way the bookmark list does. Search ignores letter case."

## Clarifications

### Session 2026-10-25

- Q: When the search has several words, must a title contain all of them, or is any one of them enough? → A: All words must appear in the title, in any order.
- Q: Does a search word have to match a whole word in the title, or does matching part of a word count? → A: Whole words only.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Search bookmarks by title words (Priority: P1)

A user remembers part of a bookmark's title, for example "postgres indexing", and searches for it
instead of scrolling through the whole list. They get back the bookmarks whose titles match, with
the most recently saved at the top.

**Why this priority**: This is the feature. Once a user has many bookmarks, finding one by what it
was called is the most direct way back to it; everything else in this spec refines this search.

**Independent Test**: Can be fully tested by saving bookmarks with different titles, searching for
a word that appears in some of them, and confirming that only those bookmarks are returned, newest
first.

**Acceptance Scenarios**:

1. **Given** bookmarks titled "Postgres indexing guide", "Python packaging" and "Indexing in
   Postgres 17", saved in that order, **When** the user searches for "indexing", **Then** "Indexing
   in Postgres 17" and "Postgres indexing guide" are returned, in that order, and "Python packaging"
   is not.
2. **Given** a bookmark titled "FastAPI Tips", **When** the user searches for "fastapi", "FASTAPI"
   or "FastAPI", **Then** the bookmark is returned each time (search ignores letter case).
3. **Given** bookmarks titled "Postgres indexing guide" and "Postgres backups", **When** the user
   searches for "postgres indexing" or "indexing postgres", **Then** only "Postgres indexing guide"
   is returned (every search word must be in the title, in any order).
4. **Given** a bookmark titled "Postgres indexing guide", **When** the user searches for "index",
   **Then** the bookmark is not returned (search words match whole title words only).
5. **Given** bookmarks exist, **When** the user searches for a word no title contains, **Then** an
   empty list with a total count of zero and no next-page token is returned.
6. **Given** any state, **When** the user sends a search that is empty or only spaces, or longer
   than 200 characters, **Then** the user receives a validation error explaining what is allowed.

---

### User Story 2 - Combine search with the tag filter (Priority: P2)

A user who has tagged their bookmarks narrows a search to one tag, for example title words
"indexing" within bookmarks tagged "postgres".

**Why this priority**: The tag filter already exists; letting search and tags work together makes
both more useful, but search alone already delivers value.

**Independent Test**: Can be tested by saving bookmarks whose titles match a search word with and
without a given tag, then searching with that tag and confirming only bookmarks matching both are
returned, newest first.

**Acceptance Scenarios**:

1. **Given** bookmarks "Postgres indexing guide" tagged "postgres", "Indexing in SQLite" tagged
   "sqlite" and "Postgres backups" tagged "postgres", **When** the user searches for "indexing"
   with the tag filter "postgres", **Then** only "Postgres indexing guide" is returned.
2. **Given** a bookmark "Postgres indexing guide" tagged "postgres", **When** the user searches for
   "indexing" with the tag filter "Postgres", **Then** the bookmark is returned (the tag filter is
   normalized exactly as it is for the bookmark list).
3. **Given** bookmarks exist, **When** the user searches with a tag no matching bookmark has,
   **Then** an empty list with a total count of zero is returned.
4. **Given** any state, **When** the user searches with an invalid tag filter, **Then** the user
   receives the same validation error the bookmark list gives for that tag.

---

### User Story 3 - Page through search results (Priority: P3)

A user whose search matches many bookmarks reads the results a page at a time, exactly as they
page through their bookmark list.

**Why this priority**: Paging matters only once a search returns more than one page; small
collections are fully served by Story 1.

**Independent Test**: Can be tested by saving more bookmarks with a matching title than fit on one
page, then following the next-page token until it runs out, and confirming every match appears
exactly once, newest first.

**Acceptance Scenarios**:

1. **Given** 25 bookmarks whose titles contain "python", **When** the user searches for "python"
   without paging options, **Then** the 20 newest are returned with a total count of 25 and a
   next-page token; **When** the user asks for the next page with that token, **Then** the remaining
   5 are returned with no next-page token.
2. **Given** matching bookmarks exist, **When** the user asks for more than 100 per page, or sends a
   next-page token that is malformed, **Then** the user receives the same error the bookmark list
   gives for those cases.
3. **Given** 25 matching bookmarks and the user has fetched the first page, **When** a new matching
   bookmark is saved and the user asks for the next page with the token, **Then** the next page
   holds exactly the 5 older matches, with no bookmark repeated or skipped.
4. **Given** the user has a next-page token from one search, **When** they use it with a different
   search or a different tag filter, **Then** the user receives a validation error rather than a
   page from the wrong result set.

---

### Edge Cases

- Search ignores letter case in both the search words and the titles.
- Spaces at the start or end of the search, and repeated spaces between words, are ignored.
- Punctuation in titles separates words, so "Postgres: indexing" contains the words "postgres" and
  "indexing".
- A search that is empty, only spaces, or longer than 200 characters is rejected with a validation
  error.
- Two bookmarks saved at the same moment still have a stable newest-first order across pages.
- A next-page token issued for one search and tag filter is rejected when used with another.
- Bookmarks saved or deleted between page requests never cause a match to be repeated or skipped.
- A search with no matches returns an empty list, a total of zero and no next-page token, not an
  error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST let a user search their bookmarks by one or more words, returning only
  bookmarks whose titles contain every one of those words, in any order.
- **FR-002**: System MUST ignore letter case when matching search words against titles.
- **FR-003**: System MUST match each search word against whole words in the title only; part of a
  word does not match (a search for "index" does not match a title containing only "indexing").
- **FR-004**: System MUST return search results ordered by saved time, most recent first, with a
  stable order for bookmarks saved at the same moment.
- **FR-005**: System MUST let the user combine a search with the existing tag filter, returning
  only bookmarks that match both; the tag filter value is normalized and validated exactly as it is
  for the bookmark list.
- **FR-006**: System MUST page search results the same way as the bookmark list: 20 per page by
  default and at most 100, the total number of matching bookmarks, and an opaque next-page token
  (none on the last page). Paging MUST NOT repeat or skip a match when bookmarks are saved or
  deleted between requests, and MUST NOT use offset paging.
- **FR-007**: System MUST reject a next-page token that is malformed or that was issued for a
  different search or tag filter, with a validation error.
- **FR-008**: System MUST reject a search that is empty or only spaces after trimming, or longer
  than 200 characters, with a validation error that explains what is allowed.
- **FR-009**: System MUST return every search error in the same error format as the rest of the
  API.
- **FR-010**: System MUST leave the existing bookmark list and tag filter unchanged for requests
  that do not include a search.

### Key Entities *(include if feature involves data)*

- **Bookmark**: The existing saved link (identifier, link, title, saved time, tags). Search reads
  its title, saved time and tags; this feature adds no new stored data that users see.
- **Search**: What the user asks for: one or more words, optionally with a tag filter and paging
  options. It is not saved.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can find a saved bookmark by a word in its title with a single search request.
- **SC-002**: In 100% of tested cases, a search returns every bookmark whose title matches and no
  bookmark whose title does not.
- **SC-003**: In 100% of tested cases, a search with a tag filter returns only bookmarks that match
  both the words and the tag.
- **SC-004**: Paging through any search result, while bookmarks are added between requests, shows
  every match exactly once.
- **SC-005**: With 10,000 saved bookmarks, 95% of searches return their first page in under one
  second.
- **SC-006**: Every acceptance scenario above is covered by an automated test that passes, and
  every error a user can trigger returns the same error format.

## Assumptions

- The API still serves a single user, as in the bookmarks API; "their bookmarks" means all
  bookmarks.
- Search looks only at titles. Links, tags (other than through the tag filter) and any page content
  are not searched.
- Search words are matched as typed after case is ignored; there is no stemming, spelling
  correction, synonyms or relevance ranking. Results are always newest first.
- Letters with accents are matched as typed; "café" does not match "cafe".
- The 200-character limit on a search matches the 200-character limit on titles.
- Search is offered on the existing list of bookmarks rather than as a separate kind of result,
  so a search page has the same shape as a list page.
- Editing titles remains out of scope, so a bookmark's title words do not change after it is saved.
