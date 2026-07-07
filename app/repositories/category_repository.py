import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category


class CategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, category_id: uuid.UUID) -> Category | None:
        result = await self._session.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Category | None:
        result = await self._session.execute(
            select(Category).where(Category.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Category | None:
        result = await self._session.execute(
            select(Category).where(Category.name == name)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Category]:
        result = await self._session.execute(
            select(Category).order_by(Category.name.asc())
        )
        return list(result.scalars().all())

    async def count_photos(self, category_id: uuid.UUID) -> int:
        from app.models.photo import Photo

        result = await self._session.execute(
            select(func.count()).where(Photo.category_id == category_id)
        )
        return result.scalar_one()

    async def create(self, data: dict) -> Category:
        category = Category(**data)
        self._session.add(category)
        await self._session.flush()
        await self._session.refresh(category)
        return category

    async def update(self, category: Category, data: dict) -> Category:
        for key, value in data.items():
            setattr(category, key, value)
        self._session.add(category)
        await self._session.flush()
        await self._session.refresh(category)
        return category

    async def delete(self, category: Category) -> None:
        await self._session.delete(category)
        await self._session.flush()
