"""Tests for dashboard API routes."""

from fastapi.testclient import TestClient

from backend.main import app


def test_revenue_endpoint(monkeypatch) -> None:
	"""Return revenue payload with running totals.

	Args:
		monkeypatch: Pytest monkeypatch fixture.

	Returns:
		None.

	Raises:
		None.
	"""
	monkeypatch.setattr(
		"backend.routes.revenue.get_monthly_revenue",
		lambda year: [
			{"month": "01", "revenue": 100.0},
			{"month": "02", "revenue": 200.0},
		],
	)
	client = TestClient(app)
	response = client.get("/api/revenue", params={"period": "month", "from": "2025-01", "to": "2025-02"})
	assert response.status_code == 200
	payload = response.json()
	assert payload["labels"] == ["2025-01", "2025-02"]
	assert payload["values"] == [100.0, 200.0]
	assert payload["running_total"] == [100.0, 300.0]


def test_hours_endpoint_client(monkeypatch) -> None:
	"""Return hours grouped by client.

	Args:
		monkeypatch: Pytest monkeypatch fixture.

	Returns:
		None.

	Raises:
		None.
	"""
	monkeypatch.setattr(
		"backend.routes.hours.get_hours_by_client",
		lambda start, end: [
			{"client": "Acme", "hours": 12.5, "revenue": 1000.0},
			{"client": "Beta", "hours": 5.0, "revenue": 400.0},
		],
	)
	client = TestClient(app)
	response = client.get("/api/hours", params={"groupBy": "client"})
	assert response.status_code == 200
	payload = response.json()
	assert payload["labels"] == ["Acme", "Beta"]
	assert payload["values"] == [12.5, 5.0]


def test_hours_endpoint_project(monkeypatch) -> None:
	"""Return hours grouped by project.

	Args:
		monkeypatch: Pytest monkeypatch fixture.

	Returns:
		None.

	Raises:
		None.
	"""
	monkeypatch.setattr(
		"backend.routes.hours.get_hours_by_project",
		lambda start, end: [
			{"project": "Website", "hours": 8.0, "revenue": 800.0},
		],
	)
	client = TestClient(app)
	response = client.get("/api/hours", params={"groupBy": "project"})
	assert response.status_code == 200
	payload = response.json()
	assert payload["labels"] == ["Website"]
	assert payload["values"] == [8.0]


def test_hours_endpoint_week(monkeypatch) -> None:
	"""Return hours grouped by week.

	Args:
		monkeypatch: Pytest monkeypatch fixture.

	Returns:
		None.

	Raises:
		None.
	"""
	monkeypatch.setattr(
		"backend.routes.hours.get_hours_by_week",
		lambda start, end: [
			{"week": "2025-W01", "hours": 10.0},
		],
	)
	client = TestClient(app)
	response = client.get("/api/hours", params={"groupBy": "week"})
	assert response.status_code == 200
	payload = response.json()
	assert payload["labels"] == ["2025-W01"]
	assert payload["values"] == [10.0]


def test_clients_summary(monkeypatch) -> None:
	"""Return client summary list.

	Args:
		monkeypatch: Pytest monkeypatch fixture.

	Returns:
		None.

	Raises:
		None.
	"""
	monkeypatch.setattr(
		"backend.routes.clients.get_client_summary",
		lambda: [
			{
				"name": "Acme",
				"total_hours": 10.0,
				"total_revenue": 1000.0,
				"avg_rate": 100.0,
				"project_count": 2,
			}
		],
	)
	client = TestClient(app)
	response = client.get("/api/clients/summary")
	assert response.status_code == 200
	payload = response.json()
	assert payload[0]["name"] == "Acme"


def test_invoices_endpoint(monkeypatch) -> None:
	"""Return invoices with status filtering.

	Args:
		monkeypatch: Pytest monkeypatch fixture.

	Returns:
		None.

	Raises:
		None.
	"""
	monkeypatch.setattr(
		"backend.routes.invoices.get_invoices",
		lambda status: [
			{
				"number": "2025-001",
				"client": "Acme",
				"amount": 100.0,
				"due_date": "2025-02-14",
				"status": status,
			}
		],
	)
	client = TestClient(app)
	response = client.get("/api/invoices", params={"status": "paid"})
	assert response.status_code == 200
	payload = response.json()
	assert payload[0]["status"] == "paid"


def test_heatmap_endpoint(monkeypatch) -> None:
	"""Return heatmap data.

	Args:
		monkeypatch: Pytest monkeypatch fixture.

	Returns:
		None.

	Raises:
		None.
	"""
	monkeypatch.setattr(
		"backend.routes.hours.get_activity_heatmap",
		lambda year: [{"date": "2025-01-01", "hours": 4.0}],
	)
	client = TestClient(app)
	response = client.get("/api/heatmap", params={"year": 2025})
	assert response.status_code == 200
	payload = response.json()
	assert payload[0]["count"] == 4.0


def test_kpis_endpoint(monkeypatch) -> None:
	"""Return KPI payload.

	Args:
		monkeypatch: Pytest monkeypatch fixture.

	Returns:
		None.

	Raises:
		None.
	"""
	monkeypatch.setattr(
		"backend.routes.revenue.get_kpis",
		lambda: {
			"mtd_revenue": 100.0,
			"mtd_hours": 5.0,
			"ytd_revenue": 400.0,
			"active_projects_count": 2,
		},
	)
	client = TestClient(app)
	response = client.get("/api/kpis")
	assert response.status_code == 200
	payload = response.json()
	assert payload["active_projects_count"] == 2


def test_invalid_period_returns_422() -> None:
	"""Return 422 for invalid period.

	Args:
		None.

	Returns:
		None.

	Raises:
		None.
	"""
	client = TestClient(app)
	response = client.get("/api/revenue", params={"period": "invalid"})
	assert response.status_code == 422
