"""Add categories table and migrate photos.category string → category_id FK.

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-07
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | None = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. Create categories table
    # ------------------------------------------------------------------
    op.create_table(
        "categories",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
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
        sa.UniqueConstraint("name", name="uq_categories_name"),
        sa.UniqueConstraint("slug", name="uq_categories_slug"),
    )
    op.create_index("ix_categories_slug", "categories", ["slug"])

    # ------------------------------------------------------------------
    # 2. Drop the old plain-text category column from photos
    # ------------------------------------------------------------------
    op.drop_index("ix_photos_category", table_name="photos")
    op.drop_column("photos", "category")

    # ------------------------------------------------------------------
    # 3. Add category_id FK column (nullable during transition, NOT NULL after seed)
    # ------------------------------------------------------------------
    op.add_column(
        "photos",
        sa.Column(
            "category_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,  # temporarily nullable; 0004 seeds then drops nullability
        ),
    )
    op.create_foreign_key(
        "fk_photos_category_id",
        "photos",
        "categories",
        ["category_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_photos_category_id", "photos", ["category_id"])


def downgrade() -> None:
    op.drop_index("ix_photos_category_id", table_name="photos")
    op.drop_constraint("fk_photos_category_id", "photos", type_="foreignkey")
    op.drop_column("photos", "category_id")

    op.add_column(
        "photos",
        sa.Column("category", sa.String(100), nullable=False, server_default="uncategorized"),
    )
    op.create_index("ix_photos_category", "photos", ["category"])

    op.drop_index("ix_categories_slug", table_name="categories")
    op.drop_table("categories")
