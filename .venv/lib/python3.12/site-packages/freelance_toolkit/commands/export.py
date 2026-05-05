"""Export commands for the CLI."""

from __future__ import annotations

import csv
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from sqlmodel import select

from ..config import load_config
from ..db.database import get_session
from ..db.models import Client, Project, TimeEntry
from ..display import show_error, show_success

export_app = typer.Typer(help="Export commands")

DEFAULT_CSV_NAME = "time_entries.csv"
DEFAULT_SENDER_NAME = "Freelancer"
DEFAULT_CLIENT_NAME = "Client"
DEFAULT_ITEM_DESCRIPTION = "Work"
DEFAULT_ADDRESS = ""


def _with_spinner(message: str) -> Progress:
	"""Create a progress spinner context.

	Args:
		message: Spinner message.

	Returns:
		Progress instance.

	Raises:
		None.
	"""
	progress = Progress(SpinnerColumn(), TextColumn("{task.description}"), transient=True)
	progress.add_task(message, total=None)
	return progress


def _month_range(target: date) -> tuple[datetime, datetime]:
	"""Return datetime range for the given month.

	Args:
		target: Target month date.

	Returns:
		Start and end datetime values.

	Raises:
		None.
	"""
	start = target.replace(day=1)
	next_month = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
	end = next_month - timedelta(seconds=1)
	return (
		datetime.combine(start, datetime.min.time()),
		datetime.combine(end, datetime.max.time()),
	)


def _load_entries(month: str | None) -> list[TimeEntry]:
	"""Load time entries for an optional month filter.

	Args:
		month: Month string in YYYY-MM format.

	Returns:
		List of time entries.

	Raises:
		typer.Exit: If month format is invalid.
	"""
	with get_session() as session:
		if month:
			try:
				target = datetime.strptime(month, "%Y-%m").date()
			except ValueError:
				show_error("Invalid month format. Use YYYY-MM.")
				raise typer.Exit(code=1)

			start, end = _month_range(target)
			statement = select(TimeEntry).where(
				TimeEntry.started_at >= start,
				TimeEntry.started_at <= end,
			)
		else:
			statement = select(TimeEntry)

		return session.exec(statement).all()


@export_app.command("csv")
def export_csv(
	month: str = typer.Option("", "--month", help="Month format YYYY-MM"),
	output: str = typer.Option("", "--output", help="Output CSV path"),
) -> None:
	"""Export time entries to CSV.

	Args:
		month: Month filter.
		output: Output file path.

	Returns:
		None.

	Raises:
		typer.Exit: On validation errors.
	"""
	with _with_spinner("Exporting CSV") as progress:
		entries = _load_entries(month or None)
		with get_session() as session:
			projects = {project.id: project for project in session.exec(select(Project))}
			clients = {client.id: client for client in session.exec(select(Client))}
		progress.stop()

	output_path = Path(output) if output else Path(DEFAULT_CSV_NAME)
	with output_path.open("w", newline="", encoding="utf-8") as handle:
		writer = csv.writer(handle)
		writer.writerow([
			"date",
			"client",
			"project",
			"task",
			"duration_hours",
			"amount",
		])
		for entry in entries:
			project = projects.get(entry.project_id)
			client = clients.get(project.client_id) if project else None
			duration_hours = entry.duration_hours or 0.0
			amount = None
			if project and project.hourly_rate:
				amount = duration_hours * project.hourly_rate
			writer.writerow([
				entry.started_at.date().isoformat(),
				client.name if client else "-",
				project.name if project else "-",
				entry.task or "-",
				f"{duration_hours:.2f}",
				f"{amount:.2f}" if amount is not None else "-",
			])

	show_success(f"CSV exported to {output_path}")


@export_app.command("invoice")
def export_invoice(
	month: str = typer.Option("", "--month", help="Month format YYYY-MM"),
) -> None:
	"""Export a PDF invoice using invoice-gen if available.

	Args:
		month: Month filter.

	Returns:
		None.

	Raises:
		typer.Exit: On validation errors.
	"""
	try:
		from invoice_gen import generate_invoice
	except Exception:
		show_error("invoice-gen is not installed.")
		raise typer.Exit(code=1)

	config = load_config()
	entries = _load_entries(month or None)
	if not entries:
		show_error("No entries found for invoice export.")
		raise typer.Exit(code=1)

	invoice_data = {
		"sender": {
			"name": DEFAULT_SENDER_NAME,
			"address": DEFAULT_ADDRESS,
			"email": DEFAULT_ADDRESS,
			"tax_note": config.tax_note,
		},
		"client": {
			"name": DEFAULT_CLIENT_NAME,
			"address": DEFAULT_ADDRESS,
		},
		"meta": {
			"number": config.invoice_number_format.format(
				YEAR=date.today().year, SEQ=1
			),
			"invoice_date": date.today().isoformat(),
			"due_date": (date.today() + timedelta(days=14)).isoformat(),
			"currency": config.currency,
		},
		"items": [
			{
				"description": entry.task or DEFAULT_ITEM_DESCRIPTION,
				"quantity": entry.duration_hours or 0.0,
				"unit": "h",
				"unit_price": 0.0,
			}
			for entry in entries
		],
	}

	output_dir = Path(config.invoice_output_dir).expanduser()
	output_dir.mkdir(parents=True, exist_ok=True)
	output_path = output_dir / "invoice.pdf"
	generate_invoice(invoice_data, output=str(output_path), template=config.invoice_template)
	show_success(f"Invoice exported to {output_path}")
