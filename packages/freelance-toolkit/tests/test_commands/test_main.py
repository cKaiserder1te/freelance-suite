"""Tests for the CLI main entry point."""

from typer.testing import CliRunner

from freelance_toolkit.main import app


def test_root_shows_welcome(runner: CliRunner, db_path) -> None:
    """Ensure the root command shows the welcome panel.

    Args:
        runner: Typer CLI runner.
        db_path: Temporary database path fixture.

    Returns:
        None.

    Raises:
        None.
    """
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "Welcome to freelance-toolkit" in result.output
