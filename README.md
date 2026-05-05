# 🧾 freelance-suite

> An open-source ecosystem of tools for independent developers and freelancers —
> built by a freelancer, for freelancers. No bloat, no SaaS, no subscriptions.
> Just clean, local-first tooling that gets the job done.

---

## 📦 Monorepo Structure

This repository contains three standalone but interoperable packages:

```
freelance-suite/
├── packages/
│   ├── invoice-gen/          # Core library: generate professional invoices as PDF
│   ├── freelance-toolkit/    # CLI tool: time tracking, project management, exports
│   └── freelance-dashboard/  # Local web dashboard: revenue, hours, open invoices
├── docs/                     # Shared documentation & screenshots
├── examples/                 # Example configs, templates, outputs
├── .github/
│   └── workflows/            # CI/CD: test, lint, publish
├── LICENSE                   # MIT
└── README.md                 # You are here
```

Each package can be used **independently** or together as a full suite.

---

## 🚀 Packages Overview

### 1. `invoice-gen` — Invoice Generation Library

> **"Turn a JSON config into a professional PDF invoice in one function call."**

A zero-dependency-at-runtime Python library (and Node.js port) that generates clean, customizable PDF invoices from structured data. Publishable on PyPI and npm.

#### Core Features
- Generate PDF invoices from Python dict / JSON / YAML config
- Fully customizable templates (logo, colors, fonts, layout)
- Multi-currency support with locale-aware formatting
- Line items with quantity, unit price, tax, discount
- Automatic total, subtotal, VAT calculation
- Legally compliant fields (invoice number, date, due date, payment terms)
- German Kleinunternehmerregelung disclaimer support (§19 UStG)
- Export to PDF, HTML, or JSON
- No external API calls – 100% local

#### Tech Stack
- **Language:** Python 3.10+
- **PDF Engine:** `reportlab` or `weasyprint` (configurable)
- **Optional Node.js port:** via `pdfkit` or `puppeteer`
- **Config formats:** Python dict, JSON, YAML
- **Testing:** `pytest` with snapshot testing for PDF output
- **Publishing:** PyPI (`pip install invoice-gen`) + npm (`npm install invoice-gen`)

#### File Structure
```
invoice-gen/
├── src/
│   └── invoice_gen/
│       ├── __init__.py          # Public API: generate_invoice()
│       ├── models.py            # Pydantic models: Invoice, LineItem, Client, Sender
│       ├── renderer.py          # PDF rendering logic
│       ├── templates/
│       │   ├── default.html     # Default HTML template (for weasyprint)
│       │   ├── minimal.html     # Minimal clean template
│       │   └── german.html      # German-language / DACH-compliant template
│       ├── calculator.py        # Tax, discount, total calculations
│       ├── formatter.py         # Currency, date, number formatting
│       └── utils.py             # Helpers: logo embedding, font loading
├── tests/
│   ├── test_models.py
│   ├── test_calculator.py
│   ├── test_renderer.py
│   └── snapshots/               # Reference PDFs for snapshot testing
├── examples/
│   ├── basic_invoice.py
│   ├── german_invoice.py
│   └── output/                  # Example PDFs
├── pyproject.toml
├── README.md
└── CHANGELOG.md
```

#### Usage Example
```python
from invoice_gen import generate_invoice

invoice = generate_invoice({
    "sender": {
        "name": "Max Mustermann",
        "address": "Musterstraße 1, 12345 Berlin",
        "email": "max@example.com",
        "tax_note": "Gemäß §19 UStG wird keine Umsatzsteuer berechnet."
    },
    "client": {
        "name": "Acme GmbH",
        "address": "Acme-Allee 42, 10115 Berlin"
    },
    "invoice": {
        "number": "2025-001",
        "date": "2025-01-15",
        "due_date": "2025-02-14",
        "currency": "EUR"
    },
    "items": [
        {
            "description": "Web Development – Projektphase 1",
            "quantity": 20,
            "unit": "h",
            "unit_price": 95.00
        },
        {
            "description": "UI/UX Design Review",
            "quantity": 5,
            "unit": "h",
            "unit_price": 80.00
        }
    ]
}, output="invoice_2025-001.pdf")
```

