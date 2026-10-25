"""User Story 1 - Search bookmarks by title words (specs/002-bookmark-title-search/spec.md,
scenarios 1 to 5 and Edge Cases)."""

import pytest
from fastapi.testclient import TestClient

_counter = iter(range(1, 1_000_000))


def save(client: TestClient, title: str, tags: list[str] | None = None, url: str | None = None) -> int:
    url = url or f"https://example.com/search/{next(_counter)}"
    response = client.post("/bookmarks", json={"url": url, "title": title, "tags": tags or []})
    assert response.status_code == 201, response.text
    return response.json()["id"]


def search(client: TestClient, q: str, **params) -> dict:
    response = client.get("/bookmarks/search", params={"q": q, **params})
    assert response.status_code == 200, response.text
    return response.json()


def ids(body: dict) -> list[int]:
    return [item["id"] for item in body["items"]]


def test_returns_matching_titles_newest_first(client: TestClient) -> None:
    indexing = save(client, "Postgres indexing guide")
    save(client, "FastAPI tutorial")
    backups = save(client, "Postgres backups")

    body = search(client, "postgres")

    assert ids(body) == [backups, indexing]
    assert body["total"] == 2
    assert body["limit"] == 20
    assert body["next_cursor"] is None


@pytest.mark.parametrize("q", ["postgresql", "POSTGRESQL", "PostgreSQL"])
def test_letter_case_is_ignored(client: TestClient, q: str) -> None:
    learning = save(client, "Learning PostgreSQL")

    assert ids(search(client, q)) == [learning]


def test_no_match_returns_empty_page_not_an_error(client: TestClient) -> None:
    save(client, "Postgres backups")

    response = client.get("/bookmarks/search", params={"q": "kubernetes"})

    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0, "limit": 20, "next_cursor": None}


def test_every_word_must_appear_in_any_order(client: TestClient) -> None:
    guide = save(client, "Postgres indexing guide")

    assert ids(search(client, "indexing postgres")) == [guide]
    assert ids(search(client, "postgres backups")) == []


@pytest.mark.parametrize(
    "params",
    [{}, {"q": ""}, {"q": "  -- !"}, {"q": "x" * 201}, {"q": "½"}],
    ids=["missing", "empty", "only-separators", "201-characters", "only-a-symbol"],
)
def test_invalid_search_is_rejected(client: TestClient, params: dict) -> None:
    response = client.get("/bookmarks/search", params=params)

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    assert error["details"][0]["field"] == "query.q"
    assert error["message"]


def test_200_character_search_is_accepted(client: TestClient) -> None:
    long_word = "a" * 200
    match = save(client, long_word)

    assert ids(search(client, long_word)) == [match]


def test_extra_spaces_are_ignored(client: TestClient) -> None:
    guide = save(client, "Postgres indexing guide")

    assert ids(search(client, "  postgres   guide ")) == [guide]


def test_hyphen_and_punctuation_separate_words(client: TestClient) -> None:
    spec_kit = save(client, "Spec-Kit guide")
    fastapi = save(client, "FastAPI: a tutorial")

    assert ids(search(client, "spec-kit")) == [spec_kit]
    assert ids(search(client, "kit")) == [spec_kit]
    assert ids(search(client, "fastapi tutorial")) == [fastapi]
    assert ids(search(client, "FastAPI:")) == [fastapi]


def test_only_whole_words_match(client: TestClient) -> None:
    save(client, "Postgres backups")

    assert ids(search(client, "post")) == []
    assert ids(search(client, "gres")) == []


def test_digits_belong_to_the_word(client: TestClient) -> None:
    py3 = save(client, "Python3 release notes")

    assert ids(search(client, "python3")) == [py3]
    assert ids(search(client, "python")) == []


def test_letter_case_is_ignored_for_non_english_letters(client: TestClient) -> None:
    greek = save(client, "ΟΔΟΣ")
    turkish = save(client, "İstanbul guide")

    assert ids(search(client, "ΟΔΟΣ")) == [greek]
    assert ids(search(client, "οδοσ")) == [greek]
    assert ids(search(client, "İstanbul")) == [turkish]


def test_symbols_that_are_not_letters_or_digits_separate_words(client: TestClient) -> None:
    fraction = save(client, "x½y")

    assert ids(search(client, "x")) == [fraction]
    assert ids(search(client, "y")) == [fraction]


def test_only_the_title_is_searched(client: TestClient) -> None:
    save(client, "Release notes", tags=["kubernetes"], url="https://kubernetes.io/notes")

    assert ids(search(client, "kubernetes")) == []
    assert ids(search(client, "notes")) != []


def test_deleted_bookmark_no_longer_appears(client: TestClient) -> None:
    gone = save(client, "Postgres backups")
    kept = save(client, "Postgres indexing guide")
    assert client.delete(f"/bookmarks/{gone}").status_code == 204

    assert ids(search(client, "postgres")) == [kept]


def test_bookmark_list_is_unchanged(client: TestClient) -> None:
    """FR-011: the list has no search option; an unknown q is simply ignored by the list."""
    first = save(client, "Postgres backups")
    second = save(client, "FastAPI tutorial")

    body = client.get("/bookmarks", params={"q": "postgres"}).json()

    assert ids(body) == [second, first]
    assert body["total"] == 2


def test_search_is_in_the_openapi_document(client: TestClient) -> None:
    """Constitution I quality gate: the endpoint is published with request and response models."""
    spec = client.get("/openapi.json").json()
    operation = spec["paths"]["/bookmarks/search"]["get"]

    q = next(p for p in operation["parameters"] if p["name"] == "q")
    assert q["required"] is True
    assert {p["name"] for p in operation["parameters"]} >= {"q", "tag", "limit", "cursor"}
    ok_schema = operation["responses"]["200"]["content"]["application/json"]["schema"]
    assert ok_schema["$ref"].endswith("/BookmarkPage")
    error_schema = operation["responses"]["422"]["content"]["application/json"]["schema"]
    assert error_schema["$ref"].endswith("/ErrorResponse")
