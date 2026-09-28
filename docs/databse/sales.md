# AMAS FARM — POS SUBSYSTEM

## Sales, Purchases & Expenses

We have completed the **Farm Management subsystem** and the **Inventory Management subsystem**, including both backend and frontend.

We are now beginning the largest and most business-critical subsystem of the AMAS FARM system.

For this project, we will refer to this subsystem as:

**POS — Sales, Purchases & Expenses**

This subsystem is critical because the data generated here will eventually feed the company's financial and management reports. The quality and correctness of this subsystem will directly affect the accuracy of Profit & Loss, Cash Flow, inventory valuation, customer balances, supplier balances, and management decision-making.

Therefore, treat this subsystem as a **production-critical subsystem**.

---

# 1. OBJECTIVE

The POS subsystem will manage the farm's commercial transactions:

```text
POS
│
├── Customers
├── Suppliers
├── Sales
├── Purchases
└── Expenses
```

There are two major business sides:

```text
SELLING SIDE
│
├── Customers
└── Sales
```

and:

```text
PURCHASING SIDE
│
├── Suppliers
└── Purchases
```

Expenses are handled within the same subsystem because they represent operational money outflows that must eventually contribute to financial reporting.

---

# 2. WHY THIS SUBSYSTEM IS IMPORTANT

This is not simply another CRUD module.

The system must preserve the relationship between:

```text
Customer
   ↓
Sale
   ↓
Sale Items
   ↓
Product
   ↓
Inventory OUT
   ↓
Financial Records
```

and:

```text
Supplier
   ↓
Purchase
   ↓
Purchase Items
   ↓
Product
   ↓
Inventory IN
   ↓
Financial Records
```

and:

```text
Expense
   ↓
Financial Records
```

The goal is to create reliable transaction records that can later be used by the Finance and Reporting subsystems.

Do not treat these components as isolated CRUD operations.

---

# 3. USER ROLES

The primary roles responsible for this subsystem are:

```text
sell_manager
sell_officer
```

The existing system Administrator remains unrestricted according to the project's global RBAC rules.

## sell_manager

The `sell_manager` is the senior operational role for the POS subsystem.

The manager should be able to:

* View customers
* Create customers
* Update customers
* Manage customer records
* View suppliers
* Create suppliers
* Update suppliers
* Manage sales
* Manage purchases
* Manage expenses according to the approved business rules
* Review transactions
* Review customer balances
* Review supplier balances
* Review transaction history
* Perform management-level POS operations

## sell_officer

The `sell_officer` is the operational sales role.

The officer should primarily:

* View customers
* Register customers
* View products
* Create sales
* View sales
* Work with customer transactions
* Perform normal POS operations allowed by the business rules

The officer must not automatically receive every permission given to `sell_manager`.

RBAC must be enforced consistently through the backend.

Do not rely on frontend hiding alone for authorization.

---

# 4. SUBSYSTEM STRUCTURE

The POS subsystem should conceptually be organized as:

```text
POS
│
├── Customers
│
├── Suppliers
│
├── Sales
│   ├── Sales
│   └── Sale Items
│
├── Purchases
│   ├── Purchases
│   └── Purchase Items
│
└── Expenses
    └── Expense Categories / Expenses
```

Follow the project's established module architecture.

For example:

```text
pos/
├── models/
├── schemas/
├── repository/
├── service/
└── router/
```

Do not create a completely different architecture for POS.

The completed Farm and Inventory modules are the reference for implementation patterns.

---

# 5. CUSTOMER MANAGEMENT

The first component we will implement is:

**Customers**

Customer table:

```text
customers
```

Fields:

| Column        | Type          | Key    | Description   |
| ------------- | ------------- | ------ | ------------- |
| id            | ID            | PK     | Customer ID   |
| customer_code | VARCHAR       | UNIQUE | Customer code |
| name          | VARCHAR       |        | Customer name |
| business_type | VARCHAR       |        | Business/type |
| phone         | VARCHAR       |        | Phone         |
| email         | VARCHAR       |        | Email         |
| address       | TEXT          |        | Address       |
| credit_limit  | NUMERIC(15,2) |        | Credit limit  |
| created_at    | TIMESTAMP     |        | Creation date |
| updated_at    | TIMESTAMP     |        | Last update   |

