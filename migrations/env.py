"""Alembic environment: runs migrations against DATABASE_URL (or an explicit override)."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from bookmarks_api.config import database_url, sqlalchemy_url
from bookmarks_api.models import Base

config = context.config

if config.config_file_name is not None and config.attributes.get("configure_logging", True):
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def resolve_url() -> str:
    override = context.get_x_argument(as_dictionary=True).get("url") or config.get_main_option(
        "sqlalchemy.url"
    )
    return sqlalchemy_url(override) if override else database_url()


def run_migrations_offline() -> None:
    context.configure(url=resolve_url(), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(resolve_url(), poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
