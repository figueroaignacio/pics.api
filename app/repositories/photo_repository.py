import uuid
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.photo import Photo


@dataclass(frozen=True)
class PhotoFilters:
    category_slug: str | None = None
    favorite: bool | None = None
    search: str | None = None


@dataclass(frozen=True)
class PhotoPagination:
    page: int = 1
    size: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class PhotoRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, photo_id: uuid.UUID) -> Photo | None:
        result = await self._session.execute(select(Photo).where(Photo.id == photo_id))
        return result.scalar_one_or_none()

    async def get_all(
        self,
        filters: PhotoFilters,
        pagination: PhotoPagination,
    ) -> tuple[list[Photo], int]:
        base_query = select(Photo)

        if filters.category_slug is not None:
            base_query = base_query.join(
                Category, Photo.category_id == Category.id
            ).where(Category.slug == filters.category_slug)

        if filters.favorite is not None:
            base_query = base_query.where(Photo.favorite == filters.favorite)

        if filters.search is not None:
            base_query = base_query.where(Photo.title.ilike(f"%{filters.search}%"))

        count_result = await self._session.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total: int = count_result.scalar_one()

        paginated_query = (
            base_query.order_by(Photo.created_at.desc())
            .limit(pagination.size)
            .offset(pagination.offset)
        )
        result = await self._session.execute(paginated_query)
        photos = list(result.scalars().all())

        return photos, total

    async def create(self, data: dict) -> Photo:
        photo = Photo(**data)
        self._session.add(photo)
        await self._session.flush()
        await self._session.refresh(photo)
        return photo

    async def update(self, photo: Photo, data: dict) -> Photo:
        for key, value in data.items():
            setattr(photo, key, value)
        self._session.add(photo)
        await self._session.flush()
        await self._session.refresh(photo)
        return photo

    async def delete(self, photo: Photo) -> None:
        await self._session.delete(photo)
        await self._session.flush()
