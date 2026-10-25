"""HTTP endpoints for /bookmarks."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request, Response, status
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session

from bookmarks_api import repository
from bookmarks_api.cursor import decode_cursor, encode_cursor
from bookmarks_api.db import get_session
from bookmarks_api.errors import ErrorResponse
from bookmarks_api.schemas import Bookmark, BookmarkCreate, BookmarkListQuery, BookmarkPage

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])

SessionDep = Annotated[Session, Depends(get_session)]

ERROR_422 = {422: {"model": ErrorResponse, "description": "The request is not valid."}}

OFFSET_REMOVED = (
    "offset is not supported (Constitution VI); pass the previous page's next_cursor as cursor."
)


def reject_offset(request: Request) -> None:
    """Give a client that still sends the removed offset parameter a clear 422 (not in the schema)."""
    if "offset" in request.query_params:
        raise RequestValidationError(
            [
                {
                    "type": "value_error",
                    "loc": ("query", "offset"),
                    "msg": f"Value error, {OFFSET_REMOVED}",
                    "input": request.query_params["offset"],
                }
            ]
        )

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=Bookmark,
    summary="Save a bookmark",
    responses={
        409: {"model": ErrorResponse, "description": "This link is already bookmarked."},
        **ERROR_422,
    },
)
def create_bookmark(data: BookmarkCreate, session: SessionDep) -> Bookmark:
    return Bookmark.model_validate(repository.create_bookmark(session, data))


@router.get(
    "",
    response_model=BookmarkPage,
    summary="List bookmarks, newest first",
    responses=ERROR_422,
    dependencies=[Depends(reject_offset)],
)
def list_bookmarks(
    session: SessionDep,
    query: Annotated[BookmarkListQuery, Query()],
) -> BookmarkPage:
    after = decode_cursor(query.cursor) if query.cursor is not None else None
    rows, total, has_more = repository.list_bookmarks(
        session, limit=query.limit, after=after, tag=query.tag
    )
    next_cursor = encode_cursor(rows[-1].created_at, rows[-1].id) if has_more else None
    return BookmarkPage(
        items=[Bookmark.model_validate(row) for row in rows],
        total=total,
        limit=query.limit,
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
