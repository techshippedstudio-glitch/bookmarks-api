"""User Story 1 - Save a bookmark (spec.md, scenarios 1 to 4)."""

import threading
from datetime import datetime

import pytest
from fastapi.testclient import TestClient


def test_save_with_title_and_no_tags(client: TestClient, row_count) -> None:
    response = client.post("/bookmarks", json={"url": "https://example.com/docs", "title": "Docs"})

    assert response.status_code == 201
    body = response.json()
    assert body["url"] == "https://example.com/docs"
    assert body["title"] == "Docs"
    assert body["tags"] == []
    assert isinstance(body["id"], int)
    datetime.fromisoformat(body["created_at"])
    assert row_count() == 1


def test_tags_are_trimmed_lowercased_and_deduplicated(client: TestClient) -> None:
    response = client.post(
        "/bookmarks",
        json={"url": "https://example.com", "title": "Ex", "tags": ["Python", " api ", "python"]},
    )

    assert response.status_code == 201
    assert response.json()["tags"] == ["api", "python"]


def test_link_is_stored_as_given(client: TestClient) -> None:
    response = client.post("/bookmarks", json={"url": "HTTPS://Example.com/Docs/", "title": "X"})

    assert response.status_code == 201
    assert response.json()["url"] == "HTTPS://Example.com/Docs/"


def test_equivalent_link_returns_the_existing_bookmark(client: TestClient, row_count) -> None:
    """002 US1 AC1: a duplicate save returns 200 with the existing bookmark exactly as stored."""
    first = client.post("/bookmarks", json={"url": "https://example.com/docs", "title": "Docs"})
    second = client.post(
        "/bookmarks",
        json={"url": "HTTPS://Example.com/docs/#intro", "title": "Other title", "tags": ["x"]},
    )

    assert first.status_code == 201
    assert second.status_code == 200
    assert second.json() == first.json()
    assert second.json()["url"] == "https://example.com/docs"
    assert row_count() == 1


def test_duplicate_ignores_title_and_tags_and_leaves_the_bookmark_unchanged(
    client: TestClient, engine
) -> None:
    """002 US1 AC2 / FR-003: the request's title and tags are ignored; nothing is modified."""
    first = client.post(
        "/bookmarks", json={"url": "https://example.com/docs", "title": "Docs", "tags": ["api"]}
    )
    second = client.post(
        "/bookmarks",
        json={"url": "https://example.com/docs", "title": "Other", "tags": ["python", "new"]},
    )

    assert second.status_code == 200
    assert second.json()["title"] == "Docs"
    assert second.json()["tags"] == ["api"]
    assert second.json() == first.json()
    with engine.connect() as connection:
        rows = connection.exec_driver_sql("SELECT title, tags, created_at FROM bookmarks").all()
    assert len(rows) == 1
    title, tags, created_at = rows[0]
    assert title == "Docs"
    assert tags == ["api"]
    assert created_at == datetime.fromisoformat(first.json()["created_at"])
    listing = client.get("/bookmarks").json()
    assert listing["total"] == 1
    assert [item["title"] for item in listing["items"]] == ["Docs"]
    assert [item["tags"] for item in listing["items"]] == [["api"]]


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({"url": "https://example.com/docs", "title": "t" * 201}, id="title-over-200"),
        pytest.param(
            {
                "url": "https://example.com/docs",
                "title": "Many",
                "tags": [f"t{i}" for i in range(11)],
            },
            id="eleven-tags",
        ),
        pytest.param(
            {"url": "https://example.com/docs", "title": "Bad tag", "tags": ["no spaces"]},
            id="invalid-tag",
        ),
    ],
)
def test_invalid_duplicate_is_still_a_validation_error(
    client: TestClient, engine, payload: dict
) -> None:
    """002 FR-006: validation runs before the duplicate check."""
    client.post("/bookmarks", json={"url": "https://example.com/docs", "title": "Docs"})

    response = client.post("/bookmarks", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    with engine.connect() as connection:
        rows = connection.exec_driver_sql("SELECT title, tags FROM bookmarks").all()
    assert rows == [("Docs", [])]


def test_link_with_a_different_query_is_a_new_bookmark(client: TestClient, row_count) -> None:
    """002 Edge Case: links that differ only in the query string are different links."""
    client.post("/bookmarks", json={"url": "https://example.com/docs", "title": "Docs"})

    response = client.post("/bookmarks", json={"url": "https://example.com/docs?x=1", "title": "Q"})

    assert response.status_code == 201
    assert row_count() == 2


def test_concurrent_saves_of_the_same_link_leave_one_bookmark(
    client: TestClient, row_count
) -> None:
    """002 US2 AC1 / FR-005: one save gets 201, the other 200, both with the same bookmark."""
    for _ in range(20):
        results: list[tuple[int, dict]] = []
        barrier = threading.Barrier(2)

        def save(url: str) -> None:
            barrier.wait()
            response = client.post("/bookmarks", json={"url": url, "title": "Race"})
            results.append((response.status_code, response.json()))

        threads = [
            threading.Thread(target=save, args=("https://example.com/race",)),
            threading.Thread(target=save, args=("https://EXAMPLE.com/race/",)),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert sorted(status for status, _ in results) == [200, 201]
        assert results[0][1]["id"] == results[1][1]["id"]
        assert row_count() == 1
        assert client.delete(f"/bookmarks/{results[0][1]['id']}").status_code == 204


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({"title": "No link"}, id="missing-url"),
        pytest.param({"url": "https://example.com"}, id="missing-title"),
        pytest.param({"url": "https://example.com", "title": "   "}, id="blank-title"),
        pytest.param({"url": "ftp://example.com", "title": "FTP"}, id="ftp-link"),
        pytest.param({"url": "example.com", "title": "No scheme"}, id="no-scheme"),
        pytest.param(
            {"url": "https://example.com/" + "a" * 2048, "title": "Long"}, id="url-over-2048"
        ),
        pytest.param({"url": "https://example.com", "title": "t" * 201}, id="title-over-200"),
        pytest.param(
            {"url": "https://example.com", "title": "Many", "tags": [f"t{i}" for i in range(11)]},
            id="eleven-tags",
        ),
        pytest.param(
            {"url": "https://example.com", "title": "Bad tag", "tags": ["no spaces"]},
            id="invalid-tag",
        ),
        pytest.param(
            {"url": "https://example.com", "title": "Extra", "rating": 5}, id="unknown-field"
        ),
    ],
)
def test_invalid_input_is_rejected_and_nothing_saved(
    client: TestClient, row_count, payload: dict
) -> None:
    response = client.post("/bookmarks", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert row_count() == 0


def test_title_of_exactly_200_and_ten_tags_are_accepted(client: TestClient) -> None:
    response = client.post(
        "/bookmarks",
        json={
            "url": "https://example.com",
            "title": "t" * 200,
            "tags": [f"t{i}" for i in range(10)],
        },
    )

    assert response.status_code == 201


def test_eleven_tags_that_dedupe_to_ten_are_accepted(client: TestClient) -> None:
    tags = [f"t{i}" for i in range(10)] + ["T0"]
    response = client.post(
        "/bookmarks", json={"url": "https://example.com", "title": "Dupes", "tags": tags}
    )

    assert response.status_code == 201
    assert len(response.json()["tags"]) == 10
