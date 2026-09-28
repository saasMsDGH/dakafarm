# Phase 9: Statement of Cash Flows

## Overview
Phase 9 introduces the **Cash Flow Statement** to the Finance module. While the P&L (Phase 8) looks at accrual profitability based on invoiced Sales and Purchases, the Cash Flow Statement strictly monitors **actual cash entering and leaving the business accounts**.

It calculates the net change in cash over a specific **date range** and categorizes the movements into the three standard financial activities: Operating, Investing, and Financing.

## The Three Categories
The Cash Flow Statement bypasses the `sales` and `purchases` tables entirely, pulling 100% of its data directly from the aggregated `financial_transactions` ledger.

### 1. Operating Activities (CFO)
Cash movements related to the primary business operations.
* **Cash from Sales**: Net of `SALE` cash transactions (money collected from customers).
* **Cash to Suppliers**: Net of `PURCHASE` cash transactions (money paid to suppliers).
* **Cash for Expenses**: Net of `EXPENSE` and `PAYROLL` payments.
* **Other Operating Cash**: Net of `OTHER_INCOME` and `ADJUSTMENT` transactions.
* **Uncategorized**: Catch-all for anomalous ledger data to ensure the cash mathematically ties out perfectly.

### 2. Investing Activities (CFI)
Cash used for long-term investments.
* **Cash for Assets**: Net of `ASSET_PURCHASE` transactions.

### 3. Financing Activities (CFF)
Cash transactions involving the owners or creditors.
* **Owner Investments**: Net of `OWNER_INVESTMENT` transactions (capital injections or drawings).

## Opening & Ending Balances
If a user requests the Cash Flow Statement for "This Month", the system dynamically calculates the **Opening Balance** exactly as it stood at midnight on the first of the month.
It achieves this by summing all `opening_balance` fields from `financial_accounts` and netting all `financial_transactions` that occurred *prior* to the `start_date`.

The system mathematically guarantees:
`Opening Balance + Net Cash Flow = Ending Balance`

## Implemented Endpoint

* **`GET /api/v1/finance/cash-flow`**
  - **Auth Required**: `finance_manager` or `admin`.
  - **Query Params**: 
    - `start_date` (Optional timestamp).
    - `end_date` (Optional timestamp).
  - **Returns**: A structured JSON object containing `operating`, `investing`, and `financing` nested categories, along with the `net_change_in_cash`, `opening_balance`, and `ending_balance`.

## How to Test
Run the automated test suite:
`..\.venv\Scripts\python.exe test_finance_cash_flow.py`

This test script creates an account, injects exactly $800 of Sales Cash, $500 of Expense Cash, $2000 of Asset Cash, and $10,000 of Owner Capital Cash. It then asserts that the Operating, Investing, and Financing categories shifted perfectly, and that checking the cash flow for a future date correctly carries the ending balance forward as the new opening balance.
