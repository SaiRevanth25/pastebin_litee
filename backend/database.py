import structlog
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from config import settings

logger = structlog.get_logger(__name__)


class DatabaseManager:
    """Manages database connection lifecycle for SQLAlchemy."""

    def __init__(self) -> None:
        self.engine: AsyncEngine | None = None
        self._database_url = settings.DATABASE_URL.replace(
            "postgresql://", "postgresql+asyncpg://"
        )

    async def initialize(self) -> None:
        """Initialize the async SQLAlchemy engine."""
        self.engine = create_async_engine(
            self._database_url,
        )

        logger.info("Database engine initialized")

    async def close(self) -> None:
        """Close database connections."""
        if self.engine:
            await self.engine.dispose()

        logger.info("Database connections closed")

    def get_engine(self) -> AsyncEngine:
        """Get the SQLAlchemy engine."""
        if not self.engine:
            raise RuntimeError("Database not initialized")
        return self.engine


# Global database manager instance
db_manager = DatabaseManager()