Important:

Do not add manually maintained fields such as:

```text
total_purchases
outstanding_balance
```

unless the architecture later establishes a specific reason.

Customer balances should be derived from actual transactions and payments.

---

# 6. SALES

The Sales component records products sold to customers.

Main table:

```text
sales
```

Fields:

| Column         | Type          | Key    | Description             |
| -------------- | ------------- | ------ | ----------------------- |
| id             | ID            | PK     | Sale ID                 |
| invoice_number | VARCHAR       | UNIQUE | Invoice/receipt number  |
| customer_id    | UUID/BIGINT   | FK     | References customers.id |
| sale_date      | TIMESTAMP     |        | Sale date               |
| subtotal       | NUMERIC(15,2) |        | Subtotal                |
| discount       | NUMERIC(15,2) |        | Discount                |
| total_amount   | NUMERIC(15,2) |        | Final amount            |
| payment_status | VARCHAR       |        | Paid/partial/unpaid     |
| created_by     | UUID/BIGINT   | FK     | References users.id     |
| created_at     | TIMESTAMP     |        | Creation date           |

Sale items:

```text
sale_items
```

| Column       | Type          | Key | Description            |
| ------------ | ------------- | --- | ---------------------- |
| id           | ID            | PK  | Sale item ID           |
| sale_id      | UUID/BIGINT   | FK  | References sales.id    |
| product_id   | UUID/BIGINT   | FK  | References products.id |
| quantity     | NUMERIC(15,3) |     | Quantity               |
| unit_price   | NUMERIC(15,2) |     | Selling price          |
| total_amount | NUMERIC(15,2) |     | Quantity × price       |

Relationships:

```text
customers 1 ─────────< sales

sales 1 ─────────────< sale_items

products 1 ──────────< sale_items
```

---

# 7. SALES AND INVENTORY INTEGRATION

A successful sale must eventually produce the appropriate inventory movement.

Example:

```text
Sale
  ↓
Sale Item
  ↓
Product
  ↓
Stock Movement: OUT
```

The system must not simply decrease inventory without creating the appropriate transaction history.

We need an auditable relationship between the sale and the resulting stock movement.

The implementation must also prevent invalid operations such as selling more stock than is available
---

# 8. INVOICES AND RECEIPTS

The POS must distinguish between transaction/payment states.

For a customer who purchases on credit:

```text
Customer
   ↓
Sale
   ↓
Outstanding amount
   ↓
Invoice
```

For a customer who has already paid:

```text
Customer
   ↓
Sale
   ↓
Payment completed
   ↓
Receipt
```

The exact invoice/receipt generation mechanism should be designed carefully during the Sales implementation.

Do not implement a superficial PDF/document generator without first establishing the correct transaction and payment logic.

---

# 9. SUPPLIERS

Purchases handle products and services coming into the farm.

Supplier table:

```text
suppliers
```

Fields:

| Column             | Type        | Key    | Description      |
| ------------------ | ----------- | ------ | ---------------- |
| id                 | ID          | PK     | Supplier ID      |
| supplier_code      | VARCHAR     | UNIQUE | Supplier code    |
| name               | VARCHAR     |        | Supplier/company |
| product_or_service | VARCHAR     |        | Main supply      |
| phone              | VARCHAR     |        | Phone            |
| email              | VARCHAR     |        | Email            |
| address            | TEXT        |        | Location         |
| payment_terms_days | INTEGER     |        | Payment terms    |
| created_at         | TIMESTAMP   |        | Creation date    |
| updated_at         | TIMESTAMP   |        | Last update      |

Outstanding payable should be calculated from actual purchases and payments rather than manually maintained.

---

# 10. PURCHASES

Main table:

```text
purchases
```

