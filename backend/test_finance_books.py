import requests
import uuid
import time
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000"
RUN_ID = uuid.uuid4().hex[:6]
ADMIN_EMAIL = f"admin_books_{RUN_ID}@amas.com"

PASS_COUNT = 0
FAIL_COUNT = 0

def req(method, path, json=None, token=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    r = requests.request(method, BASE_URL + path, json=json, headers=headers)
    try:
        return r.status_code, r.json()
    except:
        return r.status_code, r.text

def form_req(path, data):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(BASE_URL + path, data=data, headers=headers)
    return r.status_code, r.json()

def check(name, status, body, expected_status, additional_check=None):
    global PASS_COUNT, FAIL_COUNT
    if status == expected_status and (additional_check is None or additional_check(body)):
        print("PASS: " + name)
        PASS_COUNT += 1
    else:
        print("FAIL: " + name)
        print("   Status:", status, "Expected:", expected_status)
        if status == expected_status:
            print("   Additional check failed. Body:", body)
        else:
            print("   Body:", body)
        FAIL_COUNT += 1

print("--- FINANCE BOOKS (PHASE 5) TESTS ---")

# 1. Setup Auth
req("POST", "/api/v1/user/", {
    "first_name": "Admin", "last_name": "Books", "email": ADMIN_EMAIL,
    "phone": "0700111222", "password_hash": "Admin@1234", "role": "admin"
})
s, b = form_req("/login", f"username={ADMIN_EMAIL}&password=Admin@1234")
token = b.get("access_token")

# 2. Setup Accounts
s, b = req("POST", "/api/v1/finance/accounts/", {
    "name": f"Cash_{RUN_ID}", "account_type": "CASH", "opening_balance": 500000.00
}, token=token)
cash_id = b.get("id")

s, b = req("POST", "/api/v1/finance/accounts/", {
    "name": f"Bank_{RUN_ID}", "account_type": "BANK", "opening_balance": 100000.00
}, token=token)
bank_id = b.get("id")

s, b = req("POST", "/api/v1/finance/accounts/", {
    "name": f"Mobile_{RUN_ID}", "account_type": "MOBILE_MONEY", "opening_balance": 0.00
}, token=token)
mobile_id = b.get("id")

# 3. Create Transactions for Cash Account (Controlled Scenario)
# Opening = 500,000
# IN 100,000 -> 600,000
# OUT 50,000 -> 550,000
# IN 200,000 -> 750,000
# OUT 25,000 -> 725,000
req("POST", "/api/v1/finance/transactions/", {
    "account_id": cash_id, "transaction_type": "SALE", "direction": "IN", "amount": 100000, "description": "T1"
}, token=token)
time.sleep(0.1) # Ensure chronological order in DB

req("POST", "/api/v1/finance/transactions/", {
    "account_id": cash_id, "transaction_type": "EXPENSE", "direction": "OUT", "amount": 50000, "description": "T2"
}, token=token)
time.sleep(0.1)

req("POST", "/api/v1/finance/transactions/", {
    "account_id": cash_id, "transaction_type": "SALE", "direction": "IN", "amount": 200000, "description": "T3"
}, token=token)
time.sleep(0.1)

req("POST", "/api/v1/finance/transactions/", {
    "account_id": cash_id, "transaction_type": "EXPENSE", "direction": "OUT", "amount": 25000, "description": "T4"
}, token=token)
time.sleep(0.1)

# Add a Bank transaction to test isolation
req("POST", "/api/v1/finance/transactions/", {
    "account_id": bank_id, "transaction_type": "OWNER_INVESTMENT", "direction": "IN", "amount": 999999, "description": "B1"
}, token=token)

# 4. Test Cash Book
s, b = req("GET", f"/api/v1/finance/books/cash?account_id={cash_id}", token=token)
def check_cash_book(body):
    if body["opening_balance"] != "500000.00": return False
    if body["closing_balance"] != "725000.00": return False
    if body["total_money_in"] != "300000.00": return False
    if body["total_money_out"] != "75000.00": return False
    if len(body["items"]) != 4: return False
    
    # Check running balances
    if body["items"][0]["balance"] != "600000.00": return False
    if body["items"][1]["balance"] != "550000.00": return False
    if body["items"][2]["balance"] != "750000.00": return False
    if body["items"][3]["balance"] != "725000.00": return False
    return True

check("Cash Book - Correct Running Balance & Isolation", s, b, 200, check_cash_book)

# 5. Type Enforcement Test
s, b = req("GET", f"/api/v1/finance/books/bank?account_id={cash_id}", token=token)
check("Cash account on Bank Book endpoint -> 400", s, b, 400)

s, b = req("GET", f"/api/v1/finance/books/cash", token=token)
check("Missing account_id -> 422", s, b, 422)

# 6. Pagination & Gap Sum Test (Page 2)
s, b = req("GET", f"/api/v1/finance/books/cash?account_id={cash_id}&page=2&limit=2", token=token)
def check_pagination(body):
    # Page 2 skips T1 and T2, meaning opening balance for this page includes them.
    # T1 (+100k), T2 (-50k). So page opening balance = 500k + 100k - 50k = 550k.
    # Then it returns T3 and T4.
    if body["opening_balance"] != "550000.00": return False
    if body["closing_balance"] != "725000.00": return False
    if body["items"][0]["description"] != "T3": return False
    if body["items"][0]["balance"] != "750000.00": return False
    return True

check("Cash Book - Pagination / Gap Sum Running Balance", s, b, 200, check_pagination)

print(f"--- TESTS COMPLETED: {PASS_COUNT} PASSED, {FAIL_COUNT} FAILED ---")
