"""SC-004: a search of 100,000 bookmarks returns its first page in under one second
(specs/002-bookmark-title-search/spec.md)."""

import time

from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

ROWS = 100_000


def test_first_page_of_a_search_over_100k_bookmarks_is_under_one_second(
    client: TestClient, engine: Engine
) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO bookmarks (url, url_normalized, title)
                SELECT 'https://example.com/perf/' || g,
                       'https://example.com/perf/' || g,
                       'Bookmark number ' || g
                         || CASE WHEN g % 100 = 0 THEN ' postgres guide' ELSE '' END
                FROM generate_series(1, :rows) AS g
                """
            ),
            {"rows": ROWS},
        )
        connection.execute(text("ANALYZE bookmarks"))

    started = time.perf_counter()
    response = client.get("/bookmarks/search", params={"q": "postgres guide"})
    elapsed = time.perf_counter() - started

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == ROWS // 100
    assert len(body["items"]) == 20
    assert body["next_cursor"]
    assert elapsed < 1.0, f"first page took {elapsed:.3f}s"
