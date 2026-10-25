# 01 specify (feature2-r2)

Start: 2026-10-25T12:16:17Z

Command: `/speckit-specify Let users search their bookmarks by words in the title. A search returns matching bookmarks newest first, can be combined with the tag filter, and pages the same way the bookmark list does. Search ignores letter case.`

## Pre-Execution Checks

.specify/extensions.yml parsed; hooks.before_specify has one enabled hook with condition null:

```
## Extension Hooks

**Automatic Pre-Hook**: git
Executing: `/speckit-git-feature`
EXECUTE_COMMAND: speckit.git.feature

Wait for the result of the hook command before proceeding to the Outline.
```

Mandatory hook carried out per .claude/skills/speckit-git-feature/SKILL.md (run rule: mandatory hooks).
Branch numbering: git-config.yml branch_numbering=sequential; branch_template and branch_prefix empty. Short name generated: bookmark-title-search.

```console
$ git rev-parse --is-inside-work-tree 2>/dev/null
true
[exit 0]
```

```console
$ .specify/extensions/git/scripts/bash/create-new-feature-branch.sh --json --short-name "bookmark-title-search" "Let users search their bookmarks by words in the title. A search returns matching bookmarks newest first, can be combined with the tag filter, and pages the same way the bookmark list does. Search ignores letter case."
# To persist: export SPECIFY_FEATURE=002-bookmark-title-search
{"BRANCH_NAME":"002-bookmark-title-search","FEATURE_NUM":"002"}
[exit 0]
```

```console
$ git rev-parse --abbrev-ref HEAD; git branch
002-bookmark-title-search
* 002-bookmark-title-search
  main
[exit 0]
```

## Outline step 3: feature directory

init-options.json feature_numbering=sequential; highest existing in specs/ is 001, so SPECIFY_FEATURE_DIRECTORY=specs/002-bookmark-title-search.

