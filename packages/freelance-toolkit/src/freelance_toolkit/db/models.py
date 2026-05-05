"""SQLModel database models for freelance-toolkit."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Client(SQLModel, table=True):
	"""Client table model."""

	__tablename__ = "clients"

	id: Optional[int] = Field(default=None, primary_key=True)
	name: str = Field(index=True)
	email: Optional[str] = Field(default=None)
	default_rate: Optional[float] = Field(default=None)

	def __repr__(self) -> str:
		"""Return a readable representation for debugging.

		Args:
			None.

		Returns:
			String representation of the client.

		Raises:
			None.
		"""
		return (
			"Client(id={id}, name={name!r}, email={email!r}, default_rate={rate!r})"
		).format(
			id=self.id,
			name=self.name,
			email=self.email,
			rate=self.default_rate,
		)


class Project(SQLModel, table=True):
	"""Project table model."""

	__tablename__ = "projects"

	id: Optional[int] = Field(default=None, primary_key=True)
	client_id: int = Field(foreign_key="clients.id", index=True)
	name: str = Field(index=True)
	hourly_rate: Optional[float] = Field(default=None)
	active: bool = Field(default=True)

	def __repr__(self) -> str:
		"""Return a readable representation for debugging.

		Args:
			None.

		Returns:
			String representation of the project.

		Raises:
			None.
		"""
		return (
			"Project(id={id}, client_id={client_id}, name={name!r}, "
			"hourly_rate={rate!r}, active={active})"
		).format(
			id=self.id,
			client_id=self.client_id,
			name=self.name,
			rate=self.hourly_rate,
			active=self.active,
		)


class TimeEntry(SQLModel, table=True):
	"""Time entry table model."""

	__tablename__ = "time_entries"

	id: Optional[int] = Field(default=None, primary_key=True)
	project_id: int = Field(foreign_key="projects.id", index=True)
	task: Optional[str] = Field(default=None)
	started_at: datetime = Field(index=True)
	stopped_at: Optional[datetime] = Field(default=None, index=True)
	paused_duration: int = Field(default=0)
	notes: Optional[str] = Field(default=None)

	@property
	def is_running(self) -> bool:
		"""Return True when the timer is running.

		Args:
			None.

		Returns:
			True if the entry has no stop time.

		Raises:
			None.
		"""
		return self.stopped_at is None

	@property
	def is_paused(self) -> bool:
		"""Return True when the timer is paused.

		Args:
			None.

		Returns:
			True if paused duration is recorded while running.

		Raises:
			None.
		"""
		return self.paused_duration > 0 and self.stopped_at is None

	@property
	def duration_seconds(self) -> Optional[int]:
		"""Return the duration in seconds once the entry is stopped.

		Args:
			None.

		Returns:
			Total duration in seconds or None if still running.

		Raises:
			None.
		"""
		if self.stopped_at is None:
			return None
		duration = (self.stopped_at - self.started_at).total_seconds()
		return max(0, int(duration - self.paused_duration))

	@property
	def duration_hours(self) -> Optional[float]:
		"""Return the duration in hours once the entry is stopped.

		Args:
			None.

		Returns:
			Duration in hours or None if still running.

		Raises:
			None.
		"""
		seconds = self.duration_seconds
		if seconds is None:
			return None
		return seconds / 3600.0

	def billable_amount(self, rate: float) -> Optional[float]:
		"""Calculate the billable amount for a given rate.

		Args:
			rate: Hourly rate to apply.

		Returns:
			Billable amount or None if duration is unavailable.

		Raises:
			None.
		"""
		hours = self.duration_hours
		if hours is None:
			return None
		return hours * rate

	def __repr__(self) -> str:
		"""Return a readable representation for debugging.

		Args:
			None.

		Returns:
			String representation of the time entry.

		Raises:
			None.
		"""
		return (
			"TimeEntry(id={id}, project_id={project_id}, task={task!r}, "
			"started_at={started!r}, stopped_at={stopped!r})"
		).format(
			id=self.id,
			project_id=self.project_id,
			task=self.task,
			started=self.started_at,
			stopped=self.stopped_at,
		)
