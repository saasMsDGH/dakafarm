import requests
import uuid
from decimal import Decimal

BASE_URL = "http://localhost:8000"
RUN_ID = uuid.uuid4().hex[:6]
ADMIN_EMAIL = f"admin_bs_{RUN_ID}@amas.com"

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

print("--- FINANCE BALANCE SHEET (PHASE 10) TESTS ---")

# 1. Setup Auth
req("POST", "/api/v1/user/", {
    "first_name": "Admin", "last_name": "BS", "email": ADMIN_EMAIL,
    "phone": "0700999666", "password_hash": "Admin@1234", "role": "admin"
})
s, b = form_req("/login", f"username={ADMIN_EMAIL}&password=Admin@1234")
token = b.get("access_token")

# 2. Get baseline Balance Sheet
s, bs_baseline = req("GET", "/api/v1/finance/balance-sheet", token=token)

def dec(v): return Decimal(str(v))

# Baseline must be balanced
def check_balanced(b):
    return b.get("is_balanced") is True

check("Balance Sheet - Baseline Mathematical Equilibrium", s, bs_baseline, 200, check_balanced)

# 3. Setup Prerequisites
s, b = req("POST", "/api/v1/finance/accounts/", {
    "name": f"Bank_{RUN_ID}", "account_type": "BANK", "opening_balance": 50000
}, token=token)
acc_id = b.get("id")

s, b = req("POST", "/api/v1/pos/customers/", {
    "name": f"Cust_{RUN_ID}", "customer_code": f"C_{RUN_ID}", "credit_limit": 100000
}, token=token)
cust_id = b.get("id")

s, b = req("GET", "/api/v1/inventory/products/?limit=1", token=token)
if s == 200 and len(b.get("items", [])) > 0:
    prod_id = b["items"][0]["id"]
else:
    prod_id = 1

# 4. Inject Transactions to test Asset/Liability/Equity shifts
# a) Sale on Credit (Assets (AR) +2000, Equity (Retained Earnings) +2000)
req("POST", "/api/v1/pos/sales/", {
    "customer_id": cust_id, "amount_paid": 0, "account_id": acc_id,
    "payment_method": "CASH",
    "items": [{"product_id": prod_id, "quantity": 10, "unit_price": 200}]
}, token=token)

# b) Asset Purchase (Cash -5000, Fixed Assets +5000 -> Total Assets unchanged)
req("POST", "/api/v1/finance/transactions/", {
    "account_id": acc_id, "transaction_type": "ASSET_PURCHASE", "direction": "OUT", "amount": 5000, "description": "Tractor"
}, token=token)

# c) Owner Draw (Cash -2000, Equity (Capital) -2000)
req("POST", "/api/v1/finance/transactions/", {
    "account_id": acc_id, "transaction_type": "OWNER_INVESTMENT", "direction": "OUT", "amount": 2000, "description": "Draw"
}, token=token)

# 5. Fetch New Balance Sheet
s, bs_new = req("GET", "/api/v1/finance/balance-sheet", token=token)

check("Balance Sheet - New Equilibrium After Injection", s, bs_new, 200, check_balanced)

def check_deltas(b):
    # Expected changes from Baseline:
    # 1. Opening Balance (+50000) => Cash +50000, Owner Capital +50000
    # 2. Sale Credit (+2000) => AR +2000, Retained Earnings +2000
    # 3. Asset Purchase => Cash -5000, Fixed Asset +5000 (Net 0)
    # 4. Owner Draw => Cash -2000, Owner Capital -2000
    
    # Net Deltas:
    # Cash: 50000 - 5000 - 2000 = +43000
    # AR: +2000
    # Fixed Assets: +5000
    # Total Assets: 43000 + 2000 + 5000 = +50000
    
    # Owner Capital: 50000 - 2000 = +48000
    # Retained Earnings: +2000
    # Total Equity: 48000 + 2000 = +50000
    
    diff_cash = dec(b["assets"]["cash_and_bank"]) - dec(bs_baseline["assets"]["cash_and_bank"])
    diff_fixed = dec(b["assets"]["fixed_assets"]) - dec(bs_baseline["assets"]["fixed_assets"])
    
    # Because AR might be deeply negative (Unearned Revenue), the +2000 sale might 
    # either increase AR (if net positive) or decrease Unearned Revenue (if net negative).
    # What truly matters is the NET change in Assets - Liabilities.
    diff_net_assets = (dec(b["assets"]["total_assets"]) - dec(b["liabilities"]["total_liabilities"])) - \
                      (dec(bs_baseline["assets"]["total_assets"]) - dec(bs_baseline["liabilities"]["total_liabilities"]))
    
    diff_cap = dec(b["equity"]["owner_capital"]) - dec(bs_baseline["equity"]["owner_capital"])
    diff_re = dec(b["equity"]["retained_earnings"]) - dec(bs_baseline["equity"]["retained_earnings"])
    diff_equity = dec(b["equity"]["total_equity"]) - dec(bs_baseline["equity"]["total_equity"])
    
    res = True
    if diff_cash != 43000: print(f"Cash diff should be 43000, got {diff_cash}"); res = False
    if diff_fixed != 5000: print(f"Fixed Assets diff should be 5000, got {diff_fixed}"); res = False
    if diff_net_assets != 50000: print(f"Net Assets diff should be 50000, got {diff_net_assets}"); res = False
        
    if diff_cap != 48000: print(f"Owner Capital diff should be 48000, got {diff_cap}"); res = False
    if diff_re != 2000: print(f"Retained Earnings diff should be 2000, got {diff_re}"); res = False
    if diff_equity != 50000: print(f"Total Equity diff should be 50000, got {diff_equity}"); res = False
        
    return res

check("Balance Sheet - Specific Category Deltas", s, bs_new, 200, check_deltas)

print(f"--- TESTS COMPLETED: {PASS_COUNT} PASSED, {FAIL_COUNT} FAILED ---")
