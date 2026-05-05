"""Pydantic models for invoices and related entities."""

from __future__ import annotations

from datetime import date as Date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, StrictFloat, StrictStr
from pydantic import field_validator, model_validator


class Sender(BaseModel):
	"""Invoice sender details."""

	model_config = ConfigDict(strict=True)

	name: StrictStr = Field(description="Full name of the sender.")
	address: StrictStr = Field(description="Postal address of the sender.")
	email: StrictStr = Field(description="Email address of the sender.")
	phone: Optional[StrictStr] = Field(default=None, description="Phone number.")
	website: Optional[StrictStr] = Field(default=None, description="Website URL.")
	bank_iban: Optional[StrictStr] = Field(
		default=None, description="IBAN for bank transfers."
	)
	bank_bic: Optional[StrictStr] = Field(
		default=None, description="BIC for bank transfers."
	)
	tax_id: Optional[StrictStr] = Field(default=None, description="Tax ID.")
	tax_note: Optional[StrictStr] = Field(
		default=None, description="Tax note such as §19 UStG disclaimer."
	)


class Client(BaseModel):
	"""Invoice client details."""

	model_config = ConfigDict(strict=True)

	name: StrictStr = Field(description="Full name of the client.")
	address: StrictStr = Field(description="Postal address of the client.")
	email: Optional[StrictStr] = Field(default=None, description="Client email.")
	company: Optional[StrictStr] = Field(
		default=None, description="Company name, if applicable."
	)


class LineItem(BaseModel):
	"""Single invoice line item."""

	model_config = ConfigDict(strict=True)

	description: StrictStr = Field(description="Line item description.")
	quantity: StrictFloat = Field(description="Quantity of the item.")
	unit: StrictStr = Field(description="Unit label, e.g., h, days, pcs.")
	unit_price: StrictFloat = Field(description="Unit price before tax.")
	tax_rate: StrictFloat = Field(
		default=0.0, description="Tax rate as a decimal fraction."
	)
	discount: StrictFloat = Field(
		default=0.0, description="Discount as a decimal fraction."
	)

	@field_validator("quantity")
	@classmethod
	def validate_quantity(cls, value: float) -> float:
		"""Ensure quantity is positive.

		Args:
			value: Quantity value to validate.

		Returns:
			The validated quantity.

		Raises:
			ValueError: If the quantity is not greater than zero.
		"""
		if value <= 0:
			raise ValueError("quantity must be greater than 0")
		return value

	@field_validator("unit_price")
	@classmethod
	def validate_unit_price(cls, value: float) -> float:
		"""Ensure unit price is non-negative.

		Args:
			value: Unit price value to validate.

		Returns:
			The validated unit price.

		Raises:
			ValueError: If the unit price is negative.
		"""
		if value < 0:
			raise ValueError("unit_price must be greater than or equal to 0")
		return value

	@property
	def line_total(self) -> float:
		"""Compute the total for this line item.

		Returns:
			The line total after discount and tax.
		"""
		discounted = self.quantity * self.unit_price * (1 - self.discount)
		return discounted * (1 + self.tax_rate)


class InvoiceMeta(BaseModel):
	"""Metadata about the invoice."""

	model_config = ConfigDict(strict=True)

	number: StrictStr = Field(description="Invoice number.")
	date: date = Field(description="Invoice issue date.")
	due_date: Date = Field(description="Payment due date.")
	currency: StrictStr = Field(default="EUR", description="Currency code.")
	payment_terms: Optional[StrictStr] = Field(
		default=None, description="Payment terms description."
	)
	notes: Optional[StrictStr] = Field(
		default=None, description="Additional invoice notes."
	)


class Invoice(BaseModel):
	"""Complete invoice payload including parties and line items."""

	model_config = ConfigDict(strict=True)

	sender: Sender = Field(description="Invoice sender.")
	client: Client = Field(description="Invoice recipient.")
	meta: InvoiceMeta = Field(description="Invoice metadata.")
	items: list[LineItem] = Field(description="Invoice line items.")

	@model_validator(mode="after")
	def validate_due_date(self) -> "Invoice":
		"""Ensure due date is after the invoice date.

		Returns:
			The validated invoice.

		Raises:
			ValueError: If due date is not after the invoice date.
		"""
		if self.meta.due_date <= self.meta.invoice_date:
			raise ValueError("due_date must be after date")
		return self

	@property
	def subtotal(self) -> float:
		"""Compute the invoice subtotal before tax.

		Returns:
			The subtotal value.
		"""
		return sum(
			item.quantity * item.unit_price * (1 - item.discount)
			for item in self.items
		)

	@property
	def total_tax(self) -> float:
		"""Compute the total tax amount.

		Returns:
			The total tax value.
		"""
		return sum(
			item.quantity * item.unit_price * (1 - item.discount) * item.tax_rate
			for item in self.items
		)

	@property
	def total(self) -> float:
		"""Compute the total invoice amount including tax.

		Returns:
			The total invoice amount.
		"""
		return self.subtotal + self.total_tax


if __name__ == "__main__":
	SAMPLE_SENDER = Sender(
		name="Max Mustermann",
		address="Musterstrasse 1, 12345 Berlin",
		email="max@example.com",
		tax_note="Gemaess §19 UStG wird keine Umsatzsteuer berechnet.",
	)
	SAMPLE_CLIENT = Client(
		name="Acme GmbH",
		address="Acme-Allee 42, 10115 Berlin",
	)
	SAMPLE_META = InvoiceMeta(
		number="2025-001",
		date=Date(2025, 1, 15),
		due_date=Date(2025, 2, 14),
		currency="EUR",
	)
	SAMPLE_ITEMS = [
		LineItem(
			description="Web Development - Project Phase 1",
			quantity=20.0,
			unit="h",
			unit_price=95.0,
		),
		LineItem(
			description="UI/UX Design Review",
			quantity=5.0,
			unit="h",
			unit_price=80.0,
			tax_rate=0.19,
		),
	]

	SAMPLE_INVOICE = Invoice(
		sender=SAMPLE_SENDER,
		client=SAMPLE_CLIENT,
		meta=SAMPLE_META,
		items=SAMPLE_ITEMS,
	)
	print(SAMPLE_INVOICE.model_dump())
