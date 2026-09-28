# Phase 11: Finance Dashboard API

## Overview
Phase 11 introduces the **Dashboard API**, a lightweight endpoint designed to power the frontend "Management Dashboard". It aggregates the most critical KPIs (Key Performance Indicators) from the farm's financial statements into a single, lightning-fast response.

## Architecture
To prevent duplicate calculation logic, the Dashboard Service does not query the database directly. Instead, it re-uses the battle-tested algorithms built in Phase 8 (P&L) and Phase 10 (Balance Sheet).

### The 6 KPIs
1. **`cash_on_hand`**: Sourced from the current Balance Sheet. Represents all available liquid capital.
2. **`accounts_receivable`**: Sourced from the current Balance Sheet. Represents money owed to the farm.
3. **`accounts_payable`**: Sourced from the current Balance Sheet. Represents money the farm owes to suppliers.
4. **`monthly_revenue`**: Sourced from the P&L, filtered dynamically to start on the 1st of the current UTC month.
5. **`monthly_expenses`**: Sourced from the P&L, filtered dynamically to start on the 1st of the current UTC month.
6. **`monthly_net_profit`**: Sourced from the P&L, filtered dynamically to start on the 1st of the current UTC month.

## Implemented Endpoint

* **`GET /api/v1/finance/dashboard`**
  - **Auth Required**: `finance_manager` or `admin`.
  - **Returns**: A flat JSON object containing the 6 KPIs.

## How to Test
Run the automated test suite:
`..\.venv\Scripts\python.exe test_finance_dashboard.py`

This test script takes a baseline snapshot of the Dashboard. It then creates a new Bank Account (with a 10k opening balance), registers a $3,000 Sale, and pays a $500 Utility bill.
It verifies that:
- Cash on Hand increases by exactly $9,500.
- Monthly Revenue increases by exactly $3,000.
- Monthly Expenses increase by exactly $500.
- Monthly Net Profit increases by exactly $2,500.
