# Step 06 — converge (forward-r3)

Start: 2026-10-24T12:44:16Z

## Round 1

### Commands

```console
$ .specify/scripts/bash/check-prerequisites.sh --json --require-spec --require-tasks --include-tasks
{"FEATURE_DIR":"/home/claude/runs/forward-r3/specs/002-idempotent-duplicate-save","AVAILABLE_DOCS":["research.md","data-model.md","contracts/","quickstart.md","tasks.md"]}
[exit 0]
```

```console
$ sha256sum specs/002-idempotent-duplicate-save/tasks.md; grep -oE "^- \[.\] T[0-9]{3}" specs/002-idempotent-duplicate-save/tasks.md | tail -1; grep -E "^## Phase" specs/002-idempotent-duplicate-save/tasks.md
ba707f347ca5061c7b60b68cc196635283b5ea25bd8d15c3f29c57abc877c0cb  specs/002-idempotent-duplicate-save/tasks.md
- [X] T015
## Phase 1: Setup (Shared Infrastructure)
## Phase 2: Foundational (Blocking Prerequisites)
## Phase 3: User Story 1 - Saving an already-saved link returns the existing bookmark (Priority: P1) 🎯 MVP
## Phase 4: User Story 2 - Concurrent saves of the same new link store one bookmark (Priority: P2)
## Phase 5: Polish & Cross-Cutting Concerns
[exit 0]
```

```console
$ sed -n "/^def _find_existing/,/^def list_bookmarks/p" src/bookmarks_api/repository.py; sed -n "/^@router.post/,/^@router.get/p" src/bookmarks_api/routes.py; grep -n "Duplicate\|409" src/bookmarks_api/errors.py
def _find_existing(session: Session, normalized: str) -> BookmarkRow | None:
    """Return the bookmark stored for a normalized link, or None."""
    return session.scalars(
        select(BookmarkRow).where(BookmarkRow.url_normalized == normalized)
    ).one_or_none()


def create_bookmark(session: Session, data: BookmarkCreate) -> tuple[BookmarkRow, bool]:
    """Save a bookmark and return ``(row, created)``.

    If the normalized link is new, the row is inserted and ``created`` is True. If it is already
    bookmarked, the existing row is returned unchanged and ``created`` is False; the request's
    title and tags are ignored (specs/002-idempotent-duplicate-save FR-001, FR-002).

    ON CONFLICT DO NOTHING relies on the unique index, so this holds under concurrent saves: the
    losing insert waits for the winner, inserts nothing, then reads the committed row. If that row
    is deleted before it can be read, the insert is retried.
    """
    normalized = normalize_url(data.url)
    statement = (
        insert(BookmarkRow)
        .values(url=data.url, url_normalized=normalized, title=data.title, tags=data.tags)
        .on_conflict_do_nothing(index_elements=[BookmarkRow.url_normalized])
        .returning(BookmarkRow)
    )
    for _ in range(MAX_SAVE_ATTEMPTS):
        row = session.scalars(statement).one_or_none()
        if row is not None:
            session.commit()
            return row, True
        session.rollback()
        existing = _find_existing(session, normalized)
        if existing is not None:
            # Nothing was written; the read-only transaction ends when the session closes.
            # (A rollback here would expire the loaded row and force a reload.)
            return existing, False
    raise RuntimeError(
        f"Could not save or find a bookmark for {normalized!r} after {MAX_SAVE_ATTEMPTS} attempts."
    )


def list_bookmarks(
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=Bookmark,
    summary="Save a bookmark",
    responses={
        200: {
            "model": Bookmark,
            "description": (
                "This link is already bookmarked; the existing bookmark is returned unchanged."
            ),
        },
        **ERROR_422,
    },
)
def create_bookmark(data: BookmarkCreate, session: SessionDep, response: Response) -> Bookmark:
    row, created = repository.create_bookmark(session, data)
    if not created:
        response.status_code = status.HTTP_200_OK
    return Bookmark.model_validate(row)


@router.get(
35:STATUS_CODES = {400: "bad_request", 404: "not_found", 405: "method_not_allowed", 409: "conflict"}
[exit 0]
```

```console
$ set -a; . ./.env; set +a; uv run --python 3.13 python - <<EOF
from fastapi.testclient import TestClient
from bookmarks_api.main import create_app
spec = TestClient(create_app()).get("/openapi.json").json()
post = spec["paths"]["/bookmarks"]["post"]["responses"]
print({k: (v["content"]["application/json"]["schema"]["\$ref"] if "content" in v else None) for k, v in post.items()})
print("ErrorResponse code enum in generated doc:", spec["components"]["schemas"]["ErrorBody"]["properties"]["code"])
EOF
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
{'201': '#/components/schemas/Bookmark', '200': '#/components/schemas/Bookmark', '422': '#/components/schemas/ErrorResponse'}
ErrorResponse code enum in generated doc: {'type': 'string', 'title': 'Code'}
[exit 0]
```

```console
$ set -a; . ./.env; set +a; uv run --python 3.13 pytest -q tests/integration/test_create_bookmark.py tests/integration/test_errors.py -v 2>&1 | grep -E "PASSED|FAILED|ERROR|passed|failed" | sed "s/ *\[ *[0-9]*%\]//"
============================== 31 passed in 1.17s ==============================
[exit 0]
```

