"""SQLAlchemy mapping for the bookmarks table (see specs/001-bookmarks-api/data-model.md)."""

from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, Identity, Index, String, Text, func, text
from sqlalchemy.dialects.postgresql import ARRAY, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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
