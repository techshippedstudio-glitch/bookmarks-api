# Step 01 — fix (flowback-r2)

Start: 2026-10-24T11:57:52Z

## Baseline test run (before change)

```console
$ uv run --python 3.13 pytest -q
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
Using CPython 3.13.17 interpreter at: /usr/local/bin/python3.13
Creating virtual environment at: .venv
   Building bookmarks-api @ file:///home/claude/runs/flowback-r2
      Built bookmarks-api @ file:///home/claude/runs/flowback-r2
Installed 29 packages in 15ms
........................................................................ [ 73%]
..........................                                               [100%]
98 passed in 2.39s
[exit 0]
```

## Change made

repository.create_bookmark now returns (row, created); on conflict it reads and returns the existing row unchanged. routes.create_bookmark sets 200 when not created and documents 200/201 instead of 409. DuplicateUrlError and its 409 handler removed. Tests updated: duplicate -> 200 with identical body, stored row unchanged, concurrent saves -> [200, 201] with identical bodies, OpenAPI documents 200+201 and no 409.

```console
$ git diff --stat
 src/bookmarks_api/errors.py               | 11 ---------
 src/bookmarks_api/repository.py           | 22 ++++++++++-------
 src/bookmarks_api/routes.py               | 14 ++++++++---
 tests/integration/test_create_bookmark.py | 39 ++++++++++++++++++++-----------
 tests/integration/test_errors.py          | 18 ++++----------
 5 files changed, 55 insertions(+), 49 deletions(-)
```

## Test run after change

```console
$ uv run --python 3.13 pytest -q
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.
........................................................................ [ 74%]
.........................                                                [100%]
97 passed in 2.48s
[exit 0]
```

## Concurrency test repeated 20 times

```console
$ uv run --python 3.13 pytest -q --count 20 -k concurrent 2>/dev/null || for i in $(seq 20); do uv run --python 3.13 pytest -q -k concurrent 2>&1 | tail -1; done
1 passed, 96 deselected in 0.21s
1 passed, 96 deselected in 0.18s
1 passed, 96 deselected in 0.19s
1 passed, 96 deselected in 0.20s
1 passed, 96 deselected in 0.16s
1 passed, 96 deselected in 0.16s
1 passed, 96 deselected in 0.16s
1 passed, 96 deselected in 0.17s
1 passed, 96 deselected in 0.17s
1 passed, 96 deselected in 0.15s
1 passed, 96 deselected in 0.21s
1 passed, 96 deselected in 0.17s
1 passed, 96 deselected in 0.17s
1 passed, 96 deselected in 0.16s
1 passed, 96 deselected in 0.19s
1 passed, 96 deselected in 0.19s
1 passed, 96 deselected in 0.19s
1 passed, 96 deselected in 0.16s
1 passed, 96 deselected in 0.16s
1 passed, 96 deselected in 0.17s
[exit 0]
```

(Note: pytest-repeat is not installed, so `--count` failed silently (stderr discarded) and the shell loop fallback ran 20 times; all 20 passed.)

End: 2026-10-24T11:59:20Z
