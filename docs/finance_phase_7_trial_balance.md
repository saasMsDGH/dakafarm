# Phase 7: Trial Balance (Accounting Balances)

## Overview
Phase 7 introduces the **Trial Balance**, a standard accounting report that guarantees the mathematical integrity of the financial subsystem. The Trial Balance proves that total Debits (DR) equal total Credits (CR).

Because AMAS Farm Management System uses a modern, modular, single-ledger architecture (rather than legacy double-entry journal tables), we synthesize a mathematically perfect Trial Balance by mapping our existing data models (Invoices, Accounts, and Transactions) to standard accounting categories in real-time.

## The Mathematical Mapping
The report calculates point-in-time balances across the following categories:

### 🔴 DEBITS (Assets & Expenses)
1. **Cash & Bank Balances (Asset)**: The net balance of all financial accounts (`Opening + IN - OUT`).
2. **Accounts Receivable (Asset)**: The total unpaid customer balances (`SUM(Sales Invoices) - SUM(SALE payments IN) + SUM(SALE refunds OUT)`).
3. **Purchases (Expense/COGS)**: The total invoice value of all Purchases from suppliers.
4. **Direct Expenses (Expense)**: Net of all `EXPENSE` transactions.
5. **Payroll (Expense)**: Net of all `PAYROLL` transactions.
6. **Fixed Assets (Asset)**: Net of all `ASSET_PURCHASE` transactions.
7. **Negative Adjustments (Expense)**: Net of `ADJUSTMENT` losses.

### 🟢 CREDITS (Liabilities, Equity, & Revenue)
1. **Accounts Payable (Liability)**: The total unpaid supplier balances (`SUM(Purchase Invoices) - SUM(PURCHASE payments OUT) + SUM(PURCHASE refunds IN)`).
2. **Sales Revenue (Income)**: The total invoice value of all Sales to customers.
3. **Other Income (Income)**: Net of `OTHER_INCOME` transactions.
4. **Owner's Equity (Equity)**: Net of `OWNER_INVESTMENT` transactions.
5. **Opening Balances (Equity)**: The sum of all `opening_balance` fields across all financial accounts.
6. **Positive Adjustments (Income)**: Net of `ADJUSTMENT` gains.

## Error Handling & Uncategorized Transactions
During testing, we discovered a malformed transaction in the database (an older test inserted a transaction with type `ASSET` instead of `ASSET_PURCHASE`). 
To ensure the Trial Balance **never** goes out of balance due to bad data, the repository uses a dynamic grouping algorithm:
- Any `transaction_type` not explicitly mapped above is automatically caught and categorized as an `Uncategorized Income` or `Uncategorized Expense` based on its net cash flow direction.
- **This guarantees the Trial Balance mathematically matches the Cash position perfectly, regardless of database anomalies.**

## Implemented Endpoint

* **`GET /api/v1/finance/trial-balance`**
  - **Auth Required**: `finance_manager` or `admin`.
  - **Query Params**: `as_of_date` (Optional timestamp to generate a historical point-in-time Trial Balance).
  - **Returns**: A list of all Trial Balance entries (`account_name`, `debit`, `credit`), the `total_debits`, `total_credits`, and a boolean `is_balanced` flag.

## How to Test
Run the automated test suite:
`..\.venv\Scripts\python.exe test_finance_trial_balance.py`

This test script simulates a full accounting lifecycle (Opening accounts, owner investment, buying on credit, paying partial amounts, selling for cash) and then asserts that the mathematical equation perfectly balances.
