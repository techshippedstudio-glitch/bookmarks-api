"""User Story 2 - List bookmarks, newest first (spec.md, scenarios 1 to 4)."""

import pytest
from fastapi.testclient import TestClient


def save(client: TestClient, n: int, tags: list[str] | None = None) -> int:
    response = client.post(
        "/bookmarks",
        json={"url": f"https://example.com/{n}", "title": f"Bookmark {n}", "tags": tags or []},
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_lists_newest_first_with_total(client: TestClient) -> None:
    ids = [save(client, n) for n in range(3)]

    body = client.get("/bookmarks").json()

    assert [item["id"] for item in body["items"]] == list(reversed(ids))
    assert body["total"] == 3
    assert body["limit"] == 20
    assert body["offset"] == 0


def test_empty_list_is_not_an_error(client: TestClient) -> None:
    response = client.get("/bookmarks")

    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0, "limit": 20, "offset": 0}


def test_pages_of_twenty_by_default(client: TestClient) -> None:
    ids = [save(client, n) for n in range(25)]
    newest_first = list(reversed(ids))

    first = client.get("/bookmarks").json()
    second = client.get("/bookmarks", params={"offset": 20}).json()

    assert [item["id"] for item in first["items"]] == newest_first[:20]
    assert first["total"] == 25
    assert [item["id"] for item in second["items"]] == newest_first[20:]
    assert second["total"] == 25


def test_custom_limit(client: TestClient) -> None:
    for n in range(5):
        save(client, n)

    body = client.get("/bookmarks", params={"limit": 2}).json()

    assert len(body["items"]) == 2
    assert body["limit"] == 2
    assert body["total"] == 5


def test_offset_past_the_end_returns_empty_page_with_total(client: TestClient) -> None:
    for n in range(3):
        save(client, n)

    body = client.get("/bookmarks", params={"offset": 50}).json()

    assert body["items"] == []
    assert body["total"] == 3


@pytest.mark.parametrize(
    "params",
    [{"limit": 101}, {"limit": 0}, {"offset": -1}, {"limit": "many"}],
    ids=["limit-over-100", "limit-zero", "negative-offset", "limit-not-a-number"],
)
def test_invalid_paging_is_rejected(client: TestClient, params: dict) -> None:
    response = client.get("/bookmarks", params=params)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
