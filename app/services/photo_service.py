import math
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import CategoryNotFoundError, PhotoNotFoundError
from app.core.logging import get_logger
from app.repositories.category_repository import CategoryRepository
from app.repositories.photo_repository import (
    PhotoFilters,
    PhotoPagination,
    PhotoRepository,
)
from app.schemas.photo import (
    PhotoCreate,
    PhotoListResponse,
    PhotoResponse,
    PhotoUpdate,
)

logger = get_logger(__name__)


class PhotoService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = PhotoRepository(session)
        self._category_repo = CategoryRepository(session)

    async def get_photo(self, photo_id: uuid.UUID) -> PhotoResponse:
        photo = await self._repo.get_by_id(photo_id)
        if photo is None:
            raise PhotoNotFoundError(photo_id)
        logger.debug("Photo retrieved: id=%s", photo_id)
        return PhotoResponse.model_validate(photo)

    async def list_photos(
        self,
        *,
        page: int,
        size: int,
        category_slug: str | None,
        favorite: bool | None,
        search: str | None,
    ) -> PhotoListResponse:
        filters = PhotoFilters(
            category_slug=category_slug,
            favorite=favorite,
            search=search,
        )
        pagination = PhotoPagination(page=page, size=size)

        photos, total = await self._repo.get_all(filters, pagination)
        pages = max(1, math.ceil(total / size)) if total > 0 else 1

        logger.debug("Photos listed: page=%d size=%d total=%d", page, size, total)

        return PhotoListResponse(
            items=[PhotoResponse.model_validate(p) for p in photos],
            total=total,
            page=page,
            size=size,
            pages=pages,
        )

    async def create_photo(self, payload: PhotoCreate) -> PhotoResponse:
        category = await self._category_repo.get_by_id(payload.category_id)
        if category is None:
            raise CategoryNotFoundError(payload.category_id)

        data = payload.model_dump()
        photo = await self._repo.create(data)
        logger.info("Photo created: id=%s title=%r", photo.id, photo.title)
        return PhotoResponse.model_validate(photo)

    async def update_photo(
        self, photo_id: uuid.UUID, payload: PhotoUpdate
    ) -> PhotoResponse:
        photo = await self._repo.get_by_id(photo_id)
        if photo is None:
            raise PhotoNotFoundError(photo_id)

        data = payload.model_dump(exclude_none=True)

        if "category_id" in data:
            category = await self._category_repo.get_by_id(data["category_id"])
            if category is None:
                raise CategoryNotFoundError(data["category_id"])

        updated = await self._repo.update(photo, data)
        logger.info("Photo updated: id=%s fields=%s", photo_id, list(data.keys()))
        return PhotoResponse.model_validate(updated)

    async def delete_photo(self, photo_id: uuid.UUID) -> None:
        photo = await self._repo.get_by_id(photo_id)
        if photo is None:
            raise PhotoNotFoundError(photo_id)
        await self._repo.delete(photo)
        logger.info("Photo deleted: id=%s", photo_id)
