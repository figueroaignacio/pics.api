"""Initial migration — create photos table.

Revision ID: 0001
Revises: —
Create Date: 2026-07-07
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "photos",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("cloudflare_image_id", sa.String(255), nullable=False),
        sa.Column("image_url", sa.String(2048), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("spotify_url", sa.String(2048), nullable=True),
        sa.Column("taken_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column(
            "favorite",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # Indexes
    op.create_index("ix_photos_title", "photos", ["title"])
    op.create_index("ix_photos_category", "photos", ["category"])
    op.create_unique_constraint(
        "uq_photos_cloudflare_image_id", "photos", ["cloudflare_image_id"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_photos_cloudflare_image_id", "photos", type_="unique")
    op.drop_index("ix_photos_category", table_name="photos")
    op.drop_index("ix_photos_title", table_name="photos")
    op.drop_table("photos")
