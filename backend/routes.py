import os
import structlog
from orm import get_session
from service import paste_service
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse

from model import (
    CreatePasteRequest,
    CreatePasteResponse,
    GetPasteResponse,
    HealthResponse,
)

router = APIRouter(tags=["pastes"])

logger = structlog.get_logger(__name__)


@router.get("/healthz", response_model=HealthResponse)
async def health_check(session: AsyncSession = Depends(get_session)):
    """
    Health check endpoint.
    
    Returns HTTP 200 with JSON if the application can access the persistence layer.
    """
    try:
        # Verify database connectivity with a simple query
        from sqlalchemy import text
        await session.execute(text("SELECT 1"))
        return HealthResponse(ok=True)
    except Exception as e:
        logger.exception("[healthz] database check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        )


@router.post("/pastes", response_model=CreatePasteResponse)
async def create_paste(
    request: CreatePasteRequest,
    session: AsyncSession = Depends(get_session),
    http_request: Request = None,
):
    """
    Create a new paste.

    Request body:
    {
        "content": "string",
        "ttl_seconds": 60,  # optional
        "max_views": 5     # optional
    }

    Response (2xx):
    {
        "id": "string",
        "url": "https://your-app.vercel.app/p/<id>"
    }

    Error cases return 4xx with JSON error body.
    """
    try:
        logger.info("[create_paste] creating new paste")
        
        # Get TEST_MODE header if provided
        test_now_ms = None
        if http_request:
            test_now_ms_header = http_request.headers.get("x-test-now-ms")
            if test_now_ms_header:
                try:
                    test_now_ms = int(test_now_ms_header)
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid x-test-now-ms header: must be an integer",
                    )

        result = await paste_service.create_paste(
            content=request.content,
            ttl_seconds=request.ttl_seconds,
            max_views=request.max_views,
            session=session,
            test_now_ms=test_now_ms,
        )

        logger.info(f"[create_paste] successfully created paste with id={result['id']}")
        return CreatePasteResponse(id=result["id"], url=result["url"])

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"[create_paste] validation error: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(f"[create_paste] error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create paste",
        )


@router.get("/pastes/{paste_id}", response_model=GetPasteResponse)
async def get_paste(
    paste_id: str,
    session: AsyncSession = Depends(get_session),
    http_request: Request = None,
):
    """
    Fetch a paste (API endpoint).

    Successful response (JSON, 200):
    {
        "content": "string",
        "remaining_views": 4,
        "expires_at": "2026-01-01T00:00:00.000Z"
    }

    Notes:
    - remaining_views may be null if unlimited
    - expires_at may be null if no TTL
    - Each successful API fetch counts as a view

    Unavailable cases (all return 404):
    - Missing paste
    - Expired paste
    - View limit exceeded
    """
    try:
        logger.info(f"[get_paste] retrieving paste {paste_id}")

        # Get TEST_MODE header if provided
        test_now_ms = None
        if http_request:
            test_now_ms_header = http_request.headers.get("x-test-now-ms")
            if test_now_ms_header:
                try:
                    test_now_ms = int(test_now_ms_header)
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid x-test-now-ms header: must be an integer",
                    )

        paste = await paste_service.get_paste(
            paste_id=paste_id,
            session=session,
            test_now_ms=test_now_ms,
            increment_view=True,
        )

        if paste is None:
            logger.info(f"[get_paste] paste {paste_id} not found or unavailable")
            raise HTTPException(status_code=404, detail="Paste not found")

        logger.info(f"[get_paste] successfully retrieved paste {paste_id}")
        return GetPasteResponse(**paste)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[get_paste] error retrieving paste {paste_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve paste",
        )


@router.get("/p/{paste_id}", response_class=HTMLResponse)
async def view_paste(
    paste_id: str,
    session: AsyncSession = Depends(get_session),
    http_request: Request = None,
):
    """
    View a paste as HTML.

    Returns HTML (200) containing the paste content.
    If the paste is unavailable, returns HTTP 404.
    Paste content is rendered safely (no script execution).
    """
    try:
        logger.info(f"[view_paste] viewing paste {paste_id}")

        # Get TEST_MODE header if provided
        test_now_ms = None
        if http_request:
            test_now_ms_header = http_request.headers.get("x-test-now-ms")
            if test_now_ms_header:
                try:
                    test_now_ms = int(test_now_ms_header)
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid x-test-now-ms header: must be an integer",
                    )

        paste = await paste_service.get_paste(
            paste_id=paste_id,
            session=session,
            test_now_ms=test_now_ms,
            increment_view=True,
        )

        if paste is None:
            logger.info(f"[view_paste] paste {paste_id} not found or unavailable")
            raise HTTPException(status_code=404, detail="Paste not found")

        # Escape HTML to prevent script execution
        content = paste.get("content", "")
        escaped_content = (
            content.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Paste {paste_id}</title>
            <style>
                body {{ font-family: monospace; margin: 20px; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                pre {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }}
                .metadata {{ color: #666; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Paste {paste_id}</h1>
                <pre>{escaped_content}</pre>
                <div class="metadata">
                    {f'<p>Remaining views: {paste["remaining_views"]}</p>' if paste["remaining_views"] is not None else ''}
                    {f'<p>Expires at: {paste["expires_at"]}</p>' if paste["expires_at"] else ''}
                </div>
            </div>
        </body>
        </html>
        """
        
        logger.info(f"[view_paste] successfully served paste {paste_id} as HTML")
        return html

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[view_paste] error viewing paste {paste_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve paste",
        )
