# 02 clarify (feature2-r2)

Start: 2026-10-25T12:18:58Z

Command: `/speckit-clarify` (no arguments)

## Pre-Execution Checks

hooks.before_clarify: one enabled hook, optional: true, condition null. Output:

```
## Extension Hooks

**Optional Pre-Hook**: git
Command: `/speckit-git-commit`
Description: Auto-commit before spec clarification

Prompt: Commit outstanding changes before clarification?
To execute: `/speckit-git-commit`
```

Optional hook run by run rule (`/speckit-git-commit`, event before_clarify). commit_style fixed.

```console
$ git status --short
[exit 0]
```

```console
$ .specify/extensions/git/scripts/bash/auto-commit.sh before_clarify
[exit 0]
```
(No output: git-config.yml has auto_commit.before_clarify.enabled: false, so the script exits 0 without committing.)
## Outline step 1

```console
$ .specify/scripts/bash/check-prerequisites.sh --json --paths-only
{"REPO_ROOT":"/home/claude/ep08-runs/feature2-r2/repo","BRANCH":"002-bookmark-title-search","FEATURE_DIR":"/home/claude/ep08-runs/feature2-r2/repo/specs/002-bookmark-title-search","FEATURE_SPEC":"/home/claude/ep08-runs/feature2-r2/repo/specs/002-bookmark-title-search/spec.md","IMPL_PLAN":"/home/claude/ep08-runs/feature2-r2/repo/specs/002-bookmark-title-search/plan.md","TASKS":"/home/claude/ep08-runs/feature2-r2/repo/specs/002-bookmark-title-search/tasks.md"}
[exit 0]
```

## Outline step 2-4: constitution loaded; coverage scan (internal map, recorded here for the capture)

| Category | Status | Note |
|---|---|---|
| Functional scope & behavior | Clear | title-only search, all words, whole words, newest first |
| Domain & data model | Clear | no new stored data; Search is transient |
| Interaction & UX flow | Partial | whether search is its own request or an option on the list decides what a request without search words does (FR-008 vs FR-011) |
| Non-functional (performance) | Clear | SC-004: first page < 1 s at 100k bookmarks |
| Non-functional (observability, security) | Clear | single user, read-only; same as 001 |
| Integration & external dependencies | Clear | none |
| Edge cases & failure handling | Partial | which characters belong to a word (hyphens, apostrophes, digits, non-English letters) is not defined, so "punctuation separates words" is not fully testable; a next-page token reused with a different search or tag is undefined |
| Constraints & tradeoffs | Clear | |
| Terminology & consistency | Clear | "search", "next-page token" used consistently |
| Completion signals | Clear | |
| Misc / placeholders | Clear | no markers |

Queue (internal, max 5): 3 questions with material impact. Asked one at a time.

## Questions asked (verbatim, one at a time) and answers

### Question 1

**Question:** Should searching be a separate request of its own, or an optional search option added to the existing bookmark list request?

Why it matters: it decides whether a request with no search words is an error (FR-008) or simply the normal list, and whether the existing list request changes at all (FR-011).

**Recommended:** Option A - A separate search request keeps the existing list exactly as it is (FR-011) and lets a missing or empty search be a clear error (FR-008) instead of silently returning everything.

| Option | Description |
|--------|-------------|
| A | A separate search request that requires search words; the bookmark list request is unchanged |
| B | An optional search option on the bookmark list request; leaving it out lists all bookmarks |
| Short | Provide a different short answer (<=5 words) |

You can reply with the option letter (e.g., "A"), accept the recommendation by saying "yes" or "recommended", or provide your own short answer.

**Answer given:** "recommended" (→ A).
**Rule used:** clarify: the feature request ("search their bookmarks ... can be combined with the tag filter, and pages the same way the bookmark list does") does not say whether search is its own request or part of the list, so it does not cover the question; multiple-choice → "recommended".

Integrated: Clarifications section created with Session 2026-10-25; FR-001 updated. Spec saved.

### Question 2

**Question:** Which characters make up a word, in both the search and the title?

