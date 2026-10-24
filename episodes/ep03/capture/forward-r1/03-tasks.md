# Step 03 — tasks (forward-r1)

Start: 2026-10-24T11:44:56Z

`.specify/extensions.yml` absent: no before_tasks / after_tasks hooks.

```console
$ .specify/scripts/bash/setup-tasks.sh --json | python3 -c "import json,sys; d=json.load(sys.stdin); d[\"TASKS_TEMPLATE_CONTENT\"]=d.get(\"TASKS_TEMPLATE_CONTENT\",\"\")[:200]+\"...(truncated in capture)\"; print(json.dumps(d,indent=1))"
{
 "FEATURE_DIR": "/home/claude/runs/forward-r1/specs/002-idempotent-duplicate-save",
 "AVAILABLE_DOCS": [
  "research.md",
  "data-model.md",
  "contracts/",
  "quickstart.md"
 ],
 "TASKS_TEMPLATE": "/home/claude/runs/forward-r1/.specify/templates/tasks-template.md",
 "TASKS_TEMPLATE_CONTENT": "---\n\ndescription: \"Task list template for feature implementation\"\n---\n\n# Tasks: [FEATURE NAME]\n\n**Input**: Design documents from `/specs/[###-feature-name]/`\n\n**Prerequisites**: plan.md (required), sp...(truncated in capture)"
}
[exit 0]
```

```console
$ grep -cE "^- \[ \] T[0-9]{3} " specs/002-idempotent-duplicate-save/tasks.md; grep -E "^- \[ \] T[0-9]{3} " specs/002-idempotent-duplicate-save/tasks.md | grep -vcE "^- \[ \] T[0-9]{3} (\[P\] )?(\[US[0-9]\] )?"
14
0
[exit 1]
```

## Spec Kit tasks — completion report (verbatim)

- Path: `specs/002-idempotent-duplicate-save/tasks.md`
- Total tasks: 14
- Per user story: US1 = 8 (T001–T008: 5 test, 3 implementation); US2 = 2 (T009 test, T010 confirm no code change); Setup 0; Foundational 0; Polish = 4 (T011–T014)
- Parallel opportunities: T001–T005 tests (T001–T004 share one file, so apply together; T005 separate file); T007 ∥ T008 after T006; T011 any time
- Independent test criteria: US1 — duplicate save of `HTTPS://Example.com/docs/#intro` returns 200 with a body identical to the first save, one row, original title/tags; US2 — invalid re-save of an existing link returns 422 and leaves the row unchanged
- Suggested MVP: User Story 1 (Phase 3)
- Format validation: all 14 tasks follow `- [ ] T### [P?] [US?] description with file path` (count check above: 14 matched, 0 malformed)
- Tests included because spec SC-004 and Constitution V require them.
- Questions asked: none. Hooks: none (`.specify/extensions.yml` absent).

End: 2026-10-24T11:45:42Z
