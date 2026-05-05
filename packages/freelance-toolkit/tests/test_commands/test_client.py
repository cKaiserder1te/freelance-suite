"""Tests for client CLI commands."""

from typer.testing import CliRunner

from freelance_toolkit.main import app


def test_client_add_and_list(runner: CliRunner, db_path) -> None:
    """Add a client and list it.

    Args:
        runner: Typer CLI runner.
        db_path: Temporary database path fixture.

    Returns:
        None.

    Raises:
        None.
    """
    result = runner.invoke(
        app, ["client", "add", "Acme", "--email", "info@acme.test", "--rate", "120"]
    )
    assert result.exit_code == 0

    result = runner.invoke(app, ["client", "list"])
    assert result.exit_code == 0
    assert "Acme" in result.output
