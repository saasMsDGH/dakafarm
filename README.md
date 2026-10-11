<div align="center">

# AMAS FARM Management System

**A full-stack ERP platform for poultry farm operations, sales, inventory, HR, assets and double-ledger finance.**

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?style=flat-square&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

</div>

---

## Overview

AMAS FARM Management System replaces scattered paper and spreadsheet records with one connected platform. Farm activity, sales, purchasing, stock, payroll, assets and accounting all share one database and one ledger. A payment recorded in one module shows up in the finance reports without any manual re-entry.

The system has a role-based React dashboard and an asynchronous FastAPI backend on PostgreSQL. It is organised as seven subsystems, and each one has its own models, repositories, services and routers.

## Key Features

### Farm Operations
- Houses and flocks lifecycle management
- Daily feed, production (eggs), mortality, vaccination and medication records
- Consolidated farm performance report

### Sales and Business (POS)
- Customers and suppliers
- Sales and purchases with partial-payment tracking
- Operating expenses with payment history

### Inventory
- Product catalogue and categories
- Stock movements (in, out, adjustments) with a live inventory status view

### Finance
- Unified ledger of financial accounts (cash, bank, mobile money) and transactions
- Receivables and payables (debts) tracking
- Trial balance, profit and loss, cash flow and balance sheet
- Finance dashboard with key indicators

### Human Resources
- Employee records
- Payroll generation and payroll payments

### Asset Management
- Asset register with purchase and payment tracking

### Administration and Reporting
- User and role management
- Operations report that combines data across all subsystems
- English and Swahili interface (i18n)

## Architecture

```text
+--------------------+        REST / JSON        +----------------------------+
|  React 18 (Vite)   |  <--------------------->  |  FastAPI (async)           |
|  Role-based UI     |      JWT Bearer auth      |  Router > Service > Repo   |
|  i18n (EN / SW)    |                           +-------------+--------------+
+--------------------+                                         |
                                                    SQLAlchemy 2 (asyncpg)
                                                               |
                                                  +------------v-------------+
                                                  |  PostgreSQL 15           |
                                                  |  Alembic migrations      |
                                                  +--------------------------+
```

The backend follows a layered design:

| Layer | Responsibility |
|-------|----------------|
| **Router** | HTTP endpoints, request validation, role checks |
| **Schemas** | Pydantic models for input and output contracts |
| **Service** | Business rules and transaction orchestration |
| **Repository** | Database access through SQLAlchemy |
| **Models** | ORM entities |

### Transactional finance flow

Every payment (expense, payroll, asset purchase) runs inside one atomic database transaction:

1. Validate the amount against the remaining balance, and check the account exists and has sufficient funds.
2. Insert the domain payment record, such as `PayrollPayment`, `ExpensePayment` or `AssetPayment`.
3. Update the parent record's `amount_paid` and recalculate its status (`UNPAID`, `PARTIAL`, `PAID`).
4. Insert the matching `FinancialTransaction` into the ledger.
5. Commit, or roll everything back on any failure.

This keeps the ledger consistent even when a request fails halfway through.

### Role-based access control

Authentication uses JWT with Argon2 password hashing. The ten roles are `admin`, `finance_manager`, `Farm Manager`, `Farm Worker`, `hr_manager`, `hr_officer`, `inventory_admin`, `sell_manager`, `sell_officer` and `asset_manager`. Access is enforced on the API, and the frontend only shows the routes and menu items each role may use.

## Tech Stack

| Area | Technologies |
|------|--------------|
| Backend | Python 3.11, FastAPI, SQLAlchemy 2 (async), asyncpg, Pydantic, Alembic |
| Security | JWT (PyJWT), Argon2 (pwdlib), CORS configuration |
| Database | PostgreSQL 15 |
| Frontend | React 18, Vite, React Router, Axios, Bootstrap 5 (Volt dashboard theme), Recharts, Chartist |
| UX | i18next (English / Swahili), SweetAlert2, printable reports |
| DevOps | Docker, Docker Compose |

## Project Structure

```text
AMAS-FARM-Management-System/
|-- backend/
|   |-- app/
|   |   |-- api/v1/
|   |   |   |-- farm/        # houses, flocks, feed, production, mortality, health
|   |   |   |-- pos/         # customers, suppliers, sales, purchases, expenses
|   |   |   |-- inventory/   # products, categories, stock movements
|   |   |   |-- finance/     # accounts, transactions, statements, dashboard
|   |   |   |-- hr/          # employees, payroll
|   |   |   |-- assets/      # assets and asset payments
|   |   |   |-- reports/     # cross-module operations report
|   |   |   `-- user/        # users and roles
|   |   |-- auth/            # login, JWT, role guards
|   |   `-- core/            # config, database, security, role seeding
|   |-- migrations/          # Alembic
|   `-- dockerfile
|-- frontend/
|   `-- src/
|       |-- pages/           # farm, pos, inventory, finance, hr, admin, reports
|       |-- components/      # navbar, sidebar, layout
|       |-- context/         # authentication context
|       `-- api/             # Axios client and API helpers
|-- docs/                    # database, API and module documentation
`-- docker-compose.yml
```

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Node.js 18 or later (for the frontend)

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/AMAS-FARM-Management-System.git
cd AMAS-FARM-Management-System
```

### 2. Configure the environment

Create a `.env` file in the project root:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=change_me
POSTGRES_DB=amas_farm

SECRET_KEY=replace_with_a_long_random_string
ALGORITHM=HS256
CORS_ORIGINS=http://localhost:5173
```

### 3. Start the database and API

```bash
docker compose up --build
```

- API: http://localhost:8000
- Interactive API docs (Swagger UI): http://localhost:8000/docs

Apply the database migrations:

```bash
docker compose exec backend alembic upgrade head
```

### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

The app is served at http://localhost:3000.

## Documentation

Detailed documentation lives in the [`docs`](docs) folder:

- [Database architecture](docs/database/database-architecture.md) and the [ER diagrams](docs/database/README.md)
- [API reference](docs/api.md)
- [Frontend notes](docs/frontend.md)
- [Finance subsystem flow](docs/finance_backend_flow.md)
- [Development setup](docs/development/setup.md)

## What This Project Demonstrates

- Designing a large relational schema (farm, commerce, HR, assets and accounting) and evolving it with migrations
- Building a layered, fully asynchronous REST API in FastAPI
- Maintaining ledger integrity with atomic transactions and payment-status state tracking
- Implementing authentication and fine-grained role-based authorization on both API and UI
- Producing financial statements (trial balance, P&L, cash flow, balance sheet) from transactional data
- Delivering a localised, role-aware React interface
- Containerising the stack for reproducible local setup

## License

Released under the MIT License. See [LICENSE](LICENSE) for details. The frontend is based on the open source [Volt React Dashboard](https://github.com/themesberg/volt-react-dashboard) template by Themesberg (MIT).

## Author

**Your Name**
[GitHub](https://github.com/<tajirdev>) | [LinkedIn](https://www.linkedin.com/in/<alfred-christopher>) | mgenialfred671@gmail.com
