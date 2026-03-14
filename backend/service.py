import json
import os
from uuid import uuid4
from typing import Optional

from orm import Textlite
from config import settings

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone


def get_current_time(test_now_ms: Optional[int] = None) -> datetime:
    """Get current time, respecting TEST_MODE with x-test-now-ms header."""
    if test_now_ms is not None:
        return datetime.fromtimestamp(test_now_ms / 1000.0, tz=timezone.utc)
    return datetime.now(timezone.utc)


class PasteService:
    """Service for paste operations."""

    BASE_URL = settings.FRONTEND_URL

    @staticmethod
    def _generate_paste_id() -> str:
        """Generate a random paste ID."""
        return str(uuid4())[:8]

    @staticmethod
    def generate_url(paste_id: str) -> str:
        """Generate the full shareable URL."""
        return f"{PasteService.BASE_URL}/p/{paste_id}"

    async def create_paste(
        self,
        content: str,
        ttl_seconds: Optional[int],
        max_views: Optional[int],
        session: AsyncSession,
        test_now_ms: Optional[int] = None,
    ) -> dict:
        """
        Create a new paste.

        Args:
            content: The paste content (non-empty string)
            ttl_seconds: Time-to-live in seconds (optional, must be ≥ 1)
            max_views: Maximum number of views (optional, must be ≥ 1)
            session: AsyncSession for database operations
            test_now_ms: Milliseconds since epoch for TEST_MODE (optional)

        Returns:
            Dictionary with id and url
        """
        paste_id = self._generate_paste_id()

        # Ensure paste_id is unique (retry if collision)
        existing = await session.scalar(
            select(Textlite).where(Textlite.public_id == paste_id)
        )
        if existing:
            # Retry with a new ID
            return await self.create_paste(content, ttl_seconds, max_views, session, test_now_ms)

        # Calculate expiration time if ttl_seconds is provided
        current_time = get_current_time(test_now_ms)
        expires_at = None
        if ttl_seconds is not None:
            expires_at = current_time + timedelta(seconds=ttl_seconds)

        paste = Textlite(
            id=str(uuid4()),
            json_content={"content": content},
            public_id=paste_id,
            expires_at=expires_at,
            max_views=max_views,
            view_count=0,
        )
        session.add(paste)
        await session.commit()
        await session.refresh(paste)

        return {
            "id": paste.public_id,
            "url": self.generate_url(paste.public_id),
        }

    async def get_paste(
        self,
        paste_id: str,
        session: AsyncSession,
        test_now_ms: Optional[int] = None,
        increment_view: bool = False,
    ) -> Optional[dict]:
        """
        Retrieve a paste by its ID.

        Args:
            paste_id: The paste ID
            session: AsyncSession for database operations
            test_now_ms: Milliseconds since epoch for TEST_MODE (optional)
            increment_view: Whether to increment the view count

        Returns:
            Dictionary with content, remaining_views, expires_at, or None if unavailable
        """
        paste = await session.scalar(
            select(Textlite).where(Textlite.public_id == paste_id)
        )

        if paste is None:
            return None

        current_time = get_current_time(test_now_ms)

        # Check if expired
        if paste.expires_at is not None and current_time >= paste.expires_at:
            return None

        # Check if view limit exceeded
        if paste.max_views is not None and paste.view_count >= paste.max_views:
            return None

        # Increment view count if requested
        if increment_view:
            paste.view_count += 1
            await session.commit()
            await session.refresh(paste)

        # Calculate remaining_views
        remaining_views = None
        if paste.max_views is not None:
            remaining_views = max(0, paste.max_views - paste.view_count)

        return {
            "content": paste.json_content.get("content", ""),
            "remaining_views": remaining_views,
            "expires_at": paste.expires_at.isoformat() if paste.expires_at else None,
        }

    async def cleanup_expired_pastes(self, session: AsyncSession) -> int:
        """
        Delete all expired pastes.

        Returns:
            Number of pastes deleted
        """
        now = datetime.now(timezone.utc)
        stmt = delete(Textlite).where(Textlite.expires_at <= now)
        result = await session.execute(stmt)
        await session.commit()

        return result.rowcount


# Global instance
paste_service = PasteService()
