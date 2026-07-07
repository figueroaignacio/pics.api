from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def create_engine() -> AsyncEngine:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.is_development,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_recycle=300,
    )
    logger.info("Database engine created (env=%s)", settings.APP_ENV)
    return engine


engine: AsyncEngine = create_engine()
