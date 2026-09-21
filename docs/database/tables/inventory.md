# Inventory Tables

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
