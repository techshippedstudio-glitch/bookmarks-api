"""The search pre-check (specs/002-bookmark-title-search, FR-008).

Splitting the search into words happens in PostgreSQL (title_words), so it is tested through the
API in tests/integration/test_search_bookmarks.py. This pure function only decides whether a
search has anything to look for.
"""

import pytest

from bookmarks_api.normalize import has_word_character


@pytest.mark.parametrize("query", ["postgres", "Python3", "3", "ΣΟΦΙΑ", "  a  "])
def test_has_word_character(query: str) -> None:
    assert has_word_character(query) is True


@pytest.mark.parametrize(
    "query",
    ["", "   ", "  -- !", "_", "½", "²"],
    ids=["empty", "spaces", "punctuation", "underscore", "fraction", "superscript"],
)
def test_has_no_word_character(query: str) -> None:
    assert has_word_character(query) is False
