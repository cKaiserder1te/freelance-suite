"""Formatting helpers for currency, dates, and numbers."""

from __future__ import annotations

import contextlib
import locale as pylocale
from datetime import date
from typing import Final, Generator

SUPPORTED_LOCALES: Final[list[str]] = ["de_DE", "en_US", "en_GB", "fr_FR"]

LOCALE_SEPARATORS: Final[dict[str, dict[str, str]]] = {
	"de_DE": {"thousands": ".", "decimal": ","},
	"en_US": {"thousands": ",", "decimal": "."},
	"en_GB": {"thousands": ",", "decimal": "."},
	"fr_FR": {"thousands": " ", "decimal": ","},
}

CURRENCY_FORMATS: Final[dict[str, dict[str, str]]] = {
	"EUR": {"symbol": "€", "position": "suffix", "spacer": " "},
	"USD": {"symbol": "$", "position": "prefix", "spacer": ""},
}

MONTH_NAMES: Final[dict[str, list[str]]] = {
	"de_DE": [
		"Januar",
		"Februar",
		"Maerz",
		"April",
		"Mai",
		"Juni",
		"Juli",
		"August",
		"September",
		"Oktober",
		"November",
		"Dezember",
	],
	"en_US": [
		"January",
		"February",
		"March",
		"April",
		"May",
		"June",
		"July",
		"August",
		"September",
		"October",
		"November",
		"December",
	],
	"en_GB": [
		"January",
		"February",
		"March",
		"April",
		"May",
		"June",
		"July",
		"August",
		"September",
		"October",
		"November",
		"December",
	],
	"fr_FR": [
		"janvier",
		"fevrier",
		"mars",
		"avril",
		"mai",
		"juin",
		"juillet",
		"aout",
		"septembre",
		"octobre",
		"novembre",
		"decembre",
	],
}

PAYMENT_TERMS: Final[dict[str, str]] = {
	"de_DE": "Zahlbar innerhalb von {days} Tagen",
	"en_US": "Due within {days} days",
	"en_GB": "Due within {days} days",
	"fr_FR": "Paiement sous {days} jours",
}


@contextlib.contextmanager
def _temporary_locale(category: int, locale_name: str) -> Generator[None, None, None]:
	"""Temporarily set a locale for formatting.

	Args:
		category: Locale category to set.
		locale_name: Locale name to apply.

	Yields:
		None.

	Raises:
		locale.Error: If the locale cannot be set.
	"""
	current_locale = pylocale.setlocale(category)
	pylocale.setlocale(category, locale_name)
	try:
		yield
	finally:
		pylocale.setlocale(category, current_locale)


def _format_number(amount: float, *, locale: str) -> str:
	"""Format a number with locale-aware separators.

	Args:
		amount: Amount to format.
		locale: Locale string.

	Returns:
		Formatted number string with two decimals.

	Raises:
		ValueError: If the locale is not supported.
	"""
	if locale not in LOCALE_SEPARATORS:
		raise ValueError(f"Unsupported locale: {locale}")

	separators = LOCALE_SEPARATORS[locale]
	integer_part, _, fraction = f"{amount:.2f}".partition(".")
	grouped = ""
	while integer_part:
		prefix = integer_part[-3:]
		if grouped:
			grouped = prefix + separators["thousands"] + grouped
		else:
			grouped = prefix
		integer_part = integer_part[:-3]
	return f"{grouped}{separators['decimal']}{fraction}"


def format_date(d: date, locale: str = "de_DE") -> str:
	"""Format a date for display.

	Args:
		d: Date to format.
		locale: Locale string.

	Returns:
		Formatted date string.

	Raises:
		ValueError: If the locale is not supported.
	"""
	if locale not in SUPPORTED_LOCALES:
		raise ValueError(f"Unsupported locale: {locale}")

	try:
		with _temporary_locale(pylocale.LC_TIME, locale):
			if locale in {"de_DE", "fr_FR"}:
				return d.strftime("%d. %B %Y")
			if locale == "en_GB":
				return d.strftime("%d %B %Y")
			return d.strftime("%B %d, %Y")
	except (pylocale.Error, ValueError):
		month_name = MONTH_NAMES[locale][d.month - 1]
		if locale == "de_DE":
			return f"{d.day}. {month_name} {d.year}"
		if locale == "en_GB":
			return f"{d.day} {month_name} {d.year}"
		if locale == "fr_FR":
			return f"{d.day} {month_name} {d.year}"
		return f"{month_name} {d.day}, {d.year}"


def format_currency(
	amount: float, currency: str = "EUR", locale: str = "de_DE"
) -> str:
	"""Format a currency value for display.

	Args:
		amount: Amount to format.
		currency: Currency code.
		locale: Locale string.

	Returns:
		Formatted currency string.

	Raises:
		ValueError: If the currency or locale is not supported.
	"""
	if currency not in CURRENCY_FORMATS:
		raise ValueError(f"Unsupported currency: {currency}")
	if locale not in SUPPORTED_LOCALES:
		raise ValueError(f"Unsupported locale: {locale}")

	number = _format_number(amount, locale=locale)
	currency_format = CURRENCY_FORMATS[currency]
	if currency_format["position"] == "prefix":
		return f"{currency_format['symbol']}{currency_format['spacer']}{number}"
	return f"{number}{currency_format['spacer']}{currency_format['symbol']}"


def format_invoice_number(template: str, year: int, seq: int) -> str:
	"""Format an invoice number based on a template.

	Args:
		template: Format template using YEAR and SEQ placeholders.
		year: Year value.
		seq: Sequence number.

	Returns:
		Formatted invoice number.

	Raises:
		ValueError: If the template is invalid.
	"""
	try:
		return template.format(YEAR=year, SEQ=seq)
	except (KeyError, ValueError) as exc:
		raise ValueError("Invalid invoice number template") from exc


def format_payment_terms(days: int, locale: str = "de_DE") -> str:
	"""Format payment terms text.

	Args:
		days: Number of days until due.
		locale: Locale string.

	Returns:
		Payment terms string.

	Raises:
		ValueError: If the locale is not supported.
	"""
	if locale not in PAYMENT_TERMS:
		raise ValueError(f"Unsupported locale: {locale}")
	return PAYMENT_TERMS[locale].format(days=days)


def get_supported_locales() -> list[str]:
	"""Return the list of supported locales.

	Args:
		None.

	Returns:
		List of supported locale strings.

	Raises:
		None.
	"""
	return list(SUPPORTED_LOCALES)
