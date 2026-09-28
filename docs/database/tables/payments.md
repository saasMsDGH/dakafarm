# Payments Tables
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
