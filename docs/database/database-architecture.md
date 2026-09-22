# Database Architecture

## 1. Database Technology
* **Database Engine**: PostgreSQL
* **ORM**: SQLAlchemy
* **Migrations**: Alembic
* **API Framework**: FastAPI
* **Connection**: psycopg2 / asyncpg

## 2. Architecture Flow
```text
React Frontend (Vite)
      |
FastAPI (Python)
      |
Service Layer (Business Logic)
      |
Repository Layer (CRUD)
      |
SQLAlchemy (ORM)
      |
PostgreSQL (Database)
```

## 3. Database Design Principles
* **Relational Database**: Fully normalized SQL structure.
* **Foreign Key Integrity**: Using strict RESTRICT and CASCADE behaviors where appropriate.
* **Transactional Immutability**: Core financial records (like Payments and Transactions) rely heavily on append-only models for audits.
* **Timestamps**: created_at and updated_at (timezone aware) are standard on all major operational tables.

## 4. Financial Data Model
Data flows from core operations into the unified financial ledger.
```text
Sales / Purchases / Payroll / Expenses
                    |
                    v
          Specific Payment Tables 
          (e.g., purchase_payments)
                    |
                    v
          Financial Transactions
                    |
                    v
           Financial Accounts
```
* **Business Transaction**: The overarching event (Sale, Purchase).
* **Payment**: The specific movement of money against a business event.
* **Financial Transaction**: The ultimate general ledger entry that debits/credits an account.
