"""Cursor encoding round-trips and rejects anything the API did not issue."""

from datetime import UTC, datetime

import pytest

from bookmarks_api.cursor import decode_cursor, encode_cursor


def test_round_trip_keeps_microseconds_and_id() -> None:
    created_at = datetime(2026, 10, 21, 9, 30, 15, 123456, tzinfo=UTC)

    assert decode_cursor(encode_cursor(created_at, 42)) == (created_at, 42)


def test_cursor_is_url_safe() -> None:
    cursor = encode_cursor(datetime(2026, 10, 21, tzinfo=UTC), 7)

    assert cursor.replace("-", "").replace("_", "").isalnum()


@pytest.mark.parametrize(
    "bad",
    ["", "%%%", "bm90IGpzb24", "eyJ0IjoxfQ", "eyJ0IjoiMjAyNi0xMC0yMVQwMDowMDowMCswMDowMCIsImlkIjowfQ"],
    ids=["empty", "not-base64", "not-json", "time-not-a-string", "id-zero"],
)
def test_invalid_cursors_raise_value_error(bad: str) -> None:
    with pytest.raises(ValueError, match="cursor"):
        decode_cursor(bad)
