import json
import urllib.error
import urllib.parse
import urllib.request
import time

BASE = "http://localhost:8000"

def req(method, path, body=None, token=None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=10) as r:
            status = r.status
            raw = r.read().decode()
            resp = json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        status = e.code
        try:
            resp = json.loads(e.read().decode())
        except Exception:
            resp = {}

    return status, resp

def form_req(path, body_str):
    data = body_str.encode()
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    request = urllib.request.Request(BASE + path, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=10) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())

UNIQUE_SUFFIX = int(time.time())
ADMIN_EMAIL = f"admin_inv_{UNIQUE_SUFFIX}@amasfarm.com"

print(f"\n[Setup] Creating admin user {ADMIN_EMAIL}...")
req("POST", "/api/v1/user/", {
    "first_name": "Admin",
    "last_name": "User",
    "email": ADMIN_EMAIL,
    "phone": "0700000000",
    "password_hash": "Admin@1234",
    "role": "admin"
})

s, b = form_req("/login", f"username={ADMIN_EMAIL}&password=Admin@1234")
admin_token = b.get("access_token")

# Create a category
s, b = req("POST", "/api/v1/inventory/product-categories/", {
    "name": f"Feed Category {UNIQUE_SUFFIX}",
    "description": "Feed"
}, token=admin_token)
category_id = b.get("id")

# Create a product (Out of Stock by default since current_stock = 0.0)
print("\n[Setup] Creating product (default stock 0.0) ...")
s, b = req("POST", "/api/v1/inventory/products/", {
    "name": f"Layer Mash {UNIQUE_SUFFIX}",
    "category_id": category_id,
    "unit_of_measure": "bags",
    "reorder_level": 10.0
}, token=admin_token)
product_id = b.get("id")

print(f"\n[Test 1] GET /api/v1/inventory/stock/{product_id}")
s, b = req("GET", f"/api/v1/inventory/stock/{product_id}", token=admin_token)
print(f"Status: {s}")
print(f"Response: {json.dumps(b, indent=2)}")
if b.get("status") == "Out of Stock":
    print("-> PASS: Detected Out of Stock")
else:
    print("-> FAIL: Expected Out of Stock")

# Update product stock directly to simulate stock update
s, b = req("PUT", f"/api/v1/inventory/products/{product_id}", {
    "current_stock": 35.0
}, token=admin_token)

print(f"\n[Test 2] GET /api/v1/inventory/stock/{product_id} after updating stock to 35 bags")
s, b = req("GET", f"/api/v1/inventory/stock/{product_id}", token=admin_token)
print(f"Status: {s}")
print(f"Response: {json.dumps(b, indent=2)}")
if b.get("status") == "In Stock":
    print("-> PASS: Detected In Stock")
else:
    print("-> FAIL: Expected In Stock")

print(f"\n[Test 3] GET /api/v1/inventory/stock/")
s, b = req("GET", "/api/v1/inventory/stock/", token=admin_token)
print(f"Status: {s}")
if s == 200 and "items" in b:
    print("-> PASS: List works")
else:
    print("-> FAIL: List failed")

print("\nTests complete")
