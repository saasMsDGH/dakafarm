import requests
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal

BASE_URL = "http://localhost:8000"
RUN_ID = uuid.uuid4().hex[:6]
ADMIN_EMAIL = f"admin_cf_{RUN_ID}@amas.com"

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

print("--- FINANCE CASH FLOW (PHASE 9) TESTS ---")

# 1. Setup Auth
req("POST", "/api/v1/user/", {
    "first_name": "Admin", "last_name": "CF", "email": ADMIN_EMAIL,
    "phone": "0700999777", "password_hash": "Admin@1234", "role": "admin"
})
s, b = form_req("/login", f"username={ADMIN_EMAIL}&password=Admin@1234")
token = b.get("access_token")

# 2. Get baseline Cash Flow
s, cf_baseline = req("GET", "/api/v1/finance/cash-flow", token=token)

def dec(v): return Decimal(str(v))

# 3. Setup Prerequisites (Account)
# Creating a new account should NOT affect the net flow for this period unless money moves.
# Wait, if we create an account with an opening_balance, it INCREASES the opening_balance total, 
# AND increases the ending_balance total, but the net_change_in_cash is zero because opening balances aren't transactions!
# Let's test that!
s, b = req("POST", "/api/v1/finance/accounts/", {
    "name": f"Cash_{RUN_ID}", "account_type": "CASH", "opening_balance": 1000
}, token=token)
acc_id = b.get("id")

s, cf_after_acct = req("GET", "/api/v1/finance/cash-flow", token=token)

# The ending balance should go up by 1000 compared to baseline, but net_change_in_cash should be the same.
def check_opening_balance_math(b):
    diff_open = dec(b["opening_balance"]) - dec(cf_baseline["opening_balance"])
    diff_net = dec(b["net_change_in_cash"]) - dec(cf_baseline["net_change_in_cash"])
    
    return diff_open == 1000 and diff_net == 0 and dec(b["ending_balance"]) == dec(b["opening_balance"]) + dec(b["net_change_in_cash"])

check("Cash Flow - Opening Balance Injection", s, cf_after_acct, 200, check_opening_balance_math)

# 4. Inject some new cash movements
# a) Owner Investment (Financing IN = +10000)
req("POST", "/api/v1/finance/transactions/", {
    "account_id": acc_id, "transaction_type": "OWNER_INVESTMENT", "direction": "IN", "amount": 10000, "description": "Capital"
}, token=token)

# b) Direct Expense (Operating OUT = -500)
req("POST", "/api/v1/finance/transactions/", {
    "account_id": acc_id, "transaction_type": "EXPENSE", "direction": "OUT", "amount": 500, "description": "Rent"
}, token=token)

# c) Asset Purchase (Investing OUT = -2000)
req("POST", "/api/v1/finance/transactions/", {
    "account_id": acc_id, "transaction_type": "ASSET_PURCHASE", "direction": "OUT", "amount": 2000, "description": "Tractor"
}, token=token)

# d) Sale Cash (Operating IN = +800)
req("POST", "/api/v1/finance/transactions/", {
    "account_id": acc_id, "transaction_type": "SALE", "direction": "IN", "amount": 800, "description": "Sale Payment"
}, token=token)

# 5. Fetch New Cash Flow
s, cf_new = req("GET", "/api/v1/finance/cash-flow", token=token)

def check_deltas(b):
    diff_ops = dec(b["operating"]["net_operating_cash_flow"]) - dec(cf_after_acct["operating"]["net_operating_cash_flow"])
    diff_inv = dec(b["investing"]["net_investing_cash_flow"]) - dec(cf_after_acct["investing"]["net_investing_cash_flow"])
    diff_fin = dec(b["financing"]["net_financing_cash_flow"]) - dec(cf_after_acct["financing"]["net_financing_cash_flow"])
    
    # Expected:
    # Ops: +800 (Sale) - 500 (Expense) = +300
    # Inv: -2000 (Asset) = -2000
    # Fin: +10000 (Owner) = +10000
    # Total Change = +8300
    
    res = True
    if diff_ops != 300: print(f"Ops diff should be 300, got {diff_ops}"); res = False
    if diff_inv != -2000: print(f"Inv diff should be -2000, got {diff_inv}"); res = False
    if diff_fin != 10000: print(f"Fin diff should be 10000, got {diff_fin}"); res = False
        
    diff_net = dec(b["net_change_in_cash"]) - dec(cf_after_acct["net_change_in_cash"])
    if diff_net != 8300: print(f"Net diff should be 8300, got {diff_net}"); res = False
    
    # Mathematical Integrity
    if dec(b["ending_balance"]) != dec(b["opening_balance"]) + dec(b["net_change_in_cash"]):
        print("Ending balance math is wrong")
        res = False
        
    return res

check("Cash Flow - Category Deltas & Math", s, cf_new, 200, check_deltas)

# 6. Test Date Filtering
now = datetime.now(timezone.utc)
tomorrow = now + timedelta(days=1)
future_date_str = tomorrow.isoformat().replace("+", "%2B")

s, cf_future = req("GET", f"/api/v1/finance/cash-flow?start_date={future_date_str}", token=token)

def check_empty_future(b):
    # In the future, the opening balance should carry forward exactly the current ending balance.
    # The net change should be zero because no transactions occurred in the future.
    # Therefore opening == ending == current ending.
    curr_ending = dec(cf_new["ending_balance"])
    fut_opening = dec(b["opening_balance"])
    fut_ending = dec(b["ending_balance"])
    fut_change = dec(b["net_change_in_cash"])
    
    return fut_opening == curr_ending and fut_ending == curr_ending and fut_change == 0

check("Cash Flow - Date Filtering (Future carries balances)", s, cf_future, 200, check_empty_future)

print(f"--- TESTS COMPLETED: {PASS_COUNT} PASSED, {FAIL_COUNT} FAILED ---")
