import requests
import uuid
from datetime import datetime

BASE_URL = "http://localhost:8000"
RUN_ID = uuid.uuid4().hex[:6]
ADMIN_EMAIL = f"admin_tb_{RUN_ID}@amas.com"

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

print("--- FINANCE TRIAL BALANCE (PHASE 7) TESTS ---")

# 1. Setup Auth
req("POST", "/api/v1/user/", {
    "first_name": "Admin", "last_name": "TB", "email": ADMIN_EMAIL,
    "phone": "0700111222", "password_hash": "Admin@1234", "role": "admin"
})
s, b = form_req("/login", f"username={ADMIN_EMAIL}&password=Admin@1234")
token = b.get("access_token")

# 2. Setup Prerequisites (Account, Product, Customer, Supplier)
s, b = req("POST", "/api/v1/finance/accounts/", {
    "name": f"Cash_{RUN_ID}", "account_type": "CASH", "opening_balance": 1000
}, token=token)
acc_id = b.get("id")

s, b = req("POST", "/api/v1/pos/customers/", {
    "name": f"Cust_{RUN_ID}", "customer_code": f"C_{RUN_ID}", "credit_limit": 100000
}, token=token)
cust_id = b.get("id")

s, b = req("POST", "/api/v1/pos/suppliers/", {
    "name": f"Supp_{RUN_ID}", "supplier_code": f"S_{RUN_ID}"
}, token=token)
supp_id = b.get("id")

s, b = req("GET", "/api/v1/inventory/products/?limit=1", token=token)
if s == 200 and len(b.get("items", [])) > 0:
    prod_id = b["items"][0]["id"]
else:
    prod_id = 1

# 3. Operations to seed the Trial Balance
# a) Owner Investment (Cash IN 500)
req("POST", "/api/v1/finance/transactions/", {
    "account_id": acc_id, "transaction_type": "OWNER_INVESTMENT", "direction": "IN", "amount": 500, "description": "Investment"
}, token=token)

# b) Purchase on Credit (Buy 300 of goods, pay 100) -> Accounts Payable = 200
req("POST", "/api/v1/pos/purchases/", {
    "supplier_id": supp_id, "amount_paid": 100, "account_id": acc_id,
    "payment_method": "CASH",
    "items": [{"product_id": prod_id, "quantity": 10, "unit_cost": 30}]
}, token=token)

# c) Sale for Cash (Sell 800 worth) -> Accounts Receivable = 0
req("POST", "/api/v1/pos/sales/", {
    "customer_id": cust_id, "amount_paid": 800, "account_id": acc_id,
    "payment_method": "CASH",
    "items": [{"product_id": prod_id, "quantity": 8, "unit_price": 100}]
}, token=token)

# Expected Balances Analysis (ignoring historical data from other tests since the DB is shared, 
# BUT Trial Balance is holistic! It covers EVERYTHING in the DB. We just need to check if it's perfectly balanced!)

# 4. Fetch Trial Balance
s, b = req("GET", "/api/v1/finance/trial-balance", token=token)
def check_trial_balance(body):
    # The most critical check is that total_debits == total_credits
    is_balanced = body.get("is_balanced", False)
    total_debits = float(body.get("total_debits", 0))
    total_credits = float(body.get("total_credits", 0))
    
    if not is_balanced:
        print(f"\n   NOT BALANCED! Debits: {total_debits}, Credits: {total_credits}")
        print("   Entries:", body.get("entries"))
        return False
    else:
        print(f"\n   BALANCED! Debits: {total_debits}, Credits: {total_credits}")
        print("   Entries:")
        for e in body.get("entries", []):
            print(f"      {e['account_name']:<35} DR: {e['debit']:>15} CR: {e['credit']:>15}")
        return True

check("Trial Balance - Mathematical Equilibrium", s, b, 200, check_trial_balance)

print(f"--- TESTS COMPLETED: {PASS_COUNT} PASSED, {FAIL_COUNT} FAILED ---")
