"""Revenue API routes."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ..queries import get_kpis, get_monthly_revenue

router = APIRouter()


class RevenueResponse(BaseModel):
    """Response model for revenue data."""

    labels: list[str] = Field(description="Label list")
    values: list[float] = Field(description="Revenue values")
    running_total: list[float] = Field(description="Cumulative totals")


class KpisResponse(BaseModel):
    """Response model for KPI data."""

    mtd_revenue: float
    mtd_hours: float
    ytd_revenue: float
    active_projects_count: int


def _parse_month(value: str) -> date:
    """Parse a YYYY-MM month value.

    Args:
        value: Month string.

    Returns:
        Parsed date at the first of the month.

    Raises:
        ValueError: If the value is invalid.
    """
    return datetime.strptime(value, "%Y-%m").date().replace(day=1)


def _month_range(from_value: str | None, to_value: str | None) -> tuple[date, date]:
    """Build a month range from query values.

    Args:
        from_value: Start month string.
        to_value: End month string.

    Returns:
        Start and end month dates.

    Raises:
        ValueError: If date parsing fails.
    """
    if from_value:
        start = _parse_month(from_value)
    elif to_value:
        start = _parse_month(to_value)
    else:
        start = date.today().replace(month=1, day=1)

    if to_value:
        end = _parse_month(to_value)
    elif from_value:
        end = _parse_month(from_value)
    else:
        end = date.today().replace(month=12, day=1)

    if start > end:
        raise ValueError("from must be before to")
    if start.year != end.year:
        raise ValueError("Range must be within a single year")
    return start, end


def _build_running_total(values: list[float]) -> list[float]:
    """Build a running total list.

    Args:
        values: Revenue values.

    Returns:
        Running total values.

    Raises:
        None.
    """
    total = 0.0
    running = []
    for value in values:
        total += value
        running.append(total)
    return running


@router.get("/revenue", response_model=RevenueResponse)
def revenue(
    period: Literal["month", "quarter", "year"] = Query(
        "month", description="Aggregation period"
    ),
    from_value: str | None = Query(None, alias="from", description="Start month"),
    to_value: str | None = Query(None, alias="to", description="End month"),
) -> RevenueResponse:
    """Return revenue aggregation data.

    Args:
        period: Aggregation period.
        from_value: Start month.
        to_value: End month.

    Returns:
        Revenue response payload.

    Raises:
        HTTPException: On validation or processing errors.
    """
    try:
        start, end = _month_range(from_value, to_value)
        monthly = get_monthly_revenue(start.year)
        revenue_map = {int(item["month"]): float(item["revenue"]) for item in monthly}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to load revenue") from exc

    try:
        months = list(range(start.month, end.month + 1))
        if period == "month":
            labels = [f"{start.year}-{month:02d}" for month in months]
            values = [revenue_map.get(month, 0.0) for month in months]
        elif period == "quarter":
            quarters: dict[int, float] = {}
            for month in months:
                quarter = ((month - 1) // 3) + 1
                quarters[quarter] = quarters.get(quarter, 0.0) + revenue_map.get(
                    month, 0.0
                )
            labels = [f"Q{quarter} {start.year}" for quarter in sorted(quarters)]
            values = [quarters[quarter] for quarter in sorted(quarters)]
        else:
            labels = [str(start.year)]
            values = [sum(revenue_map.get(month, 0.0) for month in months)]
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to aggregate revenue") from exc

    return RevenueResponse(
        labels=labels,
        values=values,
        running_total=_build_running_total(values),
    )


@router.get("/kpis", response_model=KpisResponse)
def kpis() -> KpisResponse:
    """Return KPI data.

    Args:
        None.

    Returns:
        KPI payload.

    Raises:
        HTTPException: On processing errors.
    """
    try:
        return KpisResponse(**get_kpis())
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to load KPIs") from exc
