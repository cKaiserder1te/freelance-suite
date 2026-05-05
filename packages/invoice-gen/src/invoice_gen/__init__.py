"""Public API for generating invoice PDFs and HTML.

Exposes helpers for loading data, rendering invoices, and listing templates.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from .models import Invoice
from .renderer import render_html_to_file, render_pdf
from .utils import get_template_dir

__all__ = [
	"generate_invoice",
	"generate_html",
	"load_from_json",
	"load_from_yaml",
	"list_templates",
]


def generate_invoice(
	data: dict,
	output: str = "invoice.pdf",
	template: str = "default",
	locale: str = "de_DE",
) -> Path:
	"""Generate a PDF invoice from a data dictionary.

	Args:
		data: Invoice payload as a dictionary.
		output: Output PDF file path.
		template: Template name without extension.
		locale: Locale string for formatting.

	Returns:
		Path to the generated PDF file.

	Raises:
		ValueError: If the invoice data fails validation.
	"""
	try:
		invoice = Invoice(**data)
	except ValidationError as exc:
		raise ValueError(f"Invalid invoice data: {exc}") from exc

	return render_pdf(invoice, output=output, template=template, locale=locale)


def generate_html(
	data: dict,
	output: str = "invoice.html",
	template: str = "default",
	locale: str = "de_DE",
) -> Path:
	"""Generate an HTML invoice file from a data dictionary.

	Args:
		data: Invoice payload as a dictionary.
		output: Output HTML file path.
		template: Template name without extension.
		locale: Locale string for formatting.

	Returns:
		Path to the generated HTML file.

	Raises:
		ValueError: If the invoice data fails validation.
	"""
	try:
		invoice = Invoice(**data)
	except ValidationError as exc:
		raise ValueError(f"Invalid invoice data: {exc}") from exc

	return render_html_to_file(
		invoice, output=output, template=template, locale=locale
	)


def load_from_json(path: str | Path) -> dict[str, Any]:
	"""Load invoice data from a JSON file.

	Args:
		path: Path to a JSON file.

	Returns:
		Parsed JSON data as a dictionary.

	Raises:
		OSError: If the file cannot be read.
		json.JSONDecodeError: If the JSON is invalid.
	"""
	file_path = Path(path)
	return json.loads(file_path.read_text(encoding="utf-8")) 

def load_from_yaml(path: str | Path) -> dict[str, Any]:
	"""Load invoice data from a YAML file.

	Args:
		path: Path to a YAML file.

	Returns:
		Parsed YAML data as a dictionary.

	Raises:
		OSError: If the file cannot be read.
		yaml.YAMLError: If the YAML is invalid.
	"""
	file_path = Path(path)
	return yaml.safe_load(file_path.read_text(encoding="utf-8"))


def list_templates() -> list[str]:
	"""List available template names.

	Args:
		None.

	Returns:
		Sorted list of template names without file extensions.

	Raises:
		OSError: If the template directory cannot be read.
	"""
	template_dir = get_template_dir()
	return sorted(
		path.stem for path in template_dir.iterdir() if path.suffix == ".html"
	)
