"""Test setup: a real PostgreSQL test database, migrated once and emptied before each test.

Constitution II: no database mocks. Set TEST_DATABASE_URL to point at another database.
"""

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from bookmarks_api.config import sqlalchemy_url
from bookmarks_api.db import get_session
from bookmarks_api.main import create_app

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TEST_DATABASE_URL = "postgresql://bookmarks:bookmarks@localhost:5432/bookmarks_test"
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", DEFAULT_TEST_DATABASE_URL)


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    config.attributes["configure_logging"] = False
    command.upgrade(config, "head")
    engine = create_engine(sqlalchemy_url(TEST_DATABASE_URL))
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)


@pytest.fixture
def clean_database(engine: Engine) -> None:
    """Empty the table. Integration tests use it automatically (tests/integration/conftest.py)."""
    with engine.begin() as connection:
        connection.execute(text("TRUNCATE bookmarks RESTART IDENTITY"))


@pytest.fixture
def client(session_factory: sessionmaker[Session]) -> Iterator[TestClient]:
    app = create_app()

    def override_session() -> Iterator[Session]:
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_session
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.fixture
def row_count(engine: Engine):
    def count() -> int:
        with engine.connect() as connection:
            return connection.execute(text("SELECT count(*) FROM bookmarks")).scalar_one()

    return count
