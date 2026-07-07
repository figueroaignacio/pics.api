import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.utils.slugify import slugify


class _CategoryBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class CategoryCreate(_CategoryBase):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Category name (1–100 characters). Must be unique.",
        examples=["Friends"],
    )
    slug: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="URL-safe slug. Auto-generated from 'name' if omitted. Must be unique.",
        examples=["friends"],
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Optional description of the category.",
        examples=["Photos with friends and people I love."],
    )

    @field_validator("slug")
    @classmethod
    def normalise_slug(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return slugify(v)

    @model_validator(mode="after")
    def auto_generate_slug(self) -> "CategoryCreate":
        if not self.slug:
            self.slug = slugify(self.name)
        return self


class CategoryUpdate(_CategoryBase):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="New category name.",
        examples=["Best Friends"],
    )
    slug: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="New slug. If omitted when 'name' is provided, slug is regenerated.",
        examples=["best-friends"],
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="New description.",
    )

    @field_validator("slug")
    @classmethod
    def normalise_slug(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return slugify(v)

    @model_validator(mode="after")
    def check_payload(self) -> "CategoryUpdate":
        if not self.model_dump(exclude_none=True):
            raise ValueError("At least one field must be provided for update.")
        if self.name and not self.slug:
            self.slug = slugify(self.name)
        return self


class CategorySummary(_CategoryBase):
    id: uuid.UUID
    name: str
    slug: str


class CategoryResponse(_CategoryBase):
    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class CategoryListResponse(_CategoryBase):
    items: list[CategoryResponse] = Field(description="All categories.")
    total: int = Field(description="Total number of categories.", examples=[15])
