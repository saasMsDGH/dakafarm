import requests
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal

BASE_URL = "http://localhost:8000"
RUN_ID = uuid.uuid4().hex[:6]
ADMIN_EMAIL = f"admin_pnl_{RUN_ID}@amas.com"

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

print("--- FINANCE PROFIT & LOSS (PHASE 8) TESTS ---")

# 1. Setup Auth
req("POST", "/api/v1/user/", {
    "first_name": "Admin", "last_name": "PnL", "email": ADMIN_EMAIL,
    "phone": "0700999888", "password_hash": "Admin@1234", "role": "admin"
})
s, b = form_req("/login", f"username={ADMIN_EMAIL}&password=Admin@1234")
token = b.get("access_token")

# 2. Get baseline P&L
s, pnl_baseline = req("GET", "/api/v1/finance/pnl", token=token)

def dec(v): return Decimal(str(v))

bl_revenue = dec(pnl_baseline["revenue"]["total_revenue"])
bl_cogs = dec(pnl_baseline["cogs"]["total_cogs"])
bl_direct_exp = dec(pnl_baseline["opex"]["direct_expenses"])
bl_payroll = dec(pnl_baseline["opex"]["payroll"])
bl_other_inc = dec(pnl_baseline["non_operating"]["other_income"])

# 3. Setup Prerequisites (Account, Product, Customer, Supplier)
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

# 4. Inject some new transactions
# a) Sale (Revenue = +1500)
req("POST", "/api/v1/pos/sales/", {
    "customer_id": cust_id, "amount_paid": 1500, "account_id": acc_id,
    "payment_method": "CASH",
    "items": [{"product_id": prod_id, "quantity": 10, "unit_price": 150}]
}, token=token)

# b) Purchase (COGS = +600)
req("POST", "/api/v1/pos/purchases/", {
    "supplier_id": supp_id, "amount_paid": 600, "account_id": acc_id,
    "payment_method": "CASH",
    "items": [{"product_id": prod_id, "quantity": 10, "unit_cost": 60}]
}, token=token)

# c) Direct Expense (OPEX = +200)
req("POST", "/api/v1/finance/transactions/", {
    "account_id": acc_id, "transaction_type": "EXPENSE", "direction": "OUT", "amount": 200, "description": "Utilities"
}, token=token)

# d) Payroll (OPEX = +300)
req("POST", "/api/v1/finance/transactions/", {
    "account_id": acc_id, "transaction_type": "PAYROLL", "direction": "OUT", "amount": 300, "description": "Staff"
}, token=token)

# e) Other Income (Non-Op = +100)
req("POST", "/api/v1/finance/transactions/", {
    "account_id": acc_id, "transaction_type": "OTHER_INCOME", "direction": "IN", "amount": 100, "description": "Consulting"
}, token=token)

# f) Asset Purchase (Should NOT affect P&L)
req("POST", "/api/v1/finance/transactions/", {
    "account_id": acc_id, "transaction_type": "ASSET_PURCHASE", "direction": "OUT", "amount": 5000, "description": "Tractor"
}, token=token)

# 5. Fetch New P&L
s, pnl_new = req("GET", "/api/v1/finance/pnl", token=token)

# Verify Deltas
def check_deltas(b):
    diff_rev = dec(b["revenue"]["total_revenue"]) - bl_revenue
    diff_cogs = dec(b["cogs"]["total_cogs"]) - bl_cogs
    diff_exp = dec(b["opex"]["direct_expenses"]) - bl_direct_exp
    diff_pay = dec(b["opex"]["payroll"]) - bl_payroll
    diff_other = dec(b["non_operating"]["other_income"]) - bl_other_inc
    
    # Assertions
    res = True
    if diff_rev != 1500:
        print(f"Revenue diff should be 1500, got {diff_rev}")
        res = False
    if diff_cogs != 600:
        print(f"COGS diff should be 600, got {diff_cogs}")
        res = False
    if diff_exp != 200:
        print(f"Direct Exp diff should be 200, got {diff_exp}")
        res = False
    if diff_pay != 300:
        print(f"Payroll diff should be 300, got {diff_pay}")
        res = False
    if diff_other != 100:
        print(f"Other Income diff should be 100, got {diff_other}")
        res = False
        
    # Check mathematical integrity of the response itself
    gp = dec(b["gross_profit"])
    if gp != dec(b["revenue"]["total_revenue"]) - dec(b["cogs"]["total_cogs"]):
        print("Gross Profit math is wrong")
        res = False
        
    op = dec(b["operating_profit"])
    if op != gp - dec(b["opex"]["total_opex"]):
        print("Operating Profit math is wrong")
        res = False
        
    np = dec(b["net_profit"])
    if np != op + dec(b["non_operating"]["total_non_operating"]):
        print("Net Profit math is wrong")
        res = False
        
    return res

check("P&L - Component Deltas & Math", s, pnl_new, 200, check_deltas)

# 6. Test Date Filtering
now = datetime.now(timezone.utc)
tomorrow = now + timedelta(days=1)
future_date_str = tomorrow.isoformat().replace("+", "%2B")

# If we ask for P&L starting tomorrow, it should be all zeros since we just inserted everything today!
s, pnl_future = req("GET", f"/api/v1/finance/pnl?start_date={future_date_str}", token=token)

def check_empty_future(b):
    return (
        dec(b["revenue"]["total_revenue"]) == 0 and
        dec(b["cogs"]["total_cogs"]) == 0 and
        dec(b["net_profit"]) == 0
    )

check("P&L - Date Filtering (Future is Empty)", s, pnl_future, 200, check_empty_future)

print(f"--- TESTS COMPLETED: {PASS_COUNT} PASSED, {FAIL_COUNT} FAILED ---")
