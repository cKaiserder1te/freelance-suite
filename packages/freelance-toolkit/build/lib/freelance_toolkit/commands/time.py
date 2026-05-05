"""Time tracking commands for the CLI."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from sqlmodel import select

from ..db.database import get_session
from ..db.models import Client, Project, TimeEntry
from ..display import show_active_timer, show_error, show_status_idle, show_success

time_app = typer.Typer(help="Time tracking commands")

PAUSED_MARKER = "paused_at="


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


def _get_active_entry(session) -> Optional[TimeEntry]:
	"""Return the currently active time entry.

	Args:
		session: Database session.

	Returns:
		Active TimeEntry or None.

	Raises:
		None.
	"""
	statement = select(TimeEntry).where(TimeEntry.stopped_at.is_(None))
	return session.exec(statement).first()


def _get_project_by_name(session, name: str) -> Optional[Project]:
	"""Find a project by name.

	Args:
		session: Database session.
		name: Project name.

	Returns:
		Project or None.

	Raises:
		None.
	"""
	statement = select(Project).where(Project.name == name)
	return session.exec(statement).first()


def _extract_paused_at(notes: Optional[str]) -> Optional[datetime]:
	"""Extract paused timestamp from notes.

	Args:
		notes: Notes string.

	Returns:
		Paused timestamp or None.

	Raises:
		ValueError: If the timestamp cannot be parsed.
	"""
	if not notes:
		return None
	for line in notes.splitlines():
		if line.startswith(PAUSED_MARKER):
			return datetime.fromisoformat(line[len(PAUSED_MARKER) :])
	return None


def _set_paused_marker(notes: Optional[str], paused_at: datetime) -> str:
	"""Set the paused marker in notes.

	Args:
		notes: Existing notes.
		paused_at: Paused timestamp.

	Returns:
		Updated notes string.

	Raises:
		None.
	"""
	lines = [line for line in (notes or "").splitlines() if line]
	lines = [line for line in lines if not line.startswith(PAUSED_MARKER)]
	lines.append(f"{PAUSED_MARKER}{paused_at.isoformat()}")
	return "\n".join(lines)


def _clear_paused_marker(notes: Optional[str]) -> str:
	"""Remove the paused marker from notes.

	Args:
		notes: Existing notes.

	Returns:
		Updated notes string.

	Raises:
		None.
	"""
	if not notes:
		return ""
	lines = [line for line in notes.splitlines() if line]
	lines = [line for line in lines if not line.startswith(PAUSED_MARKER)]
	return "\n".join(lines)


@time_app.command("start")
def start(project_name: str, task: str) -> None:
	"""Start a time entry for a project.

	Args:
		project_name: Project name.
		task: Task description.

	Returns:
		None.

	Raises:
		typer.Exit: On validation errors.
	"""
	with _with_spinner("Starting timer") as progress:
		with get_session() as session:
			active = _get_active_entry(session)
			if active:
				progress.stop()
				show_error("A timer is already running.")
				raise typer.Exit(code=1)

			project = _get_project_by_name(session, project_name)
			if not project:
				progress.stop()
				show_error("Project not found.")
				raise typer.Exit(code=1)

			entry = TimeEntry(
				project_id=project.id,
				task=task,
				started_at=datetime.now(),
			)
			session.add(entry)
			session.commit()
			session.refresh(entry)

			client = session.get(Client, project.client_id)
			progress.stop()
			if client:
				show_active_timer(entry, project, client)


@time_app.command("stop")
def stop() -> None:
	"""Stop the active time entry.

	Args:
		None.

	Returns:
		None.

	Raises:
		typer.Exit: On validation errors.
	"""
	with _with_spinner("Stopping timer") as progress:
		with get_session() as session:
			entry = _get_active_entry(session)
			if not entry:
				progress.stop()
				show_status_idle()
				raise typer.Exit(code=1)

			paused_at = _extract_paused_at(entry.notes)
			if paused_at:
				pause_delta = datetime.now() - paused_at
				entry.paused_duration = max(0, entry.paused_duration - 1) + int(
					pause_delta.total_seconds()
				)
				entry.notes = _clear_paused_marker(entry.notes)

			entry.stopped_at = datetime.now()
			session.add(entry)
			session.commit()

			project = session.get(Project, entry.project_id)
			client = session.get(Client, project.client_id) if project else None
			progress.stop()

			if entry.duration_hours is not None and project and project.hourly_rate:
				amount = entry.billable_amount(project.hourly_rate)
				show_success(
					f"Stopped timer. Duration: {entry.duration_hours:.2f}h, "
					f"Amount: {amount:.2f}"
				)
			elif client:
				show_success("Stopped timer.")


@time_app.command("pause")
def pause() -> None:
	"""Pause the active timer.

	Args:
		None.

	Returns:
		None.

	Raises:
		typer.Exit: On validation errors.
	"""
	with _with_spinner("Pausing timer") as progress:
		with get_session() as session:
			entry = _get_active_entry(session)
			if not entry:
				progress.stop()
				show_status_idle()
				raise typer.Exit(code=1)

			if _extract_paused_at(entry.notes):
				progress.stop()
				show_error("Timer is already paused.")
				raise typer.Exit(code=1)

			entry.notes = _set_paused_marker(entry.notes, datetime.now())
			entry.paused_duration = max(1, entry.paused_duration + 1)
			session.add(entry)
			session.commit()
			progress.stop()
			show_success("Paused timer.")


@time_app.command("resume")
def resume() -> None:
	"""Resume a paused timer.

	Args:
		None.

	Returns:
		None.

	Raises:
		typer.Exit: On validation errors.
	"""
	with _with_spinner("Resuming timer") as progress:
		with get_session() as session:
			entry = _get_active_entry(session)
			if not entry:
				progress.stop()
				show_status_idle()
				raise typer.Exit(code=1)

			paused_at = _extract_paused_at(entry.notes)
			if not paused_at:
				progress.stop()
				show_error("Timer is not paused.")
				raise typer.Exit(code=1)

			pause_delta = datetime.now() - paused_at
			entry.paused_duration = max(0, entry.paused_duration - 1) + int(
				pause_delta.total_seconds()
			)
			entry.notes = _clear_paused_marker(entry.notes)
			session.add(entry)
			session.commit()
			progress.stop()
			show_success("Resumed timer.")


@time_app.command("status")
def status() -> None:
	"""Show the active timer status.

	Args:
		None.

	Returns:
		None.

	Raises:
		None.
	"""
	with _with_spinner("Checking status") as progress:
		with get_session() as session:
			entry = _get_active_entry(session)
			if not entry:
				progress.stop()
				show_status_idle()
				return

			project = session.get(Project, entry.project_id)
			client = session.get(Client, project.client_id) if project else None
			progress.stop()
			if project and client:
				show_active_timer(entry, project, client)
