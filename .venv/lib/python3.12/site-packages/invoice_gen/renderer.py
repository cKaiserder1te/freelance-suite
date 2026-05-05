"""Invoice rendering interfaces and helpers."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateNotFound, select_autoescape
from weasyprint import HTML

from .calculator import (
	calculate_grand_total,
	calculate_line_total,
	calculate_subtotal,
	calculate_total_tax,
)
from .formatter import format_currency, format_date
from .models import Invoice


class InvoiceRenderError(Exception):
	"""Raised when invoice rendering fails."""


def _get_templates_path() -> Path:
	"""Resolve the templates directory path.

	Args:
		None.

	Returns:
		Path to the templates directory.

	Raises:
		None.
	"""
	return Path(__file__).resolve().parent / "templates"


def _build_context(invoice: Invoice, locale: str) -> dict[str, object]:
	"""Build the template context for an invoice.

	Args:
		invoice: Invoice model to render.
		locale: Locale string for formatting.

	Returns:
		Template context dictionary.

	Raises:
		None.
	"""
	invoice_data = invoice.model_dump()
	invoice_data["meta"]["date"] = format_date(invoice.meta.invoice_date, locale=locale)
	invoice_data["meta"]["due_date"] = format_date(invoice.meta.due_date, locale=locale)

	formatted_items: list[dict[str, object]] = []
	for item in invoice.items:
		formatted_items.append(
			{
				"description": item.description,
				"quantity": item.quantity,
				"unit": item.unit,
				"unit_price": format_currency(
					item.unit_price, currency=invoice.meta.currency, locale=locale
				),
				"total": format_currency(
					calculate_line_total(item),
					currency=invoice.meta.currency,
					locale=locale,
				),
			}
		)

	subtotal = calculate_subtotal(invoice.items)
	total_tax = calculate_total_tax(invoice.items)
	grand_total = calculate_grand_total(invoice.items)

	calculated = {
		"subtotal": format_currency(
			subtotal, currency=invoice.meta.currency, locale=locale
		),
		"total_tax": format_currency(
			total_tax, currency=invoice.meta.currency, locale=locale
		),
		"grand_total": format_currency(
			grand_total, currency=invoice.meta.currency, locale=locale
		),
		"formatted_items": formatted_items,
	}

	return {"invoice": invoice_data, "calculated": calculated}


def render_html(
	invoice: Invoice,
	template: str = "default",
	locale: str = "de_DE",
) -> str:
	"""Render an invoice to HTML using a template.

	Args:
		invoice: Invoice model to render.
		template: Template name without extension.
		locale: Locale string for formatting.

	Returns:
		Rendered HTML string.

	Raises:
		InvoiceRenderError: If the template cannot be loaded.
	"""
	templates_path = _get_templates_path()
	env = Environment(
		loader=FileSystemLoader(str(templates_path)),
		autoescape=select_autoescape(["html"]),
	)
	template_name = f"{template}.html"

	try:
		compiled_template = env.get_template(template_name)
	except TemplateNotFound as exc:
		raise InvoiceRenderError(f"Template not found: {template}") from exc

	context = _build_context(invoice, locale=locale)
	return compiled_template.render(context)


def render_pdf(
	invoice: Invoice,
	output: str | Path,
	template: str = "default",
	locale: str = "de_DE",
) -> Path:
	"""Render an invoice to a PDF file.

	Args:
		invoice: Invoice model to render.
		output: Output file path.
		template: Template name without extension.
		locale: Locale string for formatting.

	Returns:
		Path to the rendered PDF file.

	Raises:
		InvoiceRenderError: If PDF rendering fails.
	"""
	output_path = Path(output)
	html = render_html(invoice, template=template, locale=locale)
	try:
		HTML(string=html).write_pdf(str(output_path))
	except Exception as exc:
		raise InvoiceRenderError("Failed to render PDF") from exc
	return output_path


def render_html_to_file(
	invoice: Invoice,
	output: str | Path,
	template: str = "default",
	locale: str = "de_DE",
) -> Path:
	"""Render an invoice to an HTML file.

	Args:
		invoice: Invoice model to render.
		output: Output file path.
		template: Template name without extension.
		locale: Locale string for formatting.

	Returns:
		Path to the rendered HTML file.

	Raises:
		InvoiceRenderError: If template rendering fails.
	"""
	output_path = Path(output)
	html = render_html(invoice, template=template, locale=locale)
	try:
		output_path.write_text(html, encoding="utf-8")
	except OSError as exc:
		raise InvoiceRenderError("Failed to write HTML file") from exc
	return output_path
