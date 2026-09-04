# AMAS FARM Database Design

## 1. Overview

The AMAS FARM Management System uses a centralized PostgreSQL database organized around:

- User & Access Management
- Farm Operations
- Sales & Business
- Inventory
- Finance
- Human Resources
- Asset Management
- Central Reporting

Operational transactions are stored once and reused by the relevant subsystems and reports.

> **Principle:** Profit & Loss, Cash Flow, and management reports should be generated from transaction data instead of being manually entered as independent records.

---

## 2. Entity Relationship Overview

```text
USERS ───────── USER_ROLES ───────── ROLES

CUSTOMERS ─────── SALES ─────── SALE_ITEMS ─────── PRODUCTS
                                                      │
SUPPLIERS ───── PURCHASES ─── PURCHASE_ITEMS ─────────┤
                                                      ▼
                                                   INVENTORY
                                                      │
                                               STOCK_MOVEMENTS
                                                      │
                           ┌──────────────────────────┼──────────────────┐
                           │                          │                  │
                         FEED                    MEDICATION         VACCINATION
                           │                          │                  │
                           └──────────────────────────┼──────────────────┘
                                                      │
                                                    FLOCKS
                                                      │
                           ┌──────────────────────────┼──────────────────┐
                           │                          │                  │
                      PRODUCTION                 MORTALITY          FEED_RECORDS

EXPENSES ────────────────┐
PAYROLL ─────────────────┤
SALES/PURCHASE PAYMENTS ─┼── FINANCIAL_TRANSACTIONS ── FINANCIAL_ACCOUNTS
ASSET PURCHASES ─────────┘

EMPLOYEES ───────── PAYROLL

ASSETS
```

---

# 3. User & Access Management

## 3.1 `users`

| Column | Type | Key | Description |
|---|---|---|---|
| id | UUID/BIGINT | PK | Unique user ID |
| first_name | VARCHAR | | First name |
| last_name | VARCHAR | | Last name |
| email | VARCHAR | UNIQUE | Login email |
| phone | VARCHAR | | Phone number |
| password_hash | VARCHAR | | Hashed password |
| is_active | BOOLEAN | | Account status |
| created_at | TIMESTAMP | | Creation date |
| updated_at | TIMESTAMP | | Last update |

## 3.2 `roles`

| Column | Type | Key | Description |
|---|---|---|---|
| id | UUID/BIGINT | PK | Role ID |
| name | VARCHAR | UNIQUE | Role name |
| description | TEXT | | Role description |

Possible roles:

- Administrator
- Chairperson
- Farm Manager
- Accountant
- Sales Officer
- Farm Worker

## 3.3 `user_roles`

| Column | Type | Key | Description |
|---|---|---|---|
| user_id | UUID/BIGINT | PK/FK | References `users.id` |
| role_id | UUID/BIGINT | PK/FK | References `roles.id` |

Relationship:

```text
users 1 ────────< user_roles >──────── 1 roles
```

---

# 4. Farm Operations

## 4.1 `houses`

| Column | Type | Key | Description |
|---|---|---|---|
| id | UUID/BIGINT | PK | House ID |
| name | VARCHAR | UNIQUE | House name |
| location | VARCHAR | | Location |
| capacity | INTEGER | | Maximum capacity |
| description | TEXT | | Description |
| created_at | TIMESTAMP | | Creation date |
| updated_at | TIMESTAMP | | Last update |

## 4.2 `flocks`

| Column | Type | Key | Description |
|---|---|---|---|
| id | UUID/BIGINT | PK | Flock ID |
| flock_code | VARCHAR | UNIQUE | Flock identifier |
| house_id | UUID/BIGINT | FK | References `houses.id` |
| breed | VARCHAR | | Breed/type |
| initial_quantity | INTEGER | | Initial birds |
| arrival_date | DATE | | Arrival date |
| status | VARCHAR | | Active/completed/etc. |
| created_at | TIMESTAMP | | Creation date |
| updated_at | TIMESTAMP | | Last update |

Relationship:

```text
houses 1 ─────────< flocks
```

---

# 5. Products & Categories

## 5.1 `product_categories`

| Column | Type | Key | Description |
|---|---|---|---|
| id | UUID/BIGINT | PK | Category ID |
| name | VARCHAR | UNIQUE | Category name |
| description | TEXT | | Description |

Examples:

- Eggs
- Chickens
- Chicks
- Feed
- Medication
- Vaccines
- Equipment
- Services
- Manure

## 5.2 `products`

