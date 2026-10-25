"""User Story 2 - Combine search with the tag filter (specs/002-bookmark-title-search/spec.md,
scenarios 1 to 4)."""

import pytest
from fastapi.testclient import TestClient

_counter = iter(range(1, 1_000_000))


def save(client: TestClient, title: str, tags: list[str]) -> int:
    url = f"https://example.com/tagged/{next(_counter)}"
    response = client.post("/bookmarks", json={"url": url, "title": title, "tags": tags})
    assert response.status_code == 201, response.text
    return response.json()["id"]


def ids(body: dict) -> list[int]:
    return [item["id"] for item in body["items"]]


def test_search_and_tag_must_both_match(client: TestClient) -> None:
    python_testing = save(client, "Testing in Python", ["python"])
    save(client, "Testing in Go", ["go"])
    save(client, "Python packaging", ["python"])

    body = client.get("/bookmarks/search", params={"q": "testing", "tag": "python"}).json()

    assert ids(body) == [python_testing]
    assert body["total"] == 1


def test_tag_is_normalized_like_the_list(client: TestClient) -> None:
    python_testing = save(client, "Testing in Python", ["python"])

    body = client.get("/bookmarks/search", params={"q": "testing", "tag": " Python "}).json()

    assert ids(body) == [python_testing]


def test_tag_no_match_carries_returns_empty_page(client: TestClient) -> None:
    save(client, "Testing in Python", ["python"])
    save(client, "Testing in Go", ["go"])

    response = client.get("/bookmarks/search", params={"q": "testing", "tag": "rust"})

    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0, "limit": 20, "next_cursor": None}


def test_tag_alone_or_words_alone_are_not_enough(client: TestClient) -> None:
    save(client, "Python packaging", ["python"])  # tag matches, words do not
    save(client, "Testing in Go", ["go"])  # words match, tag does not

    body = client.get("/bookmarks/search", params={"q": "testing", "tag": "python"}).json()

    assert body["items"] == []
    assert body["total"] == 0


@pytest.mark.parametrize("bad", ["no spaces", "x" * 31, "c++"])
def test_invalid_tag_gives_the_same_error_as_the_list(client: TestClient, bad: str) -> None:
    searched = client.get("/bookmarks/search", params={"q": "testing", "tag": bad})
    listed = client.get("/bookmarks", params={"tag": bad})

    assert searched.status_code == listed.status_code == 422
    assert searched.json() == listed.json()
    assert searched.json()["error"]["details"][0]["field"] == "query.tag"
