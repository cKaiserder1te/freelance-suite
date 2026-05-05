"""Rich display helpers for CLI output."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.style import Style

from .db.models import Client, Project, TimeEntry

THEME: dict[str, str] = {
	"primary": "cyan",
	"secondary": "magenta",
	"muted": "grey62",
	"success": "green",
	"error": "red",
	"warning": "yellow",
}

CONSOLE = Console()


def _format_duration(seconds: int) -> str:
	"""Format a duration in seconds to H:MM:SS.

	Args:
		seconds: Duration in seconds.

	Returns:
		Duration string.

	Raises:
		None.
	"""
	duration = timedelta(seconds=max(0, seconds))
	total_seconds = int(duration.total_seconds())
	hours = total_seconds // 3600
	minutes = (total_seconds % 3600) // 60
	secs = total_seconds % 60
	return f"{hours}:{minutes:02d}:{secs:02d}"


def _format_money(amount: float | None) -> str:
	"""Format a monetary amount with two decimals.

	Args:
		amount: Amount to format.

	Returns:
		Formatted amount string.

	Raises:
		None.
	"""
	if amount is None:
		return "-"
	return f"{amount:.2f}"


def _elapsed_seconds(entry: TimeEntry) -> int:
	"""Calculate elapsed seconds for a running entry.

	Args:
		entry: Time entry to measure.

	Returns:
		Elapsed seconds.

	Raises:
		None.
	"""
	now = datetime.now(tz=entry.started_at.tzinfo)
	elapsed = (now - entry.started_at).total_seconds() - entry.paused_duration
	return max(0, int(elapsed))


def _build_entries_table(
	entries: list[TimeEntry],
	projects: dict[int, Project],
	clients: dict[int, Client],
) -> Table:
	"""Build a Rich table for time entries.

	Args:
		entries: Time entries to render.
		projects: Mapping of project ID to Project.
		clients: Mapping of client ID to Client.

	Returns:
		Rich Table instance.

	Raises:
		None.
	"""
	table = Table(show_header=True, header_style=Style(color=THEME["primary"]))
	table.add_column("Date", style=Style(color=THEME["muted"]))
	table.add_column("Client")
	table.add_column("Project")
	table.add_column("Task")
	table.add_column("Duration", justify="right")
	table.add_column("Amount", justify="right")

	for entry in entries:
		project = projects.get(entry.project_id)
		client = clients.get(project.client_id) if project else None

		if entry.stopped_at is None:
			duration_seconds = _elapsed_seconds(entry)
		else:
			duration_seconds = entry.duration_seconds or 0

		duration_label = _format_duration(duration_seconds)
		rate = project.hourly_rate if project else None
		amount = None
		if rate is not None:
			amount = (duration_seconds / 3600.0) * rate

		table.add_row(
			entry.started_at.date().isoformat(),
			client.name if client else "-",
			project.name if project else "-",
			entry.task or "-",
			duration_label,
			_format_money(amount),
		)

	return table


def show_active_timer(entry: TimeEntry, project: Project, client: Client) -> None:
	"""Display the active timer status panel.

	Args:
		entry: Active time entry.
		project: Associated project.
		client: Associated client.

	Returns:
		None.

	Raises:
		None.
	"""
	elapsed_seconds = _elapsed_seconds(entry) if entry.is_running else 0
	rate = project.hourly_rate
	amount = None
	if rate is not None:
		amount = (elapsed_seconds / 3600.0) * rate

	content = Table.grid(padding=(0, 1))
	content.add_row("Project", Text(project.name, style=Style(color=THEME["primary"])))
	content.add_row("Client", Text(client.name, style=Style(color=THEME["secondary"])))
	content.add_row("Task", Text(entry.task or "-"))
	content.add_row("Elapsed", Text(_format_duration(elapsed_seconds)))
	content.add_row("Amount", Text(_format_money(amount)))

	panel = Panel(
		content,
		title="Active Timer",
		border_style=Style(color=THEME["primary"]),
	)
	CONSOLE.print(panel)


def show_time_entries_table(
	entries: list[TimeEntry],
	projects: dict[int, Project],
	clients: dict[int, Client],
) -> None:
	"""Render a table of time entries.

	Args:
		entries: Time entries to display.
		projects: Mapping of project ID to Project.
		clients: Mapping of client ID to Client.

	Returns:
		None.

	Raises:
		None.
	"""
	table = _build_entries_table(entries, projects, clients)
	CONSOLE.print(table)


def show_weekly_report(data: dict[str, Any]) -> None:
	"""Render a weekly report layout.

	Args:
		data: Report data payload.

	Returns:
		None.

	Raises:
		None.
	"""
	entries = data.get("entries", [])
	projects = data.get("projects", {})
	clients = data.get("clients", {})
	summary = data.get("summary", {})
	week_range = data.get("range", "Weekly Report")

	header = Panel(
		Text(str(week_range), style=Style(color=THEME["primary"], bold=True)),
		border_style=Style(color=THEME["primary"]),
	)
	entries_table = _build_entries_table(entries, projects, clients)

	summary_table = Table.grid(padding=(0, 1))
	summary_table.add_row("Total Hours", str(summary.get("total_hours", "-")))
	summary_table.add_row("Total Revenue", str(summary.get("total_revenue", "-")))
	summary_table.add_row("Top Project", str(summary.get("top_project", "-")))
	summary_panel = Panel(
		summary_table,
		title="Summary",
		border_style=Style(color=THEME["secondary"]),
	)

	layout = Layout()
	layout.split_column(
		Layout(header, name="header", size=3),
		Layout(entries_table, name="entries"),
		Layout(summary_panel, name="summary", size=8),
	)
	CONSOLE.print(layout)


def show_monthly_report(data: dict[str, Any]) -> None:
	"""Render a monthly report layout.

	Args:
		data: Report data payload.

	Returns:
		None.

	Raises:
		None.
	"""
	entries = data.get("entries", [])
	projects = data.get("projects", {})
	clients = data.get("clients", {})
	summary = data.get("summary", {})
	month_range = data.get("range", "Monthly Report")

	header = Panel(
		Text(str(month_range), style=Style(color=THEME["primary"], bold=True)),
		border_style=Style(color=THEME["primary"]),
	)
	entries_table = _build_entries_table(entries, projects, clients)

	summary_table = Table.grid(padding=(0, 1))
	summary_table.add_row("Total Hours", str(summary.get("total_hours", "-")))
	summary_table.add_row("Total Revenue", str(summary.get("total_revenue", "-")))
	summary_table.add_row("Top Project", str(summary.get("top_project", "-")))
	summary_panel = Panel(
		summary_table,
		title="Summary",
		border_style=Style(color=THEME["secondary"]),
	)

	layout = Layout()
	layout.split_column(
		Layout(header, name="header", size=3),
		Layout(entries_table, name="entries"),
		Layout(summary_panel, name="summary", size=8),
	)
	CONSOLE.print(layout)


def show_projects_table(projects: list[Project], clients: dict[int, Client]) -> None:
	"""Render a table of projects.

	Args:
		projects: Projects to display.
		clients: Mapping of client ID to Client.

	Returns:
		None.

	Raises:
		None.
	"""
	table = Table(show_header=True, header_style=Style(color=THEME["primary"]))
	table.add_column("Name")
	table.add_column("Client")
	table.add_column("Rate", justify="right")
	table.add_column("Active", justify="center")
	table.add_column("Total Hours", justify="right")

	for project in projects:
		client = clients.get(project.client_id)
		table.add_row(
			project.name,
			client.name if client else "-",
			_format_money(project.hourly_rate),
			"Yes" if project.active else "No",
			"-",
		)

	CONSOLE.print(table)


def show_clients_table(clients: list[Client]) -> None:
	"""Render a table of clients.

	Args:
		clients: Clients to display.

	Returns:
		None.

	Raises:
		None.
	"""
	table = Table(show_header=True, header_style=Style(color=THEME["primary"]))
	table.add_column("Name")
	table.add_column("Email")
	table.add_column("Rate", justify="right")
	table.add_column("Projects", justify="right")
	table.add_column("Revenue", justify="right")

	for client in clients:
		table.add_row(
			client.name,
			client.email or "-",
			_format_money(client.default_rate),
			"-",
			"-",
		)

	CONSOLE.print(table)


def show_status_idle() -> None:
	"""Display the idle status panel.

	Args:
		None.

	Returns:
		None.

	Raises:
		None.
	"""
	message = "No active timer. Run `ft start <project> <task>`."
	panel = Panel(
		Text(message, style=Style(color=THEME["muted"])),
		border_style=Style(color=THEME["muted"]),
	)
	CONSOLE.print(panel)


def show_error(message: str) -> None:
	"""Display an error panel.

	Args:
		message: Error message to display.

	Returns:
		None.

	Raises:
		None.
	"""
	panel = Panel(
		Text(f"ERROR: {message}", style=Style(color=THEME["error"], bold=True)),
		border_style=Style(color=THEME["error"]),
	)
	CONSOLE.print(panel)


def show_success(message: str) -> None:
	"""Display a success panel.

	Args:
		message: Success message to display.

	Returns:
		None.

	Raises:
		None.
	"""
	panel = Panel(
		Text(f"SUCCESS: {message}", style=Style(color=THEME["success"], bold=True)),
		border_style=Style(color=THEME["success"]),
	)
	CONSOLE.print(panel)
