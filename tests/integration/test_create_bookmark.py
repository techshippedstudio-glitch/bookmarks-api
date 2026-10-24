"""User Story 1 - Save a bookmark (spec.md, scenarios 1 to 4)."""

import threading
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event, text
from sqlalchemy.orm import Session


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


def test_saving_an_equivalent_link_returns_the_existing_bookmark(
    client: TestClient, row_count
) -> None:
    first = client.post("/bookmarks", json={"url": "https://example.com/docs", "title": "Docs"})
    second = client.post(
        "/bookmarks",
        json={"url": "HTTPS://Example.com/docs/#intro", "title": "Other title", "tags": ["x"]},
    )

    assert first.status_code == 201
    assert second.status_code == 200
    assert second.json() == first.json()
    assert row_count() == 1


def test_saving_a_duplicate_leaves_the_existing_bookmark_unchanged(
    client: TestClient, engine
) -> None:
    client.post(
        "/bookmarks", json={"url": "https://example.com/docs", "title": "Docs", "tags": ["a"]}
    )
    response = client.post(
        "/bookmarks", json={"url": "https://example.com/docs/", "title": "Changed", "tags": ["b"]}
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Docs"
    assert response.json()["tags"] == ["a"]
    assert response.json()["url"] == "https://example.com/docs"
    with engine.connect() as connection:
        row = connection.exec_driver_sql("SELECT url, title, tags FROM bookmarks").one()
    assert tuple(row) == ("https://example.com/docs", "Docs", ["a"])


def test_concurrent_saves_of_the_same_link_leave_one_bookmark(client: TestClient, row_count) -> None:
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
    assert results[0][1] == results[1][1]
    assert row_count() == 1


def test_save_racing_a_delete_of_the_same_link_saves_a_new_bookmark(
    client: TestClient, engine, row_count
) -> None:
    """The existing bookmark is deleted after the insert is skipped but before it is read."""
    first = client.post("/bookmarks", json={"url": "https://example.com/gone", "title": "Old"})
    deleted: list[bool] = []

    def delete_existing(_session: Session) -> None:
        if not deleted:
            deleted.append(True)
            with engine.begin() as connection:
                connection.execute(text("DELETE FROM bookmarks"))

    event.listen(Session, "after_rollback", delete_existing)
    try:
        response = client.post(
            "/bookmarks", json={"url": "https://EXAMPLE.com/gone/", "title": "New"}
        )
    finally:
        event.remove(Session, "after_rollback", delete_existing)

    assert deleted == [True]
    assert response.status_code == 201
    assert response.json()["title"] == "New"
    assert response.json()["id"] != first.json()["id"]
    assert row_count() == 1


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
