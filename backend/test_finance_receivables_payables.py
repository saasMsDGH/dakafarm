import requests
import uuid
import time
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000"
RUN_ID = uuid.uuid4().hex[:6]
ADMIN_EMAIL = f"admin_rp_{RUN_ID}@amas.com"

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

print("--- FINANCE RECEIVABLES & PAYABLES (PHASE 6) TESTS ---")

# 1. Setup Auth
req("POST", "/api/v1/user/", {
    "first_name": "Admin", "last_name": "RP", "email": ADMIN_EMAIL,
    "phone": "0700111222", "password_hash": "Admin@1234", "role": "admin"
})
s, b = form_req("/login", f"username={ADMIN_EMAIL}&password=Admin@1234")
token = b.get("access_token")

# 2. Setup Base Entities (Customer, Supplier, Product, Account)
s, b = req("POST", "/api/v1/pos/customers/", {
    "name": f"Cust_{RUN_ID}", "customer_code": f"C_{RUN_ID}", "phone": "12345",
    "credit_limit": 1000000
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
    print("NO PRODUCTS FOUND!")
    prod_id = 1

s, b = req("POST", "/api/v1/finance/accounts/", {
    "name": f"Cash_{RUN_ID}", "account_type": "CASH"
}, token=token)
acc_id = b.get("id")

# 3. Create a Sale (UNPAID)
s, b = req("POST", "/api/v1/pos/sales/", {
    "customer_id": cust_id, "amount_paid": 0, "account_id": acc_id,
    "items": [{"product_id": prod_id, "quantity": 5, "unit_price": 100}] # Total: 500
}, token=token)
if s != 201 and s != 200:
    print("SALE ERROR:", b)
sale_id = b.get("id")

# 4. Create a Purchase (PARTIAL)
s, b = req("POST", "/api/v1/pos/purchases/", {
    "supplier_id": supp_id, "amount_paid": 200, "account_id": acc_id,
    "payment_method": "CASH",
    "items": [{"product_id": prod_id, "quantity": 10, "unit_cost": 50}] # Total: 500, Paid: 200, Owe: 300
}, token=token)
if s != 201 and s != 200:
    print("PURCHASE ERROR:", b)
purch_id = b.get("id")

# 5. Test Receivables
s, b = req("GET", "/api/v1/finance/receivables/customers", token=token)
def check_rec_sum(body):
    for item in body["items"]:
        if item["customer_id"] == cust_id and str(item["outstanding_balance"]) == "500.00":
            return True
    return False
check("Receivables Summary", s, b, 200, check_rec_sum)

s, b = req("GET", f"/api/v1/finance/receivables/customers/{cust_id}", token=token)
def check_rec_det(body):
    return (
        body["customer_id"] == cust_id and 
        str(body["total_outstanding"]) == "500.00" and
        len(body["sales"]) == 1 and
        str(body["sales"][0]["balance_due"]) == "500.00"
    )
check("Receivables Detail", s, b, 200, check_rec_det)

# 6. Test Payables
s, b = req("GET", "/api/v1/finance/payables/suppliers", token=token)
def check_pay_sum(body):
    for item in body["items"]:
        if item["supplier_id"] == supp_id and str(item["outstanding_balance"]) == "300.00":
            return True
    return False
check("Payables Summary", s, b, 200, check_pay_sum)

s, b = req("GET", f"/api/v1/finance/payables/suppliers/{supp_id}", token=token)
def check_pay_det(body):
    return (
        body["supplier_id"] == supp_id and 
        str(body["total_outstanding"]) == "300.00" and
        len(body["purchases"]) == 1 and
        str(body["purchases"][0]["balance_due"]) == "300.00"
    )
check("Payables Detail", s, b, 200, check_pay_det)

# 7. Make a payment to fully clear the sale and check if it disappears
req("POST", f"/api/v1/pos/sales/{sale_id}/payments", {
    "account_id": acc_id, "amount": 500, "payment_method": "CASH"
}, token=token)

s, b = req("GET", f"/api/v1/finance/receivables/customers/{cust_id}", token=token)
check("Receivables Detail (Cleared)", s, b, 200, lambda bd: float(bd["total_outstanding"]) == 0.0 and len(bd["sales"]) == 0)

print(f"--- TESTS COMPLETED: {PASS_COUNT} PASSED, {FAIL_COUNT} FAILED ---")
