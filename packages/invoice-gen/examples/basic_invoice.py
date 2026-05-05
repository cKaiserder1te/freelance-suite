"""Basic invoice generation example."""

from invoice_gen import generate_invoice


def main() -> None:
	"""Generate a sample invoice PDF.

	Args:
		None.

	Returns:
		None.

	Raises:
		None.
	"""
	generate_invoice(
		{
			"sender": {
				"name": "Max Mustermann",
				"address": "Musterstrasse 1, 12345 Berlin",
				"email": "max@example.com",
				"tax_note": "Gemaess 19 UStG wird keine Umsatzsteuer berechnet.",
			},
			"client": {
				"name": "Acme GmbH",
				"address": "Acme-Allee 42, 10115 Berlin",
			},
			"meta": {
				"number": "2025-001",
				"invoice_date": "2025-01-15",
				"due_date": "2025-02-14",
				"currency": "EUR",
			},
			"items": [
				{
					"description": "Web Development - Projektphase 1",
					"quantity": 20,
					"unit": "h",
					"unit_price": 95.00,
				},
				{
					"description": "UI/UX Design Review",
					"quantity": 5,
					"unit": "h",
					"unit_price": 80.00,
				},
			],
		},
		output="invoice_2025-001.pdf",
	)


if __name__ == "__main__":
	main()
