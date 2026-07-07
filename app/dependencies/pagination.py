from fastapi import Query

from app.core.config import settings


class PaginationParams:
    def __init__(
        self,
        page: int = Query(
            default=1,
            ge=1,
            description="Page number (1-indexed).",
            examples=[1],
        ),
        size: int = Query(
            default=settings.PAGINATION_DEFAULT_SIZE,
            ge=1,
            le=settings.PAGINATION_MAX_SIZE,
            description=f"Items per page (max {settings.PAGINATION_MAX_SIZE}).",
            examples=[20],
        ),
    ) -> None:
        self.page = page
        self.size = size
