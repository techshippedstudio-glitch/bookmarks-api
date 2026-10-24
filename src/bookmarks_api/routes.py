"""HTTP endpoints for /bookmarks."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status
from pydantic import AfterValidator
from sqlalchemy.orm import Session

from bookmarks_api import repository
from bookmarks_api.cursor import decode_cursor, encode_cursor
from bookmarks_api.db import get_session
from bookmarks_api.errors import ErrorResponse
from bookmarks_api.normalize import normalize_tag
from bookmarks_api.schemas import Bookmark, BookmarkCreate, BookmarkPage

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])

SessionDep = Annotated[Session, Depends(get_session)]

ERROR_422 = {422: {"model": ErrorResponse, "description": "The request is not valid."}}

OFFSET_REMOVED = (
    "offset is not supported (Constitution VI); pass the previous page's next_cursor as cursor."
)


def _check_cursor(value: str | None) -> str | None:
    if value is not None:
        decode_cursor(value)  # raises ValueError for a malformed cursor
    return value


def _reject_offset(value: str | None) -> None:
    if value is not None:
        raise ValueError(OFFSET_REMOVED)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=Bookmark,
    summary="Save a bookmark",
    description=(
        "Saves a new link and returns 201. If the link, after normalization, is already "
        "bookmarked, nothing is stored or changed: the existing bookmark is returned unchanged "
        "with 200, and the title and tags in the request are ignored."
    ),
    responses={
        200: {
            "model": Bookmark,
            "description": "The link is already bookmarked; the existing bookmark, unchanged.",
        },
        201: {"description": "Bookmark saved."},
        **ERROR_422,
    },
)
def create_bookmark(data: BookmarkCreate, session: SessionDep, response: Response) -> Bookmark:
    row, created = repository.create_bookmark(session, data)
    if not created:
        response.status_code = status.HTTP_200_OK
    return Bookmark.model_validate(row)


@router.get(
    "",
    response_model=BookmarkPage,
    summary="List bookmarks, newest first",
    responses=ERROR_422,
)
def list_bookmarks(
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=100, description="Page size, 1 to 100.")] = 20,
    cursor: Annotated[
        str | None,
        Query(description="The next_cursor from the previous page; omit for the first page."),
        AfterValidator(_check_cursor),
    ] = None,
    tag: Annotated[
        str | None,
        Query(description="Only bookmarks with this tag (normalized like tags)."),
        AfterValidator(lambda value: normalize_tag(value) if value is not None else None),
    ] = None,
    offset: Annotated[
        str | None, Query(include_in_schema=False), AfterValidator(_reject_offset)
    ] = None,
) -> BookmarkPage:
    after = decode_cursor(cursor) if cursor is not None else None
    rows, total, has_more = repository.list_bookmarks(session, limit=limit, after=after, tag=tag)
    next_cursor = encode_cursor(rows[-1].created_at, rows[-1].id) if has_more else None
    return BookmarkPage(
        items=[Bookmark.model_validate(row) for row in rows],
        total=total,
        limit=limit,
        next_cursor=next_cursor,
    )


@router.delete(
    "/{bookmark_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a bookmark",
    responses={404: {"model": ErrorResponse, "description": "No bookmark with this id."}, **ERROR_422},
)
def delete_bookmark(
    bookmark_id: Annotated[int, Path(ge=1, description="The bookmark's id.")], session: SessionDep
) -> Response:
    repository.delete_bookmark(session, bookmark_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