```console
$ grep -n "409" README.md || echo "README: no 409"; ls .specify/extensions.yml
README: no 409
ls: cannot access '.specify/extensions.yml': No such file or directory
[exit 2]
```

(Note: the `-v | grep PASSED` filter above printed only the summary line because pytest's verbose lines were reformatted by the sed; the run result is 31 passed for the two touched test modules.)

### Converge report — round 1 (verbatim)

## Convergence Findings

No findings.

Assessment against `specs/002-idempotent-duplicate-save` (spec.md, plan.md, tasks.md) and constitution v1.1.0:

| Item | Evidence | Status |
|------|----------|--------|
| FR-001 duplicate → 200 with existing bookmark | `routes.create_bookmark` sets `HTTP_200_OK` when `created` is false; `repository.create_bookmark` returns `(existing, False)`; `test_equivalent_link_returns_existing_bookmark` | met |
| FR-002 title/tags ignored, stored row unchanged | duplicate branch performs no write (only `_find_existing` SELECT); `test_duplicate_leaves_the_existing_bookmark_unchanged` checks title, tags, created_at, list order | met |
| FR-003 new link → 201 | route default `status_code=201`; `test_save_with_title_and_no_tags`, `test_different_query_string_is_a_new_bookmark` | met |
| FR-004 one row under concurrency; one 201 + one 200 same bookmark | ON CONFLICT on `uq_bookmarks_url_normalized`; `test_concurrent_saves_of_the_same_link_leave_one_bookmark` (20/20 repeated runs in implement) | met |
| FR-005 validation on duplicate saves | `BookmarkCreate` validation precedes handler; `test_invalid_duplicate_save_is_still_rejected[title-over-200, invalid-tag]` | met |
| FR-006 API description: 200 + 201, no 409 | generated `/openapi.json` POST responses = {201: Bookmark, 200: Bookmark, 422: ErrorResponse}; `test_openapi_documents_every_operation[/bookmarks-post]` | met |
| US1/AC1-AC4, US2/AC1 | tests listed above | met |
| Edge cases (invalid duplicate, never modifies, save after delete → 201, does not move in list, no conflict error) | tests above + `test_bookmark_deleted_mid_save_is_saved_as_new`; existing 001 delete test `test_resave_after_delete` style coverage in test_delete_bookmark.py | met |
| SC-001..SC-005 | above; full suite 101 passed on 3.11/3.12/3.13 | met |
| plan: keep ON CONFLICT + unique index, no migration | repository.py; migrations/ unchanged | met |
| plan: `DuplicateUrlError` and 409 handler removed | errors.py has no `DuplicateUrlError`; only generic `409: "conflict"` in `STATUS_CODES` (kept by research decision) | met |
| plan: README endpoint row | README.md no longer mentions 409 | met |
| research: bounded retry when row deleted mid-save | `MAX_SAVE_ATTEMPTS = 3` loop; `RuntimeError` → 500 envelope via the generic handler | met |
| Constitution I-VI | typed `Bookmark` model for both success codes; real-DB tests; error envelope unchanged; no new dependencies; tests shipped with change; no list changes | met |

Observation (not actionable for this feature's scope): the generated OpenAPI types `ErrorBody.code` as a plain string, while `contracts/openapi.yaml` (copied from 001) lists an enum; this predates 002 and is not an obligation introduced by 002's spec, plan or tasks.

**Summary metrics:**

- Requirements / acceptance criteria checked: 6 FR + 5 SC + 5 acceptance scenarios + 5 edge cases = 21
- Plan decisions checked: 5 (ON CONFLICT kept/no migration, route status + responses, remove duplicate error, README, bounded retry)
- Constitution principles checked: 6
- Findings by gap type: missing 0 / partial 0 / contradicts 0 / unrequested 0
- Findings by severity: CRITICAL 0 / HIGH 0 / MEDIUM 0 / LOW 0

**✅ Converged — the implementation satisfies the spec, plan, and tasks.**

tasks.md left byte-for-byte unchanged (no Convergence phase appended).

**Next Actions**: proceed to review / opening a PR. No further implement pass is needed for this feature's specified scope.

(after_converge hooks: `.specify/extensions.yml` does not exist — skipped.)

```console
$ sha256sum specs/002-idempotent-duplicate-save/tasks.md; git status --short
ba707f347ca5061c7b60b68cc196635283b5ea25bd8d15c3f29c57abc877c0cb  specs/002-idempotent-duplicate-save/tasks.md
?? episodes/ep03/capture/forward-r3/06-converge.md
[exit 0]
```

```console
$ grep -n "def test" tests/integration/test_delete_bookmark.py
13:def test_deleted_bookmark_disappears_from_list_and_filter(client: TestClient, row_count) -> None:
26:def test_deleting_unknown_bookmark_returns_not_found(client: TestClient) -> None:
35:def test_deleting_twice_returns_not_found_the_second_time(client: TestClient) -> None:
42:def test_link_can_be_saved_again_after_delete(client: TestClient) -> None:
53:def test_invalid_id_is_a_validation_error(client: TestClient, bad_id: str) -> None:
[exit 0]
```

Correction to the report above: the existing 001 test covering "save after delete → new bookmark" is `test_link_can_be_saved_again_after_delete` in tests/integration/test_delete_bookmark.py (line 42), not "test_resave_after_delete".

Converge rounds: 1 (converged on the first round; no implement re-run needed).
End: 2026-10-24T12:44:47Z
