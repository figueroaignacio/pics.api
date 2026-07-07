import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.category import CategorySummary

_SPOTIFY_PATTERN = re.compile(
    r"^https://open\.spotify\.com/(track|album|playlist|artist)/[A-Za-z0-9]+(\?.*)?$"
)

_URL_PATTERN = re.compile(
    r"^https?://"
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
    r"localhost|\d{1,3}(?:\.\d{1,3}){3})"
    r"(?::\d+)?"
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)


def _validate_url(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    if not _URL_PATTERN.match(value):
        raise ValueError(f"'{field_name}' must be a valid HTTP/HTTPS URL.")
    return value


class _PhotoBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class PhotoCreate(_PhotoBase):
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Photo title (1–200 characters).",
        examples=["Golden Hour at Patagonia"],
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
        description="Optional description of the photo.",
        examples=["Sunset over Torres del Paine."],
    )
    r2_object_key: str = Field(
        ...,
        min_length=1,
        max_length=1024,
        description="Object key (path) of the file inside the R2 bucket.",
        examples=["photos/2024/patagonia.jpg"],
    )
    image_url: str = Field(
        ...,
        max_length=2048,
        description="Public delivery URL for the image.",
        examples=["https://pub-xxxxxxxxxxxxxxxx.r2.dev/photos/2024/patagonia.jpg"],
    )
    category_id: uuid.UUID = Field(
        ...,
        description="UUID of the category this photo belongs to.",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"],
    )
    spotify_url: str | None = Field(
        default=None,
        max_length=2048,
        description="Optional Spotify track/album/playlist URL.",
        examples=["https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT"],
    )
    taken_at: datetime | None = Field(
        default=None,
        description="Date and time the photo was taken (ISO 8601).",
        examples=["2024-06-15T18:30:00Z"],
    )
    location: str | None = Field(
        default=None,
        max_length=255,
        description="Optional location description.",
        examples=["Torres del Paine, Chile"],
    )
    favorite: bool = Field(
        default=False,
        description="Mark this photo as a favourite.",
        examples=[False],
    )

    @field_validator("image_url")
    @classmethod
    def validate_image_url(cls, v: str) -> str:
        result = _validate_url(v, "image_url")
        assert result is not None
        return result

    @field_validator("spotify_url")
    @classmethod
    def validate_spotify_url(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if not _SPOTIFY_PATTERN.match(v):
            raise ValueError(
                "spotify_url must be a valid Spotify URL "
                "(e.g. https://open.spotify.com/track/...)."
            )
        return v


class PhotoUpdate(_PhotoBase):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="New title.",
        examples=["Blue Hour — Atacama"],
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
        description="New description.",
    )
    category_id: uuid.UUID | None = Field(
        default=None,
        description="New category UUID.",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"],
    )
    spotify_url: str | None = Field(
        default=None,
        max_length=2048,
        description="New or updated Spotify URL.",
    )
    taken_at: datetime | None = Field(
        default=None,
        description="New capture date/time.",
    )
    location: str | None = Field(
        default=None,
        max_length=255,
        description="New location.",
    )
    favorite: bool | None = Field(
        default=None,
        description="Toggle favourite status.",
    )

    @field_validator("spotify_url")
    @classmethod
    def validate_spotify_url(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if not _SPOTIFY_PATTERN.match(v):
            raise ValueError(
                "spotify_url must be a valid Spotify URL "
                "(e.g. https://open.spotify.com/track/...)."
            )
        return v

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "PhotoUpdate":
        values = self.model_dump(exclude_none=True)
        if not values:
            raise ValueError("At least one field must be provided for update.")
        return self


class PhotoResponse(_PhotoBase):
    id: uuid.UUID
    title: str
    description: str | None
    r2_object_key: str
    image_url: str
    category: CategorySummary
    spotify_url: str | None
    taken_at: datetime | None
    location: str | None
    favorite: bool
    created_at: datetime
    updated_at: datetime


class PhotoListResponse(_PhotoBase):
    items: list[PhotoResponse] = Field(description="Photos on the current page.")
    total: int = Field(description="Total number of matching photos.", examples=[42])
    page: int = Field(description="Current page number (1-indexed).", examples=[1])
    size: int = Field(description="Number of items per page.", examples=[20])
    pages: int = Field(description="Total number of pages.", examples=[3])
