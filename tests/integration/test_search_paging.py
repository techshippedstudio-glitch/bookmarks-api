"""User Story 3 - Page through search results (specs/002-bookmark-title-search/spec.md).

Includes the Constitution VI quality gate (page through everything while rows are added) and the
SC-006 timing check.
"""

import time
from itertools import count

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

_urls = count()


def save(client: TestClient, title: str, tags: list[str] | None = None) -> int:
    response = client.post(
        "/bookmarks",
        json={"url": f"https://example.com/p{next(_urls)}", "title": title, "tags": tags or []},
    )
    assert response.status_code == 201
    return response.json()["id"]


def seed(client: TestClient, matching: int, other: int = 0) -> list[int]:
    """Save matching ("Python ...") and non-matching bookmarks, interleaved; return matching ids."""
    ids = []
    for n in range(max(matching, other)):
        if n < matching:
            ids.append(save(client, f"Python note {n}"))
        if n < other:
            save(client, f"Rust note {n}")
    return ids


def ids_of(body: dict) -> list[int]:
    return [item["id"] for item in body["items"]]


def test_pages_of_twenty_by_default(client: TestClient) -> None:
    newest_first = list(reversed(seed(client, matching=25, other=5)))

    first = client.get("/bookmarks/search", params={"q": "python"}).json()
    second = client.get(
        "/bookmarks/search", params={"q": "python", "cursor": first["next_cursor"]}
    ).json()

    assert ids_of(first) == newest_first[:20]
    assert first["total"] == 25
    assert first["next_cursor"]
    assert ids_of(second) == newest_first[20:]
    assert second["total"] == 25
    assert second["next_cursor"] is None


def test_exactly_one_full_page_has_no_next_cursor(client: TestClient) -> None:
    seed(client, matching=20, other=3)

    body = client.get("/bookmarks/search", params={"q": "python"}).json()

    assert len(body["items"]) == 20
    assert body["next_cursor"] is None


def test_new_match_before_the_next_page_repeats_and_skips_nothing(client: TestClient) -> None:
    newest_first = list(reversed(seed(client, matching=25)))

    first = client.get("/bookmarks/search", params={"q": "python"}).json()
    save(client, "Python brand new")
    second = client.get(
        "/bookmarks/search", params={"q": "python", "cursor": first["next_cursor"]}
    ).json()

    assert ids_of(second) == newest_first[20:]


def test_saves_between_pages_cause_no_duplicates_or_gaps(client: TestClient) -> None:
    """Constitution VI quality gate: page through every match while new matches arrive."""
    expected = list(reversed(seed(client, matching=25, other=10)))

    page = client.get("/bookmarks/search", params={"q": "python", "limit": 10}).json()
    seen = ids_of(page)
    while page["next_cursor"]:
        save(client, "Python arrives mid-paging")  # a newer match before every page request
        save(client, "Rust arrives mid-paging")
        page = client.get(
            "/bookmarks/search",
            params={"q": "python", "limit": 10, "cursor": page["next_cursor"]},
        ).json()
        seen += ids_of(page)

    assert seen == expected


def test_deletes_between_pages_skip_nothing(client: TestClient) -> None:
    newest_first = list(reversed(seed(client, matching=25)))

    first = client.get("/bookmarks/search", params={"q": "python", "limit": 10}).json()
    assert client.delete(f"/bookmarks/{newest_first[0]}").status_code == 204
    second = client.get(
        "/bookmarks/search", params={"q": "python", "limit": 10, "cursor": first["next_cursor"]}
    ).json()

    assert ids_of(second) == newest_first[10:20]


def test_search_and_tag_page_together(client: TestClient) -> None:
    wanted = []
    for n in range(7):
        wanted.append(save(client, f"Python tagged {n}", ["web"]))
        save(client, f"Python untagged {n}")
    expected = list(reversed(wanted))

    page = client.get("/bookmarks/search", params={"q": "python", "tag": "web", "limit": 3}).json()
    seen = ids_of(page)
    assert page["total"] == 7
    while page["next_cursor"]:
        page = client.get(
            "/bookmarks/search",
            params={"q": "python", "tag": "web", "limit": 3, "cursor": page["next_cursor"]},
        ).json()
        seen += ids_of(page)

    assert seen == expected


