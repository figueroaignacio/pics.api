"""Models package — re-export all models so Alembic can discover them."""

from app.models.category import Category
from app.models.photo import Photo

__all__ = ["Category", "Photo"]
