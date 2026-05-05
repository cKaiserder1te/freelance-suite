"""FastAPI application for the freelance dashboard."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from .routes import clients, hours, invoices, revenue

ALLOWED_ORIGINS = [
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:8765",
    "http://127.0.0.1:8765",
]



def _get_db_path() -> Path:
    return Path.home() / ".freelance" / "data.db"


def _test_db_connection(db_path: Path) -> None:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.close()


def _get_frontend_path() -> Path:
    """Return the frontend directory path.

    Args:
        None.

    Returns:
        Path to the frontend assets.

    Raises:
        None.
    """
    return Path(__file__).resolve().parent.parent / "frontend"


app = FastAPI(title="freelance-dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(revenue.router, prefix="/api")
app.include_router(hours.router, prefix="/api")
app.include_router(clients.router, prefix="/api")
app.include_router(invoices.router, prefix="/api")

frontend_path = _get_frontend_path()
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


@app.on_event("startup")
def _on_startup() -> None:
    """Initialize the backend on startup.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.
    """
    db_path = _get_db_path()
    try:
        _test_db_connection(db_path)
    except sqlite3.Error:
        pass
    app.state.db_path = db_path


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint.

    Args:
        None.

    Returns:
        Health status payload.

    Raises:
        None.
    """
    db_path = getattr(app.state, "db_path", _get_db_path())
    return {"status": "ok", "db": str(db_path)}


def run() -> None:
    """Run the dashboard server.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.
    """
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8765, reload=False)

@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint.

    Args:
        None.

    Returns:
        Health status payload.

    Raises:
        None.
    """
    db_path = getattr(app.state, "db_path", _get_db_path())
    return {"status": "ok", "db": str(db_path)}


def run() -> None:
    """Run the dashboard server.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.
    """
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8765, reload=False)
