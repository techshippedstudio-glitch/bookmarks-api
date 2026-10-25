"""User Story 1 - Search bookmarks by title words (specs/002-bookmark-title-search/spec.md)."""

from itertools import count

import pytest
from fastapi.testclient import TestClient

_urls = count()


def save(client: TestClient, title: str, tags: list[str] | None = None) -> int:
    response = client.post(
        "/bookmarks",
        json={"url": f"https://example.com/{next(_urls)}", "title": title, "tags": tags or []},
    )
    assert response.status_code == 201
    return response.json()["id"]


def search(client: TestClient, **params: object) -> dict:
    response = client.get("/bookmarks/search", params=params)
    assert response.status_code == 200, response.text
    return response.json()


def titles(body: dict) -> list[str]:
    return [item["title"] for item in body["items"]]


def test_returns_matches_newest_first_with_total(client: TestClient) -> None:
    save(client, "Postgres indexing guide")
    save(client, "Python tips")
    save(client, "Advanced Postgres tuning")

    body = search(client, q="postgres")

    assert titles(body) == ["Advanced Postgres tuning", "Postgres indexing guide"]
    assert body["total"] == 2
    assert body["limit"] == 20
    assert body["next_cursor"] is None


@pytest.mark.parametrize("q", ["fastapi", "FASTAPI", "FastAPI"])
def test_search_ignores_letter_case(client: TestClient, q: str) -> None:
    bookmark_id = save(client, "FastAPI Tutorial")

    body = search(client, q=q)

    assert [item["id"] for item in body["items"]] == [bookmark_id]


@pytest.mark.parametrize("q", ["postgres guide", "guide postgres"])
def test_every_word_must_appear_in_any_order(client: TestClient, q: str) -> None:
    save(client, "Postgres indexing guide")
    save(client, "Postgres backup scripts")

    assert titles(search(client, q=q)) == ["Postgres indexing guide"]


def test_no_match_is_an_empty_page_not_an_error(client: TestClient) -> None:
    save(client, "Python tips")

    assert search(client, q="kubernetes") == {
        "items": [],
        "total": 0,
        "limit": 20,
        "next_cursor": None,
    }


@pytest.mark.parametrize(
    "params",
    [{"q": ""}, {"q": "   "}, {"q": "\t"}, {"q": "a" * 201}, {}],
    ids=["empty", "spaces", "tab", "too-long", "missing"],
)
def test_invalid_search_is_rejected(client: TestClient, params: dict) -> None:
    response = client.get("/bookmarks/search", params=params)

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    assert error["message"]
    assert error["details"][0]["field"] == "query.q"


def test_word_matches_inside_a_longer_word(client: TestClient) -> None:
    save(client, "Postgres internals")
    save(client, "Start here")

    assert titles(search(client, q="post")) == ["Postgres internals"]
    assert titles(search(client, q="art")) == ["Start here"]


def test_one_character_word_matches_every_title_containing_it(client: TestClient) -> None:
    save(client, "C tips")
    save(client, "Rust book")
    save(client, "Docker basics")

    assert titles(search(client, q="c")) == ["Docker basics", "C tips"]


@pytest.mark.parametrize(
    ("q", "expected"),
    [
        ("%", ["50% off"]),
        ("_", ["snake_case names"]),
        ("*", ["Glob * patterns"]),
        ("/", ["Read/write locks"]),
    ],
)
def test_pattern_characters_match_literally(client: TestClient, q: str, expected: list[str]) -> None:
    for title in ["50% off", "snake_case names", "Glob * patterns", "Read/write locks", "Plain"]:
        save(client, title)

    assert titles(search(client, q=q)) == expected


def test_accented_capitals_fold_like_other_letters(client: TestClient) -> None:
    save(client, "école primaire")
    save(client, "Cafe menu")

    assert titles(search(client, q="ÉCOLE")) == ["école primaire"]
    assert titles(search(client, q="café")) == []  # accents are not ignored (spec Assumptions)


def test_repeating_a_word_changes_nothing(client: TestClient) -> None:
    save(client, "Postgres indexing guide")
    save(client, "Python tips")

    assert search(client, q="postgres Postgres  POSTGRES") == search(client, q="postgres")


def test_surrounding_and_repeated_whitespace_is_ignored(client: TestClient) -> None:
    save(client, "Postgres indexing guide")

    assert titles(search(client, q="  postgres \t  guide  ")) == ["Postgres indexing guide"]


def test_results_look_exactly_like_the_list(client: TestClient) -> None:
    save(client, "Postgres indexing guide", ["Postgres", "db"])
    save(client, "Python tips")

    found = search(client, q="indexing")["items"]
    listed = client.get("/bookmarks", params={"tag": "postgres"}).json()["items"]

    assert found == listed


def test_search_changes_no_bookmark(client: TestClient, row_count) -> None:
    save(client, "Postgres indexing guide")
    before = client.get("/bookmarks").json()

    search(client, q="postgres")
    search(client, q="nothing")

    assert client.get("/bookmarks").json() == before
    assert row_count() == 1


def test_nul_character_is_a_validation_error_not_a_server_error(client: TestClient) -> None:
    response = client.get("/bookmarks/search", params={"q": "a\x00b"})

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    assert error["details"][0]["field"] == "query.q"


@pytest.mark.parametrize("q", ["Straße STRASSE", "STRASSE Straße"])
def test_word_order_never_changes_results(client: TestClient, q: str) -> None:
    save(client, "Straße notes")
    save(client, "STRASSE map")
    both = save(client, "Straße or STRASSE")

    assert [item["id"] for item in search(client, q=q)["items"]] == [both]
