"""Seed default categories and make photos.category_id NOT NULL.

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-07
"""

import uuid
from datetime import datetime

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | None = None


DEFAULT_CATEGORIES = [
    "Random",
    "Memories",
    "Friends",
    "Family",
    "Pets",
    "Food",
    "Travel",
    "Nature",
    "City",
    "Sunsets",
    "Night",
    "Gaming",
    "Coffee",
    "Work",
    "Events",
]


def _slugify(text: str) -> str:
    """Inline slugify — avoids importing app code during migrations."""
    import re
    import unicodedata

    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")


def upgrade() -> None:
    conn = op.get_bind()

    for name in DEFAULT_CATEGORIES:
        slug = _slugify(name)
        # Skip if name or slug already exists (idempotent)
        existing = conn.execute(
            sa.text(
                "SELECT id FROM categories WHERE name = :name OR slug = :slug LIMIT 1"
            ),
            {"name": name, "slug": slug},
        ).first()

        if existing is None:
            conn.execute(
                sa.text(
                    """
                    INSERT INTO categories (id, name, slug, created_at, updated_at)
                    VALUES (
                        gen_random_uuid(),
                        :name,
                        :slug,
                        now(),
                        now()
                    )
                    """
                ),
                {"name": name, "slug": slug},
            )

    # Make category_id NOT NULL (safe: photos table is empty at this point)
    op.alter_column("photos", "category_id", nullable=False)



def downgrade() -> None:
    # Make category_id nullable again
    op.alter_column("photos", "category_id", nullable=True)

    # Remove seeded categories (only those that match seed names)
    conn = op.get_bind()
    names = [f"'{n}'" for n in DEFAULT_CATEGORIES]
    conn.execute(
        sa.text(f"DELETE FROM categories WHERE name IN ({', '.join(names)})")
    )
