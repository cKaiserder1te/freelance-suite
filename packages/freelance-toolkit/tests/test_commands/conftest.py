"""Pytest fixtures for CLI command tests."""

from pathlib import Path
from typing import Generator

import pytest
from typer.testing import CliRunner

from freelance_toolkit.db import database


@pytest.fixture()
def runner() -> CliRunner:
    """Provide a Typer CLI runner.

    Args:
        None.

    Returns:
        CliRunner instance.

    Raises:
        None.
    """
    return CliRunner()


@pytest.fixture()
def db_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Provide an isolated database path for tests.

    Args:
        tmp_path: Temporary directory path.
        monkeypatch: Pytest monkeypatch fixture.

    Returns:
        Path to the test database file.

    Raises:
        None.
    """
    path = tmp_path / "data.db"

    def _path() -> Path:
        """Return the mocked database path.

        Args:
            None.

        Returns:
            Path to the test database.

        Raises:
            None.
        """
        return path

    monkeypatch.setattr(database, "get_db_path", _path)
    database.init_db()
    return path
