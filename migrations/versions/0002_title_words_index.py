"""Add a GIN index on the words of each bookmark title (specs/002-bookmark-title-search).

The expression must stay identical to bookmarks_api.models.title_words so search queries use it.

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-25
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

TITLE_WORDS = "array_remove(regexp_split_to_array(lower(title), '[^[:alnum:]]+'), '')"


def upgrade() -> None:
    op.create_index(
        "ix_bookmarks_title_words",
        "bookmarks",
        [sa.text(TITLE_WORDS)],
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index("ix_bookmarks_title_words", table_name="bookmarks")
