"""Search-word parsing (specs/002-bookmark-title-search/data-model.md, "Search words")."""

import pytest

from bookmarks_api.normalize import MAX_SEARCH_LENGTH, search_words


def test_single_word() -> None:
    assert search_words("postgres") == ["postgres"]


def test_splits_on_whitespace_and_drops_case_insensitive_repeats() -> None:
    assert search_words("  Postgres   guide postgres ") == ["Postgres", "guide"]


@pytest.mark.parametrize("separator", ["\t", "\n", "\r\n", " \t "])
def test_tabs_and_line_breaks_separate_words(separator: str) -> None:
    assert search_words(f"indexing{separator}guide") == ["indexing", "guide"]


def test_keeps_order_of_first_appearance() -> None:
    assert search_words("guide INDEXING Guide indexing") == ["guide", "INDEXING"]


def test_one_character_word_is_allowed() -> None:
    assert search_words("c") == ["c"]


@pytest.mark.parametrize("blank", ["", " ", "   ", "\t", " \n "], ids=["empty", "space", "spaces", "tab", "mixed"])
def test_blank_search_is_rejected(blank: str) -> None:
    with pytest.raises(ValueError, match="non-space"):
        search_words(blank)


def test_limit_is_200_characters_as_sent() -> None:
    assert MAX_SEARCH_LENGTH == 200
    assert search_words("a" * 200) == ["a" * 200]
    with pytest.raises(ValueError, match="200"):
        search_words("a" * 201)
    with pytest.raises(ValueError, match="200"):
        search_words(" " + "a" * 199 + " ")  # surrounding spaces count (spec FR-004)


@pytest.mark.parametrize("word", ["%", "_", "/", "*", "50%_off", "a/b"])
def test_pattern_characters_are_ordinary(word: str) -> None:
    assert search_words(word) == [word]


def test_nul_character_is_rejected() -> None:
    with pytest.raises(ValueError, match="control"):
        search_words("a\x00b")


def test_words_are_merged_only_when_they_match_identically() -> None:
    # "ß" lowercases to itself but casefolds to "ss"; the database match uses lowercase.
    assert search_words("Straße STRASSE") == ["Straße", "STRASSE"]
    assert search_words("Straße STRAßE") == ["Straße"]
