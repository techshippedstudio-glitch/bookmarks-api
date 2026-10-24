# Step 07 — implement, round 2 (forward-r4)

Start: 2026-10-24T12:45:07Z

Skill: `.claude/skills/speckit-implement/SKILL.md` re-run on tasks.md (open tasks: T012-T014 in Phase 6: Convergence).

```console
$ ls .specify/extensions.yml 2>&1; .specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks; for f in specs/002-idempotent-duplicate-save/checklists/*.md; do t=$(grep -cE "^- \[( |x|X)\]" $f); c=$(grep -cE "^- \[(x|X)\]" $f); echo "$f total=$t checked=$c unchecked=$((t-c))"; done; grep -n "^- \[ \]" specs/002-idempotent-duplicate-save/tasks.md | cut -c1-80
ls: cannot access '.specify/extensions.yml': No such file or directory
{"FEATURE_DIR":"/home/claude/runs/forward-r4/specs/002-idempotent-duplicate-save","AVAILABLE_DOCS":["research.md","data-model.md","contracts/","quickstart.md","tasks.md"]}
specs/002-idempotent-duplicate-save/checklists/requirements.md total=16 checked=16 unchecked=0
159:- [ ] T012 Add an invalid-tag case (`{"url": "https://example.com/docs", "ti
160:- [ ] T013 Assert the listed bookmark's tags are `["api"]` in `test_duplicat
161:- [ ] T014 Align the `create_bookmark` docstring in `src/bookmarks_api/route
[exit 0]
```

T012 (invalid-tag param), T013 (listing tags assert), T014 (docstring = contract description) applied; marked [X].

```console
$ git diff -- src tests
diff --git a/src/bookmarks_api/routes.py b/src/bookmarks_api/routes.py
index 13fb865..00d42da 100644
--- a/src/bookmarks_api/routes.py
+++ b/src/bookmarks_api/routes.py
@@ -51,8 +51,9 @@ def _reject_offset(value: str | None) -> None:
     },
 )
 def create_bookmark(data: BookmarkCreate, session: SessionDep, response: Response) -> Bookmark:
-    """201 with the new bookmark, or 200 with the existing one if the link is already saved
-    (specs/002-idempotent-duplicate-save)."""
+    """Saves a link. If the link, after normalization, is already bookmarked, nothing is written
+    and the existing bookmark is returned unchanged with 200; the title and tags in the request
+    are ignored. Request validation runs first in both cases."""
     row, created = repository.create_bookmark(session, data)
     if not created:
         response.status_code = status.HTTP_200_OK
diff --git a/tests/integration/test_create_bookmark.py b/tests/integration/test_create_bookmark.py
index 0209c97..f061d65 100644
--- a/tests/integration/test_create_bookmark.py
+++ b/tests/integration/test_create_bookmark.py
@@ -78,6 +78,7 @@ def test_duplicate_ignores_title_and_tags_and_leaves_the_bookmark_unchanged(
     listing = client.get("/bookmarks").json()
     assert listing["total"] == 1
     assert [item["title"] for item in listing["items"]] == ["Docs"]
+    assert [item["tags"] for item in listing["items"]] == [["api"]]
 
 
 @pytest.mark.parametrize(
@@ -92,6 +93,10 @@ def test_duplicate_ignores_title_and_tags_and_leaves_the_bookmark_unchanged(
             },
             id="eleven-tags",
         ),
+        pytest.param(
+            {"url": "https://example.com/docs", "title": "Bad tag", "tags": ["no spaces"]},
+            id="invalid-tag",
+        ),
     ],
 )
 def test_invalid_duplicate_is_still_a_validation_error(
[exit 0]
```

```console
$ uv run --python 3.13 python -c "from bookmarks_api.main import create_app; print(repr(create_app().openapi()[\"paths\"][\"/bookmarks\"][\"post\"].get(\"description\")))" 2>&1 | grep -v UV_NATIVE
'Saves a link. If the link, after normalization, is already bookmarked, nothing is written\nand the existing bookmark is returned unchanged with 200; the title and tags in the request\nare ignored. Request validation runs first in both cases.'
[exit 0]
```

```console
$ set -a; . ./.env; set +a; for v in 3.11 3.12 3.13; do echo "== python $v"; uv run --python $v pytest -q 2>&1 | tail -1; done
== python 3.11
102 passed in 3.61s
== python 3.12
102 passed in 3.97s
== python 3.13
102 passed in 3.94s
[exit 0]
```

```console
$ git diff --stat; grep -c "^- \[X\]" specs/002-idempotent-duplicate-save/tasks.md; grep -c "^- \[ \]" specs/002-idempotent-duplicate-save/tasks.md
 specs/002-idempotent-duplicate-save/tasks.md | 6 +++---
 src/bookmarks_api/routes.py                  | 5 +++--
 tests/integration/test_create_bookmark.py    | 5 +++++
 3 files changed, 11 insertions(+), 5 deletions(-)
14
0
[exit 1]
```

### Review (code + artifact diffs)

- routes.py: docstring now matches the contract's `POST /bookmarks` description word for word (generated description shown above); no behavior change.
- test_create_bookmark.py: one new parametrized case (invalid tag on a duplicate link → 422, stored row unchanged) and one listing-tags assertion. 102 tests (was 101).
- tasks.md: T012-T014 marked [X]; no other task touched.

## Spec Kit completion report (verbatim)

- Tasks: 14/14 complete ([X]); this pass completed T012, T013, T014 (Phase 6: Convergence).
- Tests: 102 passed on Python 3.11, 3.12 and 3.13.
- Extension hooks: none registered — skipped.

End: 2026-10-24T12:45:40Z
