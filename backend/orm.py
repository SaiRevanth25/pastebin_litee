from datetime import datetime
from collections.abc import AsyncIterator


from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, declarative_base, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from sqlalchemy import (
    TIMESTAMP,
    Index,
    Text,
    text,
)
Base = declarative_base()

class Textlite(Base):
    """ORM model for storing pastes with public links."""

    __tablename__ = "textlites"

    id: Mapped[str] = mapped_column(
        Text, primary_key=True, server_default=text("uuid_generate_v4()::text")
    )
    json_content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    public_id: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    max_views: Mapped[int | None] = mapped_column(nullable=True)
    view_count: Mapped[int] = mapped_column(default=0)

    __table_args__ = (
        Index("idx_textlite_public_id", "public_id", unique=True),
        Index("idx_textlite_created_at", "created_at"),
        Index("idx_textlite_expires_at", "expires_at"),
    )


# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------

async_session_maker: async_sessionmaker[AsyncSession] | None = None


def _get_session_maker() -> async_sessionmaker[AsyncSession]:
    """Return a cached async_sessionmaker bound to db_manager.engine."""
    global async_session_maker
    if async_session_maker is None:
        from database import db_manager

        engine = db_manager.get_engine()
        async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
    return async_session_maker


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency that yields an AsyncSession."""
    maker = _get_session_maker()
    async with maker() as session:
        yield session