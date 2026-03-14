import asyncio
from datetime import datetime, timezone

import structlog
from orm import _get_session_maker
from service import paste_service

logger = structlog.get_logger(__name__)


class BackgroundTaskRunner:
    """Runner for background maintenance tasks."""

    def __init__(self):
        self.is_running = False

    async def cleanup_expired_pastes(self):
        """
        Periodically clean up expired pastes.
        """
        try:
            session_maker = _get_session_maker()
            async with session_maker() as session:
                deleted_count = await paste_service.cleanup_expired_pastes(session)
                logger.info(
                    f"[background_tasks] Cleaned up {deleted_count} expired pastes"
                )
        except Exception as e:
            logger.exception(
                f"[background_tasks] Error during paste cleanup: {e}"
            )

    async def run_cleanup_loop(self, interval_hours: int = 24):
        """
        Run all cleanup tasks in a loop.

        Args:
            interval_hours: How often to run cleanups (default: 24 hours/1 day)
        """
        self.is_running = True
        logger.info(
            f"[background_tasks] Starting cleanup tasks (runs every {interval_hours} hours)"
        )

        # Run cleanups immediately on startup
        await self.cleanup_expired_pastes()

        # Then run periodically
        while self.is_running:
            try:
                await asyncio.sleep(interval_hours * 3600)  # Convert hours to seconds
                await self.cleanup_expired_pastes()
            except asyncio.CancelledError:
                logger.info("[background_tasks] Cleanup tasks cancelled")
                self.is_running = False
                break
            except Exception as e:
                logger.exception(f"[background_tasks] Unexpected error in cleanup loop: {e}")
                # Continue running despite errors
                await asyncio.sleep(60)  # Wait 1 minute before retrying

    async def stop(self):
        """Stop all background tasks."""
        self.is_running = False
        logger.info("[background_tasks] Stopping background tasks")


# Global instance
background_task_runner = BackgroundTaskRunner()
