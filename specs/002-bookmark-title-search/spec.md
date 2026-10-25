# Feature Specification: Bookmark Title Search

**Feature Branch**: `002-bookmark-title-search`

**Created**: 2026-10-25

**Status**: Draft

**Input**: User description: "Let users search their bookmarks by words in the title. A search returns matching bookmarks newest first, can be combined with the tag filter, and pages the same way the bookmark list does. Search ignores letter case."

## Clarifications

### Session 2026-10-25

- Q: When a client takes a next-page token from one search and sends it with a different search or tag filter, what should happen? → A: Same as the bookmark list: the token only marks a position; the next page holds the bookmarks after that position that match the search now sent, with no error.
- Q: How fast must a search answer for a collection of 10,000 bookmarks? → A: 95% of searches answer in under 1 second.
- Q: Should a search word have a minimum length, given that a word matches anywhere in a title? → A: No minimum: any search word of at least 1 character is allowed.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Search bookmarks by title words (Priority: P1)

A user remembers a word or two from the title of something they saved and searches for it, getting
back only the bookmarks whose title contains those words, with the most recently saved first.

**Why this priority**: Finding a saved link by what it was called is the whole point of the
feature; the tag combination and paging build on it.

**Independent Test**: Can be fully tested by saving bookmarks with different titles, searching for
a word that appears in some of them, and confirming only those are returned, newest first, whatever
the letter case of the search or the title.

**Acceptance Scenarios**:

1. **Given** bookmarks titled "Postgres indexing guide", "Python tips" and "Advanced Postgres
   tuning" saved in that order, **When** the user searches for "postgres", **Then** "Advanced
   Postgres tuning" and "Postgres indexing guide" are returned, in that order, with a total count of
   2.
2. **Given** a bookmark titled "FastAPI Tutorial", **When** the user searches for "fastapi",
   "FASTAPI" or "FastAPI", **Then** the bookmark is returned each time (search ignores letter case).
3. **Given** bookmarks titled "Postgres indexing guide" and "Postgres backup scripts", **When** the
   user searches for "postgres guide", **Then** only "Postgres indexing guide" is returned (every
   search word must appear in the title, in any order).
4. **Given** bookmarks exist, **When** the user searches for a word no title contains, **Then** an
   empty list with a total count of 0 is returned, not an error.
5. **Given** any state, **When** the user sends no search, a search that is empty or contains only
   spaces, or one longer than 200 characters, **Then** the user receives an error explaining what is
   allowed.

---

### User Story 2 - Combine search with the tag filter (Priority: P2)

A user narrows a search to one tag, for example titles mentioning "indexing" among bookmarks tagged
"postgres".

**Why this priority**: The tag filter already exists; combining the two lets a growing collection
stay usable, but search alone already delivers value.

**Independent Test**: Can be tested by saving bookmarks with overlapping title words and different
tags, then searching with a tag filter and confirming only bookmarks matching both are returned,
newest first.

**Acceptance Scenarios**:

1. **Given** bookmarks titled "Indexing basics" tagged "postgres", "Indexing basics for search"
   tagged "search", and "Postgres roles" tagged "postgres", **When** the user searches for
   "indexing" with the tag filter "postgres", **Then** only "Indexing basics" tagged "postgres" is
   returned.
2. **Given** a bookmark titled "Indexing basics" tagged "postgres", **When** the user searches for
   "INDEXING" with the tag filter "Postgres", **Then** the bookmark is returned (both the search and
   the tag filter ignore letter case).
3. **Given** bookmarks exist, **When** the user searches for a word that some titles contain with a
   tag none of those bookmarks carry, **Then** an empty list with a total count of 0 is returned.

---

### User Story 3 - Page through search results (Priority: P3)

A user whose search matches many bookmarks moves through the results page by page, exactly as they
would through the bookmark list.

**Why this priority**: Paging matters only once a search matches more than one page of bookmarks;
small collections are fully served by stories 1 and 2.

**Independent Test**: Can be tested by saving more matching bookmarks than fit on one page, then
following next-page tokens until the last page and confirming every match appears exactly once,
newest first.

**Acceptance Scenarios**:

1. **Given** 25 bookmarks whose titles contain "python" and 5 whose titles do not, **When** the user
   searches for "python" without paging options, **Then** the 20 newest matching bookmarks are
   returned with a total count of 25 and a next-page token; **When** the user asks for the next page
   with that token and the same search, **Then** the remaining 5 matching bookmarks are returned
   with no next-page token.
