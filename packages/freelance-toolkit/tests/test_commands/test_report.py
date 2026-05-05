"""Tests for report CLI commands."""

from datetime import datetime, timedelta

from typer.testing import CliRunner

from freelance_toolkit.db.database import get_session
from freelance_toolkit.db.models import Client, Project, TimeEntry
from freelance_toolkit.main import app


def test_weekly_report(runner: CliRunner, db_path) -> None:
    """Generate a weekly report with sample data.

    Args:
        runner: Typer CLI runner.
        db_path: Temporary database path fixture.

    Returns:
        None.

    Raises:
        None.
    """
    with get_session() as session:
        client = Client(name="Acme", email="info@acme.test", default_rate=120.0)
        session.add(client)
        session.commit()
        session.refresh(client)

        project = Project(name="Website", client_id=client.id, hourly_rate=95.0)
        session.add(project)
        session.commit()
        session.refresh(project)

        started = datetime.now() - timedelta(hours=2)
        stopped = datetime.now() - timedelta(hours=1)
        entry = TimeEntry(
            project_id=project.id,
            task="Development",
            started_at=started,
            stopped_at=stopped,
            paused_duration=0,
        )
        session.add(entry)
        session.commit()

    result = runner.invoke(app, ["report", "week"])
    assert result.exit_code == 0
    assert "Summary" in result.output


def test_monthly_report(runner: CliRunner, db_path) -> None:
    """Generate a monthly report with sample data.

    Args:
        runner: Typer CLI runner.
        db_path: Temporary database path fixture.

    Returns:
        None.

    Raises:
        None.
    """
    with get_session() as session:
        client = Client(name="Beta", email="info@beta.test", default_rate=110.0)
        session.add(client)
        session.commit()
        session.refresh(client)

        project = Project(name="Mobile", client_id=client.id, hourly_rate=90.0)
        session.add(project)
        session.commit()
        session.refresh(project)

        started = datetime.now() - timedelta(days=1, hours=2)
        stopped = datetime.now() - timedelta(days=1, hours=1)
        entry = TimeEntry(
            project_id=project.id,
            task="Design",
            started_at=started,
            stopped_at=stopped,
            paused_duration=0,
        )
        session.add(entry)
        session.commit()

    result = runner.invoke(app, ["report", "month"])
    assert result.exit_code == 0
    assert "Summary" in result.output
