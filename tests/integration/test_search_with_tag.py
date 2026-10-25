"""User Story 2 - Combine search with the tag filter (specs/002-bookmark-title-search/spec.md)."""

from itertools import count

import pytest
from fastapi.testclient import TestClient

_urls = count()


def save(client: TestClient, title: str, tags: list[str]) -> int:
    response = client.post(
        "/bookmarks",
        json={"url": f"https://example.com/t{next(_urls)}", "title": title, "tags": tags},
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_search_and_tag_must_both_match(client: TestClient) -> None:
    wanted = save(client, "Indexing basics", ["postgres"])
    save(client, "Indexing basics for search", ["search"])
    save(client, "Postgres roles", ["postgres"])

    body = client.get("/bookmarks/search", params={"q": "indexing", "tag": "postgres"}).json()

    assert [item["id"] for item in body["items"]] == [wanted]
    assert body["total"] == 1


def test_search_and_tag_both_ignore_letter_case(client: TestClient) -> None:
    wanted = save(client, "Indexing basics", ["postgres"])

    body = client.get("/bookmarks/search", params={"q": "INDEXING", "tag": "Postgres"}).json()

    assert [item["id"] for item in body["items"]] == [wanted]


def test_matching_titles_without_the_tag_give_an_empty_page(client: TestClient) -> None:
    save(client, "Indexing basics", ["postgres"])

    body = client.get("/bookmarks/search", params={"q": "indexing", "tag": "python"}).json()

    assert body == {"items": [], "total": 0, "limit": 20, "next_cursor": None}


def test_combined_results_stay_newest_first(client: TestClient) -> None:
    older = save(client, "Postgres indexing guide", ["postgres"])
    save(client, "Postgres indexing for MySQL users", ["mysql"])
    newer = save(client, "Advanced indexing", ["postgres"])

    body = client.get("/bookmarks/search", params={"q": "indexing", "tag": "postgres"}).json()

    assert [item["id"] for item in body["items"]] == [newer, older]


@pytest.mark.parametrize("bad", ["bad tag!", "", "x" * 31])
def test_invalid_tag_filter_is_rejected(client: TestClient, bad: str) -> None:
    response = client.get("/bookmarks/search", params={"q": "indexing", "tag": bad})

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    assert error["details"][0]["field"] == "query.tag"
