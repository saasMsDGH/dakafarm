# Finance Tables

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
