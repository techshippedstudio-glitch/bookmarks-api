# Step 06 — converge (Spec Kit converge command), round 1

Start: 2026-10-24T12:08:37Z

```console
$ test -f .specify/extensions.yml && cat .specify/extensions.yml || echo 'no .specify/extensions.yml (before_converge hooks skipped)'
no .specify/extensions.yml (before_converge hooks skipped)
[exit 0]
```

```console
$ .specify/scripts/bash/check-prerequisites.sh --json --require-spec --require-tasks --include-tasks
{"FEATURE_DIR":"/home/claude/runs/living-r2/specs/001-bookmarks-api","AVAILABLE_DOCS":["research.md","data-model.md","contracts/","quickstart.md","tasks.md"]}
[exit 0]
```

```console
$ grep -n 'version' src/bookmarks_api/main.py specs/001-bookmarks-api/contracts/openapi.yaml; grep -n -E 'STATUS_CODES|http_error' src/bookmarks_api/errors.py; grep -n -A3 'enum' specs/001-bookmarks-api/contracts/openapi.yaml; grep -n 'method_not_allowed' tests -r
src/bookmarks_api/main.py:12:        version="0.1.0",
specs/001-bookmarks-api/contracts/openapi.yaml:4:  version: 0.2.0
35:STATUS_CODES = {400: "bad_request", 404: "not_found", 405: "method_not_allowed", 409: "conflict"}
64:        code = STATUS_CODES.get(exc.status_code, "http_error")
135:              enum: [validation_error, not_found, internal_error]
136-            message: { type: string }
137-            details:
138-              description: Extra information, e.g. field errors
tests/integration/test_errors.py:34:    assert_envelope(client.put("/bookmarks"), 405, "method_not_allowed")
grep: tests/integration/__pycache__/test_errors.cpython-313-pytest-9.1.1.pyc: binary file matches
grep: tests/integration/__pycache__/test_errors.cpython-311-pytest-9.1.1.pyc: binary file matches
grep: tests/integration/__pycache__/test_errors.cpython-312-pytest-9.1.1.pyc: binary file matches
[exit 0]
```

```console
$ grep -n -E '^## Phase|T0[0-9]{2} ' specs/001-bookmarks-api/tasks.md | grep -E 'Phase|T030' | cut -c1-60
32:## Phase 1: Setup (Shared Infrastructure)
42:## Phase 2: Foundational (Blocking Prerequisites)
58:## Phase 3: User Story 1 - Save a bookmark (Priority: P1)
86:## Phase 4: User Story 2 - List bookmarks, newest first (
108:## Phase 5: User Story 3 - Filter bookmarks by tag (Prio
127:## Phase 6: User Story 4 - Delete a bookmark (Priority: 
147:## Phase 7: Polish & Cross-Cutting Concerns
153:- [X] T030 Run the full test suite on Python 3.11, 3.12 
171:  error); T028 and T029 can run alongside T015 to T017; 
209:- 2026-10-21: the original list (T001 to T028) built off
210:  delete id >= 1, tag limit after de-duplication, Python
[exit 0]
```

## Converge round 1 — findings (verbatim)

Intent inventory: spec.md FR-001..FR-011, SC-002..SC-005 (SC-001 is an outcome measure), US1/AC1-4,
US2/AC1-5, US3/AC1-3, US4/AC1-3, 8 edge cases; plan.md decisions (FastAPI + Pydantic, SQLAlchemy
2.0 sync + psycopg 3, Alembic, unique index + ON CONFLICT DO NOTHING with 201/200, text[] + GIN,
keyset paging, one error envelope, Python 3.11/3.12/3.13, project structure, contract in
contracts/openapi.yaml); tasks T001-T030 (all `[X]`; completion claims not taken as evidence);
constitution I-VI. Code scope: the files named in plan.md's Project Structure and tasks.md.

Evidence checked for the revised rule: `repository.create_bookmark` returns `(row, created)` from
ON CONFLICT DO NOTHING and reads the existing row with no write (US1/AC3, FR-004); route sets 200
when not created (FR-004); generated OpenAPI POST = {200: Bookmark, 201: Bookmark, 422:
ErrorResponse} (Constitution I, contract); tests cover AC3 body equality, row unchanged,
concurrent [200, 201] same id one row, retry path (Constitution II/V); DuplicateUrlError gone; full
suite green on 3.11/3.12/3.13 (step 5).

## Convergence Findings

