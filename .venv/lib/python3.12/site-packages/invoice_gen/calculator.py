"""Invoice calculation utilities."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_EVEN
from typing import Final

from .models import LineItem

DEFAULT_DECIMALS: Final[int] = 2

LOCALE_FORMATS: Final[dict[str, dict[str, str]]] = {
	"de_DE": {"thousands_sep": ".", "decimal_sep": ","},
	"en_US": {"thousands_sep": ",", "decimal_sep": "."},
}

CURRENCY_FORMATS: Final[dict[str, dict[str, str]]] = {
	"EUR": {"symbol": "€", "position": "suffix", "spacer": " "},
	"USD": {"symbol": "$", "position": "prefix", "spacer": ""},
}


def _to_decimal(value: float) -> Decimal:
	"""Convert a float to Decimal using a string representation.

	Args:
		value: Numeric value to convert.

	Returns:
		Decimal representation of the value.

	Raises:
		None.
	"""
	return Decimal(str(value))


def _format_number(value: float, *, decimals: int, locale: str) -> str:
	"""Format a number with locale-aware separators.

	Args:
		value: Value to format.
		decimals: Number of decimal places.
		locale: Locale string, e.g., de_DE or en_US.

	Returns:
		Locale-formatted number string.

	Raises:
		ValueError: If the locale is not supported.
	"""
	if locale not in LOCALE_FORMATS:
		raise ValueError(f"Unsupported locale: {locale}")

	separators = LOCALE_FORMATS[locale]
	quantized = _to_decimal(value).quantize(
		Decimal("1." + ("0" * decimals)), rounding=ROUND_HALF_EVEN
	)
	integer_part, _, fractional_part = f"{quantized:.{decimals}f}".partition(".")
	grouped = ""
	while integer_part:
		prefix = integer_part[-3:]
		if grouped:
			grouped = prefix + separators["thousands_sep"] + grouped
		else:
			grouped = prefix
		integer_part = integer_part[:-3]
	return f"{grouped}{separators['decimal_sep']}{fractional_part}"


def calculate_line_total(item: LineItem) -> float:
	"""Calculate a line total after discount and tax.

	Args:
		item: Line item to calculate.

	Returns:
		Line total including tax.

	Raises:
		None.
	"""
	base = item.quantity * item.unit_price * (1 - item.discount)
	return base * (1 + item.tax_rate)


def calculate_subtotal(items: list[LineItem]) -> float:
	"""Calculate the subtotal before tax.

	Args:
		items: Line items to sum.

	Returns:
		Subtotal for all items before tax.

	Raises:
		None.
	"""
	return sum(item.quantity * item.unit_price * (1 - item.discount) for item in items)


def calculate_total_tax(items: list[LineItem]) -> float:
	"""Calculate the total tax amount.

	Args:
		items: Line items to sum tax for.

	Returns:
		Total tax across all items.

	Raises:
		None.
	"""
	return sum(
		item.quantity * item.unit_price * (1 - item.discount) * item.tax_rate
		for item in items
	)


def calculate_grand_total(items: list[LineItem]) -> float:
	"""Calculate the grand total including tax.

	Args:
		items: Line items to sum.

	Returns:
		Total amount including tax.

	Raises:
		None.
	"""
	return calculate_subtotal(items) + calculate_total_tax(items)


def round_currency(value: float, decimals: int = DEFAULT_DECIMALS) -> float:
	"""Round a currency value using banker's rounding.

	Args:
		value: Value to round.
		decimals: Number of decimal places to keep.

	Returns:
		Rounded float value.

	Raises:
		ValueError: If decimals is negative.
	"""
	if decimals < 0:
		raise ValueError("decimals must be non-negative")
	quantized = _to_decimal(value).quantize(
		Decimal("1." + ("0" * decimals)), rounding=ROUND_HALF_EVEN
	)
	return float(quantized)


def format_currency(
	value: float,
	currency: str = "EUR",
	locale: str = "de_DE",
) -> str:
	"""Format a currency value for display.

	Args:
		value: Numeric value to format.
		currency: Currency code, e.g., EUR or USD.
		locale: Locale string, e.g., de_DE or en_US.

	Returns:
		Formatted currency string.

	Raises:
		ValueError: If the currency code is not supported.
	"""
	if currency not in CURRENCY_FORMATS:
		raise ValueError(f"Unsupported currency: {currency}")

	currency_format = CURRENCY_FORMATS[currency]
	number = _format_number(value, decimals=DEFAULT_DECIMALS, locale=locale)
	if currency_format["position"] == "prefix":
		return f"{currency_format['symbol']}{currency_format['spacer']}{number}"
	return f"{number}{currency_format['spacer']}{currency_format['symbol']}"
