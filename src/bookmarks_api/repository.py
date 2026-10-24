"""Database queries for bookmarks."""

from datetime import datetime

from sqlalchemy import delete, func, select, tuple_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from bookmarks_api.errors import NotFoundError
from bookmarks_api.models import BookmarkRow
from bookmarks_api.normalize import normalize_url
from bookmarks_api.schemas import BookmarkCreate

# One retry covers the case where the existing bookmark is deleted between the conflicting
# insert and the lookup; the retry then either inserts or finds a row saved meanwhile.
_INSERT_ATTEMPTS = 2


def _find_by_normalized_url(session: Session, normalized: str) -> BookmarkRow | None:
    return session.scalars(
        select(BookmarkRow).where(BookmarkRow.url_normalized == normalized)
    ).one_or_none()


def create_bookmark(session: Session, data: BookmarkCreate) -> tuple[BookmarkRow, bool]:
    """Save a bookmark and return ``(row, created)``.

    A new normalized link is inserted and returned with ``created=True``. A link that is already
    saved returns the existing row unchanged with ``created=False``; the request's title and tags
    are ignored (FR-004). ON CONFLICT DO NOTHING relies on the unique index, so two concurrent
    saves of a new link store one row: under READ COMMITTED the loser's insert waits for the
    winner to commit, and its follow-up select (a new statement) sees the winner's row.
    """
    normalized = normalize_url(data.url)
    statement = (
        insert(BookmarkRow)
        .values(url=data.url, url_normalized=normalized, title=data.title, tags=data.tags)
        .on_conflict_do_nothing(index_elements=[BookmarkRow.url_normalized])
        .returning(BookmarkRow)
    )
    for _ in range(_INSERT_ATTEMPTS):
        row = session.scalars(statement).one_or_none()
        if row is not None:
            session.commit()
            return row, True
        session.rollback()
        existing = _find_by_normalized_url(session, normalized)
        # End the read-only transaction without expiring the loaded row (rollback would expire
        # it; the sessions use expire_on_commit=False). Nothing was written, so commit is a no-op.
        session.commit()
        if existing is not None:
            return existing, False
    raise RuntimeError("Could not save or find the bookmark after a concurrent delete.")


def list_bookmarks(
    session: Session,
    *,
    limit: int,
    after: tuple[datetime, int] | None = None,
    tag: str | None = None,
) -> tuple[list[BookmarkRow], int, bool]:
    """Return one page of bookmarks, newest first, the total matching the filter, and whether
    more pages follow.

    Keyset pagination (Constitution VI): the page starts strictly after the (created_at, id)
    position in ``after``, so saves and deletes between requests never shift the page. The
    row comparison matches the (created_at DESC, id DESC) index, so every page is a range scan.
    """
    conditions = [BookmarkRow.tags.contains([tag])] if tag else []
    total = session.scalar(select(func.count()).select_from(BookmarkRow).where(*conditions))
    page_conditions = list(conditions)
    if after is not None:
        page_conditions.append(tuple_(BookmarkRow.created_at, BookmarkRow.id) < tuple_(*after))
    rows = session.scalars(
        select(BookmarkRow)
        .where(*page_conditions)
        .order_by(BookmarkRow.created_at.desc(), BookmarkRow.id.desc())
        .limit(limit + 1)
    ).all()
    return list(rows[:limit]), total or 0, len(rows) > limit


def delete_bookmark(session: Session, bookmark_id: int) -> None:
    """Delete a bookmark by id, or raise NotFoundError if there is none."""
    result = session.execute(delete(BookmarkRow).where(BookmarkRow.id == bookmark_id))
    if result.rowcount == 0:
        session.rollback()
        raise NotFoundError(f"No bookmark with id {bookmark_id}.")
    session.commit()
