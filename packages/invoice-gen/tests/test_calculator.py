"""Tests for invoice calculation utilities."""

import pytest

from invoice_gen.calculator import (
	calculate_grand_total,
	calculate_line_total,
	calculate_subtotal,
	calculate_total_tax,
	format_currency,
)
from invoice_gen.models import LineItem


def test_zero_tax_zero_discount_baseline() -> None:
	"""Calculate totals with no tax and no discount.

	Args:
		None.

	Returns:
		None.

	Raises:
		None.
	"""
	item = LineItem(
		description="Development",
		quantity=2.0,
		unit="h",
		unit_price=100.0,
	)
	assert calculate_line_total(item) == pytest.approx(200.0)
	assert calculate_subtotal([item]) == pytest.approx(200.0)
	assert calculate_total_tax([item]) == pytest.approx(0.0)
	assert calculate_grand_total([item]) == pytest.approx(200.0)


def test_vat_calculation_19_percent() -> None:
	"""Apply 19% VAT to a line item.

	Args:
		None.

	Returns:
		None.

	Raises:
		None.
	"""
	item = LineItem(
		description="Development",
		quantity=1.0,
		unit="h",
		unit_price=100.0,
		tax_rate=0.19,
	)
	assert calculate_subtotal([item]) == pytest.approx(100.0)
	assert calculate_total_tax([item]) == pytest.approx(19.0)
	assert calculate_grand_total([item]) == pytest.approx(119.0)


def test_discount_applied_before_tax() -> None:
	"""Apply discount before calculating tax.

	Args:
		None.

	Returns:
		None.

	Raises:
		None.
	"""
	item = LineItem(
		description="Design",
		quantity=2.0,
		unit="h",
		unit_price=100.0,
		discount=0.1,
		tax_rate=0.2,
	)
	expected_subtotal = 2.0 * 100.0 * (1 - 0.1)
	expected_tax = expected_subtotal * 0.2
	assert calculate_subtotal([item]) == pytest.approx(expected_subtotal)
	assert calculate_total_tax([item]) == pytest.approx(expected_tax)
	assert calculate_grand_total([item]) == pytest.approx(expected_subtotal + expected_tax)


def test_multiple_items_different_tax_rates() -> None:
	"""Compute totals for multiple items with mixed tax rates.

	Args:
		None.

	Returns:
		None.

	Raises:
		None.
	"""
	items = [
		LineItem(
			description="Development",
			quantity=1.0,
			unit="h",
			unit_price=100.0,
			tax_rate=0.19,
		),
		LineItem(
			description="Consulting",
			quantity=2.0,
			unit="h",
			unit_price=150.0,
			tax_rate=0.07,
		),
	]
	subtotal = (1.0 * 100.0) + (2.0 * 150.0)
	total_tax = (1.0 * 100.0 * 0.19) + (2.0 * 150.0 * 0.07)
	assert calculate_subtotal(items) == pytest.approx(subtotal)
	assert calculate_total_tax(items) == pytest.approx(total_tax)
	assert calculate_grand_total(items) == pytest.approx(subtotal + total_tax)


def test_half_hour_quantity() -> None:
	"""Support fractional quantities like half hours.

	Args:
		None.

	Returns:
		None.

	Raises:
		None.
	"""
	item = LineItem(
		description="Support",
		quantity=0.5,
		unit="h",
		unit_price=120.0,
	)
	assert calculate_subtotal([item]) == pytest.approx(60.0)


def test_currency_formatting_eur_and_usd() -> None:
	"""Format EUR and USD values with locale-aware separators.

	Args:
		None.

	Returns:
		None.

	Raises:
		None.
	"""
	assert format_currency(1234.56, currency="EUR", locale="de_DE") == "1.234,56 €"
	assert format_currency(1234.56, currency="USD", locale="en_US") == "$1,234.56"
