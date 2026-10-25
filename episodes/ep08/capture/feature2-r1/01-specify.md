# 01-specify (feature2-r1)

Start: 2026-10-25T12:16:11Z

Command: `/speckit-specify Let users search their bookmarks by words in the title. A search returns matching bookmarks newest first, can be combined with the tag filter, and pages the same way the bookmark list does. Search ignores letter case.`

Read .claude/skills/speckit-specify/SKILL.md in full.

## Pre-Execution Checks

```console
$ python3 -c "import yaml,json; d=yaml.safe_load(open('.specify/extensions.yml')); print(json.dumps(d['hooks']['before_specify'], indent=1))"
[
 {
  "extension": "git",
  "command": "speckit.git.feature",
  "enabled": true,
  "optional": false,
  "priority": 10,
  "prompt": "Execute speckit.git.feature?",
  "description": "Create feature branch before specification",
  "condition": null
 }
]
[exit 0]
```

Emitted (per SKILL.md, mandatory hook):

```
## Extension Hooks

**Automatic Pre-Hook**: git
Executing: `/speckit-git-feature`
EXECUTE_COMMAND: speckit.git.feature

Wait for the result of the hook command before proceeding to the Outline.
```

### Hook: /speckit-git-feature (mandatory, run per .claude/skills/speckit-git-feature/SKILL.md)

Prerequisite check, numbering mode (git-config.yml `branch_numbering: sequential`), template (`branch_template: ""` -> default `{number}-{slug}`). Short name chosen: `bookmark-title-search`. No GIT_BRANCH_NAME given, no --number passed.

```console
$ git rev-parse --is-inside-work-tree 2>/dev/null
true
[exit 0]
```

```console
$ grep -E '^(branch_numbering|branch_template|branch_prefix):' .specify/extensions/git/git-config.yml
branch_numbering: sequential
branch_template: ""
branch_prefix: ""
[exit 0]
```

```console
$ .specify/extensions/git/scripts/bash/create-new-feature-branch.sh --json --short-name "bookmark-title-search" "Let users search their bookmarks by words in the title. A search returns matching bookmarks newest first, can be combined with the tag filter, and pages the same way the bookmark list does. Search ignores letter case."
# To persist: export SPECIFY_FEATURE=002-bookmark-title-search
{"BRANCH_NAME":"002-bookmark-title-search","FEATURE_NUM":"002"}
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

## Outline step 3: create spec directory (feature_numbering: sequential; next number after scanning specs/)
```console
$ cat .specify/scripts/bash/resolve-template.sh
#!/usr/bin/env bash

set -e

SCRIPT_DIR="$(CDPATH="" cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

JSON_MODE=false
TEMPLATE_NAME=""

for arg in "$@"; do
    case "$arg" in
        --json) JSON_MODE=true ;;
        --help|-h)
            echo "Usage: $0 <template-name> [--json]"
            exit 0
            ;;
        -*)
            echo "ERROR: Unknown option '$arg'" >&2
            exit 1
            ;;
        *)
            if [[ -n "$TEMPLATE_NAME" ]]; then
                echo "ERROR: Unexpected argument '$arg'" >&2
                exit 1
            fi
            TEMPLATE_NAME="$arg"
            ;;
    esac
done

if [[ -z "$TEMPLATE_NAME" ]]; then
    echo "ERROR: Template name is required" >&2
    exit 1
fi

REPO_ROOT=$(get_repo_root)
if TEMPLATE_CONTENT=$(resolve_template_content "$TEMPLATE_NAME" "$REPO_ROOT"; status=$?; printf x; exit "$status"); then
    TEMPLATE_CONTENT="${TEMPLATE_CONTENT%x}"
else
    echo "ERROR: Could not resolve required $TEMPLATE_NAME from the template override stack for $REPO_ROOT" >&2
    exit 1
fi

if $JSON_MODE; then
    if has_jq; then
        jq -cn \
            --arg template_name "$TEMPLATE_NAME" \
            --arg template_content "$TEMPLATE_CONTENT" \
            '{TEMPLATE_NAME:$template_name,TEMPLATE_CONTENT:$template_content}'
    else
        printf '{"TEMPLATE_NAME":"%s","TEMPLATE_CONTENT":"%s"}\n' \
            "$(json_escape "$TEMPLATE_NAME")" "$(json_escape "$TEMPLATE_CONTENT")"
    fi
