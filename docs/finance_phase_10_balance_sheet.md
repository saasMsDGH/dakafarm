# Phase 10: Balance Sheet

## Overview
Phase 10 introduces the **Balance Sheet** to the Finance module. This is the ultimate financial report, acting as a point-in-time snapshot of the farm's entire financial position.

It mathematically proves the fundamental accounting equation:
**Assets = Liabilities + Equity**

## The Structure

### 1. Assets (What the farm owns)
* **Cash & Bank**: Total available cash in all accounts (`SUM(Opening Balances) + Cash IN - Cash OUT`).
* **Accounts Receivable**: Unpaid customer sales.
* **Prepaid Purchases**: If we overpay a supplier, the excess negative payable dynamically flips into an Asset.
* **Fixed Assets**: Net capitalized asset purchases (e.g., Tractors, Land).

### 2. Liabilities (What the farm owes)
* **Accounts Payable**: Unpaid supplier bills.
* **Unearned Revenue**: If a customer overpays, the excess negative receivable dynamically flips into a Liability.

### 3. Equity (What belongs to the owners)
* **Owner's Capital**: The original cash used to open accounts, plus all subsequent net `OWNER_INVESTMENT` transactions.
* **Retained Earnings**: The lifetime Net Profit of the business (Total Revenue - Total Expenses).
  * *This bridges the P&L with the Balance Sheet, ensuring the entire accounting system balances perfectly.*

## Dynamic Equilibrium
Because the AMAS Farm system is modular and relies on aggregating live transaction data instead of double-entry ledger rows, the system includes dynamic failsafes:
* Unrecognized incoming cash is categorized as `Uncategorized Income` inside Retained Earnings.
* Unrecognized outgoing cash is categorized as `Uncategorized Expense` inside Retained Earnings.
* This guarantees that even if a developer manually inserts a bad transaction type into the database, **the Balance Sheet will NEVER go out of balance**.

## Implemented Endpoint

* **`GET /api/v1/finance/balance-sheet`**
  - **Auth Required**: `finance_manager` or `admin`.
  - **Query Params**: 
    - `as_of_date` (Optional timestamp to generate a historical point-in-time Balance Sheet).
  - **Returns**: A structured JSON object containing `assets`, `liabilities`, and `equity` categories, along with an `is_balanced` verification check.

## How to Test
Run the automated test suite:
`..\.venv\Scripts\python.exe test_finance_balance_sheet.py`

This test script takes a baseline snapshot, injects $50,000 of new owner capital, $2,000 in credit sales, and $5,000 in asset purchases. It verifies that Assets, Liabilities, and Equity shifted appropriately, and most importantly, it mathematically asserts that `Total Assets = Total Liabilities + Total Equity`.
