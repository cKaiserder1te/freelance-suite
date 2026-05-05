"""Tests for export CLI commands."""

from datetime import datetime, timedelta
from pathlib import Path
import types

import pytest
from typer.testing import CliRunner

from freelance_toolkit.config import get_config_path
from freelance_toolkit.db.database import get_session
from freelance_toolkit.db.models import Client, Project, TimeEntry
from freelance_toolkit.main import app


def _write_config(path: Path, output_dir: Path) -> None:
    """Write a default config file for tests.

    Args:
        path: Path to the config file.

    Returns:
        None.

    Raises:
        None.
    """
    path.write_text(
        """
[defaults]
currency = "EUR"
tax_note = "Gemaess 19 UStG wird keine Umsatzsteuer berechnet."
rounding = "up"
time_format = "24h"

[invoice]
template = "german"
output_dir = "{output_dir}"
number_format = "{{YEAR}}-{{SEQ:03d}}"

[display]
theme = "dark"
week_starts = "monday"
""".strip().format(output_dir=output_dir.as_posix()),
        encoding="utf-8",
    )


def _seed_entry() -> None:
    """Seed a time entry for export tests.

    Args:
        None.

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


def test_export_csv(runner: CliRunner, db_path, tmp_path: Path) -> None:
    """Export CSV to a given path.

    Args:
        runner: Typer CLI runner.
        db_path: Temporary database path fixture.
        tmp_path: Temporary directory path.

    Returns:
        None.

    Raises:
        None.
    """
    _seed_entry()
    output = tmp_path / "entries.csv"
    result = runner.invoke(app, ["export", "csv", "--output", str(output)])
    assert result.exit_code == 0
    assert output.exists()


def test_export_invoice_calls_invoice_gen(
    runner: CliRunner,
    db_path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Export invoice via invoice-gen when available.

    Args:
        runner: Typer CLI runner.
        db_path: Temporary database path fixture.
        tmp_path: Temporary directory path.
        monkeypatch: Pytest monkeypatch fixture.

    Returns:
        None.

    Raises:
        None.
    """
    _seed_entry()
    config_path = tmp_path / "config.toml"
    _write_config(config_path, tmp_path)

    def _config_path() -> Path:
        """Return the mocked config path.

        Args:
            None.

        Returns:
            Path to config file.

        Raises:
            None.
        """
        return config_path

    monkeypatch.setattr("freelance_toolkit.config.get_config_path", _config_path)

    output_path = tmp_path / "invoice.pdf"

    def _fake_generate_invoice(data, output, template, locale="de_DE"):
        """Fake invoice generator that writes a file.

        Args:
            data: Invoice payload.
            output: Output path.
            template: Template name.
            locale: Locale string.

        Returns:
            Path to output file.

        Raises:
            None.
        """
        Path(output).write_bytes(b"pdf")
        return Path(output)

    fake_module = types.SimpleNamespace(generate_invoice=_fake_generate_invoice)
    monkeypatch.setitem(__import__("sys").modules, "invoice_gen", fake_module)

    result = runner.invoke(app, ["export", "invoice"])
    assert result.exit_code == 0
    assert output_path.exists()
