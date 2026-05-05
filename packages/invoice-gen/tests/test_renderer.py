"""Tests for invoice rendering."""

from datetime import date
from pathlib import Path

import pytest

from invoice_gen.models import Client, Invoice, InvoiceMeta, LineItem, Sender
from invoice_gen.renderer import InvoiceRenderError, render_html, render_pdf


def build_invoice() -> Invoice:
	"""Build a valid invoice for rendering tests.

	Args:
		None.

	Returns:
		Invoice instance.

	Raises:
		None.
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
	items = [
		LineItem(
			description="Development",
			quantity=2.0,
			unit="h",
			unit_price=100.0,
		)
	]
	return Invoice(sender=sender, client=client, meta=meta, items=items)


def test_render_html_contains_client_name() -> None:
	"""Render HTML and ensure client name appears.

	Args:
		None.

	Returns:
		None.

	Raises:
		None.
	"""
	invoice = build_invoice()
	html = render_html(invoice, template="default", locale="de_DE")
	assert "Acme GmbH" in html


@pytest.mark.parametrize("template", ["default", "minimal", "german"])
def test_templates_render_without_error(template: str) -> None:
	"""Render all templates without errors.

	Args:
		template: Template name under test.

	Returns:
		None.

	Raises:
		None.
	"""
	invoice = build_invoice()
	html = render_html(invoice, template=template, locale="de_DE")
	assert html.strip() != ""


def test_render_pdf_creates_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
	"""Create a PDF file using the renderer.

	Args:
		tmp_path: Temporary directory for test output.
		monkeypatch: Pytest monkeypatch fixture.

	Returns:
		None.

	Raises:
		None.
	"""
	invoice = build_invoice()
	output = tmp_path / "invoice.pdf"

	class FakeHTML:
		"""Test double for WeasyPrint HTML renderer."""

		def __init__(self, string: str) -> None:
			"""Store the HTML string for test use.

			Args:
				string: Rendered HTML string.

			Returns:
				None.

			Raises:
				None.
			"""
			self.string = string

		def write_pdf(self, target: str) -> None:
			"""Write a dummy PDF payload.

			Args:
				target: Output path.

			Returns:
				None.

			Raises:
				None.
			"""
			Path(target).write_bytes(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

	monkeypatch.setattr("invoice_gen.renderer.HTML", FakeHTML)

	result = render_pdf(invoice, output, template="default", locale="de_DE")
	assert result.exists()


def test_render_html_invalid_template_raises() -> None:
	"""Raise InvoiceRenderError on unknown template.

	Args:
		None.

	Returns:
		None.

	Raises:
		None.
	"""
	invoice = build_invoice()
	with pytest.raises(InvoiceRenderError):
		render_html(invoice, template="missing", locale="de_DE")
