# Business Operations Tables (POS & Purchases)

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
