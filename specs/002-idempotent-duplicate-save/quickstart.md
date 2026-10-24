# Quickstart: validate idempotent duplicate save

Runnable checks that prove a duplicate save returns the existing bookmark with 200 OK. Request and
response shapes are in [contracts/openapi.yaml](contracts/openapi.yaml); storage is unchanged (see
[data-model.md](data-model.md)). Setup is the same as
[specs/001-bookmarks-api/quickstart.md](../001-bookmarks-api/quickstart.md).

## Prerequisites

- Python 3.11+, uv, PostgreSQL with the `bookmarks` and `bookmarks_test` databases
  (`docker compose up -d`)
- `uv sync` and `uv run alembic upgrade head` done once

## Automated validation

```bash
uv run pytest -q
```

Expected: all tests pass, including in `tests/integration/test_create_bookmark.py`:

- a duplicate save (equivalent link, different title and tags) returns 200 with the first
  bookmark's id, title, tags and `created_at`, and the table still has one row, unchanged;
- two concurrent saves of the same new link return one 201 and one 200 carrying the same id, and
  one row is stored.

## Manual validation

Start the API: `uv run uvicorn bookmarks_api.main:app --reload`, then:

| Step | Request | Expected |
| --- | --- | --- |
| 1 | `POST /bookmarks` `{"url": "https://fastapi.tiangolo.com/", "title": "FastAPI docs", "tags": ["python"]}` | 201, new bookmark |
| 2 | `POST /bookmarks` `{"url": "HTTPS://FastAPI.tiangolo.com#top", "title": "Again", "tags": ["other"]}` | 200, body identical to step 1 (same id, title "FastAPI docs", tags `["python"]`, same `created_at`) |
| 3 | `GET /bookmarks` | 200, `total` 1, the step 1 bookmark unchanged |
| 4 | `POST /bookmarks` `{"url": "https://fastapi.tiangolo.com/", "title": "t", "tags": ["no spaces"]}` | 422 `validation_error` (validation still runs on duplicates) |
| 5 | `GET /openapi.json` → `paths./bookmarks.post.responses` | has `200` and `201` (both `Bookmark`) and `422`; no `409` |
