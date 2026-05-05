"""Reporting commands for the CLI."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from sqlmodel import select

from ..db.database import get_session
from ..db.models import Client, Project, TimeEntry
from ..display import show_error, show_monthly_report, show_success, show_weekly_report

report_app = typer.Typer(help="Reporting commands")


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


def _week_range(target: date) -> tuple[date, date]:
	"""Return the Monday-Sunday range for a date.

	Args:
		target: Target date.

	Returns:
		Tuple of start and end dates.

	Raises:
		None.
	"""
	start = target - timedelta(days=target.isoweekday() - 1)
	end = start + timedelta(days=6)
	return start, end


def _month_range(target: date) -> tuple[date, date]:
	"""Return the start and end date for a month.

	Args:
		target: Target date.

	Returns:
		Tuple of start and end dates.

	Raises:
		None.
	"""
	start = target.replace(day=1)
	next_month = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
	end = next_month - timedelta(days=1)
	return start, end


def _aggregate_entries(
	entries: list[TimeEntry],
	projects: dict[int, Project],
) -> dict[str, Any]:
	"""Aggregate time entry metrics.

	Args:
		entries: Time entries to aggregate.
		projects: Mapping of project IDs to projects.

	Returns:
		Summary dictionary.

	Raises:
		None.
	"""
	total_hours = 0.0
	total_revenue = 0.0
	project_totals: dict[int, float] = {}

	for entry in entries:
		if entry.duration_hours is None:
			continue
		total_hours += entry.duration_hours
		project = projects.get(entry.project_id)
		if project and project.hourly_rate:
			revenue = entry.billable_amount(project.hourly_rate) or 0.0
			total_revenue += revenue
			project_totals[entry.project_id] = project_totals.get(entry.project_id, 0.0) + revenue

	top_project = None
	if project_totals:
		top_project_id = max(project_totals, key=project_totals.get)
		top_project = projects[top_project_id].name

	return {
		"total_hours": round(total_hours, 2),
		"total_revenue": round(total_revenue, 2),
		"top_project": top_project or "-",
	}


@report_app.command("week")
def report_week(
	week: str = typer.Option("", "--week", help="ISO week format YYYY-WNN"),
) -> None:
	"""Generate a weekly report.

	Args:
		week: ISO week string.

	Returns:
		None.

	Raises:
		typer.Exit: On validation errors.
	"""
	if week:
		try:
			year_str, week_str = week.split("-W")
			target = date.fromisocalendar(int(year_str), int(week_str), 1)
		except ValueError:
			show_error("Invalid week format. Use YYYY-WNN.")
			raise typer.Exit(code=1)
	else:
		target = date.today()

	start, end = _week_range(target)
	with _with_spinner("Loading weekly report") as progress:
		with get_session() as session:
			entries = session.exec(
				select(TimeEntry).where(
					TimeEntry.started_at >= datetime.combine(start, datetime.min.time()),
					TimeEntry.started_at <= datetime.combine(end, datetime.max.time()),
				)
			).all()
			projects = session.exec(select(Project)).all()
			clients = session.exec(select(Client)).all()
			progress.stop()

			project_map = {project.id: project for project in projects}
			client_map = {client.id: client for client in clients}
			summary = _aggregate_entries(entries, project_map)
			show_weekly_report(
				{
					"entries": entries,
					"projects": project_map,
					"clients": client_map,
					"summary": summary,
					"range": f"Week {start} - {end}",
				}
			)


@report_app.command("month")
def report_month(
	month: str = typer.Option("", "--month", help="Month format YYYY-MM"),
) -> None:
	"""Generate a monthly report.

	Args:
		month: Month string.

	Returns:
		None.

	Raises:
		typer.Exit: On validation errors.
	"""
	if month:
		try:
			target = datetime.strptime(month, "%Y-%m").date()
		except ValueError:
			show_error("Invalid month format. Use YYYY-MM.")
			raise typer.Exit(code=1)
	else:
		target = date.today()

	start, end = _month_range(target)
	with _with_spinner("Loading monthly report") as progress:
		with get_session() as session:
			entries = session.exec(
				select(TimeEntry).where(
					TimeEntry.started_at >= datetime.combine(start, datetime.min.time()),
					TimeEntry.started_at <= datetime.combine(end, datetime.max.time()),
				)
			).all()
			projects = session.exec(select(Project)).all()
			clients = session.exec(select(Client)).all()
			progress.stop()

			project_map = {project.id: project for project in projects}
			client_map = {client.id: client for client in clients}
			summary = _aggregate_entries(entries, project_map)
			show_monthly_report(
				{
					"entries": entries,
					"projects": project_map,
					"clients": client_map,
					"summary": summary,
					"range": f"Month {start:%Y-%m}",
				}
			)


@report_app.command("client")
def report_client(name: str) -> None:
	"""Generate a report for a single client.

	Args:
		name: Client name.

	Returns:
		None.

	Raises:
		typer.Exit: On validation errors.
	"""
	with _with_spinner("Loading client report") as progress:
		with get_session() as session:
			client = session.exec(select(Client).where(Client.name == name)).first()
			if not client:
				progress.stop()
				show_error("Client not found.")
				raise typer.Exit(code=1)

			projects = session.exec(
				select(Project).where(Project.client_id == client.id)
			).all()
			project_ids = [project.id for project in projects]
			if not project_ids:
				progress.stop()
				show_success("No projects found for client.")
				return

			entries = session.exec(
				select(TimeEntry).where(TimeEntry.project_id.in_(project_ids))
			).all()
			progress.stop()

			project_map = {project.id: project for project in projects}
			summary = _aggregate_entries(entries, project_map)
			show_weekly_report(
				{
					"entries": entries,
					"projects": project_map,
					"clients": {client.id: client},
					"summary": summary,
					"range": f"Client {client.name}",
				}
			)
