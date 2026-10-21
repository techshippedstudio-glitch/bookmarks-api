"""Pydantic request and response models (Constitution I: typed API contracts)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from bookmarks_api.normalize import MAX_URL_LENGTH, normalize_tags, normalize_url

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
    offset: int
