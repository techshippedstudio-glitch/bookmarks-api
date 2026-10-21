"""User Story 3 - Filter bookmarks by tag (spec.md, scenarios 1 to 3)."""

import pytest
from fastapi.testclient import TestClient


def save(client: TestClient, path: str, tags: list[str]) -> int:
    response = client.post(
        "/bookmarks", json={"url": f"https://example.com/{path}", "title": path, "tags": tags}
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_filter_returns_only_matching_bookmarks_newest_first(client: TestClient) -> None:
    save(client, "py", ["python"])
    pg = save(client, "pg", ["postgres"])
    both = save(client, "both", ["python", "postgres"])

    body = client.get("/bookmarks", params={"tag": "postgres"}).json()

    assert [item["id"] for item in body["items"]] == [both, pg]
    assert body["total"] == 2


def test_filter_is_normalized_like_tags(client: TestClient) -> None:
    pg = save(client, "pg", ["postgres"])

    body = client.get("/bookmarks", params={"tag": " Postgres "}).json()

    assert [item["id"] for item in body["items"]] == [pg]


def test_unknown_tag_returns_empty_list(client: TestClient) -> None:
    save(client, "py", ["python"])

    body = client.get("/bookmarks", params={"tag": "rust"}).json()

    assert body["items"] == []
    assert body["total"] == 0


def test_filter_works_with_paging(client: TestClient) -> None:
    ids = [save(client, f"p{n}", ["api"]) for n in range(5)]
    save(client, "other", ["misc"])

    body = client.get("/bookmarks", params={"tag": "api", "limit": 2, "offset": 2}).json()

    assert [item["id"] for item in body["items"]] == list(reversed(ids))[2:4]
    assert body["total"] == 5


@pytest.mark.parametrize("bad", ["no spaces", "x" * 31, "c++"])
def test_invalid_tag_filter_is_rejected(client: TestClient, bad: str) -> None:
    response = client.get("/bookmarks", params={"tag": bad})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
