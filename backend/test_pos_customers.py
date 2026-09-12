import requests

BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin_pos@amas.com"

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

print("--- POS CUSTOMER TESTS ---")

# 1. Create Admin & Login
req("POST", "/api/v1/user/", {
    "first_name": "Admin", "last_name": "POS", "email": ADMIN_EMAIL,
    "phone": "0700111222", "password_hash": "Admin@1234", "role": "admin"
})
s, b = form_req("/login", f"username={ADMIN_EMAIL}&password=Admin@1234")
token = b["access_token"]

# 2. Create Customer
s, b = req("POST", "/api/v1/pos/customers/", {
    "name": "Acme Corp",
    "business_type": "Wholesale",
    "phone": "0700000000",
    "email": "contact@acme.com",
    "address": "123 Business Rd",
    "credit_limit": 50000.00
}, token=token)
check("Create Customer", s, b, 201)
customer_id = b.get("id")
customer_code = b.get("customer_code")
print(f"   Created Customer Code: {customer_code}")

# 3. Get Customer
s, b = req("GET", f"/api/v1/pos/customers/{customer_id}", token=token)
check("Get Customer", s, b, 200)

# 4. List Customers (Pagination & Search)
s, b = req("GET", "/api/v1/pos/customers/?search=Acme", token=token)
check("List Customers with search", s, b, 200)
items = b.get("items", [])
if len(items) > 0 and items[0]["name"] == "Acme Corp":
    print("   ✅ Search worked correctly")
else:
    print("   ❌ Search failed")

# 5. Update Customer
s, b = req("PUT", f"/api/v1/pos/customers/{customer_id}", {
    "name": "Acme Corporation Inc.",
    "credit_limit": 75000.00
}, token=token)
check("Update Customer", s, b, 200)
if b.get("name") == "Acme Corporation Inc.":
    print("   ✅ Update applied correctly")

# 6. Delete Customer
s, b = req("DELETE", f"/api/v1/pos/customers/{customer_id}", token=token)
check("Delete Customer", s, b, 204)

# Verify Delete
s, b = req("GET", f"/api/v1/pos/customers/{customer_id}", token=token)
check("Verify Customer is Deleted", s, b, 404)

print("--- TESTS COMPLETED ---")
