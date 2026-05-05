"""Tests for project CLI commands."""

from typer.testing import CliRunner

from freelance_toolkit.main import app


def test_project_add_and_list(runner: CliRunner, db_path) -> None:
    """Add a project and list it.

    Args:
        runner: Typer CLI runner.
        db_path: Temporary database path fixture.

    Returns:
        None.

    Raises:
        None.
    """
    runner.invoke(app, ["client", "add", "Acme", "--email", "info@acme.test", "--rate", "120"])

    result = runner.invoke(
        app, ["project", "add", "Website", "--client", "Acme", "--rate", "95"]
    )
    assert result.exit_code == 0

    result = runner.invoke(app, ["project", "list"])
    assert result.exit_code == 0
    assert "Website" in result.output
