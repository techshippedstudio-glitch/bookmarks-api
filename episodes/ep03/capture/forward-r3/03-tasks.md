# Step 03 — tasks (forward-r3)

Start: 2026-10-24T12:37:09Z

## Commands

```console
$ ls .specify/extensions.yml
ls: cannot access '.specify/extensions.yml': No such file or directory
[exit 2]
```

```console
$ .specify/scripts/bash/setup-tasks.sh --json | python3 -c "import json,sys; d=json.load(sys.stdin); c=d.pop(\"TASKS_TEMPLATE_CONTENT\",None); print(json.dumps(d, indent=1)); print(\"TASKS_TEMPLATE_CONTENT: %d chars\" % len(c or \"\"))"
{
 "FEATURE_DIR": "/home/claude/runs/forward-r3/specs/002-idempotent-duplicate-save",
 "AVAILABLE_DOCS": [
  "research.md",
  "data-model.md",
  "contracts/",
  "quickstart.md"
 ],
 "TASKS_TEMPLATE": "/home/claude/runs/forward-r3/.specify/templates/tasks-template.md"
}
TASKS_TEMPLATE_CONTENT: 9134 chars
[exit 0]
```

```console
$ grep -cE "^- \[ \] T[0-9]{3}" specs/002-idempotent-duplicate-save/tasks.md; grep -E "^- \[ \] T[0-9]{3}" specs/002-idempotent-duplicate-save/tasks.md | grep -vE "^- \[ \] T[0-9]{3} (\[P\] )?(\[US[0-9]\] )?" ; echo "format-violations-above: none if blank"
14
format-violations-above: none if blank
[exit 0]
```

Extension hooks: `.specify/extensions.yml` does not exist — after_tasks hooks skipped silently.

Tests were generated because spec SC-005 requires every acceptance scenario to be covered by an automated test and Constitution V requires tests to ship with every feature.

## Spec Kit completion report (verbatim)

- **tasks.md**: `specs/002-idempotent-duplicate-save/tasks.md`
- **Total tasks**: 14
- **Per user story**: Setup 1 (T001); Foundational 0; US1 8 (T002-T009: 5 test, 3 implementation); US2 2 (T010-T011); Polish 3 (T012-T014)
- **Parallel opportunities**: T006 (test_errors.py) alongside T002-T005 (test_create_bookmark.py); T012 (README.md) alongside any implementation task
- **Independent test criteria**:
  - US1: save a link, re-save an equivalent form with different title/tags → 200 with the first bookmark exactly as stored, one row
  - US2: two threads race on a new link → statuses [200, 201], same id, one row
- **Suggested MVP scope**: User Story 1 (Phase 3)
- **Format validation**: all 14 tasks follow `- [ ] T### [P?] [US?] description with file path`
End: 2026-10-24T12:38:03Z
