"""Configuration loading and defaults for freelance-toolkit."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError

try:
	import tomllib as toml_reader
except ModuleNotFoundError:  # pragma: no cover - for Python 3.10
	import toml as toml_reader

import toml as toml_writer

LOGGER = logging.getLogger(__name__)


class FreelanceConfig(BaseModel):
	"""Typed configuration for freelance-toolkit.

	Args:
		currency: Default currency code.
		tax_note: Default tax disclaimer string.
		rounding: Rounding mode.
		time_format: Time display format.
		invoice_template: Invoice template name.
		invoice_output_dir: Default invoice output directory.
		invoice_number_format: Invoice number format template.
		theme: Display theme.
		week_starts: Week start day.

	Returns:
		None.

	Raises:
		ValidationError: If fields do not validate.
	"""

	currency: str
	tax_note: str
	rounding: str
	time_format: str
	invoice_template: str
	invoice_output_dir: str
	invoice_number_format: str
	theme: str
	week_starts: str


DEFAULT_CONFIG = FreelanceConfig(
	currency="EUR",
	tax_note="Gemaess 19 UStG wird keine Umsatzsteuer berechnet.",
	rounding="up",
	time_format="24h",
	invoice_template="german",
	invoice_output_dir="~/Documents/Invoices",
	invoice_number_format="{YEAR}-{SEQ:03d}",
	theme="dark",
	week_starts="monday",
)


def get_config_path() -> Path:
	"""Return the configuration path, creating the directory if needed.

	Args:
		None.

	Returns:
		Path to the config.toml file.

	Raises:
		OSError: If the directory cannot be created.
	"""
	config_dir = Path.home() / ".freelance"
	config_dir.mkdir(parents=True, exist_ok=True)
	return config_dir / "config.toml"


def _extract_updates(raw: dict[str, Any]) -> dict[str, Any]:
	"""Extract flattened config updates from nested TOML data.

	Args:
		raw: Parsed TOML data.

	Returns:
		Flattened config values.

	Raises:
		None.
	"""
	defaults = raw.get("defaults", {}) if isinstance(raw, dict) else {}
	invoice = raw.get("invoice", {}) if isinstance(raw, dict) else {}
	display = raw.get("display", {}) if isinstance(raw, dict) else {}

	return {
		"currency": defaults.get("currency"),
		"tax_note": defaults.get("tax_note"),
		"rounding": defaults.get("rounding"),
		"time_format": defaults.get("time_format"),
		"invoice_template": invoice.get("template"),
		"invoice_output_dir": invoice.get("output_dir"),
		"invoice_number_format": invoice.get("number_format"),
		"theme": display.get("theme"),
		"week_starts": display.get("week_starts"),
	}


def _merge_with_defaults(raw: dict[str, Any]) -> FreelanceConfig:
	"""Merge raw config data with defaults, ignoring invalid values.

	Args:
		raw: Parsed TOML data.

	Returns:
		Merged configuration object.

	Raises:
		None.
	"""
	base = DEFAULT_CONFIG.model_dump()
	updates = _extract_updates(raw)

	for key, value in updates.items():
		if value is None:
			continue
		candidate = base.copy()
		candidate[key] = value
		try:
			FreelanceConfig.model_validate(candidate)
		except ValidationError:
			LOGGER.warning("Invalid config value for %s; using default.", key)
			continue
		base[key] = value

	return FreelanceConfig.model_validate(base)


def load_config() -> FreelanceConfig:
	"""Load configuration from disk, merging with defaults.

	Args:
		None.

	Returns:
		Loaded configuration.

	Raises:
		OSError: If the config file cannot be read.
		ValueError: If TOML parsing fails.
	"""
	config_path = get_config_path()
	if not config_path.exists():
		return DEFAULT_CONFIG

	raw_text = config_path.read_text(encoding="utf-8")
	try:
		parsed = toml_reader.loads(raw_text)
	except Exception as exc:  # pragma: no cover - parser-specific exceptions
		LOGGER.warning("Invalid config file; using defaults.")
		return DEFAULT_CONFIG

	return _merge_with_defaults(parsed)


def save_config(config: FreelanceConfig) -> None:
	"""Write configuration to disk in TOML format.

	Args:
		config: Configuration to save.

	Returns:
		None.

	Raises:
		OSError: If the config file cannot be written.
	"""
	config_path = get_config_path()
	payload = {
		"defaults": {
			"currency": config.currency,
			"tax_note": config.tax_note,
			"rounding": config.rounding,
			"time_format": config.time_format,
		},
		"invoice": {
			"template": config.invoice_template,
			"output_dir": config.invoice_output_dir,
			"number_format": config.invoice_number_format,
		},
		"display": {
			"theme": config.theme,
			"week_starts": config.week_starts,
		},
	}
	config_path.write_text(toml_writer.dumps(payload), encoding="utf-8")