Fields:

| Column          | Type          | Key    | Description             |
| --------------- | ------------- | ------ | ----------------------- |
| id              | ID            | PK     | Purchase ID             |
| purchase_number | VARCHAR       | UNIQUE | LPO/Bill number         |
| supplier_id     | UUID/BIGINT   | FK     | References suppliers.id |
| purchase_date   | TIMESTAMP     |        | Purchase date           |
| subtotal        | NUMERIC(15,2) |        | Subtotal                |
| total_amount    | NUMERIC(15,2) |        | Final amount            |
| payment_status  | VARCHAR       |        | Paid/partial/unpaid     |
| created_by      | ID            | FK     | References users.id     |
| created_at      | TIMESTAMP     |        | Creation date           |

Purchase items:

```text
purchase_items
```

| Column       | Type          | Key | Description             |
| ------------ | ------------- | --- | ----------------------- |
| id           | ID            | PK  | Purchase item ID        |
| purchase_id  | UUID/BIGINT   | FK  | References purchases.id |
| product_id   | UUID/BIGINT   | FK  | References products.id  |
| quantity     | NUMERIC(15,3) |     | Quantity                |
| unit_cost    | NUMERIC(15,2) |     | Cost per unit           |
| total_amount | NUMERIC(15,2) |     | Quantity × cost         |

Relationships:

```text
suppliers 1 ─────────< purchases

purchases 1 ─────────< purchase_items

products 1 ──────────< purchase_items
```

---

# 11. PURCHASES AND INVENTORY

When products are successfully purchased and received:

```text
Purchase
   ↓
Purchase Item
   ↓
Product
   ↓
Stock Movement: IN
```

This is particularly important because purchases may involve different farm requirements such as:

* Feed
* Medication
* Vaccines
* Equipment
* Eggs/chicks/birds
* Other inventory products

The implementation must maintain a reliable audit trail.

---

# 12. EXPENSES

Expenses represent operational expenditure.

Main table:

```text
expenses
```

Fields:

| Column         | Type          | Key    | Description                      |
| -------------- | ------------- | ------ | -------------------------------- |
| id             |ID             | PK     | Expense ID                       |
| expense_number | VARCHAR       | UNIQUE | Voucher number                   |
| expense_date   | TIMESTAMP     |        | Date                             |
| category_id    | UUID/BIGINT   | FK     | References expense_categories.id |
| description    | TEXT          |        | Purpose                          |
| paid_to        | VARCHAR       |        | Recipient                        |
| amount         | NUMERIC(15,2) |        | Amount                           |
| payment_source | VARCHAR       |        | Cash/Bank                        |
| approved_by    | UUID/BIGINT   | FK     | References users.id              |
| created_by     | UUID/BIGINT   | FK     | References users.id              |
| created_at     | TIMESTAMP     |        | Creation date                    |

Relationships:

```text
expense_categories 1 ─────────< expenses

users 1 ─────────────────────< expenses (created_by)

users 1 ─────────────────────< expenses (approved_by)
```

Expenses must eventually integrate with Finance.

Do not create a duplicate financial system inside POS.
> NOTE: AFTER THIS SUBSYSTEM NEXT WILL BE FINANCE
---

# 13. TRANSACTION INTEGRITY

This subsystem contains multi-step operations.

For example:

```text
Create Sale
    ↓
Validate Customer
    ↓
Validate Products
    ↓
Validate Stock
    ↓
Create Sale
    ↓
Create Sale Items
    ↓
Create Stock Movements
    ↓
Record payment/financial effect
    ↓
Commit transaction
```

If an important step fails, the operation should not leave the database in a partially completed state.

Use proper database transactions.

The service layer should control transaction boundaries for multi-table business operations.

Do not blindly commit separately in every repository method.

---

# 14. ARCHITECTURE RULE

Follow the established AMAS architecture:

```text
Router
   ↓
Service
   ↓
Repository
   ↓
Models
   ↓
Database
```

Responsibilities:

### Router

