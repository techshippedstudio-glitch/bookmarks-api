"""SQLAlchemy mapping for the bookmarks table (specs/001-bookmarks-api and specs/002-bookmark-title-search data-model.md)."""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ColumnElement,
    Identity,
    Index,
    String,
    Text,
    func,
    literal_column,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Literal SQL constants (not bound parameters), so the query expression is textually identical to
# the index expression in migration 0002 and the planner can use the index.
WORD_SEPARATORS = literal_column("'[^[:alnum:]]+'")
EMPTY_TEXT = literal_column("''")


def title_words(expr: ColumnElement[str] | str) -> ColumnElement[list[str]]:
    """The lowercase words of a text, computed by PostgreSQL (specs/002-bookmark-title-search).

    A word is an unbroken run of letters and digits; everything else separates words. The same
    expression is used for titles (and their GIN index) and for the search, so both sides agree.
    """
    return func.array_remove(
        func.regexp_split_to_array(func.lower(expr), WORD_SEPARATORS),
        EMPTY_TEXT,
        type_=ARRAY(Text),
    )


class Base(DeclarativeBase):
    pass


class BookmarkRow(Base):
    __tablename__ = "bookmarks"
    __table_args__ = (
        CheckConstraint("char_length(title) >= 1", name="ck_bookmarks_title_not_empty"),
        CheckConstraint("cardinality(tags) <= 10", name="ck_bookmarks_max_10_tags"),
        Index("uq_bookmarks_url_normalized", "url_normalized", unique=True),
        Index("ix_bookmarks_created_at_id", text("created_at DESC"), text("id DESC")),
        Index("ix_bookmarks_tags", "tags", postgresql_using="gin"),
        Index(
            "ix_bookmarks_title_words",
            title_words(text("title")),
            postgresql_using="gin",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    url_normalized: Mapped[str] = mapped_column(String(2048), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    tags: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, server_default=text("'{}'")
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
