"""User Story 3 - Page through search results (specs/002-bookmark-title-search/spec.md,
scenarios 1 to 4; Constitution VI quality gate)."""

import pytest
from fastapi.testclient import TestClient

_counter = iter(range(1, 1_000_000))


def save(client: TestClient, title: str, tags: list[str] | None = None) -> int:
    url = f"https://example.com/paged/{next(_counter)}"
    response = client.post("/bookmarks", json={"url": url, "title": title, "tags": tags or []})
    assert response.status_code == 201, response.text
    return response.json()["id"]


def search(client: TestClient, **params) -> dict:
    response = client.get("/bookmarks/search", params=params)
    assert response.status_code == 200, response.text
    return response.json()


def ids(body: dict) -> list[int]:
    return [item["id"] for item in body["items"]]


def test_pages_of_twenty_by_default(client: TestClient) -> None:
    matches = []
    for n in range(30):
        if n % 6 == 5:
            save(client, f"Unrelated note {n}")  # 5 bookmarks that do not match
        else:
            matches.append(save(client, f"Guide number {n}"))
    newest_first = list(reversed(matches))
    assert len(newest_first) == 25

    first = search(client, q="guide")
    second = search(client, q="guide", cursor=first["next_cursor"])

    assert ids(first) == newest_first[:20]
    assert first["total"] == 25
    assert first["next_cursor"]
    assert ids(second) == newest_first[20:]
    assert second["total"] == 25
    assert second["next_cursor"] is None


def test_custom_page_size(client: TestClient) -> None:
    for n in range(5):
        save(client, f"Guide {n}")

    body = search(client, q="guide", limit=2)

    assert len(body["items"]) == 2
    assert body["limit"] == 2
    assert body["total"] == 5


def test_exactly_one_full_page_has_no_next_cursor(client: TestClient) -> None:
    for n in range(20):
        save(client, f"Guide {n}")

    body = search(client, q="guide")

    assert len(body["items"]) == 20
    assert body["next_cursor"] is None


@pytest.mark.parametrize(
    "params, field",
    [
        ({"limit": 101}, "query.limit"),
        ({"limit": 0}, "query.limit"),
        ({"limit": "many"}, "query.limit"),
        ({"cursor": "not-a-cursor"}, "query.cursor"),
        ({"cursor": ""}, "query.cursor"),
        ({"cursor": "eyJ0IjoiMjAyNi0xMC0yMVQxMDowMDowMCIsImlkIjoxfQ"}, "query.cursor"),
        ({"offset": "20"}, "query.offset"),
    ],
    ids=["limit-over-100", "limit-zero", "limit-not-a-number", "garbage-cursor", "empty-cursor",
         "no-time-zone-cursor", "offset"],
)
def test_invalid_paging_gives_the_same_error_as_the_list(
    client: TestClient, params: dict, field: str
) -> None:
    searched = client.get("/bookmarks/search", params={"q": "guide", **params})
    listed = client.get("/bookmarks", params=params)

    assert searched.status_code == listed.status_code == 422
    assert searched.json() == listed.json()
    assert searched.json()["error"]["details"][0]["field"] == field
    if field == "query.offset":
        assert "cursor" in searched.json()["error"]["details"][0]["message"]


def test_saves_between_pages_cause_no_duplicates_or_gaps(client: TestClient) -> None:
    """Constitution VI quality gate: page through every match while new matches arrive."""
    matches = [save(client, f"Guide {n}") for n in range(25)]
    for n in range(5):
        save(client, f"Other {n}")

    page = search(client, q="guide", limit=10)
    seen = ids(page)
    new = 100
    while page["next_cursor"]:
        save(client, f"Guide {new}")  # a newer match appears before every page request
        new += 1
        page = search(client, q="guide", limit=10, cursor=page["next_cursor"])
        seen += ids(page)

    assert seen == list(reversed(matches))


def test_deletes_between_pages_skip_nothing(client: TestClient) -> None:
    matches = [save(client, f"Guide {n}") for n in range(25)]
    newest_first = list(reversed(matches))

    first = search(client, q="guide", limit=10)
    assert client.delete(f"/bookmarks/{newest_first[0]}").status_code == 204
    second = search(client, q="guide", limit=10, cursor=first["next_cursor"])

    assert ids(second) == newest_first[10:20]


def test_paging_with_tag_and_cursor(client: TestClient) -> None:
    tagged = []
    for n in range(6):
        tagged.append(save(client, f"Guide {n}", ["api"]))
        save(client, f"Guide other {n}", ["misc"])
    newest_first = list(reversed(tagged))

    first = search(client, q="guide", tag="api", limit=4)
    second = search(client, q="guide", tag="api", limit=4, cursor=first["next_cursor"])

    assert ids(first) == newest_first[:4]
    assert ids(second) == newest_first[4:]
    assert first["total"] == second["total"] == 6
    assert second["next_cursor"] is None


def test_cursor_from_another_search_is_a_position(client: TestClient) -> None:
    """Clarification Q3: a next_cursor is only a position; it is accepted with other words or tag."""
    guides = []
    for n in range(6):
        guides.append(save(client, f"Postgres guide {n}", ["db"]))
    newest_first = list(reversed(guides))

    first = search(client, q="guide", limit=2)
    other_words = search(client, q="postgres", limit=10, cursor=first["next_cursor"])
    other_tag = search(client, q="guide", tag="db", limit=10, cursor=first["next_cursor"])

    assert ids(other_words) == newest_first[2:]
    assert ids(other_tag) == newest_first[2:]
