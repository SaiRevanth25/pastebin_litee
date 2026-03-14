from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class CreatePasteRequest(BaseModel):
    """Request model for creating a paste"""

    content: str = Field(..., description="The paste content (non-empty string)")
    ttl_seconds: Optional[int] = Field(None, description="Time-to-live in seconds (optional, must be ≥ 1)")
    max_views: Optional[int] = Field(None, description="Maximum number of views (optional, must be ≥ 1)")

    @field_validator('content')
    @classmethod
    def content_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('content must be a non-empty string')
        return v

    @field_validator('ttl_seconds')
    @classmethod
    def ttl_valid(cls, v):
        if v is not None and v < 1:
            raise ValueError('ttl_seconds must be an integer ≥ 1')
        return v

    @field_validator('max_views')
    @classmethod
    def max_views_valid(cls, v):
        if v is not None and v < 1:
            raise ValueError('max_views must be an integer ≥ 1')
        return v


class CreatePasteResponse(BaseModel):
    """Response model for paste creation"""

    id: str = Field(..., description="The unique paste ID")
    url: str = Field(..., description="The publicly viewable URL")


class GetPasteResponse(BaseModel):
    """Response model for retrieving a paste"""

    content: str = Field(..., description="The paste content")
    remaining_views: Optional[int] = Field(None, description="Remaining views (null if unlimited)")
    expires_at: Optional[datetime] = Field(None, description="Expiration time in ISO format (null if no TTL)")


class HealthResponse(BaseModel):
    """Response model for health check"""

    ok: bool = Field(..., description="Whether the application is healthy")