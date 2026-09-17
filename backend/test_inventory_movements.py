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
ADMIN_EMAIL = f"admin_mov_{UNIQUE_SUFFIX}@amasfarm.com"

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

# Setup Category and Product
s, b = req("POST", "/api/v1/inventory/product-categories/", {"name": f"Feed Category {UNIQUE_SUFFIX}", "description": "Feed"}, token=admin_token)
category_id = b.get("id")

s, b = req("POST", "/api/v1/inventory/products/", {
    "name": f"Layer Mash {UNIQUE_SUFFIX}",
    "category_id": category_id,
    "unit_of_measure": "bags",
    "reorder_level": 10.0
}, token=admin_token)
product_id = b.get("id")

print(f"\n[Setup] Created Product ID: {product_id} with initial stock 0.0")

print("\n[Test 1] POST IN 50 bags")
s, b = req("POST", "/api/v1/inventory/movements/", {
    "product_id": product_id,
    "movement_type": "IN",
    "quantity": 50.0,
    "reference_type": "Purchase",
    "reference_id": 101
}, token=admin_token)
if s == 201:
    print("-> PASS: IN 50")
else:
    print(f"-> FAIL: {s} - {b}")

s, p = req("GET", f"/api/v1/inventory/products/{product_id}", token=admin_token)
if p.get("current_stock") == "50.000":
    print("-> PASS: Product stock updated to 50.000")
else:
    print(f"-> FAIL: Stock is {p.get('current_stock')}")

print("\n[Test 2] POST OUT 10 bags")
s, b = req("POST", "/api/v1/inventory/movements/", {
    "product_id": product_id,
    "movement_type": "OUT",
    "quantity": 10.0,
    "reference_type": "Flock Usage",
    "reference_id": 5
}, token=admin_token)
if s == 201:
    print("-> PASS: OUT 10")
else:
    print(f"-> FAIL: {s} - {b}")

s, p = req("GET", f"/api/v1/inventory/products/{product_id}", token=admin_token)
if p.get("current_stock") == "40.000":
    print("-> PASS: Product stock updated to 40.000")
else:
    print(f"-> FAIL: Stock is {p.get('current_stock')}")

print("\n[Test 3] POST ADJUSTMENT -2 bags (damaged goods)")
s, b = req("POST", "/api/v1/inventory/movements/", {
    "product_id": product_id,
    "movement_type": "ADJUSTMENT",
    "quantity": -2.0,
    "reference_type": "Damage"
}, token=admin_token)
if s == 201:
    print("-> PASS: ADJUSTMENT -2")
else:
    print(f"-> FAIL: {s} - {b}")

s, p = req("GET", f"/api/v1/inventory/products/{product_id}", token=admin_token)
if p.get("current_stock") == "38.000":
    print("-> PASS: Product stock updated to 38.000")
else:
    print(f"-> FAIL: Stock is {p.get('current_stock')}")

print("\n[Test 4] POST OUT 100 bags (should fail)")
s, b = req("POST", "/api/v1/inventory/movements/", {
    "product_id": product_id,
    "movement_type": "OUT",
    "quantity": 100.0
}, token=admin_token)
if s == 400:
    print("-> PASS: OUT 100 rejected")
else:
    print(f"-> FAIL: Expected 400, got {s}")

print("\n[Test 5] GET List movements")
s, b = req("GET", f"/api/v1/inventory/movements/?product_id={product_id}", token=admin_token)
if s == 200 and len(b.get("items", [])) == 3:
    print("-> PASS: Correctly listed 3 movements")
else:
    print(f"-> FAIL: Expected 3 movements, got {len(b.get('items', []))}")

print("\nTests complete")
