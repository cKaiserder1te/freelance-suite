"""Tests for time tracking CLI commands."""

from typer.testing import CliRunner

from freelance_toolkit.main import app


def test_start_status_stop(runner: CliRunner, db_path) -> None:
    """Start, check status, and stop a timer.

    Args:
        runner: Typer CLI runner.
        db_path: Temporary database path fixture.

    Returns:
        None.

    Raises:
        None.
    """
    runner.invoke(app, ["client", "add", "Acme", "--email", "info@acme.test", "--rate", "120"])
    runner.invoke(
        app, ["project", "add", "Website", "--client", "Acme", "--rate", "95"]
    )

    result = runner.invoke(app, ["start", "Website", "Initial task"])
    assert result.exit_code == 0

    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0

    result = runner.invoke(app, ["stop"])
    assert result.exit_code == 0