#### Public API
```python
generate_invoice(data: dict, output: str = "invoice.pdf", template: str = "default") -> Path
load_from_yaml(path: str) -> dict
load_from_json(path: str) -> dict
list_templates() -> list[str]
```

#### Pydantic Models
```python
class Sender(BaseModel):
    name: str
    address: str
    email: str
    phone: str | None
    website: str | None
    bank_iban: str | None
    bank_bic: str | None
    tax_id: str | None
    tax_note: str | None          # e.g. §19 UStG disclaimer

class Client(BaseModel):
    name: str
    address: str
    email: str | None
    company: str | None

class LineItem(BaseModel):
    description: str
    quantity: float
    unit: str                     # "h", "days", "pcs", etc.
    unit_price: float
    tax_rate: float = 0.0
    discount: float = 0.0

class InvoiceMeta(BaseModel):
    number: str
    date: date
    due_date: date
    currency: str = "EUR"
    payment_terms: str | None
    notes: str | None

class Invoice(BaseModel):
    sender: Sender
    client: Client
    meta: InvoiceMeta
    items: list[LineItem]
```

---

### 2. `freelance-toolkit` — CLI Time Tracker & Project Manager

> **"Your terminal-native freelance OS. Track time, log projects, export reports — without ever leaving the CLI."**

A Python CLI application for freelancers who live in the terminal. Built with `typer` for a clean UX, `rich` for beautiful output, and SQLite for local persistence.

#### Core Features
- Start / stop / pause time tracking per project and task
- Manage clients and projects (CRUD)
- Set hourly rates per client or project
- Generate weekly / monthly summaries
- Export data to CSV, JSON, or pipe into `invoice-gen`
- Interactive TUI mode (optional, via `textual`)
- Shell completions (bash, zsh, fish)
- Configurable via `~/.freelance/config.toml`

#### Tech Stack
- **Language:** Python 3.10+
- **CLI Framework:** `typer` + `rich`
- **Database:** SQLite via `SQLModel` (SQLAlchemy + Pydantic)
- **Optional TUI:** `textual`
- **Config:** `tomllib` (stdlib Python 3.11+) or `toml`
- **Testing:** `pytest` + `typer.testing.CliRunner`
- **Install:** `pip install freelance-toolkit` → exposes `ft` command

#### File Structure
```
freelance-toolkit/
├── src/
│   └── freelance_toolkit/
│       ├── __init__.py
│       ├── main.py              # Typer app entry point: `ft`
│       ├── commands/
│       │   ├── time.py          # ft start, ft stop, ft pause, ft status
│       │   ├── project.py       # ft project add/list/delete
│       │   ├── client.py        # ft client add/list/delete
│       │   ├── report.py        # ft report week/month/custom
│       │   └── export.py        # ft export csv/json/invoice
│       ├── db/
│       │   ├── models.py        # SQLModel: Client, Project, TimeEntry
│       │   ├── database.py      # DB init, session management
│       │   └── queries.py       # Reusable query helpers
│       ├── config.py            # Config loading & defaults
│       ├── display.py           # Rich tables, panels, progress bars
│       └── utils.py
├── tests/
│   ├── test_commands/
│   └── test_db/
├── pyproject.toml
└── README.md
```

#### CLI Commands
```bash
# Time Tracking
ft start "Client A" "Fix login bug"     # Start timer for task
ft stop                                  # Stop active timer
ft pause                                 # Pause active timer
ft resume                                # Resume paused timer
ft status                                # Show current active timer

# Projects & Clients
ft project add "Client A" --rate 95     # Add project with hourly rate
ft project list                          # List all projects
ft client add "Acme GmbH" --email ...   # Add client

# Reports
ft report week                           # This week's summary
ft report month --month 2025-01         # January 2025 summary
ft report client "Acme GmbH"            # All time for a client

# Exports
ft export csv --month 2025-01           # Export to CSV
ft export invoice --month 2025-01       # Generate PDF via invoice-gen
```

