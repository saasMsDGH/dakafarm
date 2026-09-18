# Phase 6: Receivables & Payables (Customer & Supplier Balances)

## Overview
Phase 6 introduces the **Accounts Receivable** and **Accounts Payable** tracking layers to the Finance module.
- **Receivables (Customer Balances):** Tracks money owed to the farm by customers who purchased goods on credit (PARTIAL or UNPAID sales).
- **Payables (Supplier Balances):** Tracks money the farm owes to suppliers for inventory purchased on credit (PARTIAL or UNPAID purchases).

## Architecture & Source of Truth
Like Phase 5 (Books), we **did not create new database tables** for Receivables or Payables.
Creating a `customer_balances` table would duplicate data and cause synchronization bugs. 

Instead, the APIs calculate balances dynamically in real-time from the exact source of truth:
1. **Receivables Source:** `sales` table joined with `customers`. We filter for `payment_status` IN (`'UNPAID'`, `'PARTIAL'`) and calculate the balance as `SUM(total_amount - amount_paid)`.
2. **Payables Source:** `purchases` table joined with `suppliers`. We filter for `payment_status` IN (`'UNPAID'`, `'PARTIAL'`) and calculate the balance as `SUM(total_amount - amount_paid)`.

## Implemented Endpoints

All endpoints require the `finance_manager` or `admin` role.

### Receivables (Customers owing money)
* **`GET /api/v1/finance/receivables/customers`**
  Returns a paginated summary of all customers who currently owe the farm money.
  *Includes:* `customer_id`, `name`, `outstanding_balance`.
* **`GET /api/v1/finance/receivables/customers/{customer_id}`**
  Returns the specific, itemized unpaid/partial invoices for a single customer.

### Payables (Oweing money to Suppliers)
* **`GET /api/v1/finance/payables/suppliers`**
  Returns a paginated summary of all suppliers the farm currently owes money to.
  *Includes:* `supplier_id`, `name`, `outstanding_balance`.
* **`GET /api/v1/finance/payables/suppliers/{supplier_id}`**
  Returns the specific, itemized unpaid/partial purchase orders for a single supplier.

## How to Test the Flow

A comprehensive automated test is located at `backend/test_finance_receivables_payables.py`.

### Manual Testing Walkthrough:
1. **Create an Unpaid Sale:**
   Create a Sale for a customer where `amount_paid = 0` (Ensure the customer has a sufficient `credit_limit` to allow the sale).
2. **Check Receivables:**
   Call `GET /api/v1/finance/receivables/customers`. You will see the customer in the list with the full `outstanding_balance` equal to the sale amount.
3. **Make a Payment:**
   Call the POS payment endpoint: `POST /api/v1/pos/sales/{sale_id}/payments` and pay the full balance.
4. **Verify Clearance:**
   Call `GET /api/v1/finance/receivables/customers/{customer_id}`. The outstanding balance will be exactly `0`, and the `sales` array will be empty, proving the debt was successfully cleared and the system is perfectly synchronized with the POS.
