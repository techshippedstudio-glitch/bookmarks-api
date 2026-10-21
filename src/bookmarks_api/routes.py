"""HTTP endpoints for /bookmarks."""

from fastapi import APIRouter

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])
