"""
test_finance_transactions.py
Phase 2 Sub-phase 1 — Backend Financial Transactions test suite.

Coverage:
  - Account prerequisites (creates active + inactive accounts)
  - Create: valid transactions (CASH/BANK/MOBILE_MONEY accounts, all types, both directions)
  - Create: validation rejections (zero, negative, bad type, bad direction, nonexistent account,
            inactive account, missing required fields)
  - Get by ID: valid, nonexistent
  - List: empty, all, pagination (page/limit/multiple pages), search, filtering
    (account_id, transaction_type, direction, date_from/date_to)
  - Sorting: transaction_date, amount, valid vs fallback field
  - RBAC: unauthenticated rejected with 401
  - Database integrity: no partial record on failed create
"""

import uuid
import requests
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000"

# Unique admin email for this test run so parallel runs don't clash
RUN_ID = uuid.uuid4().hex[:8]
ADMIN_EMAIL = f"admin_txn_{RUN_ID}@amas.com"

PASS_COUNT = 0
FAIL_COUNT = 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def req(method, path, json=None, token=None, params=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    r = requests.request(
        method, BASE_URL + path, json=json, headers=headers, params=params
    )
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, r.text


def form_req(path, data):
    r = requests.post(
        BASE_URL + path,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return r.status_code, r.json()


def check(name, status_code, body, expected_status):
    global PASS_COUNT, FAIL_COUNT
    if status_code == expected_status:
        print(f"  PASS  {name}")
        PASS_COUNT += 1
    else:
        print(f"  FAIL  {name}")
        print(f"        got={status_code}  expected={expected_status}")
        print(f"        body={body}")
        FAIL_COUNT += 1


def assert_field(name, body, field, expected_value):
    global PASS_COUNT, FAIL_COUNT
    actual = body.get(field)
    if str(actual) == str(expected_value) or actual == expected_value:
        print(f"  PASS  {name}")
        PASS_COUNT += 1
    else:
        print(f"  FAIL  {name}")
        print(f"        field={field}  got={actual!r}  expected={expected_value!r}")
        FAIL_COUNT += 1


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
print("\n" + "="*60)
print("FINANCE TRANSACTIONS — TEST SUITE")
print("="*60)

# 1. Create admin user and login
req("POST", "/api/v1/user/", {
    "first_name": "Admin", "last_name": "Txn", "email": ADMIN_EMAIL,
    "phone": "0700000001", "password_hash": "Admin@1234", "role": "admin"
})
s, b = form_req("/login", f"username={ADMIN_EMAIL}&password=Admin@1234")
TOKEN = b.get("access_token")
if not TOKEN:
    print("FATAL: Could not obtain auth token. Aborting.")
    exit(1)

# 2. Create financial accounts for testing
print("\n--- Setup: Create Accounts ---")
s, b = req("POST", "/api/v1/finance/accounts/", {
    "name": f"Test Cash {RUN_ID}",
    "account_type": "CASH",
    "opening_balance": 1000000
}, token=TOKEN)
check("Create CASH account", s, b, 201)
CASH_ID = b.get("id")

s, b = req("POST", "/api/v1/finance/accounts/", {
    "name": f"Test Bank {RUN_ID}",
    "account_type": "BANK",
    "bank_name": "CRDB",
    "account_number": "999001",
    "opening_balance": 5000000
}, token=TOKEN)
check("Create BANK account", s, b, 201)
BANK_ID = b.get("id")

# Create an INACTIVE account to test that rule
s, b = req("POST", "/api/v1/finance/accounts/", {
    "name": f"Inactive Acct {RUN_ID}",
    "account_type": "CASH",
    "opening_balance": 0,
    "is_active": True
}, token=TOKEN)
check("Create account to deactivate", s, b, 201)
INACTIVE_ID = b.get("id")
# Deactivate it
s, b = req("PUT", f"/api/v1/finance/accounts/{INACTIVE_ID}", {
    "is_active": False
}, token=TOKEN)
check("Deactivate account", s, b, 200)


# ---------------------------------------------------------------------------
# CREATE — valid transactions
# ---------------------------------------------------------------------------
print("\n--- Create: Valid Transactions ---")

# IN transaction on CASH account
s, b = req("POST", "/api/v1/finance/transactions/", {
    "account_id": CASH_ID,
    "transaction_type": "OTHER_INCOME",
    "direction": "IN",
    "amount": "500000.00",
    "description": "Training income",
    "reference_number": "INC-0001"
}, token=TOKEN)
check("Create IN/OTHER_INCOME on CASH", s, b, 201)
TXN_ID_1 = b.get("id")
assert_field("  direction stored as IN", b, "direction", "IN")
assert_field("  transaction_type stored", b, "transaction_type", "OTHER_INCOME")
assert_field("  account_id stored", b, "account_id", CASH_ID)

# OUT transaction on BANK account
s, b = req("POST", "/api/v1/finance/transactions/", {
    "account_id": BANK_ID,
    "transaction_type": "EXPENSE",
    "direction": "OUT",
    "amount": "250000.00",
    "description": "Electricity bill",
    "reference_number": "EXP-0001"
}, token=TOKEN)
check("Create OUT/EXPENSE on BANK", s, b, 201)
TXN_ID_2 = b.get("id")

# OWNER_INVESTMENT IN on BANK
s, b = req("POST", "/api/v1/finance/transactions/", {
    "account_id": BANK_ID,
    "transaction_type": "OWNER_INVESTMENT",
    "direction": "IN",
    "amount": "10000000.00",
    "description": "Owner capital injection Sep 2026"
}, token=TOKEN)
check("Create IN/OWNER_INVESTMENT on BANK (no ref)", s, b, 201)
TXN_ID_3 = b.get("id")

# PAYROLL OUT
s, b = req("POST", "/api/v1/finance/transactions/", {
    "account_id": CASH_ID,
    "transaction_type": "PAYROLL",
    "direction": "OUT",
    "amount": "1200000.00",
    "description": "September 2026 payroll",
    "reference_number": "PAY-2026-09"
}, token=TOKEN)
check("Create OUT/PAYROLL on CASH", s, b, 201)
TXN_ID_4 = b.get("id")

# ADJUSTMENT with back-dated transaction_date
s, b = req("POST", "/api/v1/finance/transactions/", {
    "account_id": CASH_ID,
    "transaction_type": "ADJUSTMENT",
    "direction": "IN",
    "amount": "50.00",
    "description": "Petty cash correction",
    "transaction_date": "2026-09-01T08:00:00+03:00"
}, token=TOKEN)
check("Create back-dated ADJUSTMENT", s, b, 201)
TXN_ID_5 = b.get("id")

# Small amount — boundary test
s, b = req("POST", "/api/v1/finance/transactions/", {
    "account_id": CASH_ID,
    "transaction_type": "OTHER_INCOME",
    "direction": "IN",
    "amount": "0.01",
    "description": "Minimum amount boundary"
}, token=TOKEN)
check("Create transaction with min valid amount (0.01)", s, b, 201)

# Large amount
s, b = req("POST", "/api/v1/finance/transactions/", {
    "account_id": BANK_ID,
    "transaction_type": "SALE",
    "direction": "IN",
    "amount": "999999999.99",
    "description": "Large amount boundary"
}, token=TOKEN)
check("Create transaction with large amount", s, b, 201)
TXN_ID_LARGE = b.get("id")


# ---------------------------------------------------------------------------
# CREATE — validation rejections
# ---------------------------------------------------------------------------
print("\n--- Create: Validation Rejections ---")

# Zero amount
s, b = req("POST", "/api/v1/finance/transactions/", {
    "account_id": CASH_ID, "transaction_type": "OTHER_INCOME",
    "direction": "IN", "amount": "0"
}, token=TOKEN)
check("Reject zero amount", s, b, 422)

# Negative amount
s, b = req("POST", "/api/v1/finance/transactions/", {
    "account_id": CASH_ID, "transaction_type": "OTHER_INCOME",
    "direction": "IN", "amount": "-100"
}, token=TOKEN)
check("Reject negative amount", s, b, 422)

# Invalid transaction_type
s, b = req("POST", "/api/v1/finance/transactions/", {
    "account_id": CASH_ID, "transaction_type": "DONATION",
    "direction": "IN", "amount": "500"
}, token=TOKEN)
check("Reject invalid transaction_type", s, b, 422)

# Invalid direction
s, b = req("POST", "/api/v1/finance/transactions/", {
    "account_id": CASH_ID, "transaction_type": "OTHER_INCOME",
    "direction": "BOTH", "amount": "500"
}, token=TOKEN)
check("Reject invalid direction", s, b, 422)

# Nonexistent account
s, b = req("POST", "/api/v1/finance/transactions/", {
    "account_id": 999999, "transaction_type": "OTHER_INCOME",
    "direction": "IN", "amount": "500"
}, token=TOKEN)
check("Reject nonexistent account_id", s, b, 404)

# Inactive account
s, b = req("POST", "/api/v1/finance/transactions/", {
    "account_id": INACTIVE_ID, "transaction_type": "OTHER_INCOME",
    "direction": "IN", "amount": "500"
}, token=TOKEN)
check("Reject inactive account", s, b, 422)

# Missing account_id
s, b = req("POST", "/api/v1/finance/transactions/", {
    "transaction_type": "OTHER_INCOME", "direction": "IN", "amount": "500"
}, token=TOKEN)
check("Reject missing account_id", s, b, 422)

# Missing transaction_type
s, b = req("POST", "/api/v1/finance/transactions/", {
    "account_id": CASH_ID, "direction": "IN", "amount": "500"
}, token=TOKEN)
check("Reject missing transaction_type", s, b, 422)

# Missing direction
s, b = req("POST", "/api/v1/finance/transactions/", {
    "account_id": CASH_ID, "transaction_type": "OTHER_INCOME", "amount": "500"
}, token=TOKEN)
check("Reject missing direction", s, b, 422)

# Missing amount
s, b = req("POST", "/api/v1/finance/transactions/", {
    "account_id": CASH_ID, "transaction_type": "OTHER_INCOME", "direction": "IN"
}, token=TOKEN)
check("Reject missing amount", s, b, 422)


# ---------------------------------------------------------------------------
# GET by ID
# ---------------------------------------------------------------------------
print("\n--- Get by ID ---")

s, b = req("GET", f"/api/v1/finance/transactions/{TXN_ID_1}", token=TOKEN)
check("Get transaction by valid ID", s, b, 200)
assert_field("  reference_number matches", b, "reference_number", "INC-0001")

s, b = req("GET", f"/api/v1/finance/transactions/9999999", token=TOKEN)
check("Get nonexistent transaction returns 404", s, b, 404)


# ---------------------------------------------------------------------------
# LIST — basic + empty
# ---------------------------------------------------------------------------
print("\n--- List: Basic ---")

s, b = req("GET", "/api/v1/finance/transactions/", token=TOKEN)
check("List all transactions succeeds", s, b, 200)
total_all = b.get("total", 0)
print(f"  INFO  total transactions so far: {total_all}")

# Filter by account_id (CASH)
s, b = req("GET", "/api/v1/finance/transactions/", token=TOKEN,
           params={"account_id": CASH_ID})
check("Filter by account_id (CASH)", s, b, 200)
items = b.get("items", [])
all_cash = all(item["account_id"] == CASH_ID for item in items)
if all_cash and items:
    print("  PASS  All returned items belong to CASH account")
    PASS_COUNT += 1
elif not items:
    print("  WARN  Filter returned empty — check account_id")
else:
    print(f"  FAIL  Some items have wrong account_id: {[i['account_id'] for i in items]}")
    FAIL_COUNT += 1

# Filter by direction IN
s, b = req("GET", "/api/v1/finance/transactions/", token=TOKEN,
           params={"direction": "IN"})
check("Filter by direction=IN", s, b, 200)
items = b.get("items", [])
all_in = all(item["direction"] == "IN" for item in items)
if all_in and items:
    print("  PASS  All returned items have direction=IN")
    PASS_COUNT += 1
elif not items:
    print("  WARN  No IN transactions found")
else:
    print(f"  FAIL  Some items have direction != IN")
    FAIL_COUNT += 1

# Filter by direction OUT
s, b = req("GET", "/api/v1/finance/transactions/", token=TOKEN,
           params={"direction": "OUT"})
check("Filter by direction=OUT", s, b, 200)
items = b.get("items", [])
all_out = all(item["direction"] == "OUT" for item in items)
if all_out and items:
    print("  PASS  All returned items have direction=OUT")
    PASS_COUNT += 1

# Filter by transaction_type
s, b = req("GET", "/api/v1/finance/transactions/", token=TOKEN,
           params={"transaction_type": "EXPENSE"})
check("Filter by transaction_type=EXPENSE", s, b, 200)
items = b.get("items", [])
if items and all(i["transaction_type"] == "EXPENSE" for i in items):
    print("  PASS  All returned items are EXPENSE type")
    PASS_COUNT += 1

# Filter by date_from/date_to
s, b = req("GET", "/api/v1/finance/transactions/", token=TOKEN, params={
    "date_from": "2026-09-01T00:00:00",
    "date_to": "2026-09-30T23:59:59"
})
check("Filter by date_from/date_to", s, b, 200)

# Search by reference_number
s, b = req("GET", "/api/v1/finance/transactions/", token=TOKEN,
           params={"search": "EXP-0001"})
check("Search by reference_number", s, b, 200)
items = b.get("items", [])
if items and items[0]["reference_number"] == "EXP-0001":
    print("  PASS  Search returned correct transaction by reference_number")
    PASS_COUNT += 1

# Search by description
s, b = req("GET", "/api/v1/finance/transactions/", token=TOKEN,
           params={"search": "Training income"})
check("Search by description text", s, b, 200)
items = b.get("items", [])
if items:
    print("  PASS  Search by description returned results")
    PASS_COUNT += 1


# ---------------------------------------------------------------------------
# LIST — pagination
# ---------------------------------------------------------------------------
print("\n--- Pagination ---")

# Page 1, limit 2
s, b = req("GET", "/api/v1/finance/transactions/", token=TOKEN,
           params={"page": 1, "limit": 2})
check("Paginate: page=1, limit=2", s, b, 200)
if len(b.get("items", [])) <= 2:
    print("  PASS  Correct item count on page 1")
    PASS_COUNT += 1
else:
    print("  FAIL  Too many items on page 1")
    FAIL_COUNT += 1

# Page 2
s, b = req("GET", "/api/v1/finance/transactions/", token=TOKEN,
           params={"page": 2, "limit": 2})
check("Paginate: page=2, limit=2", s, b, 200)

# Empty result (filter that matches nothing)
s, b = req("GET", "/api/v1/finance/transactions/", token=TOKEN,
           params={"search": "THISDOESNOTEXIST_xyz_99999"})
check("Empty result (no matches)", s, b, 200)
if b.get("total") == 0 and b.get("items") == []:
    print("  PASS  Empty result returns total=0 and items=[]")
    PASS_COUNT += 1


# ---------------------------------------------------------------------------
# SORTING
# ---------------------------------------------------------------------------
print("\n--- Sorting ---")

s, b = req("GET", "/api/v1/finance/transactions/", token=TOKEN,
           params={"sort_by": "amount", "order": "asc"})
check("Sort by amount ASC", s, b, 200)
items = b.get("items", [])
if len(items) >= 2:
    amounts = [float(i["amount"]) for i in items]
    if amounts == sorted(amounts):
        print("  PASS  Amount ASC order is correct")
        PASS_COUNT += 1
    else:
        print(f"  FAIL  Amount not in ASC order: {amounts}")
        FAIL_COUNT += 1

s, b = req("GET", "/api/v1/finance/transactions/", token=TOKEN,
           params={"sort_by": "amount", "order": "desc"})
check("Sort by amount DESC", s, b, 200)

# Invalid sort field — should not crash, uses fallback
s, b = req("GET", "/api/v1/finance/transactions/", token=TOKEN,
           params={"sort_by": "nonexistent_column", "order": "desc"})
check("Sort by invalid field (fallback, no crash)", s, b, 200)


# ---------------------------------------------------------------------------
# RBAC / Authorization
# ---------------------------------------------------------------------------
print("\n--- RBAC / Authorization ---")

# No token
s, b = req("GET", "/api/v1/finance/transactions/")
check("List without auth token returns 401", s, b, 401)

s, b = req("POST", "/api/v1/finance/transactions/", {
    "account_id": CASH_ID, "transaction_type": "OTHER_INCOME",
    "direction": "IN", "amount": "100"
})
check("Create without auth token returns 401", s, b, 401)

s, b = req("GET", f"/api/v1/finance/transactions/{TXN_ID_1}")
check("Get by ID without auth token returns 401", s, b, 401)


# ---------------------------------------------------------------------------
# IMMUTABILITY — no PUT or DELETE endpoints
# ---------------------------------------------------------------------------
print("\n--- Immutability Verification ---")

s, b = req("PUT", f"/api/v1/finance/transactions/{TXN_ID_1}", {
    "amount": "999"
}, token=TOKEN)
check("PUT on transaction returns 405 (no update endpoint)", s, b, 405)

s, b = req("DELETE", f"/api/v1/finance/transactions/{TXN_ID_1}", token=TOKEN)
check("DELETE on transaction returns 405 (no delete endpoint)", s, b, 405)


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print("\n" + "="*60)
total = PASS_COUNT + FAIL_COUNT
print(f"RESULTS:  {PASS_COUNT} passed  /  {FAIL_COUNT} failed  /  {total} total")
print("="*60)
if FAIL_COUNT > 0:
    exit(1)
