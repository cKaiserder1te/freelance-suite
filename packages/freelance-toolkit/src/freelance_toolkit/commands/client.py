"""Client management commands for the CLI."""

from __future__ import annotations

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from sqlmodel import select

from ..db.database import get_session
from ..db.models import Client
from ..display import show_clients_table, show_error, show_success

client_app = typer.Typer(help="Client management commands")


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


@client_app.command("add")
def add(
	name: str,
	email: str = typer.Option("", "--email", help="Client email"),
	rate: float = typer.Option(0.0, "--rate", help="Default hourly rate"),
) -> None:
	"""Add a new client.

	Args:
		name: Client name.
		email: Client email.
		rate: Default hourly rate.

	Returns:
		None.

	Raises:
		typer.Exit: On validation errors.
	"""
	with _with_spinner("Creating client") as progress:
		with get_session() as session:
			existing = session.exec(select(Client).where(Client.name == name)).first()
			if existing:
				progress.stop()
				show_error("Client already exists.")
				raise typer.Exit(code=1)

			client = Client(
				name=name,
				email=email or None,
				default_rate=rate or None,
			)
			session.add(client)
			session.commit()
			progress.stop()
			show_success("Client created.")


@client_app.command("list")
def list_clients() -> None:
	"""List clients.

	Args:
		None.

	Returns:
		None.

	Raises:
		None.
	"""
	with _with_spinner("Loading clients") as progress:
		with get_session() as session:
			clients = session.exec(select(Client)).all()
			progress.stop()
			show_clients_table(clients)
