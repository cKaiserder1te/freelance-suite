"""Tests for invoice formatting utilities."""

from datetime import date

import pytest

from invoice_gen.formatter import (
    format_currency,
    format_date,
    format_invoice_number,
    format_payment_terms,
    get_supported_locales,
)


def test_format_date_german() -> None:
    """Format a German date string.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.
    """
    formatted = format_date(date(2025, 1, 15), locale="de_DE")
    assert formatted == "15. Januar 2025"


def test_format_date_english_us() -> None:
    """Format a US English date string.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.
    """
    formatted = format_date(date(2025, 1, 15), locale="en_US")
    assert formatted == "January 15, 2025"


def test_format_currency_german_eur() -> None:
    """Format a currency string for German EUR.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.
    """
    formatted = format_currency(1234.56, currency="EUR", locale="de_DE")
    assert formatted == "1.234,56 €"


def test_format_currency_english_usd() -> None:
    """Format a currency string for US USD.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.
    """
    formatted = format_currency(1234.56, currency="USD", locale="en_US")
    assert formatted == "$1,234.56"


def test_format_invoice_number_template() -> None:
    """Format an invoice number from template.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.
    """
    formatted = format_invoice_number("{YEAR}-{SEQ:03d}", year=2025, seq=1)
    assert formatted == "2025-001"


def test_format_payment_terms_de() -> None:
    """Format payment terms in German.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.
    """
    formatted = format_payment_terms(14, locale="de_DE")
    assert formatted == "Zahlbar innerhalb von 14 Tagen"


def test_format_payment_terms_en() -> None:
    """Format payment terms in English.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.
    """
    formatted = format_payment_terms(14, locale="en_US")
    assert formatted == "Due within 14 days"


def test_supported_locales() -> None:
    """Return the list of supported locales.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.
    """
    locales = get_supported_locales()
    assert locales == ["de_DE", "en_US", "en_GB", "fr_FR"]
