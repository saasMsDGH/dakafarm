import requests
import uuid

BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin_pos@amas.com"
uid = uuid.uuid4().hex[:4]

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

def check(name, status, body, expected):
    if status == expected:
        print(f"✅ PASS: {name}")
    else:
        print(f"❌ FAIL: {name}\n   Status: {status} (Expected {expected})\n   Body: {body}")

print(f"--- POS SALES TESTS ({uid}) ---")

s, b = form_req("/login", f"username={ADMIN_EMAIL}&password=Admin@1234")
token = b.get("access_token")

s, cat = req("POST", "/api/v1/inventory/product-categories/", {"name": f"Sales Test Cat {uid}"}, token=token)
cat_id = cat.get("id")

s, prod = req("POST", "/api/v1/inventory/products/", {
    "name": f"Test Eggs {uid}", "category_id": cat_id, "unit_of_measure": "tray", 
    "unit_price": 5000.0, "selling_price": 6000.0
}, token=token)
prod_id = prod.get("id")

req("POST", "/api/v1/inventory/movements/", {
    "product_id": prod_id, "movement_type": "IN", "quantity": 100, "reference_type": "Setup"
}, token=token)

s, cust = req("POST", "/api/v1/pos/customers/", {
    "name": f"Test Customer {uid}", "credit_limit": 50000.00
}, token=token)
cust_id = cust.get("id")

s, b = req("POST", "/api/v1/pos/sales/", {
    "customer_id": cust_id,
    "discount": 0.0,
    "amount_paid": 30000.0,
    "payment_method": "Cash",
    "items": [{"product_id": prod_id, "quantity": 5, "unit_price": 6000.0}]
}, token=token)
check("Cash Sale (30k)", s, b, 201)
print(f"   Status: {b.get('payment_status')} (Expected PAID)")
sale1_id = b.get("id")

s, b = req("POST", "/api/v1/pos/sales/", {
    "customer_id": cust_id,
    "discount": 0.0,
    "amount_paid": 0.0,
    "items": [{"product_id": prod_id, "quantity": 7, "unit_price": 6000.0}]
}, token=token)
check("Credit Sale (42k)", s, b, 201)
print(f"   Status: {b.get('payment_status')} (Expected UNPAID)")
sale2_id = b.get("id")

s, b = req("POST", "/api/v1/pos/sales/", {
    "customer_id": cust_id,
    "discount": 0.0,
    "amount_paid": 0.0,
    "items": [{"product_id": prod_id, "quantity": 2, "unit_price": 6000.0}]
}, token=token)
check("Enforce Credit Limit (Block 12k)", s, b, 400)
print(f"   Error: {b.get('detail')}")

s, b = req("POST", f"/api/v1/pos/sales/{sale2_id}/payments/", {
    "amount": 20000.0, "payment_method": "Mobile Money"
}, token=token)
check("Add Payment (20k)", s, b, 200)

s, b = req("GET", f"/api/v1/pos/sales/{sale2_id}", token=token)
check("Check Status after Payment", s, b, 200)
print(f"   Status: {b.get('payment_status')} (Expected PARTIAL), Amount Paid: {b.get('amount_paid')}")

s, b = req("POST", "/api/v1/pos/sales/", {
    "customer_id": cust_id,
    "discount": 0.0,
    "amount_paid": 0.0,
    "items": [{"product_id": prod_id, "quantity": 2, "unit_price": 6000.0}]
}, token=token)
check("Allow Sale After Payment", s, b, 201)

s, b = req("GET", f"/api/v1/inventory/stock/{prod_id}", token=token)
check("Check Inventory Reduction", s, b, 200)
print(f"   Current Stock: {b.get('quantity')} (Expected 86.000)")

print("--- TESTS COMPLETED ---")
