"""Tests for invoice-gen models."""

from datetime import date

import pytest
from pydantic import ValidationError

from invoice_gen.models import Client, Invoice, InvoiceMeta, LineItem, Sender


def build_invoice(*, item_overrides: dict | None = None) -> Invoice:
	"""Build a valid invoice with a single line item.

	Args:
		item_overrides: Optional overrides for the default line item.

	Returns:
		A valid invoice instance.
	"""
	sender = Sender(
		name="Max Mustermann",
		address="Musterstrasse 1, 12345 Berlin",
		email="max@example.com",
	)
	client = Client(
		name="Acme GmbH",
		address="Acme-Allee 42, 10115 Berlin",
	)
	meta = InvoiceMeta(
		number="2025-001",
		date=date(2025, 1, 15),
		due_date=date(2025, 2, 14),
		currency="EUR",
	)
	item_data = {
		"description": "Development work",
		"quantity": 2.0,
		"unit": "h",
		"unit_price": 100.0,
	}
	if item_overrides:
		item_data.update(item_overrides)

	items = [LineItem(**item_data)]
	return Invoice(sender=sender, client=client, meta=meta, items=items)


def test_valid_invoice_creation() -> None:
	"""Create a valid invoice without errors."""
	invoice = build_invoice()
	assert invoice.meta.number == "2025-001"
	assert len(invoice.items) == 1


def test_line_item_discount_and_tax() -> None:
	"""Validate line total with discount and tax."""
	invoice = build_invoice(
		item_overrides={"discount": 0.1, "tax_rate": 0.2, "quantity": 3.0}
	)
	item = invoice.items[0]
	expected = 3.0 * 100.0 * (1 - 0.1) * (1 + 0.2)
	assert item.line_total == pytest.approx(expected)


def test_due_date_before_date_raises() -> None:
	"""Reject due dates that are not after the invoice date."""
	sender = Sender(
		name="Max Mustermann",
		address="Musterstrasse 1, 12345 Berlin",
		email="max@example.com",
	)
	client = Client(
		name="Acme GmbH",
		address="Acme-Allee 42, 10115 Berlin",
	)
	meta = InvoiceMeta(
		number="2025-001",
		date=date(2025, 1, 15),
		due_date=date(2025, 1, 10),
		currency="EUR",
	)
	items = [
		LineItem(
			description="Development work",
			quantity=2.0,
			unit="h",
			unit_price=100.0,
		)
	]
	with pytest.raises(ValidationError):
		Invoice(sender=sender, client=client, meta=meta, items=items)


def test_quantity_must_be_positive() -> None:
	"""Reject line items with non-positive quantity."""
	with pytest.raises(ValidationError):
		build_invoice(item_overrides={"quantity": 0.0})


def test_total_calculation_multiple_items() -> None:
	"""Ensure totals are correct for multiple items."""
	sender = Sender(
		name="Max Mustermann",
		address="Musterstrasse 1, 12345 Berlin",
		email="max@example.com",
	)
	client = Client(
		name="Acme GmbH",
		address="Acme-Allee 42, 10115 Berlin",
	)
	meta = InvoiceMeta(
		number="2025-002",
		date=date(2025, 1, 20),
		due_date=date(2025, 2, 19),
		currency="EUR",
	)
	items = [
		LineItem(
			description="Development",
			quantity=2.0,
			unit="h",
			unit_price=100.0,
			discount=0.1,
			tax_rate=0.2,
		),
		LineItem(
			description="Design",
			quantity=1.0,
			unit="h",
			unit_price=200.0,
			discount=0.0,
			tax_rate=0.0,
		),
	]
	invoice = Invoice(sender=sender, client=client, meta=meta, items=items)

	expected_subtotal = (2.0 * 100.0 * (1 - 0.1)) + (1.0 * 200.0)
	expected_tax = (2.0 * 100.0 * (1 - 0.1) * 0.2) + 0.0
	expected_total = expected_subtotal + expected_tax

	assert invoice.subtotal == pytest.approx(expected_subtotal)
	assert invoice.total_tax == pytest.approx(expected_tax)
	assert invoice.total == pytest.approx(expected_total)
