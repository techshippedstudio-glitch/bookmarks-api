"""Database queries for bookmarks."""

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from bookmarks_api.errors import DuplicateUrlError, NotFoundError
from bookmarks_api.models import BookmarkRow
from bookmarks_api.normalize import normalize_url
from bookmarks_api.schemas import BookmarkCreate


def create_bookmark(session: Session, data: BookmarkCreate) -> BookmarkRow:
    """Insert a bookmark, or raise DuplicateUrlError if its normalized link already exists.

    ON CONFLICT DO NOTHING relies on the unique index, so this holds under concurrent saves.
    """
    normalized = normalize_url(data.url)
    statement = (
        insert(BookmarkRow)
        .values(url=data.url, url_normalized=normalized, title=data.title, tags=data.tags)
        .on_conflict_do_nothing(index_elements=[BookmarkRow.url_normalized])
        .returning(BookmarkRow)
    )
    row = session.scalars(statement).one_or_none()
    if row is None:
        session.rollback()
        existing_id = session.scalar(
            select(BookmarkRow.id).where(BookmarkRow.url_normalized == normalized)
        )
        raise DuplicateUrlError(existing_id)
    session.commit()
    return row


def list_bookmarks(
    session: Session, *, limit: int, offset: int, tag: str | None = None
) -> tuple[list[BookmarkRow], int]:
    """Return one page of bookmarks, newest first, and the total number matching the filter."""
    conditions = [BookmarkRow.tags.contains([tag])] if tag else []
    total = session.scalar(select(func.count()).select_from(BookmarkRow).where(*conditions))
    rows = session.scalars(
        select(BookmarkRow)
        .where(*conditions)
        .order_by(BookmarkRow.created_at.desc(), BookmarkRow.id.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return list(rows), total or 0


def delete_bookmark(session: Session, bookmark_id: int) -> None:
    """Delete a bookmark by id, or raise NotFoundError if there is none."""
    result = session.execute(delete(BookmarkRow).where(BookmarkRow.id == bookmark_id))
    if result.rowcount == 0:
        session.rollback()
        raise NotFoundError(f"No bookmark with id {bookmark_id}.")
    session.commit()
