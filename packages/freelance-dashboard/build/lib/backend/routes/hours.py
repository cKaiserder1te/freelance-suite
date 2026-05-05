"""Hours and activity API routes."""

from __future__ import annotations

from datetime import date
from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ..queries import (
    get_activity_heatmap,
    get_hours_by_client,
    get_hours_by_project,
    get_hours_by_week,
)

router = APIRouter()


class HoursResponse(BaseModel):
    """Response model for hours data."""

    labels: list[str] = Field(description="Label list")
    values: list[float] = Field(description="Hours values")


class HeatmapItem(BaseModel):
    """Response model for heatmap items."""

    date: str
    count: float


def _parse_date(value: str | None, fallback: date) -> date:
    """Parse ISO date strings with fallback.

    Args:
        value: Date string.
        fallback: Fallback date.

    Returns:
        Parsed date.

    Raises:
        None.
    """
    if not value:
        return fallback
    return date.fromisoformat(value)


@router.get("/hours", response_model=HoursResponse)
def hours(
    group_by: Literal["client", "project", "week"] = Query(
        "client", alias="groupBy", description="Grouping"
    ),
    from_value: str | None = Query(None, alias="from", description="Start date"),
    to_value: str | None = Query(None, alias="to", description="End date"),
) -> HoursResponse:
    """Return hours grouped by client.

    Args:
        group_by: Grouping type.
        from_value: Start date string.
        to_value: End date string.

    Returns:
        Aggregated hours data.

    Raises:
        None.
    """
    today = date.today()
    try:
        start = _parse_date(from_value, today.replace(month=1, day=1))
        end = _parse_date(to_value, today)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid date format") from exc

    if start > end:
        raise HTTPException(status_code=422, detail="from must be before to")

    try:
        if group_by == "client":
            data = get_hours_by_client(start, end)
            labels = [item["client"] for item in data]
        elif group_by == "project":
            data = get_hours_by_project(start, end)
            labels = [item["project"] for item in data]
        else:
            data = get_hours_by_week(start, end)
            labels = [item["week"] for item in data]
        values = [float(item.get("hours", 0.0)) for item in data]
        return HoursResponse(labels=labels, values=values)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to load hours data") from exc


@router.get("/heatmap", response_model=list[HeatmapItem])
def heatmap(year: int = Query(date.today().year, description="Target year")) -> list[HeatmapItem]:
    """Return activity heatmap data.

    Args:
        year: Target year.

    Returns:
        Heatmap data list.

    Raises:
        None.
    """
    try:
        data = get_activity_heatmap(year)
        return [HeatmapItem(date=item["date"], count=float(item["hours"])) for item in data]
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to load heatmap") from exc
