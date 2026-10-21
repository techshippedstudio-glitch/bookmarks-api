"""HTTP endpoints for /bookmarks."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status
from pydantic import AfterValidator
from sqlalchemy.orm import Session

from bookmarks_api import repository
from bookmarks_api.db import get_session
from bookmarks_api.errors import ErrorResponse
from bookmarks_api.normalize import normalize_tag
from bookmarks_api.schemas import Bookmark, BookmarkCreate, BookmarkPage

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])

SessionDep = Annotated[Session, Depends(get_session)]

ERROR_422 = {422: {"model": ErrorResponse, "description": "The request is not valid."}}


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
)
def list_bookmarks(
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=100, description="Page size, 1 to 100.")] = 20,
    offset: Annotated[int, Query(ge=0, description="Number of bookmarks to skip.")] = 0,
    tag: Annotated[
        str | None,
        Query(description="Only bookmarks with this tag (normalized like tags)."),
        AfterValidator(lambda value: normalize_tag(value) if value is not None else None),
    ] = None,
) -> BookmarkPage:
    rows, total = repository.list_bookmarks(session, limit=limit, offset=offset, tag=tag)
    return BookmarkPage(
        items=[Bookmark.model_validate(row) for row in rows],
        total=total,
        limit=limit,
        offset=offset,
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