#### SQLite Schema
```sql
CREATE TABLE clients (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    default_rate REAL
);

CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    name TEXT NOT NULL,
    hourly_rate REAL,
    active BOOLEAN DEFAULT TRUE
);

CREATE TABLE time_entries (
    id INTEGER PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    task TEXT,
    started_at DATETIME NOT NULL,
    stopped_at DATETIME,
    paused_duration INTEGER DEFAULT 0,   -- seconds
    notes TEXT
);
```

#### Config File (`~/.freelance/config.toml`)
```toml
[defaults]
currency = "EUR"
tax_note = "Gemäß §19 UStG wird keine Umsatzsteuer berechnet."
rounding = "up"              # "up", "down", "nearest"
time_format = "24h"

[invoice]
template = "german"
output_dir = "~/Documents/Invoices"
number_format = "{YEAR}-{SEQ:03d}"

[display]
theme = "dark"               # "dark", "light"
week_starts = "monday"
```

---

### 3. `freelance-dashboard` — Local Web Dashboard

> **"All your freelance data in one beautiful, private dashboard. No cloud, no account, no subscription."**

A lightweight local web application that visualizes your data from `freelance-toolkit`. Runs entirely on your machine via a simple `ft dashboard` command that spins up a local server and opens the browser.

#### Core Features
- Revenue overview: monthly, quarterly, annual charts
- Open invoices tracker with due-date alerts
- Hours logged per client / project (bar + pie charts)
- Top clients by revenue
- Daily/weekly activity heatmap (like GitHub contribution graph)
- Dark mode by default
- Responsive, works on mobile too (local network access)
- No database setup — reads directly from `~/.freelance/data.db`

#### Tech Stack
- **Backend:** Python (`FastAPI` or `Flask`) — serves data from SQLite
- **Frontend:** Vanilla JS + HTML/CSS **OR** React (lightweight Vite build)
- **Charts:** `Chart.js` (no heavy dependencies)
- **Styling:** CSS custom properties, no framework needed
- **Launch:** `ft dashboard` → opens `http://localhost:8765`
- **Optional:** Export dashboard as static HTML snapshot

#### File Structure
```
freelance-dashboard/
├── src/
│   ├── backend/
│   │   ├── main.py              # FastAPI app
│   │   ├── routes/
│   │   │   ├── revenue.py       # GET /api/revenue
│   │   │   ├── hours.py         # GET /api/hours
│   │   │   ├── clients.py       # GET /api/clients
│   │   │   └── invoices.py      # GET /api/invoices
│   │   └── queries.py           # Aggregation queries on SQLite
│   └── frontend/
│       ├── index.html
│       ├── css/
│       │   ├── main.css
│       │   └── charts.css
│       └── js/
│           ├── app.js           # Main entry, routing
│           ├── charts.js        # Chart.js initializations
│           ├── revenue.js       # Revenue page logic
│           ├── hours.js         # Hours page logic
│           └── api.js           # Fetch wrapper for backend
├── tests/
│   └── test_routes.py
├── pyproject.toml
└── README.md
```

#### API Endpoints
```
GET  /api/revenue?period=month&from=2025-01&to=2025-12
GET  /api/hours?groupBy=client&from=2025-01-01
GET  /api/clients/summary
GET  /api/invoices?status=open
GET  /api/heatmap?year=2025
```

#### Dashboard Views
```
/ ................. Overview (KPIs: revenue MTD, hours MTD, open invoices)
/revenue .......... Revenue charts (monthly bars, running total line)
/hours ............ Hours breakdown (per client pie, per week bar)
/clients .......... Client table with revenue + hours + avg rate
/invoices ......... Invoice list with status, due dates, amounts
```

---

## 🔗 How The Three Packages Work Together

