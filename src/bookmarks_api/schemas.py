"""Pydantic request and response models (Constitution I: typed API contracts)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from bookmarks_api.cursor import decode_cursor
from bookmarks_api.normalize import (
    MAX_SEARCH_LENGTH,
    MAX_URL_LENGTH,
    normalize_tag,
    normalize_tags,
    normalize_url,
    search_words,
)

MAX_TAGS = 10



class BookmarkCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: str = Field(max_length=MAX_URL_LENGTH, description="An http or https link with a host.")
    title: str = Field(min_length=1, max_length=200)
    tags: list[str] = Field(default_factory=list, description="Up to 10 tags.")

    @field_validator("url")
    @classmethod
    def check_url(cls, value: str) -> str:
        normalize_url(value)  # raises ValueError with a clear message when invalid
        return value

    @field_validator("title", mode="before")
    @classmethod
    def strip_title(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("tags")
    @classmethod
    def check_tags(cls, value: list[str]) -> list[str]:
        tags = normalize_tags(value)
        if len(tags) > MAX_TAGS:
            raise ValueError(f"A bookmark can have at most {MAX_TAGS} tags.")
        return tags


class Bookmark(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    title: str
    tags: list[str]
    created_at: datetime


class BookmarkPage(BaseModel):
    items: list[Bookmark]
    total: int = Field(description="Number of bookmarks matching the filter.")
    limit: int
    next_cursor: str | None = Field(
        description="Pass as `cursor` to get the next page; null on the last page."
    )


class BookmarkListQuery(BaseModel):
    """Query parameters for GET /bookmarks (Constitution I: an explicit request model)."""

    limit: int = Field(default=20, ge=1, le=100, description="Page size, 1 to 100.")
    cursor: str | None = Field(
        default=None,
        description="The next_cursor from the previous page; omit for the first page.",
    )
    tag: str | None = Field(
        default=None, description="Only bookmarks with this tag (normalized like tags)."
    )

    @field_validator("cursor")
    @classmethod
    def _check_cursor(cls, value: str | None) -> str | None:
        if value is not None:
            decode_cursor(value)  # raises ValueError for a malformed cursor
        return value

    @field_validator("tag")
    @classmethod
    def _normalize_tag(cls, value: str | None) -> str | None:
        return normalize_tag(value) if value is not None else None


class BookmarkSearchQuery(BookmarkListQuery):
    """Query parameters for GET /bookmarks/search: the list's parameters plus a required ``q``."""

    q: str = Field(
        min_length=1,
        max_length=MAX_SEARCH_LENGTH,
        description="One or more words separated by spaces; every word must appear in the title.",
    )

    @field_validator("q")
    @classmethod
    def _check_q(cls, value: str) -> str:
        search_words(value)  # raises ValueError for a blank search
        return value
