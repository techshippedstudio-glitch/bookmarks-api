"""User Story 1 - Save a bookmark (spec.md, scenarios 1 to 4)."""

import threading
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event


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


def test_equivalent_link_returns_the_existing_bookmark_with_200(
    client: TestClient, row_count
) -> None:
    first = client.post(
        "/bookmarks", json={"url": "https://example.com/docs", "title": "Docs", "tags": ["a"]}
    )
    second = client.post(
        "/bookmarks",
        json={"url": "HTTPS://Example.com/docs/#intro", "title": "Other", "tags": ["b"]},
    )

    assert first.status_code == 201
    assert second.status_code == 200
    assert second.json() == first.json()
    assert second.json()["url"] == "https://example.com/docs"
    assert second.json()["title"] == "Docs"
    assert second.json()["tags"] == ["a"]
    assert row_count() == 1


def test_repeat_save_leaves_the_stored_bookmark_unchanged(client: TestClient, engine) -> None:
    client.post("/bookmarks", json={"url": "https://example.com/docs", "title": "Docs", "tags": ["a"]})
    with engine.connect() as connection:
        before = connection.exec_driver_sql(
            "SELECT id, url, url_normalized, title, tags, created_at FROM bookmarks"
        ).one()

    response = client.post(
        "/bookmarks", json={"url": "https://example.com/docs/", "title": "Changed", "tags": ["b"]}
    )

    assert response.status_code == 200
    with engine.connect() as connection:
        after = connection.exec_driver_sql(
            "SELECT id, url, url_normalized, title, tags, created_at FROM bookmarks"
        ).all()
    assert after == [before]


def test_concurrent_saves_of_the_same_new_link_give_201_and_200(
    client: TestClient, row_count
) -> None:
    responses: list = []
    barrier = threading.Barrier(2)

    def save(url: str) -> None:
        barrier.wait()
        responses.append(client.post("/bookmarks", json={"url": url, "title": "Race"}))

    threads = [
        threading.Thread(target=save, args=("https://example.com/race",)),
        threading.Thread(target=save, args=("https://EXAMPLE.com/race/",)),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sorted(response.status_code for response in responses) == [200, 201]
    assert responses[0].json()["id"] == responses[1].json()["id"]
    assert row_count() == 1


def test_save_retries_when_the_existing_bookmark_is_deleted_mid_save(
    client: TestClient, engine, row_count
) -> None:
    """research.md: if the conflicting row disappears before it is read, the save inserts."""
    client.post("/bookmarks", json={"url": "https://example.com/gone", "title": "Old"})
    fired: list[bool] = []

    def delete_after_conflicting_insert(conn, cursor, statement, parameters, context, many):
        if fired or not statement.lstrip().upper().startswith("INSERT INTO BOOKMARKS"):
            return
        if cursor.rowcount == 0:  # ON CONFLICT DO NOTHING inserted nothing
            fired.append(True)
            with engine.begin() as other:  # a separate, real connection
                other.exec_driver_sql("DELETE FROM bookmarks")

    event.listen(engine, "after_cursor_execute", delete_after_conflicting_insert)
    try:
        response = client.post("/bookmarks", json={"url": "https://example.com/gone/", "title": "New"})
    finally:
        event.remove(engine, "after_cursor_execute", delete_after_conflicting_insert)

    assert fired == [True]
    assert response.status_code == 201
    assert response.json()["title"] == "New"
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
