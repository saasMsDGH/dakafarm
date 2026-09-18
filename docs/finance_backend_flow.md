# Finance Subsystem - Backend Implementation & Flow Guide

## 1. What We Accomplished
We have successfully implemented **Phase 2 (The Unified Ledger)** and **Phase 3 (Backend Payments Integration)** of the AMAS Farm Finance Subsystem.

- **Phase 2:** Created the foundational ledger tables (`FinancialAccount` and `FinancialTransaction`). This serves as the single source of truth for all cash flows (Cash, Bank, Mobile Money).
- **Phase 3:** Connected the **Expenses**, **Payroll**, and **Assets** modules directly to the ledger. Instead of floating payments, every payment now automatically updates the domain entity's payment status (`UNPAID`, `PARTIAL`, `PAID`), records a specific payment entry, and logs a strict financial transaction against a selected financial account.

## 2. How the Finance Flow Works

The architecture guarantees that data is never corrupted, even if a server crash occurs mid-payment.

### The Atomic Flow
When a user makes a payment (e.g., paying an Employee their Payroll), the backend `Service` layer orchestrates the following flow within a single **atomic database transaction**:

1. **Validation:** Ensure the payment amount does not exceed the remaining balance and that the selected `account_id` (the financial account) exists and has enough funds (for outward flows).
2. **Domain Payment Insertion:** Create a specific record (e.g., `PayrollPayment`, `ExpensePayment`, `AssetPayment`) with a generated reference number. (Passed to the database via `commit=False`).
3. **Status Update:** Update the parent record's `amount_paid` and re-calculate the `payment_status` (`PARTIAL` or `PAID`).
4. **Ledger Transaction Insertion:** Automatically generate a `FinancialTransaction` linked to the same `account_id`. For Expenses, Payroll, and Asset purchases, this is an `OUT` direction cash flow.
5. **Commit or Rollback:** The `Service` layer runs `await db.commit()`. 
   - If everything succeeds, the transaction is finalized.
   - If *any* constraint fails (e.g., the employee ID is missing), it triggers `await db.rollback()`, discarding all changes and leaving the ledger perfectly intact.

### Diagram
```text
[User Triggers Payment]
       │
       ▼
   Service Layer (Transaction Start)
       │
       ├─► 1. Validate Balance & Account
       ├─► 2. Insert Domain Payment (e.g. AssetPayment)
       ├─► 3. Update Parent Entity (e.g. Asset status -> PAID)
       ├─► 4. Insert FinancialTransaction (Ledger IN/OUT)
       │
       ▼
[db.commit() -> Success or Failure]
```

## 3. How to Test the New Flow

We have built custom standalone Python test scripts that interact directly with the database via SQLAlchemy, simulating the frontend flow. These scripts ensure all foreign keys, unique constraints, and atomic rollbacks function perfectly.

### Prerequisites
Make sure the backend container (`ms_farms`) and the database container (`ams_farm_db`) are running. The test scripts execute directly from within the backend Docker container.

### Running the Tests

To test each flow, run the following commands from your terminal (host machine):

**1. Test Expenses Flow**
```bash
docker exec ms_farms python test_expense_payments.py
```
*Expected Result:* It will ensure a dummy account exists, create an expense, add a payment against it, and verify the expense status transitions to `PARTIAL` or `PAID`.

**2. Test Payroll Flow**
```bash
docker exec ms_farms python test_payroll_payments.py
```
*Expected Result:* It will insert a dummy employee if missing, generate a payroll record, pay it via a `PayrollPayment`, and confirm the backend logged it correctly.

**3. Test Assets Flow**
```bash
docker exec ms_farms python test_asset_payments.py
```
*Expected Result:* It will log a new asset purchase, register an `AssetPayment`, transition the asset status, and output the generated reference numbers.

### Troubleshooting Tests
- If you see `ForeignKeyViolationError`, it means the test script tried to use a missing relationship (e.g., a missing user ID or account ID). The scripts are designed to auto-seed this dummy data (`ON CONFLICT DO NOTHING`).
- If you see `409: An asset with this code might already exist`, the test successfully generated an asset on a previous run but didn't finish properly. You can clear the database tables manually to run clean tests:
```bash
docker exec ams_farm_db psql -U postgres -d msa_db -c "DELETE FROM assets; DELETE FROM payrolls; DELETE FROM expenses;"
```
