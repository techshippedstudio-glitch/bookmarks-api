# Quickstart: validate idempotent duplicate save

Runnable checks for [spec.md](spec.md). The request and response shapes for `POST /bookmarks` are
in [contracts/openapi.yaml](contracts/openapi.yaml) (delta over
[001's contract](../001-bookmarks-api/contracts/openapi.yaml)); stored data is unchanged
([data-model.md](data-model.md)). Setup is the same as
[specs/001-bookmarks-api/quickstart.md](../001-bookmarks-api/quickstart.md); its manual step 2
(409 `duplicate_url`) is superseded by step 2 below.

## Automated validation

```bash
set -a; . ./.env; set +a       # TEST_DATABASE_URL
uv run pytest -q
```

Expected: all tests pass, including the duplicate-save tests in
`tests/integration/test_create_bookmark.py` (200 for an existing link, title and tags ignored,
concurrent saves → one 201 and one 200 with the same id).

## Manual validation

Start the API: `uv run uvicorn bookmarks_api.main:app --reload`.

| Step | Request | Expected |
| --- | --- | --- |
| 1 | `POST /bookmarks` `{"url": "https://fastapi.tiangolo.com/", "title": "FastAPI docs", "tags": ["api"]}` | 201, new bookmark |
| 2 | `POST /bookmarks` `{"url": "HTTPS://FastAPI.tiangolo.com", "title": "Again", "tags": ["other"]}` | 200, body identical to step 1 (same id, title "FastAPI docs", tags `["api"]`, same `created_at`) |
| 3 | `GET /bookmarks` | 200, `total` 1, the step 1 bookmark unchanged |
| 4 | `POST /bookmarks` `{"url": "https://fastapi.tiangolo.com/", "title": "t", "tags": ["no spaces"]}` | 422 `validation_error` (validation before duplicate check) |
| 5 | `GET /openapi.json` → `paths./bookmarks.post.responses` | keys `200`, `201`, `422`; no `409` |
