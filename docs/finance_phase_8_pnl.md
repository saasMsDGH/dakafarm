# Phase 8: Profit & Loss (Income Statement)

## Overview
Phase 8 introduces the **Profit & Loss (P&L)** statement to the Finance module. While the Trial Balance (Phase 7) is a snapshot of all lifetime balances, the P&L measures the financial performance of the farm over a specific **date range** (e.g., a month, a quarter, or a year).

The P&L is structured in a standard **Multi-Step Format**, meaning it isolates core operating margins from secondary income.

## The Multi-Step Structure
The P&L calculates the following performance metrics dynamically from the `sales`, `purchases`, and `financial_transactions` tables:

### 1. Operating Revenue
The income generated from the farm's primary operations (selling inventory).
* **Sales**: `SUM(Sale.total_amount)`

### 2. Cost of Goods Sold (COGS)
The direct costs attributable to acquiring the goods sold. In this cash/accrual hybrid model, it maps to inventory purchases.
* **Purchases**: `SUM(Purchase.total_amount)`

**=> GROSS PROFIT = (Operating Revenue - COGS)**

### 3. Operating Expenses (OPEX)
The day-to-day expenses required to run the farm.
* **Direct Expenses**: Net of all `EXPENSE` transactions.
* **Payroll Expenses**: Net of all `PAYROLL` transactions.
* **Negative Adjustments**: Net of `ADJUSTMENT` losses.

**=> OPERATING PROFIT = (Gross Profit - OPEX)**

### 4. Non-Operating Income
Secondary or exceptional income/expenses not related to core farm operations.
* **Other Income**: Net of `OTHER_INCOME` transactions.
* **Positive Adjustments**: Net of `ADJUSTMENT` gains.
* **Uncategorized Income/Expense**: (A failsafe catching any unmapped transaction types in the ledger, ensuring no value is "lost" off the P&L if someone manually injects bad data into the DB).

**=> NET PROFIT = (Operating Profit + Non-Operating Income)**

*(Note: Owner Investments, Owner Drawings, Asset Purchases, and Cash/Bank Balances are strictly Balance Sheet items and are correctly excluded from the P&L).*

## Implemented Endpoint

* **`GET /api/v1/finance/pnl`**
  - **Auth Required**: `finance_manager` or `admin`.
  - **Query Params**: 
    - `start_date` (Optional timestamp to begin the P&L period).
    - `end_date` (Optional timestamp to end the P&L period).
  - **Returns**: A structured JSON object containing `revenue`, `cogs`, `opex`, `non_operating` sections, and the calculated `gross_profit`, `operating_profit`, and `net_profit`.

## How to Test
Run the automated test suite:
`..\.venv\Scripts\python.exe test_finance_pnl.py`

This test simulates injecting revenue, COGS, direct expenses, payroll, and non-operating income, verifies the math updates perfectly, and then tests the date filters by asserting that a P&L fetched for "tomorrow" is completely empty (all zeroes).
