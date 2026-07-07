import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    CategoryConflictError,
    CategoryHasPhotosError,
    CategoryNotFoundError,
)
from app.core.logging import get_logger
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import (
    CategoryCreate,
    CategoryListResponse,
    CategoryResponse,
    CategoryUpdate,
)

logger = get_logger(__name__)


class CategoryService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = CategoryRepository(session)

    async def get_category(self, category_id: uuid.UUID) -> CategoryResponse:
        category = await self._repo.get_by_id(category_id)
        if category is None:
            raise CategoryNotFoundError(category_id)
        return CategoryResponse.model_validate(category)

    async def get_category_by_slug(self, slug: str) -> CategoryResponse:
        category = await self._repo.get_by_slug(slug)
        if category is None:
            raise CategoryNotFoundError(slug)
        return CategoryResponse.model_validate(category)

    async def list_categories(self) -> CategoryListResponse:
        categories = await self._repo.get_all()
        items = [CategoryResponse.model_validate(c) for c in categories]
        logger.debug("Categories listed: count=%d", len(items))
        return CategoryListResponse(items=items, total=len(items))

    async def create_category(self, payload: CategoryCreate) -> CategoryResponse:
        if await self._repo.get_by_name(payload.name):
            raise CategoryConflictError("name", payload.name)

        assert payload.slug is not None
        if await self._repo.get_by_slug(payload.slug):
            raise CategoryConflictError("slug", payload.slug)

        try:
            data = payload.model_dump()
            category = await self._repo.create(data)
        except IntegrityError as exc:
            raise CategoryConflictError("name or slug", payload.name) from exc

        logger.info("Category created: id=%s name=%r", category.id, category.name)
        return CategoryResponse.model_validate(category)

    async def update_category(
        self, category_id: uuid.UUID, payload: CategoryUpdate
    ) -> CategoryResponse:
        category = await self._repo.get_by_id(category_id)
        if category is None:
            raise CategoryNotFoundError(category_id)

        data = payload.model_dump(exclude_none=True)

        if "name" in data and data["name"] != category.name:
            if await self._repo.get_by_name(data["name"]):
                raise CategoryConflictError("name", data["name"])

        if "slug" in data and data["slug"] != category.slug:
            if await self._repo.get_by_slug(data["slug"]):
                raise CategoryConflictError("slug", data["slug"])

        try:
            updated = await self._repo.update(category, data)
        except IntegrityError as exc:
            raise CategoryConflictError("name or slug", category.name) from exc

        logger.info("Category updated: id=%s fields=%s", category_id, list(data.keys()))
        return CategoryResponse.model_validate(updated)

    async def delete_category(self, category_id: uuid.UUID) -> None:
        category = await self._repo.get_by_id(category_id)
        if category is None:
            raise CategoryNotFoundError(category_id)

        photo_count = await self._repo.count_photos(category_id)
        if photo_count > 0:
            raise CategoryHasPhotosError(category.name, photo_count)

        await self._repo.delete(category)
        logger.info("Category deleted: id=%s name=%r", category_id, category.name)