Why it matters: a test cannot decide whether "spec-kit", "don't" or "Python3" match without a rule, and the Edge Cases only say "punctuation separates words".

**Recommended:** Option A - One simple rule for every input: a word is an unbroken run of letters (in any alphabet) and digits, and everything else separates words, so "spec-kit" is the two words "spec" and "kit" in both the search and the title and still finds itself.

| Option | Description |
|--------|-------------|
| A | Letters (any alphabet) and digits; every other character separates words |
| B | Letters and digits, plus hyphens and apostrophes inside a word ("spec-kit" is one word) |
| C | Only the English letters a to z and digits; other characters separate words |
| Short | Provide a different short answer (<=5 words) |

You can reply with the option letter (e.g., "A"), accept the recommendation by saying "yes" or "recommended", or provide your own short answer.

**Answer given:** "recommended" (→ A).
**Rule used:** clarify: the feature request says "words in the title" but does not define what a word is; not covered → multiple-choice → "recommended".

Integrated: Clarifications bullet added; Edge Cases (word definition bullet replaced, no obsolete "punctuation" wording left), FR-003, FR-008, User Story 1 scenario 5 updated. Spec saved.

### Question 3

**Question:** What should happen when a next-page token from one search is sent with different search words or a different tag?

Why it matters: a test for paging needs to know whether that request is an error or simply continues from the token's place in the list, and the bookmark list's token does not record which filter produced it.

**Recommended:** Option A - It matches how the bookmark list already treats its token (a position in the newest-first order, not tied to a filter), so search "pages the same way the bookmark list does" and needs no new token format.

| Option | Description |
|--------|-------------|
| A | Accept it: the page starts after the token's position, using the new search and tag |
| B | Reject it with a validation error; a token only works with the search and tag that produced it |
| Short | Provide a different short answer (<=5 words) |

You can reply with the option letter (e.g., "A"), accept the recommendation by saying "yes" or "recommended", or provide your own short answer.

**Answer given:** "A".
**Rule used:** clarify: answered from the feature request, which covers it: "pages the same way the bookmark list does". The bookmark list (specs/001, cursor.py) uses a token that is only a position and accepts it with any tag, so the same behavior is option A. (Option A is also the marked recommendation.)

Integrated: Clarifications bullet added; new Edge Cases bullet. Spec saved. Queue exhausted after 3 questions (all critical ambiguities resolved); no further questions.

## Step 7 validation

- Clarifications session has exactly 3 bullets, one per accepted answer.
- 3 questions asked (≤ 5).
- No obsolete "spaces and punctuation" wording remains in FR-008, Edge Cases or US1-5 (replaced by "separators").
- Only new headings: `## Clarifications`, `### Session 2026-10-25`.

## Step 9: Spec quality checklist re-validation

Before snapshot: 16/16 checked. Re-evaluated against the updated spec: every item still passes; no marker changed. checklists/requirements.md not modified.

```console
$ git diff --stat
 specs/002-bookmark-title-search/spec.md | 33 ++++++++++++++++++++++++---------
 1 file changed, 24 insertions(+), 9 deletions(-)
[exit 0]
```

