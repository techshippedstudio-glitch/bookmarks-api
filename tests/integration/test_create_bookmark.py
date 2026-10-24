"""User Story 1 - Save a bookmark (specs/001 spec.md, scenarios 1 to 4), with the duplicate-save
rule superseded by specs/002-idempotent-duplicate-save (200 with the existing bookmark)."""

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


def test_equivalent_link_returns_existing_bookmark_with_200(client: TestClient, row_count) -> None:
    """specs/002 US1 AC1, FR-002: a duplicate save returns the existing bookmark with 200."""
    first = client.post("/bookmarks", json={"url": "https://example.com/docs", "title": "Docs"})
    second = client.post(
        "/bookmarks",
        json={"url": "HTTPS://Example.com/docs/#intro", "title": "Other title", "tags": ["x"]},
    )

    assert first.status_code == 201
    assert second.status_code == 200
    assert second.json() == first.json()
    assert row_count() == 1


def test_duplicate_save_ignores_title_and_tags_and_changes_nothing(
    client: TestClient, engine
) -> None:
    """specs/002 US1 AC2, FR-003: title and tags in the request are ignored; nothing is modified."""

    def stored_row():
        with engine.connect() as connection:
            return connection.exec_driver_sql(
                "SELECT id, url, title, tags, created_at FROM bookmarks"
            ).one()

    client.post(
        "/bookmarks", json={"url": "https://example.com/docs", "title": "Docs", "tags": ["ref"]}
    )
    before = stored_row()
    response = client.post(
        "/bookmarks",
        json={"url": "https://example.com/docs", "title": "Other", "tags": ["x", "y"]},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Docs"
    assert response.json()["tags"] == ["ref"]
    assert stored_row() == before


def test_concurrent_saves_of_the_same_link_leave_one_bookmark(client: TestClient, row_count) -> None:
    """specs/002 US1 AC4, FR-005: one 201 and one 200, same bookmark, one row."""
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


def test_resave_after_delete_creates_new_bookmark_with_201(client: TestClient, row_count) -> None:
    """specs/002 Edge Cases: after a delete, saving the same link creates a new bookmark."""
    first = client.post("/bookmarks", json={"url": "https://example.com/docs", "title": "Docs"})
    client.delete(f"/bookmarks/{first.json()['id']}")
    again = client.post("/bookmarks", json={"url": "https://example.com/docs", "title": "Docs"})

    assert again.status_code == 201
    assert again.json()["id"] != first.json()["id"]
    assert row_count() == 1


def test_different_query_string_is_a_new_bookmark(client: TestClient, row_count) -> None:
    """specs/002 Edge Cases, US1 AC3: different query strings are different links (201 each)."""
    a = client.post("/bookmarks", json={"url": "https://example.com/search?q=a", "title": "A"})
    b = client.post("/bookmarks", json={"url": "https://example.com/search?q=b", "title": "B"})

    assert (a.status_code, b.status_code) == (201, 201)
    assert row_count() == 2


@pytest.mark.parametrize(
    "extra",
    [
        pytest.param({"title": "t" * 201}, id="title-over-200"),
        pytest.param({"tags": [f"t{i}" for i in range(11)]}, id="eleven-tags"),
        pytest.param({"tags": ["no spaces"]}, id="invalid-tag"),
    ],
)
def test_invalid_resave_of_existing_link_is_rejected(
    client: TestClient, row_count, engine, extra: dict
) -> None:
    """specs/002 US2 AC1, FR-006: validation runs before the duplicate check."""
    client.post("/bookmarks", json={"url": "https://example.com/docs", "title": "Docs"})
    payload = {"url": "https://example.com/docs", "title": "Docs", **extra}

    response = client.post("/bookmarks", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert row_count() == 1
    with engine.connect() as connection:
        assert connection.exec_driver_sql("SELECT title FROM bookmarks").scalar_one() == "Docs"


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