| ID | Gap Type | Severity | Source | Evidence | Remaining Work |
|----|----------|----------|--------|----------|----------------|
| F1 | partial | LOW | plan: contract (contracts/openapi.yaml `info.version: 0.2.0`), Constitution I ("contract and the code cannot drift apart") | `src/bookmarks_api/main.py` still creates the app with `version="0.1.0"`, so the generated `/openapi.json` reports 0.1.0 while the design contract it must match was bumped to 0.2.0 for the changed POST responses | Set the FastAPI app version to 0.2.0 |
| F2 | contradicts | LOW | plan: contract (`ErrorResponse.error.code` enum `[validation_error, not_found, internal_error]`), FR-010 | `src/bookmarks_api/errors.py` `STATUS_CODES` and the HTTPException handler emit `bad_request`, `method_not_allowed`, `conflict` and `http_error` for framework errors; `tests/integration/test_errors.py::test_wrong_method_uses_the_envelope` asserts `method_not_allowed`, a code the contract's enum does not allow (pre-existing; not introduced by the 2026-10-24 change) | Align the enum in contracts/openapi.yaml with every code errors.py can emit |

Checked, no gap: the double-race case (link saved and deleted again during the retry) raises and
returns 500 `internal_error`; T015 and plan.md specify exactly one retry, and FR-004 governs links
that are saved at the time of the request, so this is not recorded as a gap.

**Summary metrics:**

- Requirements / acceptance criteria checked: 11 FR + 4 SC + 15 acceptance scenarios + 8 edge cases
- Plan decisions checked: 10
- Constitution principles checked: 6 (I-VI)
- Findings by gap type: missing 0 / partial 1 / contradicts 1 / unrequested 0
- Findings by severity: CRITICAL 0, HIGH 0, MEDIUM 0, LOW 2

Outcome: `tasks_appended` — appending `## Phase 8: Convergence` (T031, T032).

```console
$ git diff -- specs/001-bookmarks-api/tasks.md
diff --git a/specs/001-bookmarks-api/tasks.md b/specs/001-bookmarks-api/tasks.md
index ad7d7fd..23cfcfc 100644
--- a/specs/001-bookmarks-api/tasks.md
+++ b/specs/001-bookmarks-api/tasks.md
@@ -213,3 +213,8 @@ Task: "README POST row in README.md"
   phases (T018 to T022, T025, T027).
 - 2026-10-24: duplicate saves changed from 409 `duplicate_url` with `details.existing_id` to 200
   with the existing bookmark (T012, T015, T016, T017, T028, T029, T030).
+
+## Phase 8: Convergence
+
+- [ ] T031 Set the FastAPI app version in `src/bookmarks_api/main.py` to `0.2.0` so the generated OpenAPI matches `specs/001-bookmarks-api/contracts/openapi.yaml`, per plan: contract and Constitution I (partial)
+- [ ] T032 Align the `ErrorResponse.error.code` enum in `specs/001-bookmarks-api/contracts/openapi.yaml` with every code `src/bookmarks_api/errors.py` emits (`validation_error`, `not_found`, `internal_error`, `bad_request`, `method_not_allowed`, `conflict`, `http_error`), per plan: contract and FR-010 (contradicts)
[exit 0]
```

```console
$ test -f .specify/extensions.yml && cat .specify/extensions.yml || echo 'no .specify/extensions.yml (after_converge hooks skipped)'
no .specify/extensions.yml (after_converge hooks skipped)
[exit 0]
```

Next action: run /speckit-implement for T031-T032, then converge again (round 2).

# Implement round 2 (T031-T032)

Round start: 2026-10-24T12:10:03Z

```console
$ test -f .specify/extensions.yml && cat .specify/extensions.yml || echo 'no .specify/extensions.yml (before_implement hooks skipped)'
no .specify/extensions.yml (before_implement hooks skipped)
[exit 0]
```

```console
$ .specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
{"FEATURE_DIR":"/home/claude/runs/living-r2/specs/001-bookmarks-api","AVAILABLE_DOCS":["research.md","data-model.md","contracts/","quickstart.md","tasks.md"]}
[exit 0]
```

```console
$ for f in specs/001-bookmarks-api/checklists/*.md; do t=$(grep -c -E '^- \[( |x|X)\]' $f); c=$(grep -c -E '^- \[(x|X)\]' $f); echo "$(basename $f) total=$t checked=$c unchecked=$((t-c))"; done
requirements.md total=16 checked=16 unchecked=0
[exit 0]
```

