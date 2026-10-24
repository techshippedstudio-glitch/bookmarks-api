# Step 04 — converge (flowback-r2)

Start: 2026-10-24T12:05:40Z

## Converge round 1

Arguments: the change request text (verbatim from the run brief).

```console
$ test -f .specify/extensions.yml && cat .specify/extensions.yml || echo 'no .specify/extensions.yml'
no .specify/extensions.yml
[exit 0]
```

```console
$ export SPECIFY_FEATURE_DIRECTORY=specs/001-bookmarks-api; .specify/scripts/bash/check-prerequisites.sh --json --require-spec --require-tasks --include-tasks
{"FEATURE_DIR":"/home/claude/runs/flowback-r2/specs/001-bookmarks-api","AVAILABLE_DOCS":["research.md","data-model.md","contracts/","quickstart.md","tasks.md"]}
[exit 0]
```

### Evidence gathered during assessment

```console
$ uv run --python 3.13 python -c "import json; from bookmarks_api.main import app; s=app.openapi(); print(json.dumps(s['paths']['/bookmarks']['post']['responses'], indent=1)); print(s['components']['schemas']['ErrorBody'])"
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
{
 "201": {
  "description": "The bookmark was saved.",
  "content": {
   "application/json": {
    "schema": {
     "$ref": "#/components/schemas/Bookmark"
    }
   }
  }
 },
 "200": {
  "description": "This link is already bookmarked; the existing bookmark is returned unchanged.",
  "content": {
   "application/json": {
    "schema": {
     "$ref": "#/components/schemas/Bookmark"
    }
   }
  }
 },
 "422": {
  "description": "The request is not valid.",
  "content": {
   "application/json": {
    "schema": {
     "$ref": "#/components/schemas/ErrorResponse"
    }
   }
  }
 }
}
{'properties': {'code': {'type': 'string', 'title': 'Code'}, 'message': {'type': 'string', 'title': 'Message'}, 'details': {'title': 'Details'}}, 'type': 'object', 'required': ['code', 'message'], 'title': 'ErrorBody'}
[exit 0]
```

```console
$ grep -rn -E 'STATUS_CODES|method_not_allowed|conflict|409' src tests specs/001-bookmarks-api/contracts
src/bookmarks_api/errors.py:35:STATUS_CODES = {400: "bad_request", 404: "not_found", 405: "method_not_allowed", 409: "conflict"}
src/bookmarks_api/errors.py:64:        code = STATUS_CODES.get(exc.status_code, "http_error")
src/bookmarks_api/repository.py:30:        .on_conflict_do_nothing(index_elements=[BookmarkRow.url_normalized])
grep: src/bookmarks_api/__pycache__/repository.cpython-313.pyc: binary file matches
grep: src/bookmarks_api/__pycache__/errors.cpython-313.pyc: binary file matches
tests/integration/test_errors.py:34:    assert_envelope(client.put("/bookmarks"), 405, "method_not_allowed")
tests/integration/test_errors.py:78:        assert "409" not in operation["responses"]
grep: tests/integration/__pycache__/test_errors.cpython-313-pytest-9.1.1.pyc: binary file matches
[exit 0]
```

### Converge report — round 1 (verbatim)