| Column | Type | Key | Description |
|---|---|---|---|
| id | UUID/BIGINT | PK | Product ID |
| product_code | VARCHAR | UNIQUE | Product code |
| name | VARCHAR | | Product name |
| category_id | UUID/BIGINT | FK | References `product_categories.id` |
| unit | VARCHAR | | Unit of measurement |
| selling_price | NUMERIC(15,2) | | Default selling price |
| cost_price | NUMERIC(15,2) | | Default cost price |
| is_active | BOOLEAN | | Product status |
| created_at | TIMESTAMP | | Creation date |
| updated_at | TIMESTAMP | | Last update |

Relationship:

```text
product_categories 1 ─────────< products
```

---

# 6. Customers

## `customers`

| Column | Type | Key | Description |
|---|---|---|---|
| id | UUID/BIGINT | PK | Customer ID |
| customer_code | VARCHAR | UNIQUE | Customer code |
| name | VARCHAR | | Customer name |
| business_type | VARCHAR | | Business/type |
| phone | VARCHAR | | Phone |
| email | VARCHAR | | Email |
| address | TEXT | | Address |
| credit_limit | NUMERIC(15,2) | | Credit limit |
| created_at | TIMESTAMP | | Creation date |
| updated_at | TIMESTAMP | | Last update |

`total_purchases` and `outstanding_balance` should be calculated from transactions.

---

# 7. Suppliers

## `suppliers`

| Column | Type | Key | Description |
|---|---|---|---|
| id | UUID/BIGINT | PK | Supplier ID |
| supplier_code | VARCHAR | UNIQUE | Supplier code |
| name | VARCHAR | | Supplier/company |
| product_or_service | VARCHAR | | Main supply |
| phone | VARCHAR | | Phone |
| email | VARCHAR | | Email |
| address | TEXT | | Location |
| payment_terms_days | INTEGER | | Payment terms |
| created_at | TIMESTAMP | | Creation date |
| updated_at | TIMESTAMP | | Last update |

Outstanding payable should be calculated from purchases and payments.

---

# 8. Sales

## 8.1 `sales`

| Column | Type | Key | Description |
|---|---|---|---|
| id | UUID/BIGINT | PK | Sale ID |
| invoice_number | VARCHAR | UNIQUE | Invoice/receipt number |
| customer_id | UUID/BIGINT | FK | References `customers.id` |
| sale_date | TIMESTAMP | | Sale date |
| subtotal | NUMERIC(15,2) | | Subtotal |
| discount | NUMERIC(15,2) | | Discount |
| total_amount | NUMERIC(15,2) | | Final amount |
| payment_status | VARCHAR | | Paid/partial/unpaid |
| created_by | UUID/BIGINT | FK | References `users.id` |
| created_at | TIMESTAMP | | Creation date |

## 8.2 `sale_items`

| Column | Type | Key | Description |
|---|---|---|---|
| id | UUID/BIGINT | PK | Sale item ID |
| sale_id | UUID/BIGINT | FK | References `sales.id` |
| product_id | UUID/BIGINT | FK | References `products.id` |
| quantity | NUMERIC(15,3) | | Quantity |
| unit_price | NUMERIC(15,2) | | Selling price |
| total_amount | NUMERIC(15,2) | | Quantity × price |

Relationships:

```text
customers 1 ─────────< sales
sales 1 ─────────────< sale_items
products 1 ──────────< sale_items
```

---

# 9. Purchases

## 9.1 `purchases`

| Column | Type | Key | Description |
|---|---|---|---|
| id | UUID/BIGINT | PK | Purchase ID |
| purchase_number | VARCHAR | UNIQUE | LPO/Bill number |
| supplier_id | UUID/BIGINT | FK | References `suppliers.id` |
| purchase_date | TIMESTAMP | | Purchase date |
| subtotal | NUMERIC(15,2) | | Subtotal |
| total_amount | NUMERIC(15,2) | | Final amount |
| payment_status | VARCHAR | | Paid/partial/unpaid |
| created_by | UUID/BIGINT | FK | References `users.id` |
| created_at | TIMESTAMP | | Creation date |

## 9.2 `purchase_items`

| Column | Type | Key | Description |
|---|---|---|---|
| id | UUID/BIGINT | PK | Purchase item ID |
| purchase_id | UUID/BIGINT | FK | References `purchases.id` |
| product_id | UUID/BIGINT | FK | References `products.id` |
| quantity | NUMERIC(15,3) | | Quantity |
| unit_cost | NUMERIC(15,2) | | Cost per unit |
| total_amount | NUMERIC(15,2) | | Quantity × cost |

