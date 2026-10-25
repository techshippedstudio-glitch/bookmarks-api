"""Link and tag normalization (specs/001-bookmarks-api/data-model.md).

Pure functions using only the standard library, so they are easy to unit test.
"""

import re
from collections.abc import Iterable
from urllib.parse import urlsplit, urlunsplit

DEFAULT_PORTS = {"http": 80, "https": 443}
TAG_PATTERN = re.compile(r"^[a-z0-9-]{1,30}$")
MAX_URL_LENGTH = 2048


def normalize_url(url: str) -> str:
    """Return the normalized form of a link used to detect duplicates.

    Scheme and host are lowercased, the default port is removed, trailing slashes are removed
    from the path, the fragment is dropped and the query string is kept as is.
    Raises ValueError for anything that is not an http or https link with a host.
    """
    try:
        parts = urlsplit(url.strip())
        port = parts.port
    except ValueError as exc:
        raise ValueError("The link is not a valid web address.") from exc

    scheme = parts.scheme.lower()
    if scheme not in DEFAULT_PORTS:
        raise ValueError("The link must start with http:// or https://.")
    if not parts.hostname:
        raise ValueError("The link must include a host, such as example.com.")

    host = parts.hostname.lower()
    if ":" in host:  # IPv6 literal
        host = f"[{host}]"
    netloc = host if port in (None, DEFAULT_PORTS[scheme]) else f"{host}:{port}"
    if parts.username is not None:
        credentials = parts.username
        if parts.password is not None:
            credentials += f":{parts.password}"
        netloc = f"{credentials}@{netloc}"

    path = parts.path.rstrip("/")
    return urlunsplit((scheme, netloc, path, parts.query, ""))


def normalize_tag(tag: str) -> str:
    """Trim and lowercase a tag; raise ValueError if it is not 1-30 letters, digits or hyphens."""
    cleaned = tag.strip().lower()
    if not TAG_PATTERN.fullmatch(cleaned):
        raise ValueError(
            f"Tag {tag!r} is not valid: use 1 to 30 letters, digits or hyphens."
        )
    return cleaned


def normalize_tags(tags: Iterable[str]) -> list[str]:
    """Normalize each tag, drop duplicates and return them sorted."""
    return sorted({normalize_tag(tag) for tag in tags})


MAX_SEARCH_LENGTH = 200


def search_words(q: str) -> list[str]:
    """Split a title search into its distinct words (specs/002-bookmark-title-search).

    Words are separated by whitespace; repeats are dropped ignoring letter case, keeping the first
    spelling and the order of first appearance. Repeats are compared with ``str.lower()``, the
    same folding the database's case-insensitive match uses (``casefold()`` would merge words
    such as "Straße" and "STRASSE" that the database treats as different). The 200-character
    limit applies to ``q`` as sent. Raises ValueError when ``q`` is too long, contains a NUL
    control character (PostgreSQL cannot take it as a parameter), or has no non-space character.
    """
    if len(q) > MAX_SEARCH_LENGTH:
        raise ValueError(f"The search can be 1 to {MAX_SEARCH_LENGTH} characters long.")
    if "\x00" in q:
        raise ValueError("The search must not contain the NUL control character.")
    words: list[str] = []
    seen: set[str] = set()
    for word in q.split():
        key = word.lower()
        if key not in seen:
            seen.add(key)
            words.append(word)
    if not words:
        raise ValueError("The search must contain at least one non-space character.")
    return words
