# Quickstart: validate title search

Runnable checks that prove search works end to end. The request and response are defined in
[contracts/openapi.yaml](contracts/openapi.yaml); the word rule and index in
[data-model.md](data-model.md).

## Prerequisites

- Python 3.11+, uv, PostgreSQL with a dev and a test database (`docker compose up -d`, or the URLs
  in `.env`)

## Setup

```bash
uv sync
uv run alembic upgrade head      # applies 0002: the title-words index
```

## Automated validation

```bash
uv run pytest
```

Expected: all tests pass, the existing bookmark tests included (FR-011).

Migration round trip (dev database):

```bash
uv run alembic upgrade head && uv run alembic downgrade -1 && uv run alembic upgrade head
```

Expected: each command succeeds; after `downgrade -1` the index `ix_bookmarks_title_words` is gone
and the list still works.

## Manual validation

Start the API with `uv run uvicorn bookmarks_api.main:app --reload`, then:

| Step | Request | Expected |
| --- | --- | --- |
| 1 | `POST /bookmarks` `{"url": "https://a.example/1", "title": "Postgres indexing guide", "tags": ["db"]}` | 201 |
| 2 | `POST /bookmarks` `{"url": "https://a.example/2", "title": "FastAPI tutorial"}` | 201 |
| 3 | `POST /bookmarks` `{"url": "https://a.example/3", "title": "Postgres backups", "tags": ["db", "ops"]}` | 201 |
| 4 | `GET /bookmarks/search?q=POSTGRES` | 200, step 3 then step 1, `total` 2 |
| 5 | `GET /bookmarks/search?q=indexing%20postgres` | 200, step 1 only |
| 6 | `GET /bookmarks/search?q=post` | 200, empty, `total` 0 (whole words only) |
| 7 | `GET /bookmarks/search?q=postgres&tag=OPS` | 200, step 3 only |
| 8 | `GET /bookmarks/search?q=postgres&limit=1` then `cursor=<next_cursor>` | step 3, then step 1 with `next_cursor` null |
| 9 | `GET /bookmarks/search` and `GET /bookmarks/search?q=%20--%20` | 422 `validation_error`, field `query.q` |
| 10 | `GET /bookmarks/search?q=postgres&offset=0` | 422 `validation_error`, field `query.offset` |
| 11 | `GET /bookmarks` | 200, unchanged list of all three |

Every error response has the shape `{"error": {"code", "message", "details"}}`.
