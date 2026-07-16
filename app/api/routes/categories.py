import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.responses import success_response
from app.dependencies.database import get_db
from app.schemas.category import (
    CategoryCreate,
    CategoryListResponse,
    CategoryResponse,
    CategoryUpdate,
)
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


def get_service(session: DbDep) -> CategoryService:
    return CategoryService(session)


ServiceDep = Annotated[CategoryService, Depends(get_service)]


@router.get(
    "",
    response_model=None,
    summary="List Categories",
    description="Retrieve all categories ordered alphabetically.",
    status_code=status.HTTP_200_OK,
)
async def list_categories(service: ServiceDep):
    result: CategoryListResponse = await service.list_categories()
    return success_response(
        data=result.model_dump(mode="json"),
        message="Categories retrieved successfully.",
    )


@router.get(
    "/slug/{slug}",
    response_model=None,
    summary="Get Category by Slug",
    description="Retrieve a single category by its URL slug.",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Category found."},
        404: {"description": "Category not found."},
    },
)
async def get_category_by_slug(slug: str, service: ServiceDep):
    category: CategoryResponse = await service.get_category_by_slug(slug)
    return success_response(
        data=category.model_dump(mode="json"),
        message="Category retrieved successfully.",
    )


@router.get(
    "/{category_id}",
    response_model=None,
    summary="Get Category",
    description="Retrieve a single category by its UUID.",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Category found."},
        404: {"description": "Category not found."},
    },
)
async def get_category(category_id: uuid.UUID, service: ServiceDep):
    category: CategoryResponse = await service.get_category(category_id)
    return success_response(
        data=category.model_dump(mode="json"),
        message="Category retrieved successfully.",
    )


@router.post(
    "",
    response_model=None,
    summary="Create Category",
    description=(
        "Create a new category. The slug is auto-generated from the name if not provided. "
        "Both name and slug must be unique."
    ),
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Category created."},
        409: {"description": "Name or slug already exists."},
        422: {"description": "Validation error."},
    },
)
async def create_category(payload: CategoryCreate, service: ServiceDep):
    category: CategoryResponse = await service.create_category(payload)
    return success_response(
        data=category.model_dump(mode="json"),
        message="Category created successfully.",
        status_code=status.HTTP_201_CREATED,
    )


@router.patch(
    "/{category_id}",
    response_model=None,
    summary="Update Category",
    description="Partially update a category. Slug is regenerated from name if name changes.",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Category updated."},
        404: {"description": "Category not found."},
        409: {"description": "Name or slug conflict."},
        422: {"description": "Validation error."},
    },
)
async def update_category(
    category_id: uuid.UUID, payload: CategoryUpdate, service: ServiceDep
):
    category: CategoryResponse = await service.update_category(category_id, payload)
    return success_response(
        data=category.model_dump(mode="json"),
        message="Category updated successfully.",
    )


@router.delete(
    "/{category_id}",
    response_model=None,
    summary="Delete Category",
    description=(
        "Delete a category. Returns 409 if any photos still reference this category — "
        "reassign or delete those photos first."
    ),
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Category deleted."},
        404: {"description": "Category not found."},
        409: {"description": "Category has photos — cannot delete."},
    },
)
async def delete_category(category_id: uuid.UUID, service: ServiceDep):
    await service.delete_category(category_id)
    return success_response(message="Category deleted successfully.")
