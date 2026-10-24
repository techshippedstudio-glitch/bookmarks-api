"""Database queries for bookmarks."""

from datetime import datetime

from sqlalchemy import delete, func, select, tuple_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from bookmarks_api.errors import NotFoundError
from bookmarks_api.models import BookmarkRow
from bookmarks_api.normalize import normalize_url
from bookmarks_api.schemas import BookmarkCreate

MAX_SAVE_ATTEMPTS = 3


def _find_existing(session: Session, normalized: str) -> BookmarkRow | None:
    """Return the bookmark stored for a normalized link, or None."""
    return session.scalars(
        select(BookmarkRow).where(BookmarkRow.url_normalized == normalized)
    ).one_or_none()


def create_bookmark(session: Session, data: BookmarkCreate) -> tuple[BookmarkRow, bool]:
    """Save a bookmark and return ``(row, created)``.

    If the normalized link is new, the row is inserted and ``created`` is True. If it is already
    bookmarked, the existing row is returned unchanged and ``created`` is False; the request's
    title and tags are ignored (specs/002-idempotent-duplicate-save FR-001, FR-002).

    ON CONFLICT DO NOTHING relies on the unique index, so this holds under concurrent saves: the
    losing insert waits for the winner, inserts nothing, then reads the committed row. If that row
    is deleted before it can be read, the insert is retried.
    """
    normalized = normalize_url(data.url)
    statement = (
        insert(BookmarkRow)
        .values(url=data.url, url_normalized=normalized, title=data.title, tags=data.tags)
        .on_conflict_do_nothing(index_elements=[BookmarkRow.url_normalized])
        .returning(BookmarkRow)
    )
    for _ in range(MAX_SAVE_ATTEMPTS):
        row = session.scalars(statement).one_or_none()
        if row is not None:
            session.commit()
            return row, True
        session.rollback()
        existing = _find_existing(session, normalized)
        if existing is not None:
            # Nothing was written; the read-only transaction ends when the session closes.
            # (A rollback here would expire the loaded row and force a reload.)
            return existing, False
    raise RuntimeError(
        f"Could not save or find a bookmark for {normalized!r} after {MAX_SAVE_ATTEMPTS} attempts."
    )


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
