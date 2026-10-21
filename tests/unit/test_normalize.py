"""Unit tests for link and tag normalization (pure functions, no database)."""

import pytest

from bookmarks_api.normalize import normalize_tag, normalize_tags, normalize_url


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ("https://example.com/docs", "https://example.com/docs"),
        ("HTTPS://Example.com:443/docs/#intro", "https://example.com/docs"),
        ("http://Example.com:80/", "http://example.com"),
        ("https://example.com", "https://example.com"),
        ("https://example.com/a/b///", "https://example.com/a/b"),
        ("https://example.com:8443/x", "https://example.com:8443/x"),
        ("https://example.com/search?q=FastAPI", "https://example.com/search?q=FastAPI"),
        ("https://example.com/search/?q=FastAPI#top", "https://example.com/search?q=FastAPI"),
        ("https://user@Example.com/p", "https://user@example.com/p"),
    ],
)
def test_normalize_url(given: str, expected: str) -> None:
    assert normalize_url(given) == expected


def test_paths_keep_their_letter_case() -> None:
    assert normalize_url("https://example.com/Docs") != normalize_url("https://example.com/docs")


def test_different_queries_are_different_links() -> None:
    assert normalize_url("https://example.com/?a=1") != normalize_url("https://example.com/?a=2")


@pytest.mark.parametrize(
    "bad",
    ["ftp://example.com", "example.com", "https://", "mailto:someone@example.com", "", "https:///x"],
)
def test_normalize_url_rejects_invalid_links(bad: str) -> None:
    with pytest.raises(ValueError):
        normalize_url(bad)


def test_normalize_tags_trims_lowercases_dedupes_and_sorts() -> None:
    assert normalize_tags(["Python", " api ", "python"]) == ["api", "python"]


def test_normalize_tags_empty_list() -> None:
    assert normalize_tags([]) == []


@pytest.mark.parametrize("good", ["a", "postgres", "fast-api", "py3", "x" * 30])
def test_normalize_tag_accepts_valid_tags(good: str) -> None:
    assert normalize_tag(good) == good


@pytest.mark.parametrize("bad", ["", "   ", "no spaces", "x" * 31, "c++", "naïve", "under_score"])
def test_normalize_tag_rejects_invalid_tags(bad: str) -> None:
    with pytest.raises(ValueError):
        normalize_tag(bad)
