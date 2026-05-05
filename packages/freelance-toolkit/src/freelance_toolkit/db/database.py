"""Database initialization and session management."""

from __future__ import annotations

import contextlib
from pathlib import Path
from typing import Generator

from sqlalchemy.engine import Engine
from sqlmodel import SQLModel, Session, create_engine as sql_create_engine


def get_db_path() -> Path:
	"""Return the default SQLite database path.

	Args:
		None.

	Returns:
		Path to the SQLite database file.

	Raises:
		None.
	"""
	return Path.home() / ".freelance" / "data.db"


def create_engine() -> Engine:
	"""Create a SQLite engine for the freelance toolkit.

	Args:
		None.

	Returns:
		SQLAlchemy Engine instance.

	Raises:
		None.
	"""
	db_path = get_db_path()
	return sql_create_engine(f"sqlite:///{db_path}")


def init_db() -> None:
	"""Initialize the database schema.

	Args:
		None.

	Returns:
		None.

	Raises:
		None.
	"""
	db_path = get_db_path()
	db_path.parent.mkdir(parents=True, exist_ok=True)
	engine = create_engine()
	SQLModel.metadata.create_all(engine)


@contextlib.contextmanager
def get_session() -> Generator[Session, None, None]:
	"""Yield a database session.

	Args:
		None.

	Returns:
		Generator yielding an active SQLModel Session.

	Raises:
		None.
	"""
	engine = create_engine()
	with Session(engine) as session:
		yield session