```console
$ ls specs; .specify/scripts/bash/resolve-template.sh spec-template --json | head -c 300; echo
001-bookmarks-api
{"TEMPLATE_NAME":"spec-template","TEMPLATE_CONTENT":"# Feature Specification: [FEATURE NAME]\n\n**Feature Branch**: `[###-feature-name]`\n\n**Created**: [DATE]\n\n**Status**: Draft\n\n**Input**: User description: \"$ARGUMENTS\"\n\n## User Scenarios & Testing *(mandatory)*\n\n<!--\n  IMPORTANT: User 
[exit 0]
```

```console
$ mkdir -p specs/002-bookmark-title-search && .specify/scripts/bash/resolve-template.sh spec-template > specs/002-bookmark-title-search/spec.md && printf "{\n  \"feature_directory\": \"specs/002-bookmark-title-search\"\n}\n" > .specify/feature.json && cat .specify/feature.json && wc -l specs/002-bookmark-title-search/spec.md
{
  "feature_directory": "specs/002-bookmark-title-search"
}
131 specs/002-bookmark-title-search/spec.md
[exit 0]
```

## Spec written, validation iteration 1

Wrote specs/002-bookmark-title-search/spec.md (from the resolved spec-template) and
specs/002-bookmark-title-search/checklists/requirements.md.

```console
$ grep -n "NEEDS CLARIFICATION" specs/002-bookmark-title-search/spec.md; grep -c "NEEDS CLARIFICATION" specs/002-bookmark-title-search/spec.md
104:- How a search word matches a title word: [NEEDS CLARIFICATION: does a search word match only a
123:  [NEEDS CLARIFICATION: all of the words / any of the words / the exact phrase appear in its
2
[exit 0]
```

**[NEEDS CLARIFICATION] marker count (run rule: count before answering): 2.**

(During drafting a third marker was placed in User Story 1 scenario 4; it asked the same question as
FR-003, so it was folded into a reference to FR-003 before the count. Final count at validation: 2.)

Validation result, iteration 1: all items pass except "No [NEEDS CLARIFICATION] markers remain".

## Questions presented (verbatim)

## Question 1: Several search words

**Context**: "FR-003: ... When the search has several words, a bookmark MUST match when [NEEDS CLARIFICATION: all of the words / any of the words / the exact phrase appear in its title]."

**What we need to know**: When the search has several words, must a title contain all of them, any of them, or the exact phrase?

**Suggested Answers**:

| Option | Answer | Implications |
|--------|--------|--------------|
| A      | All of the words, in any order | Each extra word narrows the results; "indexing postgres" finds "Postgres indexing guide" |
| B      | Any of the words | Each extra word widens the results; broad searches return many bookmarks |
| C      | The exact phrase, words in order | "indexing postgres" does not find "Postgres indexing guide"; precise but unforgiving |
| Custom | Provide your own answer | Describe the rule for several words |

**Your choice**: _[Wait for user response]_

## Question 2: How a search word matches a title word

**Context**: "Edge Cases: How a search word matches a title word: [NEEDS CLARIFICATION: does a search word match only a whole title word ("post" does not find "Postgres"), the start of a title word ("post" finds "Postgres"), or any part of the title ("gres" finds "Postgres")?]"

**What we need to know**: Does a search word match only a whole title word, the start of a title word, or any part of the title?

**Suggested Answers**:

| Option | Answer | Implications |
|--------|--------|--------------|
| A      | Whole words only | "postgres" finds "Postgres backups" but "post" does not; fewest surprising matches |
| B      | Start of a word | "post" finds "Postgres"; good for partial typing, a few more matches |
| C      | Any part of the title | "gres" finds "Postgres"; most matches, including accidental ones inside longer words |
| Custom | Provide your own answer | Describe the matching rule |

**Your choice**: _[Wait for user response]_

## Answers given (run rule: "specify questions: answer from the feature request where it covers the question; otherwise answer option A")

- Q1: The feature request ("search their bookmarks by words in the title") does not say how several
  words combine. Not covered → **A** (all of the words, in any order). Rule: option A.
- Q2: The feature request says "words in the title", which points at word-based matching but does not
  decide whole word vs start of word. Not covered → **A** (whole words only). Rule: option A.

Reply recorded as: "Q1: A, Q2: A".

Spec updated with the answers: FR-003 (all words, any order), FR-004 and the Edge Case (whole words
only), User Story 1 scenario 4 made concrete. Validation iteration 2: all checklist items pass.

```console
$ grep -c "NEEDS CLARIFICATION" specs/002-bookmark-title-search/spec.md
0
```

## Mandatory Post-Execution Hooks

hooks.after_specify: one enabled hook, optional: true, condition null. Output:

```
## Extension Hooks

**Optional Hook**: git
Command: `/speckit-git-commit`
Description: Auto-commit after specification

Prompt: Commit specification changes?
To execute: `/speckit-git-commit`
```

Optional hook run by run rule (`/speckit-git-commit`, event after_specify). git-config.yml commit_style: fixed, so the script runs with just the event name.

```console
$ git status --short
?? specs/002-bookmark-title-search/
[exit 0]
```

```console
$ .specify/extensions/git/scripts/bash/auto-commit.sh after_specify
[OK] Changes committed after specify
[exit 0]
```

```console
$ git status --short; git log --oneline -3; git show --stat HEAD | cat
aee86b8 [Spec Kit] Add specification
ba2fdc9 ep08 setup: add Spec Kit git extension (1.2.2), auto-commit after specify, clarify, plan, checklist, tasks, implement
48f6e31 ep08 baseline: capture of /speckit-analyze on 001 (taken before T037)
commit aee86b8720c8a0ed005b5d79ca4d88267d87c81f
Author: Tech Shipped <techshippedstudio-glitch@users.noreply.github.com>
Date:   Sun Oct 25 12:18:23 2026 +0000

    [Spec Kit] Add specification

 .../checklists/requirements.md                     |  38 +++++
 specs/002-bookmark-title-search/spec.md            | 175 +++++++++++++++++++++
 2 files changed, 213 insertions(+)
[exit 0]
```

## Completion report (verbatim)

> Specification ready.
>
> - `SPECIFY_FEATURE_DIRECTORY`: specs/002-bookmark-title-search
> - `SPEC_FILE`: specs/002-bookmark-title-search/spec.md
> - Branch (from before_specify hook): 002-bookmark-title-search (FEATURE_NUM 002)
> - Checklist: specs/002-bookmark-title-search/checklists/requirements.md, 16/16 items pass after 2 validation iterations. Iteration 1 found 2 [NEEDS CLARIFICATION] markers (several-word rule, word-matching rule); both answered (Q1: A all words in any order; Q2: A whole words only).
> - Spec: 3 user stories (P1 search by title words, P2 combine with tag filter, P3 page through results), 14 acceptance scenarios, 11 functional requirements, 5 success criteria.
> - Commit: after_specify optional hook run, "[Spec Kit] Add specification".
> - Ready for `/speckit-clarify` (recommended) or `/speckit-plan`.

## Files created or changed

- specs/002-bookmark-title-search/spec.md (new)
- specs/002-bookmark-title-search/checklists/requirements.md (new)
- .specify/feature.json (new, git-ignored by .specify/.gitignore, so not in the commit)

## Post-step state

```console
$ git diff --stat ba2fdc9 HEAD
 .../checklists/requirements.md                     |  38 +++++
 specs/002-bookmark-title-search/spec.md            | 175 +++++++++++++++++++++
 2 files changed, 213 insertions(+)
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
aee86b8 [Spec Kit] Add specification
ba2fdc9 ep08 setup: add Spec Kit git extension (1.2.2), auto-commit after specify, clarify, plan, checklist, tasks, implement
48f6e31 ep08 baseline: capture of /speckit-analyze on 001 (taken before T037)
6f309f4 ep08 baseline: request model for GET /bookmarks query parameters (Constitution I, analyze CRITICAL)
34b667c ep08 baseline: clear pre-existing 001 spec debt (offset leftovers marked superseded, contract error-code enum matches errors.py)
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
$ git tag ep08-feature2-r2-specify && git rev-parse --short ep08-feature2-r2-specify
aee86b8
[exit 0]
```

End: 2026-10-25T12:18:34Z
