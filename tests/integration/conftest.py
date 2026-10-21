"""Every integration test starts from an empty bookmarks table."""

import pytest


@pytest.fixture(autouse=True)
def _empty_table(clean_database: None) -> None:
    return None