```console
$ git diff -- src specs
diff --git a/specs/001-bookmarks-api/contracts/openapi.yaml b/specs/001-bookmarks-api/contracts/openapi.yaml
index b4e8451..a5609ba 100644
--- a/specs/001-bookmarks-api/contracts/openapi.yaml
+++ b/specs/001-bookmarks-api/contracts/openapi.yaml
@@ -132,7 +132,7 @@ components:
           properties:
             code:
               type: string
-              enum: [validation_error, not_found, internal_error]
+              enum: [validation_error, not_found, internal_error, bad_request, method_not_allowed, conflict, http_error]
             message: { type: string }
             details:
               description: Extra information, e.g. field errors
diff --git a/specs/001-bookmarks-api/tasks.md b/specs/001-bookmarks-api/tasks.md
index 23cfcfc..d649417 100644
--- a/specs/001-bookmarks-api/tasks.md
+++ b/specs/001-bookmarks-api/tasks.md
@@ -216,5 +216,5 @@ Task: "README POST row in README.md"
 
 ## Phase 8: Convergence
 
-- [ ] T031 Set the FastAPI app version in `src/bookmarks_api/main.py` to `0.2.0` so the generated OpenAPI matches `specs/001-bookmarks-api/contracts/openapi.yaml`, per plan: contract and Constitution I (partial)
-- [ ] T032 Align the `ErrorResponse.error.code` enum in `specs/001-bookmarks-api/contracts/openapi.yaml` with every code `src/bookmarks_api/errors.py` emits (`validation_error`, `not_found`, `internal_error`, `bad_request`, `method_not_allowed`, `conflict`, `http_error`), per plan: contract and FR-010 (contradicts)
+- [X] T031 Set the FastAPI app version in `src/bookmarks_api/main.py` to `0.2.0` so the generated OpenAPI matches `specs/001-bookmarks-api/contracts/openapi.yaml`, per plan: contract and Constitution I (partial)
+- [X] T032 Align the `ErrorResponse.error.code` enum in `specs/001-bookmarks-api/contracts/openapi.yaml` with every code `src/bookmarks_api/errors.py` emits (`validation_error`, `not_found`, `internal_error`, `bad_request`, `method_not_allowed`, `conflict`, `http_error`), per plan: contract and FR-010 (contradicts)
diff --git a/src/bookmarks_api/main.py b/src/bookmarks_api/main.py
index 0489b10..833d86f 100644
--- a/src/bookmarks_api/main.py
+++ b/src/bookmarks_api/main.py
@@ -9,7 +9,7 @@ from bookmarks_api.routes import router
 def create_app() -> FastAPI:
     app = FastAPI(
         title="Bookmarks API",
-        version="0.1.0",
+        version="0.2.0",
         description="Save, list, filter and delete bookmarks.",
     )
     install_error_handlers(app)
[exit 0]
```

```console
$ uv run --python 3.11 pytest -q 2>&1 | grep -v UV_NATIVE | tail -2
..........................                                               [100%]
98 passed in 3.21s
[exit 0]
```

```console
$ uv run --python 3.12 pytest -q 2>&1 | grep -v UV_NATIVE | tail -2
..........................                                               [100%]
98 passed in 3.46s
[exit 0]
```

```console
$ uv run --python 3.13 pytest -q 2>&1 | grep -v UV_NATIVE | tail -2
..........................                                               [100%]
98 passed in 3.28s
[exit 0]
```

```console
$ uv run --python 3.13 python -c "from bookmarks_api.main import app; print(app.openapi()['info'])" 2>&1 | grep -v UV_NATIVE; python3 -c "import yaml; d=yaml.safe_load(open('specs/001-bookmarks-api/contracts/openapi.yaml')); print(d['info']['version'], d['components']['schemas']['ErrorResponse']['properties']['error']['properties']['code']['enum'])"
{'title': 'Bookmarks API', 'description': 'Save, list, filter and delete bookmarks.', 'version': '0.2.0'}
0.2.0 ['validation_error', 'not_found', 'internal_error', 'bad_request', 'method_not_allowed', 'conflict', 'http_error']
[exit 0]
```

Implement round 2 completion report: T031 (app version 0.2.0) and T032 (contract error-code enum)
done and marked `[X]`; checklist gate PASS (16/16); no ignore-file changes; 98 passed on 3.11,
3.12, 3.13; generated `/openapi.json` info.version is 0.2.0, matching the contract. Joint review:
code diff (main.py) and artifact diff (openapi.yaml, tasks.md) above are consistent with each
other. Extension hooks after implement: none.

Round end: 2026-10-24T12:10:35Z
