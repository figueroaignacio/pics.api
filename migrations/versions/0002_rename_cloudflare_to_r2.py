"""Rename cloudflare_image_id → r2_object_key, resize to 1024 chars.

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-07
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | None = None


def upgrade() -> None:
    # Rename column
    op.alter_column(
        "photos",
        "cloudflare_image_id",
        new_column_name="r2_object_key",
        existing_type=sa.String(255),
        type_=sa.String(1024),
        existing_nullable=False,
    )

    # Rename the unique constraint to match the new column name
    op.drop_constraint("uq_photos_cloudflare_image_id", "photos", type_="unique")
    op.create_unique_constraint("uq_photos_r2_object_key", "photos", ["r2_object_key"])


def downgrade() -> None:
    op.drop_constraint("uq_photos_r2_object_key", "photos", type_="unique")
    op.alter_column(
        "photos",
        "r2_object_key",
        new_column_name="cloudflare_image_id",
        existing_type=sa.String(1024),
        type_=sa.String(255),
        existing_nullable=False,
    )
    op.create_unique_constraint(
        "uq_photos_cloudflare_image_id", "photos", ["cloudflare_image_id"]
    )