Relationships:

```text
suppliers 1 ─────────< purchases
purchases 1 ─────────< purchase_items
products 1 ──────────< purchase_items
```

---

# 10. Inventory

## 10.1 `inventory`

| Column | Type | Key | Description |
|---|---|---|---|
| id | UUID/BIGINT | PK | Inventory ID |
| product_id | UUID/BIGINT | FK/UNIQUE | References `products.id` |
| quantity | NUMERIC(15,3) | | Current quantity |
| reorder_level | NUMERIC(15,3) | | Reorder threshold |
| updated_at | TIMESTAMP | | Last update |

## 10.2 `stock_movements`

| Column | Type | Key | Description |
|---|---|---|---|
| id | UUID/BIGINT | PK | Movement ID |
| product_id | UUID/BIGINT | FK | References `products.id` |
| movement_type | VARCHAR | | IN/OUT/ADJUSTMENT |
| quantity | NUMERIC(15,3) | | Quantity |
| reference_type | VARCHAR | | Purchase/Sale/Feed/Medication/etc. |
| reference_id | UUID/BIGINT | | Related transaction |
| movement_date | TIMESTAMP | | Movement date |
| created_by | UUID/BIGINT | FK | References `users.id` |

Relationships:

```text
products 1 ─────────< inventory
products 1 ─────────< stock_movements
```

---

# 11. Feed Management

## `feed_records`

| Column | Type | Key | Description |
|---|---|---|---|
| id | UUID/BIGINT | PK | Feed record ID |
| flock_id | UUID/BIGINT | FK | References `flocks.id` |
| product_id | UUID/BIGINT | FK | Feed product |
| record_date | DATE | | Record date |
| opening_quantity | NUMERIC(15,3) | | Opening quantity |
| quantity_used | NUMERIC(15,3) | | Used quantity |
| closing_quantity | NUMERIC(15,3) | | Closing quantity |
| cost_per_unit | NUMERIC(15,2) | | Cost |
| total_cost | NUMERIC(15,2) | | Total feed cost |
| recorded_by | UUID/BIGINT | FK | References `users.id` |

Relationships:

```text
flocks 1 ─────────< feed_records
products 1 ───────< feed_records
```

Feed usage should create an inventory OUT movement.

---

# 12. Medication

## `medication_records`

| Column | Type | Key | Description |
|---|---|---|---|
| id | UUID/BIGINT | PK | Medication ID |
| flock_id | UUID/BIGINT | FK | References `flocks.id` |
| drug_product_id | UUID/BIGINT | FK | References `products.id` |
| record_date | DATE | | Date |
| disease_or_symptoms | TEXT | | Disease/symptoms |
| dosage | VARCHAR | | Dosage |
| administration_method | VARCHAR | | Administration method |
| administered_by | VARCHAR | | Person administering |
| cost | NUMERIC(15,2) | | Drug cost |
| remarks | TEXT | | Notes |

Relationships:

```text
flocks 1 ─────────< medication_records
products 1 ───────< medication_records
```

---

# 13. Vaccination

## `vaccination_records`

| Column | Type | Key | Description |
|---|---|---|---|
| id | UUID/BIGINT | PK | Vaccination ID |
| flock_id | UUID/BIGINT | FK | References `flocks.id` |
| vaccine_product_id | UUID/BIGINT | FK | References `products.id` |
| vaccination_date | DATE | | Vaccination date |
| target_disease | VARCHAR | | Disease targeted |
| target_population | INTEGER | | Birds targeted |
| method | VARCHAR | | Eye drop/Water/Injection |
| responsible_officer | VARCHAR | | Responsible person |
| next_due_date | DATE | | Next vaccination |
| remarks | TEXT | | Notes |

Relationships:

```text
flocks 1 ─────────< vaccination_records
products 1 ───────< vaccination_records
```

---

# 14. Mortality

## `mortality_records`

| Column | Type | Key | Description |
|---|---|---|---|
| id | UUID/BIGINT | PK | Mortality ID |
| flock_id | UUID/BIGINT | FK | References `flocks.id` |
| record_date | DATE | | Date |
| number_of_deaths | INTEGER | | Number of deaths |
| suspected_cause | VARCHAR | | Suspected cause |
| action_taken | TEXT | | Action taken |
| reported_by | UUID/BIGINT | FK | References `users.id` |

