"""Typer application entry point for the freelance-toolkit CLI."""

from __future__ import annotations

import typer
from rich.panel import Panel
from rich.text import Text
from rich.style import Style
from rich.console import Console

from .commands.client import client_app
from .commands.export import export_app
from .commands.project import project_app
from .commands.report import report_app
from .commands.time import time_app
from .db.database import init_db

app = typer.Typer(name="ft", help="freelance-toolkit - terminal-native freelance OS")
CONSOLE = Console()

app.add_typer(time_app)
app.add_typer(project_app, name="project")
app.add_typer(client_app, name="client")
app.add_typer(report_app, name="report")
app.add_typer(export_app, name="export")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
	"""Initialize the database and show a welcome panel.

	Args:
		ctx: Typer context instance.

	Returns:
		None.

	Raises:
		None.
	"""
	init_db()
	if ctx.invoked_subcommand is None:
		panel = Panel(
			Text(
				"Welcome to freelance-toolkit. Use --help to see available commands.",
				style=Style(color="cyan"),
			),
			title="freelance-toolkit",
			border_style=Style(color="cyan"),
		)
		CONSOLE.print(panel)
