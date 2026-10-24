# Step 08 — converge, round 2 (forward-r4)

Start: 2026-10-24T12:45:45Z

Skill: `.claude/skills/speckit-converge/SKILL.md`.

```console
$ ls .specify/extensions.yml 2>&1; .specify/scripts/bash/check-prerequisites.sh --json --require-spec --require-tasks --include-tasks
ls: cannot access '.specify/extensions.yml': No such file or directory
{"FEATURE_DIR":"/home/claude/runs/forward-r4/specs/002-idempotent-duplicate-save","AVAILABLE_DOCS":["research.md","data-model.md","contracts/","quickstart.md","tasks.md"]}
[exit 0]
```

```console
$ sha256sum specs/002-idempotent-duplicate-save/tasks.md; grep -n "def test_\|id=\"" tests/integration/test_create_bookmark.py | sed -n 1,20p; sed -n 38,62p src/bookmarks_api/routes.py; grep -n "MAX_SAVE_ATTEMPTS\|return row, True\|return existing, False\|raise RuntimeError" src/bookmarks_api/repository.py; grep -n "DuplicateUrlError\|duplicate_url" -r src || echo "no DuplicateUrlError/duplicate_url in src"; grep -n "POST /bookmarks" README.md
7a08fe8499dc48dbf381cced646436e13298a558ba7cbdc881a9b54c32ab9348  specs/002-idempotent-duplicate-save/tasks.md
10:def test_save_with_title_and_no_tags(client: TestClient, row_count) -> None:
23:def test_tags_are_trimmed_lowercased_and_deduplicated(client: TestClient) -> None:
33:def test_link_is_stored_as_given(client: TestClient) -> None:
40:def test_equivalent_link_returns_the_existing_bookmark(client: TestClient, row_count) -> None:
55:def test_duplicate_ignores_title_and_tags_and_leaves_the_bookmark_unchanged(
87:        pytest.param({"url": "https://example.com/docs", "title": "t" * 201}, id="title-over-200"),
94:            id="eleven-tags",
98:            id="invalid-tag",
102:def test_invalid_duplicate_is_still_a_validation_error(
117:def test_link_with_a_different_query_is_a_new_bookmark(client: TestClient, row_count) -> None:
127:def test_concurrent_saves_of_the_same_link_leave_one_bookmark(
158:        pytest.param({"title": "No link"}, id="missing-url"),
159:        pytest.param({"url": "https://example.com"}, id="missing-title"),
160:        pytest.param({"url": "https://example.com", "title": "   "}, id="blank-title"),
161:        pytest.param({"url": "ftp://example.com", "title": "FTP"}, id="ftp-link"),
162:        pytest.param({"url": "example.com", "title": "No scheme"}, id="no-scheme"),
164:            {"url": "https://example.com/" + "a" * 2048, "title": "Long"}, id="url-over-2048"
166:        pytest.param({"url": "https://example.com", "title": "t" * 201}, id="title-over-200"),
169:            id="eleven-tags",
173:            id="invalid-tag",
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
    """Saves a link. If the link, after normalization, is already bookmarked, nothing is written
    and the existing bookmark is returned unchanged with 200; the title and tags in the request
    are ignored. Request validation runs first in both cases."""
    row, created = repository.create_bookmark(session, data)
    if not created:
        response.status_code = status.HTTP_200_OK
    return Bookmark.model_validate(row)


15:MAX_SAVE_ATTEMPTS = 3
29:    stores a new bookmark), at most MAX_SAVE_ATTEMPTS times.
38:    for _ in range(MAX_SAVE_ATTEMPTS):
42:            return row, True
49:            return existing, False
50:    raise RuntimeError(f"Could not save or find a bookmark for {normalized!r}.")
no DuplicateUrlError/duplicate_url in src
100:| `POST /bookmarks` | Save `{"url", "title", "tags"}`; 201 when new, 200 with the existing bookmark (unchanged) if the link is already saved |
[exit 0]
```

### Converge report — round 2 (verbatim)

Code scope: same as round 1 (repository.py, routes.py, errors.py, test_create_bookmark.py, test_errors.py, test_delete_bookmark.py, README.md; generated OpenAPI vs contracts/openapi.yaml). All 14 tasks, including Phase 6 T012-T014, assessed by current behavior, not checkbox state.

## Convergence Findings

No findings.

- F1 (round 1) resolved: invalid-tag duplicate case present (test_create_bookmark.py:L96-99).
- F2 resolved: listing tags asserted `[["api"]]`.
- F3 resolved: operation description now equals the contract's description; no spec path exposed.

**Summary metrics:**
- Requirements / acceptance criteria checked: 22 (6 FR, 5 SC, 4 acceptance scenarios, 7 edge cases)
- Plan decisions checked: 8
- Constitution principles checked: 6
- Findings by gap type: missing 0 / partial 0 / contradicts 0 / unrequested 0
- Findings by severity: CRITICAL 0 / HIGH 0 / MEDIUM 0 / LOW 0

**✅ Converged — the implementation satisfies the spec, plan, and tasks.**

tasks.md left byte-for-byte unchanged (sha256 before and after below). Next: review / open a PR; no further implement pass needed.

Extension hooks (after_converge): `.specify/extensions.yml` absent — skipped.

```console
$ sha256sum specs/002-idempotent-duplicate-save/tasks.md; git status --short
7a08fe8499dc48dbf381cced646436e13298a558ba7cbdc881a9b54c32ab9348  specs/002-idempotent-duplicate-save/tasks.md
?? episodes/ep03/capture/forward-r4/08-converge-2.md
[exit 0]
```

End: 2026-10-24T12:45:56Z
