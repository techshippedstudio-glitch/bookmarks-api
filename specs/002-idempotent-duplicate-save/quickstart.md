# Quickstart: validate idempotent duplicate save

Runnable checks that prove the feature works end to end. Request and response shapes are in
[contracts/openapi.yaml](contracts/openapi.yaml); storage is unchanged
([data-model.md](data-model.md)). Setup is the same as
[specs/001-bookmarks-api/quickstart.md](../001-bookmarks-api/quickstart.md).

## Automated validation

```bash
set -a; . ./.env; set +a     # TEST_DATABASE_URL for your test database
uv run pytest -q
```

Expected: all tests pass, including the duplicate-save (200), unchanged-bookmark and concurrent
save (one 201, one 200) tests in `tests/integration/test_create_bookmark.py`.

## Manual validation

Start the API: `uv run uvicorn bookmarks_api.main:app --reload`, then:

| Step | Request | Expected |
| --- | --- | --- |
| 1 | `POST /bookmarks` `{"url": "https://example.com/docs", "title": "Docs", "tags": ["api"]}` | 201, new bookmark (note `id`, `created_at`) |
| 2 | `POST /bookmarks` `{"url": "HTTPS://Example.com/docs/#intro", "title": "Other", "tags": ["python"]}` | 200, body identical to step 1 (same `id`, `url` `https://example.com/docs`, title `Docs`, tags `["api"]`, same `created_at`) |
| 3 | `GET /bookmarks` | 200, exactly one bookmark, title `Docs`, tags `["api"]` |
| 4 | `POST /bookmarks` `{"url": "https://example.com/docs", "title": "t…201 chars…"}` | 422 `validation_error` (validation runs before the duplicate check) |
| 5 | `POST /bookmarks` `{"url": "https://example.com/docs?x=1", "title": "Query"}` | 201 (different query string = different link) |
| 6 | `DELETE /bookmarks/{id from step 1}`, then repeat step 1 | 204, then 201 with a new `id` |

No step returns 409 any more.
