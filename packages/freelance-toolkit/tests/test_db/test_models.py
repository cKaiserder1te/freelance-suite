"""Tests for database models."""

from datetime import datetime

import pytest

from freelance_toolkit.db.models import Client, Project, TimeEntry


def test_client_repr() -> None:
    """Ensure Client __repr__ includes key fields.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.
    """
    client = Client(id=1, name="Acme", email="info@acme.test", default_rate=120.0)
    assert "Client" in repr(client)
    assert "Acme" in repr(client)


def test_project_repr() -> None:
    """Ensure Project __repr__ includes key fields.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.
    """
    project = Project(
        id=2,
        client_id=1,
        name="Website",
        hourly_rate=95.0,
        active=True,
    )
    assert "Project" in repr(project)
    assert "Website" in repr(project)


def test_time_entry_status_properties() -> None:
    """Verify running and paused status helpers.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.
    """
    running_entry = TimeEntry(
        project_id=1,
        task="Support",
        started_at=datetime(2025, 1, 1, 9, 0, 0),
        paused_duration=0,
    )
    assert running_entry.is_running is True
    assert running_entry.is_paused is False

    paused_entry = TimeEntry(
        project_id=1,
        task="Support",
        started_at=datetime(2025, 1, 1, 9, 0, 0),
        paused_duration=300,
    )
    assert paused_entry.is_running is True
    assert paused_entry.is_paused is True


def test_time_entry_duration_and_billable_amount() -> None:
    """Compute duration and billable amount.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.
    """
    entry = TimeEntry(
        project_id=1,
        task="Development",
        started_at=datetime(2025, 1, 1, 9, 0, 0),
        stopped_at=datetime(2025, 1, 1, 11, 0, 0),
        paused_duration=600,
    )
    assert entry.duration_seconds == 6600
    assert entry.duration_hours == pytest.approx(6600 / 3600.0)
    assert entry.billable_amount(100.0) == pytest.approx((6600 / 3600.0) * 100.0)


def test_time_entry_repr() -> None:
    """Ensure TimeEntry __repr__ includes key fields.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.
    """
    entry = TimeEntry(
        id=3,
        project_id=1,
        task="Review",
        started_at=datetime(2025, 1, 1, 12, 0, 0),
    )
    assert "TimeEntry" in repr(entry)
    assert "Review" in repr(entry)
