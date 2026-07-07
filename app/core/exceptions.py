from uuid import UUID


class AppException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        errors: list[str] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.errors = errors or []
        super().__init__(message)


class PhotoNotFoundError(AppException):
    def __init__(self, photo_id: UUID) -> None:
        super().__init__(
            message=f"Photo with id '{photo_id}' was not found.",
            status_code=404,
        )


class PhotoValidationError(AppException):
    def __init__(self, message: str, errors: list[str] | None = None) -> None:
        super().__init__(message=message, status_code=422, errors=errors or [])


class CategoryNotFoundError(AppException):
    def __init__(self, identifier: str | UUID) -> None:
        super().__init__(
            message=f"Category '{identifier}' was not found.",
            status_code=404,
        )


class CategoryConflictError(AppException):
    def __init__(self, field: str, value: str) -> None:
        super().__init__(
            message=f"A category with {field} '{value}' already exists.",
            status_code=409,
        )


class CategoryHasPhotosError(AppException):
    def __init__(self, category_name: str, photo_count: int) -> None:
        super().__init__(
            message=(
                f"Cannot delete category '{category_name}': "
                f"it is referenced by {photo_count} photo(s). "
                "Reassign or delete the photos first."
            ),
            status_code=409,
        )


class R2Error(AppException):
    def __init__(self, message: str, errors: list[str] | None = None) -> None:
        super().__init__(
            message=f"R2 storage error: {message}",
            status_code=502,
            errors=errors or [],
        )


class DatabaseError(AppException):
    def __init__(self, message: str = "An unexpected database error occurred.") -> None:
        super().__init__(message=message, status_code=500)
