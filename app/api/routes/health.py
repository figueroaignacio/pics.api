from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="Health Check",
    description="Returns the operational status of the API.",
    response_description="API is healthy.",
)
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
