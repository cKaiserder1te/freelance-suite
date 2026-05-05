"""Invoice API routes."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ..queries import get_invoices

router = APIRouter()


class InvoiceItem(BaseModel):
    """Response model for invoice items."""

    number: str = Field(description="Invoice number")
    client: str = Field(description="Client name")
    amount: float = Field(description="Invoice amount")
    due_date: str = Field(description="Due date")
    status: str = Field(description="Invoice status")


@router.get("/invoices", response_model=list[InvoiceItem])
def invoices(
    status: Literal["open", "paid", "all"] = Query(
        "open", description="Invoice status"
    ),
) -> list[InvoiceItem]:
    """Return invoice data.

    Args:
        status: Invoice status filter.

    Returns:
        Invoice list.

    Raises:
        None.
    """
    try:
        data = get_invoices(status)
        return [InvoiceItem(**item) for item in data]
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to load invoices") from exc