@pytest.mark.parametrize(
    "params",
    [{"limit": 101}, {"limit": 0}, {"limit": "many"}],
    ids=["limit-over-100", "limit-zero", "limit-not-a-number"],
)
def test_invalid_paging_is_rejected_like_the_list(client: TestClient, params: dict) -> None:
    search = client.get("/bookmarks/search", params={"q": "python", **params})
    listing = client.get("/bookmarks", params=params)

    assert search.status_code == listing.status_code == 422
    assert search.json() == listing.json()


@pytest.mark.parametrize("cursor", ["not-a-cursor", "", "eyJ0IjoieCJ9", "WzEsMl0"])
def test_malformed_cursor_is_rejected_like_the_list(client: TestClient, cursor: str) -> None:
    search = client.get("/bookmarks/search", params={"q": "python", "cursor": cursor})
    listing = client.get("/bookmarks", params={"cursor": cursor})

    assert search.status_code == 422
    assert search.json() == listing.json()
    assert search.json()["error"]["details"][0]["field"] == "query.cursor"


def test_offset_is_rejected_and_points_to_cursor(client: TestClient) -> None:
    response = client.get("/bookmarks/search", params={"q": "python", "offset": "20"})

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    assert error["details"][0]["field"] == "query.offset"
    assert "cursor" in error["details"][0]["message"]


def test_cursor_marks_a_position_only(client: TestClient) -> None:
    """Clarification: a cursor from one search, sent with another, continues the new search."""
    python_ids, rust_ids = [], []
    for n in range(6):
        python_ids.append(save(client, f"Python note {n}"))
        rust_ids.append(save(client, f"Rust note {n}"))

    first = client.get("/bookmarks/search", params={"q": "python", "limit": 2}).json()
    position = first["items"][-1]["id"]
    other = client.get(
        "/bookmarks/search", params={"q": "rust", "cursor": first["next_cursor"]}
    ).json()

    assert ids_of(other) == [i for i in reversed(rust_ids) if i < position]


def test_search_answers_within_one_second_for_ten_thousand_bookmarks(
    client: TestClient, engine: Engine
) -> None:
    """SC-006: for 10,000 bookmarks, 95% of searches return their page in under 1 second."""
    words = ["postgres", "python", "fastapi", "docker", "indexing", "guide", "tips", "notes"]
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO bookmarks (url, url_normalized, title, tags, created_at) "
                "SELECT 'https://example.com/perf/' || n, 'https://example.com/perf/' || n, "
                "initcap(w[1 + n % 8]) || ' ' || w[1 + (n / 8) % 8] || ' ' || n, "
                "ARRAY[w[1 + n % 3]], now() - n * interval '1 second' "
                "FROM generate_series(1, 10000) AS n, (SELECT CAST(:words AS text[]) AS w) AS v"
            ),
            {"words": words},
        )
    searches = [
        {"q": "postgres"},
        {"q": "python guide"},
        {"q": "fastapi", "tag": "python"},
        {"q": "o"},
        {"q": "notes 99"},
        {"q": "nothing-matches"},
        {"q": "docker", "limit": 100},
        {"q": "INDEXING tips", "tag": "postgres"},
        {"q": "9"},
        {"q": "guide postgres python"},
    ] * 2

    durations = []
    for params in searches:
        started = time.perf_counter()
        response = client.get("/bookmarks/search", params=params)
        durations.append(time.perf_counter() - started)
        assert response.status_code == 200

    assert client.get("/bookmarks/search", params={"q": "postgres"}).json()["total"] > 0
    assert sum(d < 1.0 for d in durations) >= 19  # 95% of 20