Cumulative mortality and remaining birds should preferably be calculated from flock quantity and mortality records.

Relationship:

```text
flocks 1 ─────────< mortality_records
```

---

# 15. Production

## `production_records`

| Column | Type | Key | Description |
|---|---|---|---|
| id | UUID/BIGINT | PK | Production ID |
| flock_id | UUID/BIGINT | FK | References `flocks.id` |
| record_date | DATE | | Production date |
| total_birds | INTEGER | | Birds |
| total_eggs | INTEGER | | Eggs collected |
| damaged_eggs | INTEGER | | Damaged eggs |
| good_eggs | INTEGER | | Good eggs |
| laying_percentage | NUMERIC(5,2) | | Production percentage |
| recorded_by | UUID/BIGINT | FK | References `users.id` |

Relationship:

```text
flocks 1 ─────────< production_records
```

---

# 16. Expenses

## 16.1 `expense_categories`

| Column | Type | Key | Description |
|---|---|---|---|
| id | UUID/BIGINT | PK | Category ID |
| name | VARCHAR | UNIQUE | Category name |
| description | TEXT | | Description |

## 16.2 `expenses`

| Column | Type | Key | Description |
|---|---|---|---|
| id | UUID/BIGINT | PK | Expense ID |
| expense_number | VARCHAR | UNIQUE | Voucher number |
| expense_date | TIMESTAMP | | Date |
| category_id | UUID/BIGINT | FK | References `expense_categories.id` |
| description | TEXT | | Purpose |
| paid_to | VARCHAR | | Recipient |
| amount | NUMERIC(15,2) | | Amount |
| payment_source | VARCHAR | | Cash/Bank |
| approved_by | UUID/BIGINT | FK | References `users.id` |
| created_by | UUID/BIGINT | FK | References `users.id` |
| created_at | TIMESTAMP | | Creation date |

Relationships:

```text
expense_categories 1 ─────────< expenses
users 1 ─────────────────────< expenses (created_by)
users 1 ─────────────────────< expenses (approved_by)
```

---

# 17. Financial Accounts

## 17.1 `financial_accounts`

| Column | Type | Key | Description |
|---|---|---|---|
| id | UUID/BIGINT | PK | Account ID |
| name | VARCHAR | | Account name |
| account_type | VARCHAR | | CASH/BANK |
| bank_name | VARCHAR | | Bank name if applicable |
| account_number | VARCHAR | | Bank account reference |
| opening_balance | NUMERIC(15,2) | | Opening balance |
| is_active | BOOLEAN | | Account status |
| created_at | TIMESTAMP | | Creation date |

## 17.2 `financial_transactions`

Central financial transaction ledger.

| Column | Type | Key | Description |
|---|---|---|---|
| id | UUID/BIGINT | PK | Transaction ID |
| account_id | UUID/BIGINT | FK | References `financial_accounts.id` |
| transaction_date | TIMESTAMP | | Date |
| transaction_type | VARCHAR | | SALE/PURCHASE/EXPENSE/PAYROLL/etc. |
| description | TEXT | | Details |
| reference_number | VARCHAR | | Receipt/voucher/reference |
| amount | NUMERIC(15,2) | | Amount |
| direction | VARCHAR | | IN/OUT |
| created_by | UUID/BIGINT | FK | References `users.id` |
| created_at | TIMESTAMP | | Creation date |

Relationship:

```text
financial_accounts 1 ─────────< financial_transactions
```

Cash Book and Bank Record can be generated from this ledger.

---

# 18. Employees & Payroll

## 18.1 `employees`

| Column | Type | Key | Description |
|---|---|---|---|
| id | UUID/BIGINT | PK | Employee ID |
| employee_code | VARCHAR | UNIQUE | Employee code |
| first_name | VARCHAR | | First name |
| last_name | VARCHAR | | Last name |
| position | VARCHAR | | Position |
| phone | VARCHAR | | Phone |
| employment_date | DATE | | Employment date |
| status | VARCHAR | | Active/inactive |
| created_at | TIMESTAMP | | Creation date |

## 18.2 `payroll`

| Column | Type | Key | Description |
|---|---|---|---|
| id | UUID/BIGINT | PK | Payroll ID |
| employee_id | UUID/BIGINT | FK | References `employees.id` |
| pay_period | DATE | | Payroll period |
| basic_salary | NUMERIC(15,2) | | Basic salary |
| allowances | NUMERIC(15,2) | | Allowances |
| deductions | NUMERIC(15,2) | | Deductions |
| net_salary | NUMERIC(15,2) | | Net salary |
| payment_date | DATE | | Payment date |
| payment_status | VARCHAR | | Paid/unpaid |
| created_at | TIMESTAMP | | Creation date |