* HTTP endpoints
* Request/response handling
* Authentication
* RBAC
* Calling services

### Schema

* Request validation
* Response contracts
* Query/filter/pagination inputs

### Service

* Business rules
* Workflows
* Validation involving multiple entities
* Transaction coordination

### Repository

* Database queries
* CRUD
* Search
* Filtering
* Sorting
* Pagination

### Models

* SQLAlchemy entities
* Relationships
* Constraints
* Database structure

Do not put business logic into routers.

Do not put HTTP logic into repositories.

Do not create unnecessary abstractions.

---

# 15. API VERSIONING

Continue using:

```text
/api/v1/
```

The POS endpoints should follow the established API versioning structure.

Do not introduce a new API architecture.

---

# 16. INVENTORY INTEGRATION

The POS subsystem must integrate with the already completed Inventory subsystem.

Sales:

```text
Sale → Stock OUT
```

Purchases:

```text
Purchase → Stock IN
```

Do not duplicate the inventory logic inside POS.

Reuse the existing Inventory implementation and established stock-movement pattern.

Before implementing integrations, inspect the existing Inventory code and understand exactly how it currently handles stock movements.

---

# 17. REPORTING IMPORTANCE

The following future reports will depend heavily on POS data:

```text
Sales Analysis
Purchase Analysis
Customer Balances
Supplier Payables
Revenue
Expenses
Cost of Goods Sold
Gross Profit
Cash Flow
Profit & Loss
```

Therefore:

**Never store calculated values merely because they make a screen easier to display.**

Prefer deriving financial/reporting values from reliable transaction records.

Any denormalized or cached value must have a clear reason and synchronization strategy.

---

# 18. DEVELOPMENT STRATEGY

Do NOT implement the entire POS subsystem at once.

We will build it one component at a time.

The first component is:

```text
Customers
```

Then we will proceed incrementally through:

```text
1. Customers
2. Suppliers
3. Sales
4. Purchases
5. Expenses
6. POS integrations
7. Reports/analytics required by POS
8. Full testing and verification
```

The exact sequence may change if implementation dependencies require it.

At every stage:

```text
Backend
   ↓
Tests
   ↓
Frontend
   ↓
Integration
   ↓
Verification
```

Only after one component is stable should we move to the next.

---

# 19. IMPORTANT AGENT RULES

You have autonomy to:

* Inspect the existing codebase
* Inspect the completed Farm module
* Inspect the completed Inventory module
* Reuse established patterns
* Fix routine implementation mistakes
* Run tests
* Debug errors
* Improve implementation where necessary
* Modify existing code when required for correct integration

However:

**Do not over-engineer.**

Do not introduce microservices.

Do not create unnecessary abstractions.

Do not rewrite working modules without a clear reason.

Do not create duplicate functionality.

Do not silently make major business decisions.

If a decision affects financial correctness, inventory correctness, transaction integrity, RBAC, or the overall architecture, explain the decision before proceeding when it is not already defined by these requirements.

---

# 20. CURRENT TASK

For now, do not implement Customers yet.

First inspect the existing:

```text
Farm subsystem
Inventory subsystem
Authentication
RBAC
Database configuration
Alembic
API versioning
Shared utilities
Frontend architecture
```

Pay particular attention to how the completed Farm and Inventory modules implement:

* Models
* Schemas
* Repository
* Service
* Router
* Pagination
* Search
* Filtering
* Sorting
* Authentication
* RBAC
* Error handling
* Transactions
* Frontend API integration
* Forms
* Tables
* Loading states
* Error states

Then explain:

1. Which patterns from Farm should be reused.
2. Which patterns from Inventory should be reused.
3. What existing components POS should integrate with.
4. Whether anything in the current foundation needs to be adjusted before POS development.
5. The implementation plan for the **Customer component only**.

Do not modify files yet.

Wait for approval before beginning implementation.

The priority for this subsystem is:

**Correctness → Data integrity → Security → Maintainability → Usability → Speed of development**

This subsystem is business-critical. Build it carefully.