else
    printf '%s' "$TEMPLATE_CONTENT"
fi
[exit 0]
```

```console
$ grep -n feature_numbering .specify/init-options.json; ls specs
5:  "feature_numbering": "sequential",
001-bookmarks-api
[exit 0]
```

```console
$ .specify/scripts/bash/resolve-template.sh spec-template
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
$ mkdir -p specs/002-bookmark-title-search && cp .specify/templates/spec-template.md specs/002-bookmark-title-search/spec.md && printf '{\n  "feature_directory": "specs/002-bookmark-title-search"\n}\n' > .specify/feature.json && cat .specify/feature.json
{
  "feature_directory": "specs/002-bookmark-title-search"
}
[exit 0]
```

## Outline steps 4-7: template loaded, constitution loaded, spec written to specs/002-bookmark-title-search/spec.md (agent file write)
## Step 8: Specification Quality Validation
```console
$ grep -c 'NEEDS CLARIFICATION' specs/002-bookmark-title-search/spec.md; grep -n -A2 'NEEDS CLARIFICATION' specs/002-bookmark-title-search/spec.md
1
107:- How a search word is matched against the title: [NEEDS CLARIFICATION: Must a search word match
108-  a whole word in the title, or can it match part of a word (for example, does "post" find
109-  "Postgres")?]
[exit 0]
```

```console
$ cat .specify/templates/checklist-template.md
# [CHECKLIST TYPE] Checklist: [FEATURE NAME]

**Purpose**: [Brief description of what this checklist covers]
**Created**: [DATE]
**Feature**: [Link to spec.md or relevant documentation]

**Note**: This custom checklist is generated by the `/speckit-checklist` command based on feature context and requirements.
**Review Ownership**: This checklist is a reviewer-owned requirements-quality review artifact. Mark an item `[x]` only when the reviewer determines the requirements-quality criterion is satisfied.
**Marker Semantics**: `[x]` means the criterion has been reviewed and satisfied for requirements quality. It does not mean implementation work is complete.

<!--
  ============================================================================
  IMPORTANT: The checklist items below are SAMPLE ITEMS for illustration only.

  The /speckit-checklist command MUST replace these with actual items based on:
  - User's specific checklist request
  - Feature requirements from spec.md
  - Technical context from plan.md
  - Implementation details from tasks.md

  DO NOT keep these sample items in the generated checklist file.
  ============================================================================
-->

## [Category 1]

- [ ] CHK001 First checklist item with clear action
- [ ] CHK002 Second checklist item
- [ ] CHK003 Third checklist item

## [Category 2]

- [ ] CHK004 Another category item
- [ ] CHK005 Item with specific criteria
- [ ] CHK006 Final item in this category

## Notes

