"""FastAPI application."""

from fastapi import FastAPI

from bookmarks_api.errors import install_error_handlers
from bookmarks_api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Bookmarks API",
        version="0.1.0",
        description="Save, list, filter and delete bookmarks.",
    )
    install_error_handlers(app)
    app.include_router(router)
    return app


app = create_app()