Scope assessed (from plan.md and tasks.md file paths): src/bookmarks_api/{main,config,db,models,schemas,normalize,errors,repository,routes,cursor}.py, migrations/versions/0001_create_bookmarks.py, tests/conftest.py, tests/unit/*, tests/integration/*, contracts/openapi.yaml, README.md, quickstart.md. All 38 tasks were treated as claims to verify, not evidence.

## Convergence Findings

| ID | Gap Type | Severity | Source | Evidence | Remaining Work |
|----|----------|----------|--------|----------|----------------|
| F1 | contradicts | LOW | FR-010; T026; contracts/openapi.yaml `ErrorResponse.error.code` enum | `src/bookmarks_api/errors.py` maps 405 to code `method_not_allowed` (`STATUS_CODES`), and `tests/integration/test_errors.py::test_wrong_method_uses_the_envelope` asserts it, but the contract enum lists only `[validation_error, not_found, internal_error]`. (Pre-existing: at ep03-start the enum was `[validation_error, not_found, duplicate_url, internal_error]`, also without `method_not_allowed`; the flow-back removed `duplicate_url` and exposed the remaining mismatch.) | Add `method_not_allowed` to the contract's error-code enum so the design contract lists every code a client can receive from the documented endpoints. |

Checked and satisfied (no finding): FR-001 to FR-011; SC-001 to SC-005; US1/AC1-AC4 (AC3: `test_saving_an_equivalent_link_returns_the_existing_bookmark` asserts 200 and an identical body; `test_saving_a_duplicate_leaves_the_existing_bookmark_unchanged` asserts the stored row is unchanged), US2/AC1-AC5, US3/AC1-AC3, US4/AC1-AC3; every Edge Case including concurrent saves (`[200, 201]`, identical bodies, one row) and the save/delete race (T038 test); plan decisions (FastAPI/Pydantic, SQLAlchemy 2.0 + psycopg 3, Alembic migrations used by tests, unique index + ON CONFLICT, GIN tag index, keyset paging, one error envelope); generated OpenAPI for POST /bookmarks declares 200 and 201 with `Bookmark` and 422 with `ErrorResponse`, no 409, matching contracts/openapi.yaml.

Considered, not raised: `STATUS_CODES` still maps a generic 409 to `conflict`. No endpoint raises 409 any more, but the map is the generic Starlette HTTPException translator (Constitution III names 409 as an error class), not part of the duplicate rule.

**Summary metrics:**

- Requirements / acceptance criteria checked: 11 FR + 5 SC + 15 acceptance scenarios + 9 edge cases
- Plan decisions checked: 8
- Constitution principles checked: 6 (I-VI) + 5 quality gates
- Findings by gap type: missing 0 / partial 0 / contradicts 1 / unrequested 0
- Findings by severity: CRITICAL 0 / HIGH 0 / MEDIUM 0 / LOW 1

Outcome: **tasks_appended** — 1 task appended under Phase 11: Convergence (T039). Next: implement T039, then run converge again.

```console
$ git diff -- specs/001-bookmarks-api/tasks.md
diff --git a/specs/001-bookmarks-api/tasks.md b/specs/001-bookmarks-api/tasks.md
index bd28463..6d15f57 100644
--- a/specs/001-bookmarks-api/tasks.md
+++ b/specs/001-bookmarks-api/tasks.md
@@ -225,3 +225,7 @@ Task: "BookmarkCreate / Bookmark in src/bookmarks_api/schemas.py"
 
 - [X] T037 [US1] Flow-back record for FR-004: an already-saved link returns the existing bookmark unchanged with 200 instead of 409 `duplicate_url`; implemented and tested as now described in T008, T012, T015, T016 and T026 (`src/bookmarks_api/errors.py`, `repository.py`, `routes.py`; `tests/integration/test_create_bookmark.py`, `test_errors.py`)
 - [X] T038 [US1] Handle a save racing a delete of the same link (found by /speckit-analyze, finding U1): in `create_bookmark` in `src/bookmarks_api/repository.py`, when the conflicting row is gone before it is read, retry the insert (at most 3 attempts) so the link is saved as new with 201; real-database test `test_save_racing_a_delete_of_the_same_link_saves_a_new_bookmark` in `tests/integration/test_create_bookmark.py`, per spec Edge Cases
+
+## Phase 11: Convergence
+
+- [ ] T039 Add `method_not_allowed` to the `ErrorResponse.error.code` enum in `specs/001-bookmarks-api/contracts/openapi.yaml`, which the 405 handler in `src/bookmarks_api/errors.py` emits and `tests/integration/test_errors.py` asserts, per FR-010 (contradicts)
[exit 0]
```

### Implement T039 (round 1 tasks)

```console
$ git diff -- specs/001-bookmarks-api/contracts/openapi.yaml specs/001-bookmarks-api/tasks.md | grep -E '^[-+][^-+]'
-              enum: [validation_error, not_found, internal_error]
+              enum: [validation_error, not_found, method_not_allowed, internal_error]
+## Phase 11: Convergence
[exit 0]
```

```console
$ uv run --python 3.13 python -c "import yaml" 2>&1 || echo 'pyyaml not available; checking YAML parse with uv --with pyyaml'; uv run --python 3.13 --with pyyaml python -c "import yaml; d=yaml.safe_load(open('specs/001-bookmarks-api/contracts/openapi.yaml')); print(sorted(d['paths']['/bookmarks']['post']['responses'])); print(d['components']['schemas']['ErrorResponse']['properties']['error']['properties']['code']['enum'])"
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import yaml
ModuleNotFoundError: No module named 'yaml'
pyyaml not available; checking YAML parse with uv --with pyyaml
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
['200', '201', '422']
['validation_error', 'not_found', 'method_not_allowed', 'internal_error']
[exit 0]
```

```console
$ uv run --python 3.13 pytest -q
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
........................................................................ [ 73%]
..........................                                               [100%]
98 passed in 2.79s
[exit 0]
```

```console
$ tail -4 specs/001-bookmarks-api/tasks.md

## Phase 11: Convergence

- [X] T039 Add `method_not_allowed` to the `ErrorResponse.error.code` enum in `specs/001-bookmarks-api/contracts/openapi.yaml`, which the 405 handler in `src/bookmarks_api/errors.py` emits and `tests/integration/test_errors.py` asserts, per FR-010 (contradicts)
[exit 0]
```

## Converge round 2

```console
$ test -f .specify/extensions.yml && cat .specify/extensions.yml || echo 'no .specify/extensions.yml'
no .specify/extensions.yml
[exit 0]
```

```console
$ export SPECIFY_FEATURE_DIRECTORY=specs/001-bookmarks-api; .specify/scripts/bash/check-prerequisites.sh --json --require-spec --require-tasks --include-tasks
{"FEATURE_DIR":"/home/claude/runs/flowback-r2/specs/001-bookmarks-api","AVAILABLE_DOCS":["research.md","data-model.md","contracts/","quickstart.md","tasks.md"]}
[exit 0]
```

```console
$ uv run --python 3.13 python -c "from bookmarks_api.main import app; import json; s=app.openapi(); print({p:{m:sorted(o['responses']) for m,o in v.items()} for p,v in s['paths'].items()})"
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
{'/bookmarks': {'post': ['200', '201', '422'], 'get': ['200', '422']}, '/bookmarks/{bookmark_id}': {'delete': ['204', '404', '422']}}
[exit 0]
```

### Converge report — round 2 (verbatim)

Same scope as round 1, all 39 tasks re-verified against the code (checkbox state not trusted).

## Convergence Findings

No findings.

- F1 (round 1) resolved: contracts/openapi.yaml error-code enum is now `[validation_error, not_found, method_not_allowed, internal_error]`, covering every code the documented endpoints emit (422, 404, 405, 500); `duplicate_url` is gone from code, tests and contract.
- Generated OpenAPI responses match contracts/openapi.yaml per operation: POST /bookmarks 200, 201, 422; GET /bookmarks 200, 422; DELETE /bookmarks/{bookmark_id} 204, 404, 422.
- FR-004 behavior verified in code (`repository.create_bookmark` returns `(row, created)`, route sets 200 when not created) and in real-database tests (duplicate → 200 with identical body, stored row unchanged, concurrent saves → one 201 + one 200 with the same bookmark and one row, save/delete race → 201 new bookmark).

**Summary metrics:**

- Requirements / acceptance criteria checked: 11 FR + 5 SC + 15 acceptance scenarios + 9 edge cases
- Plan decisions checked: 8
- Constitution principles checked: 6 (I-VI) + 5 quality gates
- Findings by gap type: missing 0 / partial 0 / contradicts 0 / unrequested 0
- Findings by severity: CRITICAL 0 / HIGH 0 / MEDIUM 0 / LOW 0

**✅ Converged — the implementation satisfies the spec, plan, and tasks.**

tasks.md left byte-for-byte unchanged by this round (sha256 before and after shown below). Next: proceed to review; no further implement pass needed.

```console
$ sha256sum specs/001-bookmarks-api/tasks.md; cat /home/claude/scratch/flowback-r2/tasks.sha
babca15de89841548c6ddcbf7a2421bd0c38b04785a7bfaaeb21a9bdca40cdf2  specs/001-bookmarks-api/tasks.md
babca15de89841548c6ddcbf7a2421bd0c38b04785a7bfaaeb21a9bdca40cdf2  specs/001-bookmarks-api/tasks.md
[exit 0]
```

## Final full test suite on 3.11, 3.12, 3.13

```console
$ uv run --python 3.11 pytest -q
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
Using CPython 3.11.17 interpreter at: /usr/bin/python3.11
Removed virtual environment at: .venv
Creating virtual environment at: .venv
Installed 29 packages in 16ms
........................................................................ [ 73%]
..........................                                               [100%]
98 passed in 2.83s
[exit 0]
```

```console
$ uv run --python 3.12 pytest -q
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
Using CPython 3.12.3 interpreter at: /usr/bin/python3.12
Removed virtual environment at: .venv
Creating virtual environment at: .venv
Installed 29 packages in 21ms
........................................................................ [ 73%]
..........................                                               [100%]
98 passed in 2.54s
[exit 0]
```

```console
$ uv run --python 3.13 pytest -q
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
Using CPython 3.13.17 interpreter at: /usr/local/bin/python3.13
Removed virtual environment at: .venv
Creating virtual environment at: .venv
Installed 29 packages in 27ms
........................................................................ [ 73%]
..........................                                               [100%]
98 passed in 2.57s
[exit 0]
```

End: 2026-10-24T12:07:17Z
