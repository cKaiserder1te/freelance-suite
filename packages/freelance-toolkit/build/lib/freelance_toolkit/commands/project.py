"""Project management commands for the CLI."""

from __future__ import annotations

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from sqlmodel import select

from ..db.database import get_session
from ..db.models import Client, Project
from ..display import show_error, show_projects_table, show_success

project_app = typer.Typer(help="Project management commands")


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


@project_app.command("add")
def add(
	name: str,
	client: str = typer.Option(..., "--client", help="Client name"),
	rate: float = typer.Option(..., "--rate", help="Hourly rate"),
) -> None:
	"""Add a new project.

	Args:
		name: Project name.
		client: Client name.
		rate: Hourly rate.

	Returns:
		None.

	Raises:
		typer.Exit: On validation errors.
	"""
	with _with_spinner("Creating project") as progress:
		with get_session() as session:
			existing = session.exec(select(Project).where(Project.name == name)).first()
			if existing:
				progress.stop()
				show_error("Project already exists.")
				raise typer.Exit(code=1)

			client_row = session.exec(
				select(Client).where(Client.name == client)
			).first()
			if not client_row:
				progress.stop()
				show_error("Client not found.")
				raise typer.Exit(code=1)

			project = Project(name=name, client_id=client_row.id, hourly_rate=rate)
			session.add(project)
			session.commit()
			progress.stop()
			show_success("Project created.")


@project_app.command("list")
def list_projects() -> None:
	"""List projects.

	Args:
		None.

	Returns:
		None.

	Raises:
		None.
	"""
	with _with_spinner("Loading projects") as progress:
		with get_session() as session:
			projects = session.exec(select(Project)).all()
			clients = session.exec(select(Client)).all()
			progress.stop()
			client_map = {client.id: client for client in clients}
			show_projects_table(projects, client_map)


@project_app.command("delete")
def delete_project(name: str) -> None:
	"""Delete a project by name.

	Args:
		name: Project name.

	Returns:
		None.

	Raises:
		typer.Exit: On validation errors.
	"""
	if not typer.confirm("Delete project?", abort=True):
		raise typer.Abort()

	with _with_spinner("Deleting project") as progress:
		with get_session() as session:
			project = session.exec(select(Project).where(Project.name == name)).first()
			if not project:
				progress.stop()
				show_error("Project not found.")
				raise typer.Exit(code=1)

			session.delete(project)
			session.commit()
			progress.stop()
			show_success("Project deleted.")
