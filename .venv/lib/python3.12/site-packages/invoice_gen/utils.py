"""Shared helpers for assets and file handling."""

from __future__ import annotations

import base64
import mimetypes
from pathlib import Path


def embed_image_as_base64(path: str | Path) -> str:
	"""Embed an image file as a base64 data URI.

	Args:
		path: Path to the image file.

	Returns:
		Data URI string suitable for HTML embedding.

	Raises:
		FileNotFoundError: If the image file does not exist.
		OSError: If the file cannot be read.
		ValueError: If the image mime type cannot be determined.
	"""
	file_path = Path(path)
	if not file_path.exists():
		raise FileNotFoundError(f"Image not found: {file_path}")

	mime_type, _ = mimetypes.guess_type(file_path.name)
	if not mime_type:
		raise ValueError("Unable to determine image mime type")

	encoded = base64.b64encode(file_path.read_bytes()).decode("ascii")
	return f"data:{mime_type};base64,{encoded}"


def get_template_dir() -> Path:
	"""Return the templates directory path.

	Args:
		None.

	Returns:
		Absolute Path to the templates directory.

	Raises:
		None.
	"""
	return Path(__file__).resolve().parent / "templates"
