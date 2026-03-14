import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware


from database import db_manager
from background_tasks import background_task_runner

from routes import router as api_router
from config import settings

import logging

logger = logging.getLogger(__name__)


async def startup_event():
    """Initialize resources on startup."""
    logger.info("Initializing application resources...")

    # Startup: Initialize database components
    await db_manager.initialize()



async def shutdown_event():
    """Cleanup resources on shutdown."""
    logger.info("Shutting down application...")

    await db_manager.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup and shutdown events."""
    # Startup event
    await startup_event()

    # Start background cleanup tasks (runs every 24 hours)
    cleanup_task = asyncio.create_task(
        background_task_runner.run_cleanup_loop(interval_hours=24)
    )

    yield

    # Shutdown event
    await background_task_runner.stop()
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass

    await shutdown_event()


app = FastAPI(title="Pastebin-lite", lifespan=lifespan)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers with /api prefix
app.include_router(api_router, prefix="/api", tags=["api"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