- Mark items `[x]` only after review confirms the requirement-quality criterion is satisfied
- Leave items unchecked when they still require clarification, correction, or reviewer evaluation
- `/speckit-implement` reads checklist checkbox state as a gate and must not modify markers
- `checklists/requirements.md` has a separate built-in lifecycle maintained by `/speckit-specify` and `/speckit-clarify`
- Add comments or findings inline
- Link to relevant resources or documentation
- Items are numbered sequentially for easy reference
[exit 0]
```

### Validation iteration 1

All items pass except "No [NEEDS CLARIFICATION] markers remain": 1 marker (Edge Cases, line 107). Checklist
written to specs/002-bookmark-title-search/checklists/requirements.md with that item unchecked.

**[NEEDS CLARIFICATION] count (run rule: count first): 1**

Question presented (verbatim):

## Question 1: How a search word matches the title

**Context**: "How a search word is matched against the title: [NEEDS CLARIFICATION: Must a search word match a whole word in the title, or can it match part of a word (for example, does "post" find "Postgres")?]"

**What we need to know**: Must a search word match a whole word in the title, or can it match part of a word?

**Suggested Answers**:

| Option | Answer | Implications |
|--------|--------|--------------|
| A      | Part of a word: each search word matches anywhere in the title, including inside a longer word ("post" finds "Postgres") | Most forgiving; users find things from fragments; can match more than expected ("art" finds "Start") |
| B      | Whole words only: each search word must equal a full word of the title ("post" does not find "Postgres") | Most precise; needs a rule for what separates words (spaces, punctuation) |
| C      | Start of a word: each search word must match the beginning of a word in the title ("post" finds "Postgres", "gres" does not) | Middle ground; also needs a word-separation rule |
| Custom | Provide your own answer | Reply "Q1: Custom - <details>" |

**Your choice**: _[Wait for user response]_

Answer given: **Q1: A**. Rule applied: "specify questions: ... Answer from the feature request where it covers the
question; otherwise answer option A." The feature request says "by words in the title" and "ignores letter case"
but does not say whether a word must match whole or in part, so it does not cover the question -> option A.

### Validation iteration 2 (after Q1: A; marker replaced in Edge Cases, FR-001 updated)
```console
$ grep -c 'NEEDS CLARIFICATION' specs/002-bookmark-title-search/spec.md; grep -c '\- \[ \]' specs/002-bookmark-title-search/checklists/requirements.md; grep -c '\- \[x\]' specs/002-bookmark-title-search/checklists/requirements.md
0
0
16
[exit 0]
```

## Mandatory Post-Execution Hooks
```console
$ python3 -c "import yaml,json; d=yaml.safe_load(open('.specify/extensions.yml')); print(json.dumps(d['hooks']['after_specify'], indent=1))"
[
 {
  "extension": "git",
  "command": "speckit.git.commit",
  "enabled": true,
  "optional": true,
  "priority": 10,
  "prompt": "Commit specification changes?",
  "description": "Auto-commit after specification",
  "condition": null
 }
]
[exit 0]
```

Emitted (optional hook):

```
## Extension Hooks

**Optional Hook**: git
Command: `/speckit-git-commit`
Description: Auto-commit after specification

Prompt: Commit specification changes?
To execute: `/speckit-git-commit`
```

Optional hook run by run rule: `/speckit-git-commit` with event `after_specify` (read .claude/skills/speckit-git-commit/SKILL.md; commit_style checked).

```console
$ grep -n '^commit_style' .specify/extensions/git/git-config.yml
25:commit_style: fixed
[exit 0]
```

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
$ git status --short

[exit 0]
```

Note: `.specify/feature.json` is git-ignored (`.specify/.gitignore:6:feature.json`), so it is never in a commit.

## Final report (verbatim)

> Specification complete.
>
> - `SPECIFY_FEATURE_DIRECTORY`: `specs/002-bookmark-title-search`
> - `SPEC_FILE`: `specs/002-bookmark-title-search/spec.md`
> - Branch (from the `before_specify` hook): `002-bookmark-title-search` (FEATURE_NUM `002`)
> - Checklist (`specs/002-bookmark-title-search/checklists/requirements.md`): 16/16 items pass after 2 iterations.
>   Iteration 1 left one [NEEDS CLARIFICATION] marker (whole-word vs part-of-word matching); Q1 answered A
>   (a search word matches anywhere in the title, including inside a longer word); marker resolved.
> - Spec contents: 3 user stories (P1 search by title words, P2 combine with tag filter, P3 page through results),
>   11 functional requirements, 6 success criteria, 2 key entities.
> - `after_specify` optional hook `/speckit-git-commit` was run: "[OK] Changes committed after specify".
> - Ready for `/speckit-clarify` (or `/speckit-plan`).

## Files created or changed

- specs/002-bookmark-title-search/spec.md (new)
- specs/002-bookmark-title-search/checklists/requirements.md (new)
- .specify/feature.json (new, git-ignored)
- git: new branch 002-bookmark-title-search (from the hook)

## Post-step state

```console
$ git diff --stat ba2fdc9 HEAD
 .../checklists/requirements.md                     |  38 +++++
 specs/002-bookmark-title-search/spec.md            | 180 +++++++++++++++++++++
 2 files changed, 218 insertions(+)
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
c3865fa [Spec Kit] Add specification
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
$ git tag ep08-feature2-r1-specify && git rev-parse --short ep08-feature2-r1-specify
c3865fa
[exit 0]
```

End: 2026-10-25T12:18:17Z