```console
$ git diff | cat
diff --git a/specs/002-bookmark-title-search/spec.md b/specs/002-bookmark-title-search/spec.md
index 4ea9ef7..e885f3c 100644
--- a/specs/002-bookmark-title-search/spec.md
+++ b/specs/002-bookmark-title-search/spec.md
@@ -8,6 +8,14 @@
 
 **Input**: User description: "Let users search their bookmarks by words in the title. A search returns matching bookmarks newest first, can be combined with the tag filter, and pages the same way the bookmark list does. Search ignores letter case."
 
+## Clarifications
+
+### Session 2026-10-25
+
+- Q: Should searching be a separate request of its own, or an optional search option added to the existing bookmark list request? → A: A separate search request that requires search words; the bookmark list request is unchanged.
+- Q: Which characters make up a word, in both the search and the title? → A: A word is an unbroken run of letters (any alphabet) and digits; every other character separates words.
+- Q: What should happen when a next-page token from one search is sent with different search words or a different tag? → A: Accept it, as the bookmark list does: the token is only a position in the newest-first order, and the page starts after that position using the new search and tag.
+
 ## User Scenarios & Testing *(mandatory)*
 
 ### User Story 1 - Search bookmarks by title words (Priority: P1)
@@ -34,8 +42,8 @@ a word that appears in some of them, and confirming only those bookmarks come ba
 4. **Given** a bookmark titled "Postgres indexing guide", **When** the user searches for
    "indexing postgres", **Then** the bookmark is returned (every word must appear, in any order);
    **When** the user searches for "postgres backups", **Then** it is not returned.
-5. **Given** any state, **When** the user sends a search that is empty, contains only spaces or
-   punctuation, or is longer than 200 characters, **Then** nothing is searched and the user
+5. **Given** any state, **When** the user sends a search that is missing, empty, contains only
+   separators (for example "  -- !"), or is longer than 200 characters, **Then** nothing is searched and the user
    receives an error explaining what is allowed.
 
 ---
@@ -100,15 +108,20 @@ following the next-page token until it runs out, confirming every match is seen
   the same bookmarks.
 - Leading, trailing and repeated spaces in the search are ignored; "  postgres   guide " is the same
   search as "postgres guide".
-- Punctuation in the search or the title separates words: a title "FastAPI: a tutorial" contains
-  the words "fastapi", "a" and "tutorial".
+- A word is an unbroken run of letters (in any alphabet) and digits; every other character,
+  including spaces, punctuation, hyphens and apostrophes, separates words, in both the search and
+  the title. A title "FastAPI: a tutorial" contains the words "fastapi", "a" and "tutorial"; a
+  title "Spec-Kit guide" contains "spec", "kit" and "guide", so the search "spec-kit" finds it.
 - A search word matches only a whole title word: "postgres" finds "Postgres backups", but "post"
   does not find "Postgres" and "gres" does not find "Postgres".
-- A search with no words left after removing spaces and punctuation is rejected with a validation
+- A search with no words left after removing separators is rejected with a validation
   error, not treated as "match everything".
 - A search for a word that appears in a bookmark's link or tags but not its title does not match
   that bookmark; only the title is searched.
 - Bookmarks saved or deleted between page requests never cause a match to be repeated or skipped.
+- A next-page token is only a position in the newest-first order. Sent with different search words
+  or a different tag, it is accepted and the page starts after that position using the new search
+  and tag, exactly as the bookmark list treats its token.
 - A deleted bookmark no longer appears in search results.
 
 ## Requirements *(mandatory)*
@@ -116,10 +129,12 @@ following the next-page token until it runs out, confirming every match is seen
 ### Functional Requirements
 
 - **FR-001**: System MUST let a user search their bookmarks by one or more words, matching against
-  the bookmark's title only.
+  the bookmark's title only. Search is a request of its own that requires search words; the
+  existing bookmark list request is not changed and gains no search option.
 - **FR-002**: Search MUST ignore letter case in both the search words and the titles.
-- **FR-003**: System MUST split the search into words on spaces and punctuation, ignoring leading,
-  trailing and repeated separators. When the search has several words, a bookmark MUST match only
+- **FR-003**: System MUST split both the search and each title into words, where a word is an
+  unbroken run of letters (any alphabet) and digits and every other character separates words,
+  ignoring leading, trailing and repeated separators. When the search has several words, a bookmark MUST match only
   when its title contains all of the words, in any order.
 - **FR-004**: A search word MUST match only a whole word of the title, never part of a longer word
   ("post" does not match "Postgres").
@@ -132,7 +147,7 @@ following the next-page token until it runs out, confirming every match is seen
   (none on the last page). Paging with the token MUST NOT repeat or skip bookmarks when bookmarks
   are saved or deleted between requests (Constitution VI).
 - **FR-008**: System MUST reject a search that is missing, empty, has no words after removing
-  spaces and punctuation, or is longer than 200 characters, and MUST explain what is allowed.
+  separators, or is longer than 200 characters, and MUST explain what is allowed.
 - **FR-009**: System MUST reject the same invalid paging and tag inputs the bookmark list rejects
   (page size outside 1 to 100, malformed next-page token, the removed offset option, invalid tag),
   with the same errors.
[exit 0]
```

