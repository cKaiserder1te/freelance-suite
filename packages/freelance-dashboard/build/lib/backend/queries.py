"""SQLite aggregation helpers for dashboard data."""

from __future__ import annotations

import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Any

MOCK_INVOICES: list[dict[str, Any]] = [
    {
        "number": "2025-001",
        "client": "Acme GmbH",
        "due_date": "2025-02-14",
        "amount": 1250.0,
        "status": "open",
    },
    {
        "number": "2025-000",
        "client": "Beta Studio",
        "due_date": "2025-01-15",
        "amount": 980.0,
        "status": "paid",
    },
]


def _get_db_path() -> Path:
    """Return the SQLite database path.

    Args:
        None.

    Returns:
        Path to the SQLite database.

    Raises:
        None.
    """
    return Path.home() / ".freelance" / "data.db"


def _get_connection() -> sqlite3.Connection | None:
    """Return a read-only SQLite connection if available.

    Args:
        None.

    Returns:
        SQLite connection or None when unavailable.

    Raises:
        None.
    """
    db_path = _get_db_path()
    if not db_path.exists():
        return None
    try:
        connection = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    except sqlite3.Error:
        return None
    connection.row_factory = sqlite3.Row
    return connection


def _fetch_all(query: str, params: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
    """Run a SQL query and return all rows.

    Args:
        query: SQL query string.
        params: Query parameters.

    Returns:
        List of sqlite3.Row items.

    Raises:
        None.
    """
    connection = _get_connection()
    if connection is None:
        return []
    try:
        cursor = connection.execute(query, params)
        rows = cursor.fetchall()
    except sqlite3.Error:
        rows = []
    finally:
        connection.close()
    return rows


def get_monthly_revenue(year: int) -> list[dict[str, Any]]:
    """Return total revenue per month for a given year.

    Args:
        year: Target year.

    Returns:
        List of dicts with month and revenue values.

    Raises:
        None.
    """
    query = """
        SELECT strftime('%m', started_at) AS month,
               SUM((strftime('%s', stopped_at) - strftime('%s', started_at) - paused_duration)
                   / 3600.0 * COALESCE(projects.hourly_rate, 0)) AS revenue
        FROM time_entries
        JOIN projects ON projects.id = time_entries.project_id
        WHERE stopped_at IS NOT NULL
          AND strftime('%Y', started_at) = ?
        GROUP BY month
        ORDER BY month
    """
    rows = _fetch_all(query, (str(year),))
    return [
        {"month": row["month"], "revenue": float(row["revenue"] or 0.0)}
        for row in rows
    ]


def get_hours_by_client(from_date: date, to_date: date) -> list[dict[str, Any]]:
    """Return hours and revenue grouped by client within a date range.

    Args:
        from_date: Start date.
        to_date: End date.

    Returns:
        List of dicts with client, hours, and revenue.

    Raises:
        None.
    """
    query = """
        SELECT clients.name AS client,
               SUM((strftime('%s', stopped_at) - strftime('%s', started_at) - paused_duration)
                   / 3600.0) AS hours,
               SUM((strftime('%s', stopped_at) - strftime('%s', started_at) - paused_duration)
                   / 3600.0 * COALESCE(projects.hourly_rate, 0)) AS revenue
        FROM time_entries
        JOIN projects ON projects.id = time_entries.project_id
        JOIN clients ON clients.id = projects.client_id
        WHERE stopped_at IS NOT NULL
          AND date(started_at) >= ?
          AND date(started_at) <= ?
        GROUP BY clients.name
        ORDER BY revenue DESC
    """
    rows = _fetch_all(query, (from_date.isoformat(), to_date.isoformat()))
    return [
        {
            "client": row["client"],
            "hours": float(row["hours"] or 0.0),
            "revenue": float(row["revenue"] or 0.0),
        }
        for row in rows
    ]


def get_open_invoices() -> list[dict[str, Any]]:
    """Return placeholder open invoice data.

    Args:
        None.

    Returns:
        List of open invoice dicts.

    Raises:
        None.
    """
    return [invoice for invoice in MOCK_INVOICES if invoice["status"] == "open"]


def get_invoices(status: str) -> list[dict[str, Any]]:
    """Return placeholder invoice data by status.

    Args:
        status: Invoice status filter.

    Returns:
        List of invoices.

    Raises:
        None.
    """
    if status == "all":
        return list(MOCK_INVOICES)
    if status == "paid":
        return [invoice for invoice in MOCK_INVOICES if invoice["status"] == "paid"]
    return get_open_invoices()


def get_hours_by_project(from_date: date, to_date: date) -> list[dict[str, Any]]:
    """Return hours grouped by project within a date range.

    Args:
        from_date: Start date.
        to_date: End date.

    Returns:
        List of dicts with project, hours, and revenue.

    Raises:
        None.
    """
    query = """
        SELECT projects.name AS project,
               SUM((strftime('%s', stopped_at) - strftime('%s', started_at) - paused_duration)
                   / 3600.0) AS hours,
               SUM((strftime('%s', stopped_at) - strftime('%s', started_at) - paused_duration)
                   / 3600.0 * COALESCE(projects.hourly_rate, 0)) AS revenue
        FROM time_entries
        JOIN projects ON projects.id = time_entries.project_id
        WHERE stopped_at IS NOT NULL
          AND date(started_at) >= ?
          AND date(started_at) <= ?
        GROUP BY projects.name
        ORDER BY revenue DESC
    """
    rows = _fetch_all(query, (from_date.isoformat(), to_date.isoformat()))
    return [
        {
            "project": row["project"],
            "hours": float(row["hours"] or 0.0),
            "revenue": float(row["revenue"] or 0.0),
        }
        for row in rows
    ]


def get_hours_by_week(from_date: date, to_date: date) -> list[dict[str, Any]]:
    """Return hours grouped by ISO week within a date range.

    Args:
        from_date: Start date.
        to_date: End date.

    Returns:
        List of dicts with week and hours.

    Raises:
        None.
    """
    query = """
        SELECT strftime('%Y', started_at) AS year,
               strftime('%W', started_at) AS week,
               SUM((strftime('%s', stopped_at) - strftime('%s', started_at) - paused_duration)
                   / 3600.0) AS hours
        FROM time_entries
        WHERE stopped_at IS NOT NULL
          AND date(started_at) >= ?
          AND date(started_at) <= ?
        GROUP BY year, week
        ORDER BY year, week
    """
    rows = _fetch_all(query, (from_date.isoformat(), to_date.isoformat()))
    results = []
    for row in rows:
        week_label = f"{row['year']}-W{int(row['week']):02d}"
        results.append({"week": week_label, "hours": float(row["hours"] or 0.0)})
    return results


def get_client_summary() -> list[dict[str, Any]]:
    """Return summary stats per client.

    Args:
        None.

    Returns:
        List of client summary dicts.

    Raises:
        None.
    """
    query = """
        SELECT clients.name AS name,
               COUNT(DISTINCT projects.id) AS project_count,
               SUM((strftime('%s', stopped_at) - strftime('%s', started_at) - paused_duration)
                   / 3600.0) AS hours,
               SUM((strftime('%s', stopped_at) - strftime('%s', started_at) - paused_duration)
                   / 3600.0 * COALESCE(projects.hourly_rate, 0)) AS revenue
        FROM clients
        LEFT JOIN projects ON projects.client_id = clients.id
        LEFT JOIN time_entries ON time_entries.project_id = projects.id
        GROUP BY clients.name
        ORDER BY revenue DESC
    """
    rows = _fetch_all(query)
    results: list[dict[str, Any]] = []
    for row in rows:
        hours = float(row["hours"] or 0.0)
        revenue = float(row["revenue"] or 0.0)
        avg_rate = (revenue / hours) if hours else 0.0
        results.append(
            {
                "name": row["name"],
                "total_hours": hours,
                "total_revenue": revenue,
                "avg_rate": avg_rate,
                "project_count": int(row["project_count"] or 0),
            }
        )
    return results


def get_activity_heatmap(year: int) -> list[dict[str, Any]]:
    """Return activity heatmap data for a year.

    Args:
        year: Target year.

    Returns:
        List of dicts with date and hours.

    Raises:
        None.
    """
    query = """
        SELECT date(started_at) AS day,
               SUM((strftime('%s', stopped_at) - strftime('%s', started_at) - paused_duration)
                   / 3600.0) AS hours
        FROM time_entries
        WHERE stopped_at IS NOT NULL
          AND strftime('%Y', started_at) = ?
        GROUP BY day
        ORDER BY day
    """
    rows = _fetch_all(query, (str(year),))
    return [
        {"date": row["day"], "hours": float(row["hours"] or 0.0)}
        for row in rows
    ]


def get_kpis() -> dict[str, Any]:
    """Return key performance indicators.

    Args:
        None.

    Returns:
        KPI dictionary.

    Raises:
        None.
    """
    today = date.today()
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)

    mtd = get_hours_by_client(month_start, today)
    ytd = get_hours_by_client(year_start, today)

    mtd_hours = sum(entry["hours"] for entry in mtd)
    mtd_revenue = sum(entry["revenue"] for entry in mtd)
    ytd_revenue = sum(entry["revenue"] for entry in ytd)

    projects_query = "SELECT COUNT(*) AS active_count FROM projects WHERE active = 1"
    rows = _fetch_all(projects_query)
    active_projects_count = int(rows[0]["active_count"]) if rows else 0

    return {
        "mtd_revenue": float(mtd_revenue),
        "mtd_hours": float(mtd_hours),
        "ytd_revenue": float(ytd_revenue),
        "active_projects_count": active_projects_count,
    }