```
                    ┌─────────────────────────┐
                    │     freelance-toolkit    │
                    │  (CLI: track time, log   │
                    │   projects, manage data) │
                    └────────────┬────────────┘
                                 │ reads/writes
                                 ▼
                    ┌─────────────────────────┐
                    │    ~/.freelance/         │
                    │    data.db (SQLite)      │
                    └──────┬──────────┬───────┘
                           │          │
              ft export    │          │  ft dashboard
              invoice      ▼          ▼
         ┌────────────────────┐  ┌────────────────────┐
         │    invoice-gen     │  │ freelance-dashboard │
         │ (generates PDF     │  │ (visualizes all    │
         │  from export data) │  │  data locally)     │
         └────────────────────┘  └────────────────────┘
```

---

## 🛠️ Installation

### Install all packages (recommended)
```bash
pip install freelance-suite        # installs all three + `ft` CLI
```

### Install individually
```bash
pip install invoice-gen            # library only
pip install freelance-toolkit      # CLI only (includes invoice-gen)
npm install invoice-gen            # Node.js version of invoice-gen
```

### From source
```bash
git clone https://github.com/yourusername/freelance-suite
cd freelance-suite
pip install -e packages/invoice-gen
pip install -e packages/freelance-toolkit
pip install -e packages/freelance-dashboard
```

---

## ⚡ Quickstart

```bash
# 1. Install
pip install freelance-suite

# 2. Add your first client
ft client add "Acme GmbH" --email contact@acme.de

# 3. Add a project
ft project add "Acme Website Relaunch" --client "Acme GmbH" --rate 95

# 4. Start tracking
ft start "Acme Website Relaunch" "Build landing page"

# ... do your work ...

ft stop

# 5. See your week
ft report week

# 6. Generate an invoice
ft export invoice --month 2025-01

# 7. Open the dashboard
ft dashboard
```

---

## 🗺️ Roadmap

### v0.1.0 — MVP (current target)
- [x] Project scaffolding & monorepo setup
- [ ] `invoice-gen`: core PDF generation, default template, Pydantic models
- [ ] `invoice-gen`: German template (§19 UStG), YAML/JSON input
- [ ] `invoice-gen`: published to PyPI
- [ ] `freelance-toolkit`: `ft start/stop/status` commands
- [ ] `freelance-toolkit`: SQLite persistence via SQLModel
- [ ] `freelance-toolkit`: `ft report week/month`
- [ ] `freelance-toolkit`: `ft export csv`
- [ ] `freelance-dashboard`: FastAPI backend with `/api/revenue` and `/api/hours`
- [ ] `freelance-dashboard`: Basic HTML dashboard with Chart.js

### v0.2.0 — Polish
- [ ] `invoice-gen`: HTML template engine, custom logo support
- [ ] `invoice-gen`: npm port
- [ ] `freelance-toolkit`: `ft export invoice` (invoice-gen integration)
- [ ] `freelance-toolkit`: Interactive TUI mode via `textual`
- [ ] `freelance-dashboard`: Heatmap view, client breakdown page

### v0.3.0 — Power Features
- [ ] `freelance-toolkit`: recurring projects / retainer tracking
- [ ] `freelance-toolkit`: budget alerts per project
- [ ] `freelance-dashboard`: static HTML export / snapshot
- [ ] Multi-language invoice templates (EN, DE, FR)
- [ ] VS Code extension for quick time tracking

---

## 🤝 Contributing

Contributions are welcome. Please open an issue before submitting a PR for larger changes.

```bash
git clone https://github.com/yourusername/freelance-suite
cd freelance-suite
python -m venv .venv && source .venv/bin/activate
pip install -e "packages/invoice-gen[dev]"
pip install -e "packages/freelance-toolkit[dev]"
pytest
```

See [CONTRIBUTING.md](./CONTRIBUTING.md) for full guidelines.

---

## 📄 License

MIT © [Your Name](https://github.com/yourusername)

---

## 💬 Why This Exists

I'm a freelance developer and WI student who got tired of juggling spreadsheets, online invoice tools, and time-tracking SaaS apps — each with their own accounts, monthly fees, and privacy concerns.

This suite is what I actually use day-to-day. It's local, fast, private, and composable. If it helps one other freelancer simplify their workflow, that's a win.

---

*Built with ☕ and too many late nights.*