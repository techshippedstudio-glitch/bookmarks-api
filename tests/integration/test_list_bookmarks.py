"""User Story 2 - List bookmarks, newest first (spec.md, scenarios 1 to 5; Constitution VI)."""

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
    assert body["next_cursor"] is None


def test_empty_list_is_not_an_error(client: TestClient) -> None:
    response = client.get("/bookmarks")

    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0, "limit": 20, "next_cursor": None}


def test_pages_of_twenty_by_default(client: TestClient) -> None:
    ids = [save(client, n) for n in range(25)]
    newest_first = list(reversed(ids))

    first = client.get("/bookmarks").json()
    second = client.get("/bookmarks", params={"cursor": first["next_cursor"]}).json()

    assert [item["id"] for item in first["items"]] == newest_first[:20]
    assert first["total"] == 25
    assert first["next_cursor"]
    assert [item["id"] for item in second["items"]] == newest_first[20:]
    assert second["total"] == 25
    assert second["next_cursor"] is None


def test_custom_limit(client: TestClient) -> None:
    for n in range(5):
        save(client, n)

    body = client.get("/bookmarks", params={"limit": 2}).json()

    assert len(body["items"]) == 2
    assert body["limit"] == 2
    assert body["total"] == 5


def test_exactly_one_full_page_has_no_next_cursor(client: TestClient) -> None:
    for n in range(20):
        save(client, n)

    body = client.get("/bookmarks").json()

    assert len(body["items"]) == 20
    assert body["next_cursor"] is None


def test_saves_between_pages_cause_no_duplicates_or_gaps(client: TestClient) -> None:
    """Constitution VI quality gate: page through everything while new bookmarks arrive."""
    ids = [save(client, n) for n in range(25)]

    page = client.get("/bookmarks", params={"limit": 10}).json()
    seen = [item["id"] for item in page["items"]]
    new = 100
    while page["next_cursor"]:
        save(client, new)  # a newer bookmark appears before every page request
        new += 1
        page = client.get("/bookmarks", params={"limit": 10, "cursor": page["next_cursor"]}).json()
        seen += [item["id"] for item in page["items"]]

    assert seen == list(reversed(ids))


def test_deletes_between_pages_skip_nothing(client: TestClient) -> None:
    ids = [save(client, n) for n in range(25)]
    newest_first = list(reversed(ids))

    first = client.get("/bookmarks", params={"limit": 10}).json()
    assert client.delete(f"/bookmarks/{newest_first[0]}").status_code == 204
    second = client.get("/bookmarks", params={"limit": 10, "cursor": first["next_cursor"]}).json()

    assert [item["id"] for item in second["items"]] == newest_first[10:20]


@pytest.mark.parametrize(
    "params",
    [{"limit": 101}, {"limit": 0}, {"limit": "many"}],
    ids=["limit-over-100", "limit-zero", "limit-not-a-number"],
)
def test_invalid_paging_is_rejected(client: TestClient, params: dict) -> None:
    response = client.get("/bookmarks", params=params)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


@pytest.mark.parametrize(
    "cursor",
    ["not-a-cursor", "", "eyJ0IjoieCJ9", "WzEsMl0", "eyJ0IjoiMjAyNi0xMC0yMVQxMDowMDowMCIsImlkIjoxfQ"],
    ids=["garbage", "empty", "bad-time", "not-an-object", "no-time-zone"],
)
def test_malformed_cursor_is_rejected(client: TestClient, cursor: str) -> None:
    response = client.get("/bookmarks", params={"cursor": cursor})

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    assert error["details"][0]["field"] == "query.cursor"


@pytest.mark.parametrize("offset", ["0", "20", "-1"])
def test_offset_is_rejected_and_points_to_cursor(client: TestClient, offset: str) -> None:
    response = client.get("/bookmarks", params={"offset": offset})

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    assert error["details"][0]["field"] == "query.offset"
    assert "cursor" in error["details"][0]["message"]
