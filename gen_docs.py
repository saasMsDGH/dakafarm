import os

base_dir = "d:/myprojects/AMAS FARM/AMAS-FARM-Management-System/docs/database"
os.makedirs(os.path.join(base_dir, 'tables'), exist_ok=True)
os.makedirs(os.path.join(base_dir, 'diagrams'), exist_ok=True)

def write_file(subpath, content):
    with open(os.path.join(base_dir, subpath), 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')

write_file('README.md', '''# Database Documentation

## Overview
Welcome to the AMAS FARM Management System Database Documentation. This documentation reflects the true, current state of the PostgreSQL database and SQLAlchemy models.

## Database Architecture
See [Database Architecture](database-architecture.md).

## Entity Relationship Diagrams
* [Database Overview](diagrams/database-overview.md)
* [Authentication ERD](diagrams/authentication-erd.md)
* [Farm ERD](diagrams/farm-erd.md)
* [Business & Sales ERD](diagrams/business-erd.md)
* [Inventory ERD](diagrams/inventory-erd.md)
* [HR & Assets ERD](diagrams/hr-assets-erd.md)
* [Finance ERD](diagrams/finance-erd.md)
* [Complete ERD](diagrams/complete-erd.md)

## Table References
* [Authentication](tables/authentication.md)
* [Farm Operations](tables/farm.md)
* [Business Operations](tables/business.md)
* [Inventory](tables/inventory.md)
* [Human Resources](tables/hr.md)
* [Assets](tables/assets.md)
* [Finance](tables/finance.md)
* [Payments](tables/payments.md)
''')

write_file('database-architecture.md', '''# Database Architecture

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
''')

auth_md = '''# Authentication Tables

## `users`
**Purpose**: Stores user authentication credentials, names, and status.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | Primary identifier |
| first_name | String | No | | | | |
| last_name | String | No | | | | |
| email | String | No | | Unique | | |
| phone | String | Yes | | | | |
| password_hash | String | Yes | | | | |
| is_active | Boolean | Yes | True | | | |
| created_at | DateTime | Yes | func.now() | | | |
| updated_at | DateTime | Yes | func.now() | | | |

## `roles`
**Purpose**: Defines system roles.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | Primary identifier |
| name | String | Yes | | | | |

## `userrole`
**Purpose**: Junction table linking users to roles.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | Primary identifier |
| user_id | Integer | Yes | | FK | users.id (CASCADE) | |
| role_id | Integer | Yes | | FK | roles.id (CASCADE) | |
'''
write_file('tables/authentication.md', auth_md)

farm_md = '''# Farm Operations Tables

## `houses`
**Purpose**: Physical poultry houses/structures on the farm.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | Primary identifier |
| name | String | No | | Unique | | |
| capacity | Integer | No | | | | |
| status | Boolean | Yes | True | | | |
| created_by | Integer | Yes | | FK | users.id | |

## `flocks`
**Purpose**: Batches of birds. Linked to a house.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | Primary identifier |
| name | String | No | | Unique | | |
| house_id | Integer | No | | FK | houses.id | |
| start_date | Date | No | | | | |
| initial_quantity | Integer | No | | | | |
| current_quantity | Integer | No | | | | |

## `medication_records`
**Purpose**: Logs treatments and medications given to a flock.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | Primary identifier |
| flock_id | Integer | No | | FK | flocks.id | |
| product_id | Integer | No | | FK | products.id | |
| record_date | Date | No | | | | |
| total_cost | Numeric | No | | | | |

## `vaccination_records`
**Purpose**: Logs vaccination schedules and completions for a flock.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | Primary identifier |
| flock_id | Integer | No | | FK | flocks.id | |
| product_id | Integer | No | | FK | products.id | |
| record_date | Date | No | | | | |
| total_cost | Numeric | No | | | | |

## `production_records`
**Purpose**: Tracks daily egg production.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| flock_id | Integer | No | | FK | flocks.id | |
| total_eggs | Integer | No | | | | |
| good_eggs | Integer | No | | | | |

## `mortality_records`
**Purpose**: Tracks bird deaths.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| flock_id | Integer | No | | FK | flocks.id | |
| quantity | Integer | No | | | | |

## `feed_records`
**Purpose**: Logs daily feed consumption.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| flock_id | Integer | No | | FK | flocks.id | |
| product_id | Integer | No | | FK | products.id | |
'''
write_file('tables/farm.md', farm_md)

business_md = '''# Business Operations Tables (POS & Purchases)

## `customers`
**Purpose**: Client details for sales.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | Primary identifier |
| name | String | No | | | | |

## `sales`
**Purpose**: Header record for a transaction.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | Primary identifier |
| invoice_number | String | No | | Unique | | |
| customer_id | Integer | No | | FK | customers.id | |
| total_amount | Numeric | No | | | | |

## `sale_items`
**Purpose**: Line items for a sale.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| sale_id | Integer | No | | FK | sales.id (CASCADE) | |
| product_id | Integer | No | | FK | products.id | |
| quantity | Numeric | No | | | | |

## `suppliers`
**Purpose**: Vendors who supply goods.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | Primary identifier |
| name | String | No | | | | |

## `purchases`
**Purpose**: Header record for procurement.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | Primary identifier |
| supplier_id | Integer | No | | FK | suppliers.id | |

## `purchase_items`
**Purpose**: Line items for a purchase.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| purchase_id | Integer | No | | FK | purchases.id (CASCADE) | |
| product_id | Integer | No | | FK | products.id | |

## `expenses`
**Purpose**: Tracks general operational expenses.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | Primary identifier |
| amount | Numeric | No | | | | |
'''
write_file('tables/business.md', business_md)

inventory_md = '''# Inventory Tables

## `product_categories`
**Purpose**: Hierarchical grouping of items.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | |
| name | String | No | | | | |

## `products`
**Purpose**: The actual items. Contains stock quantities.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| category_id | Integer | No | | FK | product_categories.id | |
| stock_quantity | Numeric | No | | | | |

## `stock_movements`
**Purpose**: Audit trail of every inventory change (IN, OUT, ADJUSTMENT).

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| product_id | Integer | No | | FK | products.id | |
| movement_type | String | No | | | | IN, OUT, ADJUSTMENT |
'''
write_file('tables/inventory.md', inventory_md)

hr_md = '''# Human Resources Tables

## `employees`
**Purpose**: Staff profiles and salary details.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | |

## `payrolls`
**Purpose**: Generated wage records.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| employee_id | Integer | No | | FK | employees.id | |
'''
write_file('tables/hr.md', hr_md)

assets_md = '''# Assets Tables

## `assets`
**Purpose**: Tracks fixed/moving farm assets (machinery, vehicles).

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | |

## `asset_distributions`
**Purpose**: Tracks where an asset is assigned.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| asset_id | Integer | No | | FK | assets.id | |
'''
write_file('tables/assets.md', assets_md)

finance_md = '''# Finance Tables

## `financial_accounts`
**Purpose**: Chart of accounts (Cash, Bank, Mobile Money).

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | |
| name | String | No | | | | |

## `financial_transactions`
**Purpose**: The general ledger recording monetary movement.

| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| account_id | Integer | No | | FK | financial_accounts.id | |
| amount | Numeric | No | | | | |
| transaction_type | String | No | | | | INCOME, EXPENSE, TRANSFER |
'''
write_file('tables/finance.md', finance_md)

payments_md = '''# Payments Tables
Records the actual monetary clearance for business operations.

## `payments` (Sales Payments)
| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | |
| sale_id | Integer | No | | FK | sales.id | |

## `purchase_payments`
| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | |
| purchase_id | Integer | No | | FK | purchases.id | |

## `expense_payments`
| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | |
| expense_id | Integer | No | | FK | expenses.id | |

## `payroll_payments`
| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | |
| payroll_id | Integer | No | | FK | payrolls.id | |

## `asset_payments`
| Column | Type | Nullable | Default | Key | References | Description |
|---|---|---|---|---|---|---|
| id | Integer | No | | PK | | |
| asset_id | Integer | No | | FK | assets.id | |
'''
write_file('tables/payments.md', payments_md)


# 4. Diagrams Documentation
write_file('diagrams/database-overview.md', '''# High-Level Database Architecture

```text
+-------------------+       +----------------+       +----------------+
| Authentication    | ----> | Business Oper. | ----> | Inventory      |
+-------------------+       +----------------+       +----------------+
                                  |
                                  v
+-------------------+       +----------------+
| Farm Operations   | ----> | Payments       |
+-------------------+       +----------------+
                                  |
                                  v
                            +----------------+
                            | Finance Ledger |
                            +----------------+
```
''')

write_file('diagrams/authentication-erd.md', '''# Authentication ERD

```mermaid
erDiagram
    USERS ||--o{ USERROLE : has
    ROLES ||--o{ USERROLE : assigned_to
```
''')

write_file('diagrams/farm-erd.md', '''# Farm ERD

```mermaid
erDiagram
    HOUSES ||--o{ FLOCKS : houses
    FLOCKS ||--o{ FEED_RECORDS : consumes
    FLOCKS ||--o{ MEDICATION_RECORDS : receives
    FLOCKS ||--o{ VACCINATION_RECORDS : receives
    FLOCKS ||--o{ MORTALITY_RECORDS : tracks
    FLOCKS ||--o{ PRODUCTION_RECORDS : produces
```
''')

write_file('diagrams/business-erd.md', '''# Business ERD

```mermaid
erDiagram
    CUSTOMERS ||--o{ SALES : makes
    SALES ||--|{ SALE_ITEMS : includes
    PRODUCTS ||--o{ SALE_ITEMS : sold_as
    SALES ||--o{ PAYMENTS : paid_via

    SUPPLIERS ||--o{ PURCHASES : supplies
    PURCHASES ||--|{ PURCHASE_ITEMS : includes
    PRODUCTS ||--o{ PURCHASE_ITEMS : bought_as
    PURCHASES ||--o{ PURCHASE_PAYMENTS : paid_via
```
''')

write_file('diagrams/inventory-erd.md', '''# Inventory ERD

```mermaid
erDiagram
    PRODUCT_CATEGORIES ||--o{ PRODUCTS : contains
    PRODUCTS ||--o{ STOCK_MOVEMENTS : tracks
```
''')

write_file('diagrams/hr-assets-erd.md', '''# HR & Assets ERD

```mermaid
erDiagram
    EMPLOYEES ||--o{ PAYROLLS : receives
    ASSETS ||--o{ ASSET_DISTRIBUTIONS : assigned
```
''')

write_file('diagrams/finance-erd.md', '''# Finance ERD

```mermaid
erDiagram
    FINANCIAL_ACCOUNTS ||--o{ FINANCIAL_TRANSACTIONS : logs
```
''')

write_file('diagrams/complete-erd.md', '''# Complete ERD

```mermaid
erDiagram
    USERS ||--o{ USERROLE : has
    ROLES ||--o{ USERROLE : assigned_to
    HOUSES ||--o{ FLOCKS : houses
    FLOCKS ||--o{ FEED_RECORDS : consumes
    FLOCKS ||--o{ MEDICATION_RECORDS : receives
    FLOCKS ||--o{ VACCINATION_RECORDS : receives
    FLOCKS ||--o{ MORTALITY_RECORDS : tracks
    FLOCKS ||--o{ PRODUCTION_RECORDS : produces
    PRODUCT_CATEGORIES ||--o{ PRODUCTS : contains
    PRODUCTS ||--o{ STOCK_MOVEMENTS : tracks
    CUSTOMERS ||--o{ SALES : makes
    SALES ||--|{ SALE_ITEMS : includes
    PRODUCTS ||--o{ SALE_ITEMS : sold_as
    SALES ||--o{ PAYMENTS : paid_via
    SUPPLIERS ||--o{ PURCHASES : supplies
    PURCHASES ||--|{ PURCHASE_ITEMS : includes
    PRODUCTS ||--o{ PURCHASE_ITEMS : bought_as
    PURCHASES ||--o{ PURCHASE_PAYMENTS : paid_via
    EMPLOYEES ||--o{ PAYROLLS : receives
    PAYROLLS ||--o{ PAYROLL_PAYMENTS : paid_via
    ASSETS ||--o{ ASSET_DISTRIBUTIONS : distributed_to
    ASSETS ||--o{ ASSET_PAYMENTS : paid_via
    FINANCIAL_ACCOUNTS ||--o{ FINANCIAL_TRANSACTIONS : logs
```
''')