## Mandatory Post-Execution Hooks

hooks.after_clarify: one enabled hook, optional: true, condition null. Output:

```
## Extension Hooks

**Optional Hook**: git
Command: `/speckit-git-commit`
Description: Auto-commit after spec clarification

Prompt: Commit clarification changes?
To execute: `/speckit-git-commit`
```

Optional hook run by run rule (`/speckit-git-commit`, event after_clarify).

```console
$ .specify/extensions/git/scripts/bash/auto-commit.sh after_clarify
[OK] Changes committed after clarify
[exit 0]
```

```console
$ git status --short; git show --stat HEAD | cat
commit f0e2089639a2f44e5b332818c54607f4e14eb077
Author: Tech Shipped <techshippedstudio-glitch@users.noreply.github.com>
Date:   Sun Oct 25 12:20:53 2026 +0000

    [Spec Kit] Clarify specification

 specs/002-bookmark-title-search/spec.md | 33 ++++++++++++++++++++++++---------
 1 file changed, 24 insertions(+), 9 deletions(-)
[exit 0]
```

## Completion report (verbatim)

> Clarification complete.
>
> - Questions asked and answered: 3 (of 5 maximum).
> - Updated spec: specs/002-bookmark-title-search/spec.md
> - Sections touched: Clarifications (new, Session 2026-10-25), User Story 1 (scenario 5), Edge Cases, Functional Requirements (FR-001, FR-003, FR-008).
> - Spec Quality Checklist: 16/16 → 16/16 items passing. No items changed state; none unchecked.
>
> | Category | Status |
> |---|---|
> | Functional scope & behavior | Clear |
> | Domain & data model | Clear |
> | Interaction & UX flow | Resolved (search is its own request) |
> | Non-functional quality attributes | Clear |
> | Integration & external dependencies | Clear |
> | Edge cases & failure handling | Resolved (word characters; token reused with another search) |
> | Constraints & tradeoffs | Clear |
> | Terminology & consistency | Clear |
> | Completion signals | Clear |
> | Misc / placeholders | Clear |
>
> No Outstanding or Deferred items. Committed by the after_clarify hook ("[Spec Kit] Clarify specification").
> Suggested next command: `/speckit-plan`.

## Files changed

- specs/002-bookmark-title-search/spec.md (24 insertions, 9 deletions; 33 diff lines)

## Post-step state

```console
$ git diff --stat ep08-feature2-r2-specify HEAD
 specs/002-bookmark-title-search/spec.md | 33 ++++++++++++++++++++++++---------
 1 file changed, 24 insertions(+), 9 deletions(-)
[exit 0]
```

```console
$ git branch
* 002-bookmark-title-search
  main
[exit 0]
```

```console
$ git rev-parse --abbrev-ref HEAD
002-bookmark-title-search
[exit 0]
```

```console
$ git log --oneline -5
f0e2089 [Spec Kit] Clarify specification
aee86b8 [Spec Kit] Add specification
ba2fdc9 ep08 setup: add Spec Kit git extension (1.2.2), auto-commit after specify, clarify, plan, checklist, tasks, implement
48f6e31 ep08 baseline: capture of /speckit-analyze on 001 (taken before T037)
6f309f4 ep08 baseline: request model for GET /bookmarks query parameters (Constitution I, analyze CRITICAL)
[exit 0]
```

```console
$ cat .specify/feature.json
{
  "feature_directory": "specs/002-bookmark-title-search"
}
[exit 0]
```

```console
$ git tag ep08-feature2-r2-clarify && git rev-parse --short ep08-feature2-r2-clarify
f0e2089
[exit 0]
```

End: 2026-10-25T12:21:01Z
