# Quickstart: validate the Bookmarks API

Runnable checks that prove the feature works end to end. Request and response shapes are defined
in [contracts/openapi.yaml](contracts/openapi.yaml); storage rules in
[data-model.md](data-model.md).

## Prerequisites

- Python 3.11+, uv, Docker
- From the repository root: `docker compose up -d` (Postgres with `bookmarks` and
  `bookmarks_test`)

## Setup

```bash
uv sync                      # install the project and test dependencies
uv run alembic upgrade head  # create the schema in the dev database
```

`DATABASE_URL` and `TEST_DATABASE_URL` default to the values in `.env.example`; export them only
if your database differs.

## Automated validation

```bash
uv run pytest
```

Expected: all tests pass. Integration tests run against `bookmarks_test` (Constitution II).

## Manual validation

Start the API: `uv run uvicorn bookmarks_api.main:app --reload`, then open
http://127.0.0.1:8000/docs, or use curl:

| Step | Request | Expected |
| --- | --- | --- |
| 1 | `POST /bookmarks` `{"url": "https://fastapi.tiangolo.com/", "title": "FastAPI docs", "tags": ["Python", "api"]}` | 201, tags `["api", "python"]` |
| 2 | `POST /bookmarks` `{"url": "HTTPS://FastAPI.tiangolo.com", "title": "Again", "tags": ["other"]}` | 200, the step 1 bookmark unchanged (same `id`, `url`, title "FastAPI docs", tags `["api", "python"]`, `created_at`) |
| 3 | `GET /bookmarks` | 200, the step 1 bookmark first, `total` 1 (step 2 created nothing) |
| 4 | `GET /bookmarks?tag=PYTHON` | 200, the step 1 bookmark |
| 5 | `GET /bookmarks?limit=500` | 422 `validation_error` |
| 6 | `DELETE /bookmarks/{id}` | 204 |
| 7 | `DELETE /bookmarks/{id}` again | 404 `not_found` |
| 8 | `POST /bookmarks` with `{"url": "ftp://example.com", "title": "x"}` | 422 `validation_error` |

Every error response has the shape `{"error": {"code", "message", "details"}}`.