2. **Given** 25 matching bookmarks and the user has fetched the first page of a search, **When** a
   new matching bookmark is saved and the user asks for the next page with the token, **Then** the
   next page holds exactly the 5 older matching bookmarks, with none repeated and none skipped.
3. **Given** any state, **When** the user searches and asks for more than 100 per page, or sends a
   next-page token that is malformed, **Then** the user receives the same error the bookmark list
   gives for those mistakes.

---

### Edge Cases

- A search with several words matches a bookmark only when every word appears in its title; the
  order of the words does not matter, and repeating a word changes nothing.
- Whitespace at the start or end of a search, and repeated whitespace between words, is ignored.
- A search that is empty or only spaces is rejected with a validation error; it is not treated as
  "no search".
- A search longer than 200 characters (the longest possible title) is rejected with a validation
  error.
- There is no minimum word length: a one-character word such as "c" is a valid search and matches
  every title that contains that character.
- Letter case never affects a match, in the search or in the title.
- A search word matches anywhere in the title, including inside a longer word: "post" finds
  "Postgres", and "art" finds "Start".
- Characters with special meaning in patterns (such as `%`, `_` or `*`) in a search are matched as
  ordinary characters, never as wildcards.
- Bookmarks saved or deleted between page requests of a search never cause a match to be repeated
  or skipped.
- A next-page token only marks a position in the newest-first order, as it does for the bookmark
  list. Sent with a different search or tag filter, it returns the bookmarks after that position
  that match the search and filter now sent; it is not an error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow a user to search their bookmarks by one or more words, returning
  only bookmarks whose title contains every search word; a word matches anywhere in the title,
  including as part of a longer word.
- **FR-002**: Search MUST ignore letter case in both the search words and the titles.
- **FR-003**: System MUST split a search into words on whitespace (spaces, tabs and line breaks),
  ignoring leading, trailing and repeated whitespace.
- **FR-004**: System MUST reject a search that is missing, empty or only whitespace, or longer than
  200 characters, with a validation error that explains what is allowed. The 200-character limit
  applies to the search exactly as sent, including any surrounding spaces.
- **FR-005**: System MUST return search results ordered by saved time, most recent first, the same
  order as the bookmark list.
- **FR-006**: System MUST allow a search to be combined with the existing tag filter, returning only
  bookmarks that match the search and carry the tag; the tag filter is normalized the same way it is
  for the bookmark list.
- **FR-007**: System MUST page search results the same way the bookmark list pages: 20 per page by
  default and at most 100, the total number of matching bookmarks, and an opaque next-page token
  (none on the last page), with no repeated or skipped bookmarks when bookmarks are saved or deleted
  between requests (Constitution VI). Invalid page sizes and malformed tokens MUST be rejected the
  same way the bookmark list rejects them.
- **FR-008**: System MUST treat every character of a search word literally; no character acts as a
  wildcard or pattern.
- **FR-009**: System MUST report every search error in the same consistent error format used by the
  rest of the API, with a machine-readable code and a human-readable message.
- **FR-010**: Search results MUST present each bookmark exactly as the bookmark list does (same
  fields and values).
- **FR-011**: Searching MUST NOT change any bookmark.

### Key Entities

- **Bookmark** (existing): A saved link with an identifier, link, title (1 to 200 characters),
  saved time and up to 10 tags. Search reads its title, tags and saved time; nothing about it
  changes.
- **Search**: What the user asks for: one or more words, optionally a tag, a page size and a
  next-page token. It is not stored.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can find a saved bookmark by any word of its title in a single search request.
- **SC-002**: In 100% of tested cases, a search returns every bookmark whose title contains all the
  search words and no bookmark whose title does not, regardless of letter case.
- **SC-003**: Paging through any search result returns every matching bookmark exactly once, even
  when bookmarks are saved between page requests.
- **SC-004**: Every acceptance scenario above is covered by an automated test that passes, and the
  existing bookmark tests still pass.
- **SC-005**: Every error a user can trigger through search returns the same error format as the
  rest of the API.
- **SC-006**: For a collection of 10,000 bookmarks, 95% of searches return their page of results
  in under 1 second.

## Assumptions

- The single-user model of the existing bookmarks API is unchanged: all bookmarks belong to one
  user, so a search covers all bookmarks.
- Only titles are searched; links and tags are not searched by text (the tag filter covers tags).
- Words are separated by whitespace; there is no support for quoted phrases, "or", exclusion or
  other search operators in this version.
- There is no relevance ranking: results are always newest first, as the feature request says.
- Letter case is ignored for ordinary letters including accented ones; matching does not ignore
  accents (for example "cafe" does not find "café").
- Saving, listing, filtering and deleting bookmarks keep working exactly as they do today.
