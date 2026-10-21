"""Configuration read from the environment.

Defaults match .env.example and the docker-compose.yml database, so local development works
without exporting anything.
"""

import os

DEFAULT_DATABASE_URL = "postgresql://bookmarks:bookmarks@localhost:5432/bookmarks"


def sqlalchemy_url(url: str) -> str:
    """Make SQLAlchemy use the psycopg 3 driver for plain postgresql:// URLs."""
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


def database_url() -> str:
    return sqlalchemy_url(os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL))
