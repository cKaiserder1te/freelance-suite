"""Client API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..queries import get_client_summary

router = APIRouter()


class ClientSummaryItem(BaseModel):
    """Response model for client summary items."""

    name: str = Field(description="Client name")
    total_hours: float = Field(description="Total hours")
    total_revenue: float = Field(description="Total revenue")
    avg_rate: float = Field(description="Average hourly rate")
    project_count: int = Field(description="Number of projects")


@router.get("/clients/summary", response_model=list[ClientSummaryItem])
def client_summary() -> list[ClientSummaryItem]:
    """Return summary data per client.

    Args:
        None.

    Returns:
        Client summary list.

    Raises:
        None.
    """
    try:
        data = get_client_summary()
        return [ClientSummaryItem(**item) for item in data]
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to load client summary") from exc
