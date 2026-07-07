import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.responses import success_response
from app.dependencies.database import get_db
from app.dependencies.pagination import PaginationParams
from app.schemas.photo import PhotoCreate, PhotoListResponse, PhotoResponse, PhotoUpdate
from app.services.photo_service import PhotoService

router = APIRouter(prefix="/photos", tags=["Photos"])

DbDep = Annotated[AsyncSession, Depends(get_db)]
PaginationDep = Annotated[PaginationParams, Depends()]


def get_service(session: DbDep) -> PhotoService:
    return PhotoService(session)


ServiceDep = Annotated[PhotoService, Depends(get_service)]


@router.get(
    "",
    response_model=None,
    summary="List Photos",
    description=(
        "Retrieve a paginated list of photos. Supports filtering by category, "
        "favourite status, and a free-text title search."
    ),
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Paginated list of photos.",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Photos retrieved successfully.",
                        "data": {
                            "items": [],
                            "total": 0,
                            "page": 1,
                            "size": 20,
                            "pages": 1,
                        },
                    }
                }
            },
        }
    },
)
async def list_photos(
    service: ServiceDep,
    pagination: PaginationDep,
    category: str | None = Query(
        default=None,
        description="Filter by category slug (e.g. 'friends', 'travel').",
        examples=["travel"],
    ),
    favorite: bool | None = Query(
        default=None,
        description="Filter by favourite status.",
        examples=[True],
    ),
    search: str | None = Query(
        default=None,
        description="Search photos by title (case-insensitive partial match).",
        examples=["patagonia"],
    ),
):
    result: PhotoListResponse = await service.list_photos(
        page=pagination.page,
        size=pagination.size,
        category_slug=category,
        favorite=favorite,
        search=search,
    )
    return success_response(
        data=result.model_dump(),
        message="Photos retrieved successfully.",
    )


@router.get(
    "/{photo_id}",
    response_model=None,
    summary="Get Photo",
    description="Retrieve a single photo by its UUID.",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Photo found."},
        404: {"description": "Photo not found."},
    },
)
async def get_photo(photo_id: uuid.UUID, service: ServiceDep):
    photo: PhotoResponse = await service.get_photo(photo_id)
    return success_response(
        data=photo.model_dump(mode="json"),
        message="Photo retrieved successfully.",
    )


@router.post(
    "",
    response_model=None,
    summary="Create Photo",
    description=(
        "Create a new photo record. The image must have already been uploaded to R2. "
        "Provide the resulting r2_object_key and image_url."
    ),
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Photo created."},
        422: {"description": "Validation error."},
    },
)
async def create_photo(payload: PhotoCreate, service: ServiceDep):
    photo: PhotoResponse = await service.create_photo(payload)
    return success_response(
        data=photo.model_dump(mode="json"),
        message="Photo created successfully.",
        status_code=status.HTTP_201_CREATED,
    )


@router.patch(
    "/{photo_id}",
    response_model=None,
    summary="Update Photo",
    description="Partially update one or more fields of an existing photo.",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Photo updated."},
        404: {"description": "Photo not found."},
        422: {"description": "Validation error."},
    },
)
async def update_photo(
    photo_id: uuid.UUID, payload: PhotoUpdate, service: ServiceDep
):
    photo: PhotoResponse = await service.update_photo(photo_id, payload)
    return success_response(
        data=photo.model_dump(mode="json"),
        message="Photo updated successfully.",
    )


@router.delete(
    "/{photo_id}",
    response_model=None,
    summary="Delete Photo",
    description="Permanently delete a photo record.",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Photo deleted."},
        404: {"description": "Photo not found."},
    },
)
async def delete_photo(photo_id: uuid.UUID, service: ServiceDep):
    await service.delete_photo(photo_id)
    return success_response(message="Photo deleted successfully.")
