"""Create the bookmarks table.

Revision ID: 0001
Revises:
Create Date: 2026-10-21
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "bookmarks",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("url", sa.String(2048), nullable=False),
        sa.Column("url_normalized", sa.String(2048), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column(
            "tags",
            postgresql.ARRAY(sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint("char_length(title) >= 1", name="ck_bookmarks_title_not_empty"),
        sa.CheckConstraint("cardinality(tags) <= 10", name="ck_bookmarks_max_10_tags"),
    )
    op.create_index("uq_bookmarks_url_normalized", "bookmarks", ["url_normalized"], unique=True)
    op.create_index(
        "ix_bookmarks_created_at_id",
        "bookmarks",
        [sa.text("created_at DESC"), sa.text("id DESC")],
    )
    op.create_index("ix_bookmarks_tags", "bookmarks", ["tags"], postgresql_using="gin")


def downgrade() -> None:
    op.drop_table("bookmarks")
