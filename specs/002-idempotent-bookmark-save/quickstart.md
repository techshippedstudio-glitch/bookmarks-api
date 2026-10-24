# Quickstart: validate idempotent bookmark save

Runnable checks that prove feature 002 works end to end. The changed operation is defined in
[contracts/openapi.yaml](contracts/openapi.yaml); everything else, including setup, is as in
[specs/001-bookmarks-api/quickstart.md](../001-bookmarks-api/quickstart.md). This guide replaces
001's manual step 2 (which expected 409 `duplicate_url`).

## Prerequisites and setup

As in 001: Postgres running, `uv sync`, `uv run alembic upgrade head`. No new migration.

## Automated validation

```bash
set -a; . ./.env; set +a
uv run pytest -q
```

Expected: all tests pass, including the re-save and concurrent-save tests in
`tests/integration/test_create_bookmark.py`.

## Manual validation

Start the API: `uv run uvicorn bookmarks_api.main:app --reload`, then:

| Step | Request | Expected |
| --- | --- | --- |
| 1 | `POST /bookmarks` `{"url": "https://fastapi.tiangolo.com/", "title": "FastAPI docs", "tags": ["python"]}` | 201, new bookmark, note its `id` |
| 2 | `POST /bookmarks` `{"url": "HTTPS://FastAPI.tiangolo.com#top", "title": "Again", "tags": ["other"]}` | 200, same `id`, title `FastAPI docs`, tags `["python"]`, same `created_at` |
| 3 | `GET /bookmarks` | 200, `total` 1, the step 1 bookmark unchanged |
| 4 | `POST /bookmarks` `{"url": "https://fastapi.tiangolo.com/?q=1", "title": "Query"}` | 201 (different query string → different link) |
| 5 | `POST /bookmarks` `{"url": "https://fastapi.tiangolo.com", "title": ""}` | 422 `validation_error` (re-saves are validated too) |
| 6 | `DELETE /bookmarks/{id from step 1}`, then repeat step 1 | 204, then 201 with a new `id` |
| 7 | `GET /openapi.json` → `paths./bookmarks.post.responses` | has `200`, `201`, `422`; no `409` |
