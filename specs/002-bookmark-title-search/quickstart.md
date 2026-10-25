# Quickstart: validate bookmark title search

Runnable checks that prove search works end to end. Request and response shapes are in
[contracts/openapi.yaml](contracts/openapi.yaml); the matching rule and request fields are in
[data-model.md](data-model.md).

## Prerequisites

- Python 3.11+, uv, PostgreSQL with a dev and a test database
- `DATABASE_URL` and `TEST_DATABASE_URL` exported if they differ from `.env.example`

## Setup

```bash
uv sync
uv run alembic upgrade head   # no new migration for this feature; the existing schema is enough
```

## Automated validation

```bash
uv run pytest
```

Expected: all tests pass, including the new search tests (unit `test_search_words.py`; integration
`test_search_bookmarks.py`, `test_search_with_tag.py`, `test_search_paging.py`) and the existing
bookmark tests (SC-004).

## Manual validation

Start the API with `uv run uvicorn bookmarks_api.main:app --reload`, then:

| Step | Request | Expected |
| --- | --- | --- |
| 1 | `POST /bookmarks` `{"url": "https://example.com/a", "title": "Postgres indexing guide", "tags": ["postgres"]}` | 201 |
| 2 | `POST /bookmarks` `{"url": "https://example.com/b", "title": "Python tips"}` | 201 |
| 3 | `POST /bookmarks` `{"url": "https://example.com/c", "title": "Advanced Postgres tuning"}` | 201 |
| 4 | `GET /bookmarks/search?q=POSTGRES` | 200, items c then a, `total` 2 |
| 5 | `GET /bookmarks/search?q=post%20guide` | 200, only a (every word, substring match) |
| 6 | `GET /bookmarks/search?q=postgres&tag=Postgres` | 200, only a |
| 7 | `GET /bookmarks/search?q=postgres&limit=1` then the same with `cursor=<next_cursor>` | first page c, second page a with `next_cursor` null |
| 8 | `GET /bookmarks/search?q=%25` | 200, empty (`%` is literal) |
| 9 | `GET /bookmarks/search?q=%20%20` | 422 `validation_error`, field `query.q` |
| 10 | `GET /bookmarks/search` | 422 `validation_error`, field `query.q` |
| 11 | `GET /bookmarks/search?q=x&offset=0` | 422, message points to `cursor` |
| 12 | `GET /openapi.json` | contains `/bookmarks/search` with the `BookmarkPage` response |