Relationship:

```text
employees 1 ─────────< payroll
```

---

# 19. Asset Management

## `assets`

| Column | Type | Key | Description |
|---|---|---|---|
| id | UUID/BIGINT | PK | Asset ID |
| asset_code | VARCHAR | UNIQUE | Asset identifier |
| name | VARCHAR | | Asset name |
| description | TEXT | | Description |
| serial_number | VARCHAR | | Serial/tag number |
| purchase_date | DATE | | Purchase date |
| cost_price | NUMERIC(15,2) | | Cost |
| location | VARCHAR | | Location |
| condition | VARCHAR | | Current condition |
| depreciation_rate | NUMERIC(5,2) | | Depreciation rate |
| status | VARCHAR | | Active/disposed/etc. |
| created_at | TIMESTAMP | | Creation date |
| updated_at | TIMESTAMP | | Last update |

---

# 20. Major Relationships

## Sales

```text
CUSTOMER
   │
   ▼
SALE
   │
   ▼
SALE_ITEM
   │
   ▼
PRODUCT
   │
   ▼
INVENTORY
```

## Purchasing

```text
SUPPLIER
   │
   ▼
PURCHASE
   │
   ▼
PURCHASE_ITEM
   │
   ▼
PRODUCT
   │
   ▼
INVENTORY
```

## Farm Operations

```text
HOUSE
  │
  ▼
FLOCK
  │
  ├── PRODUCTION
  ├── FEED_RECORDS ──── INVENTORY
  ├── MEDICATION ────── INVENTORY
  ├── VACCINATION ───── INVENTORY
  └── MORTALITY
```

## Finance

```text
SALES/PAYMENTS ────────┐
PURCHASE/PAYMENTS ─────┤
EXPENSES ──────────────┤
PAYROLL ───────────────┼── FINANCIAL_TRANSACTIONS
ASSET PURCHASES ───────┘
                              │
                              ▼
                       FINANCIAL_ACCOUNTS
                         Cash / Bank
```

---

# 21. Central Reporting

Reports are generated from operational data.

## Profit & Loss

```text
SALES
  ↓
REVENUE
  ↓
COGS
  ↓
GROSS PROFIT
  ↓
OPERATING EXPENSES
  ↓
NET PROFIT
```

## Cash Flow

```text
FINANCIAL_TRANSACTIONS
          │
          ├── Operating Activities
          ├── Investing Activities
          └── Financing Activities
                    │
                    ▼
              CASH FLOW REPORT
```

## Management Analytics

The reporting layer can combine:

- Production
- Mortality
- Feed consumption
- Medication costs
- Sales
- Purchases
- Expenses
- Cash
- Bank
- Inventory
- Payroll
- Assets
- Customers
- Suppliers

to provide management-level analysis.

---

# 22. Database Modules

```text
01. AUTH
    users
    roles
    user_roles

02. FARM
    houses
    flocks
    production_records
    feed_records
    medication_records
    vaccination_records
    mortality_records

03. BUSINESS
    customers
    suppliers
    products
    product_categories
    sales
    sale_items
    purchases
    purchase_items

04. INVENTORY
    inventory
    stock_movements

05. FINANCE
    expense_categories
    expenses
    financial_accounts
    financial_transactions

06. HR
    employees
    payroll

07. ASSETS
    assets

08. REPORTING
    Profit & Loss
    Cash Flow
    Farm Performance
    Sales Analysis
    Inventory Analysis
    Management Analytics
```

---

# 23. Design Rules

1. Every table has a primary key.
2. Relationships use foreign keys.
3. Avoid unnecessary duplication.
4. Calculated values should preferably come from source transactions.
5. Financial transactions must be traceable to their source.
6. Inventory movements must be traceable to their source.
7. Farm operational records should be linked to a flock where applicable.
8. User-created records should be traceable where appropriate.
9. Monetary values use `NUMERIC`, not floating-point types.
10. Dates and timestamps should be stored consistently.
11. Alembic will manage database migrations.
12. One PostgreSQL database will serve the centralized application while the schema remains logically modular.

---

# 24. Database Status

**Version:** v1.0  
**Status:** Initial database design approved for the System Architecture phase.

The schema may be extended or modified during development when a confirmed business requirement or architectural issue requires it.
