# 01 specify — forward-r2

Start: 2026-10-24T11:58:06Z

```console
$ ls .specify/extensions.yml 2>&1; cat .specify/init-options.json; cat .specify/feature.json 2>&1; ls specs/
ls: cannot access '.specify/extensions.yml': No such file or directory
{
  "ai": "claude",
  "ai_skills": true,
  "allow_symlinks": false,
  "feature_numbering": "sequential",
  "here": true,
  "integration": "claude",
  "script": "sh",
  "speckit_version": "1.2.2"
}
cat: .specify/feature.json: No such file or directory
001-bookmarks-api
[exit 0]
```

```console
$ bash .specify/scripts/bash/resolve-template.sh spec-template 2>&1 || head -40 .specify/scripts/bash/resolve-template.sh
# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`

**Created**: [DATE]

**Status**: Draft

**Input**: User description: "$ARGUMENTS"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - [Brief Title] (Priority: P1)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently - e.g., "Can be fully tested by [specific action] and delivers [specific value]"]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]
2. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 2 - [Brief Title] (Priority: P2)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 3 - [Brief Title] (Priority: P3)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- What happens when [boundary condition]?
- How does system handle [error scenario]?

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST [specific capability, e.g., "allow users to create accounts"]
- **FR-002**: System MUST [specific capability, e.g., "validate email addresses"]
- **FR-003**: Users MUST be able to [key interaction, e.g., "reset their password"]
- **FR-004**: System MUST [data requirement, e.g., "persist user preferences"]
- **FR-005**: System MUST [behavior, e.g., "log all security events"]

*Example of marking unclear requirements:*

- **FR-006**: System MUST authenticate users via [NEEDS CLARIFICATION: auth method not specified - email/password, SSO, OAuth?]
- **FR-007**: System MUST retain user data for [NEEDS CLARIFICATION: retention period not specified]

### Key Entities *(include if feature involves data)*

- **[Entity 1]**: [What it represents, key attributes without implementation]
- **[Entity 2]**: [What it represents, relationships to other entities]

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: [Measurable metric, e.g., "Users can complete account creation in under 2 minutes"]
- **SC-002**: [Measurable metric, e.g., "System handles 1000 concurrent users without degradation"]
- **SC-003**: [User satisfaction metric, e.g., "90% of users successfully complete primary task on first attempt"]
- **SC-004**: [Business metric, e.g., "Reduce support tickets related to [X] by 50%"]

## Assumptions

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right assumptions based on reasonable defaults
  chosen when the feature description did not specify certain details.
-->

- [Assumption about target users, e.g., "Users have stable internet connectivity"]
- [Assumption about scope boundaries, e.g., "Mobile support is out of scope for v1"]
- [Assumption about data/environment, e.g., "Existing authentication system will be reused"]
- [Dependency on existing system/service, e.g., "Requires access to the existing user profile API"]
[exit 0]
```

```console
$ mkdir -p specs/002-idempotent-bookmark-save && cp .specify/templates/spec-template.md specs/002-idempotent-bookmark-save/spec.md && printf "{\n  \"feature_directory\": \"specs/002-idempotent-bookmark-save\"\n}\n" > .specify/feature.json && cat .specify/feature.json && ls specs/002-idempotent-bookmark-save
{
  "feature_directory": "specs/002-idempotent-bookmark-save"
}
spec.md
[exit 0]
```

## Agent actions (not shell commands)

- Read `.claude/skills/speckit-specify/SKILL.md`, `.specify/memory/constitution.md`, `specs/001-bookmarks-api/spec.md`.
- Short name chosen: `idempotent-bookmark-save`. Numbering: `sequential` → next number `002`.
- No `.specify/extensions.yml` → no before/after hooks (skipped silently per skill).
- Wrote `specs/002-idempotent-bookmark-save/spec.md` (from the resolved spec-template) with the Write tool, including a "Relationship to Earlier Specifications" section linking back to `specs/001-bookmarks-api` and stating it supersedes FR-004's duplicate rule.
- Wrote `specs/002-idempotent-bookmark-save/checklists/requirements.md` with the Write tool; validation iteration 1, all items pass.
- Questions the command would ask the user: none. No [NEEDS CLARIFICATION] markers were needed; every point was answerable from the change request (status codes, ignore title/tags, unchanged stored bookmark, concurrency outcome). One assumption made without asking (validation still runs on a re-save) is recorded in the spec's Assumptions/FR-005.

```console
$ cat specs/002-idempotent-bookmark-save/spec.md
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
[exit 0]
```

```console
$ cat specs/002-idempotent-bookmark-save/checklists/requirements.md
# Specification Quality Checklist: Idempotent Bookmark Save

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-10-24
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

- The spec names the response statuses 200 OK and 201 Created. These are kept deliberately: the
  change request defines the feature in exactly these externally observable terms, and they are
  the user-visible contract rather than an implementation choice. No framework, language or
  storage detail appears.
- The spec links back to `specs/001-bookmarks-api` and states that it supersedes the duplicate rule
  of 001 FR-004 (and the 001 acceptance scenario and edge case that restate it). 001 is not edited.
- Validation iteration 1: all items pass.
[exit 0]
```

## Spec Kit completion report (verbatim)

- **SPECIFY_FEATURE_DIRECTORY**: `specs/002-idempotent-bookmark-save`
- **SPEC_FILE**: `specs/002-idempotent-bookmark-save/spec.md`
- **Checklist results**: 16/16 items pass on iteration 1 (`specs/002-idempotent-bookmark-save/checklists/requirements.md`). No [NEEDS CLARIFICATION] markers.
- **Readiness**: Ready for `/speckit-plan` (`/speckit-clarify` optional; not needed).
- Extension hooks: none registered (`.specify/extensions.yml` absent).

End: 2026-10-24T11:59:06Z

```console
$ git status --short
?? episodes/
?? specs/002-idempotent-bookmark-save/
[exit 0]
```
