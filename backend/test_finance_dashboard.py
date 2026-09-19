import requests
import uuid
from decimal import Decimal

BASE_URL = "http://localhost:8000"
RUN_ID = uuid.uuid4().hex[:6]
ADMIN_EMAIL = f"admin_dash_{RUN_ID}@amas.com"

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

print("--- FINANCE DASHBOARD (PHASE 11) TESTS ---")

# 1. Setup Auth
req("POST", "/api/v1/user/", {
    "first_name": "Admin", "last_name": "Dash", "email": ADMIN_EMAIL,
    "phone": "0700999555", "password_hash": "Admin@1234", "role": "admin"
})
s, b = form_req("/login", f"username={ADMIN_EMAIL}&password=Admin@1234")
token = b.get("access_token")

# 2. Call Dashboard API
s, dash = req("GET", "/api/v1/finance/dashboard", token=token)

def check_structure(b):
    required = ["cash_on_hand", "accounts_receivable", "accounts_payable", 
                "monthly_revenue", "monthly_expenses", "monthly_net_profit"]
    for r in required:
        if r not in b:
            return False
    return True

check("Dashboard - Returns correct KPI structure", s, dash, 200, check_structure)

def dec(v): return Decimal(str(v))

# 3. Setup Prerequisites for Injection
s, b = req("POST", "/api/v1/finance/accounts/", {
    "name": f"DashBank_{RUN_ID}", "account_type": "BANK", "opening_balance": 10000
}, token=token)
acc_id = b.get("id")

s, b = req("POST", "/api/v1/pos/customers/", {
    "name": f"Cust_{RUN_ID}", "customer_code": f"C_{RUN_ID}", "credit_limit": 100000
}, token=token)
cust_id = b.get("id")

s, b = req("GET", "/api/v1/inventory/products/?limit=1", token=token)
prod_id = b["items"][0]["id"] if s == 200 and len(b.get("items", [])) > 0 else 1

# 4. Inject Transactions to test deltas
# a) Sale (Revenue +3000, AR increases by 3000, Cash increases by 0 because it's on credit)
req("POST", "/api/v1/pos/sales/", {
    "customer_id": cust_id, "amount_paid": 0, "account_id": acc_id,
    "payment_method": "CASH",
    "items": [{"product_id": prod_id, "quantity": 10, "unit_price": 300}]
}, token=token)

# b) Direct Expense (Expense +500, Cash decreases by 500)
req("POST", "/api/v1/finance/transactions/", {
    "account_id": acc_id, "transaction_type": "EXPENSE", "direction": "OUT", "amount": 500, "description": "Utilities"
}, token=token)

# 5. Get New Dashboard
s, dash_new = req("GET", "/api/v1/finance/dashboard", token=token)

def check_deltas(b):
    diff_cash = dec(b["cash_on_hand"]) - dec(dash["cash_on_hand"])
    diff_rev = dec(b["monthly_revenue"]) - dec(dash["monthly_revenue"])
    diff_exp = dec(b["monthly_expenses"]) - dec(dash["monthly_expenses"])
    diff_profit = dec(b["monthly_net_profit"]) - dec(dash["monthly_net_profit"])
    
    # Assertions
    # Opening balance of 10000 increases cash by 10000. Expense decreases by 500. Net Cash Delta = 9500.
    # Revenue increases by 3000.
    # Expenses increases by 500.
    # Profit increases by (3000 - 500) = 2500.
    
    res = True
    if diff_cash != 9500: print(f"Cash diff should be 9500, got {diff_cash}"); res = False
    if diff_rev != 3000: print(f"Monthly Revenue diff should be 3000, got {diff_rev}"); res = False
    if diff_exp != 500: print(f"Monthly Expenses diff should be 500, got {diff_exp}"); res = False
    if diff_profit != 2500: print(f"Monthly Profit diff should be 2500, got {diff_profit}"); res = False
    
    # Internal Math Validation
    if dec(b["monthly_net_profit"]) != dec(b["monthly_revenue"]) - dec(b["monthly_expenses"]):
        print("Internal profit math failed!")
        res = False
        
    return res

check("Dashboard - Accurately updates KPIs", s, dash_new, 200, check_deltas)

print(f"--- TESTS COMPLETED: {PASS_COUNT} PASSED, {FAIL_COUNT} FAILED ---")
