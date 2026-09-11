import json
import urllib.error
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
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        return e.code, (json.loads(raw) if raw else {})

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
ADMIN_EMAIL = f"farm_inv_{UNIQUE_SUFFIX}@amasfarm.com"

# 1. Setup Admin
print("[Setup] Creating user...")
req("POST", "/api/v1/user/", {
    "first_name": "Farm", "last_name": "Test",
    "email": ADMIN_EMAIL, "phone": "0700000000",
    "password_hash": "Admin@1234", "role": "admin"
})
s, b = form_req("/login", f"username={ADMIN_EMAIL}&password=Admin@1234")
admin_token = b.get("access_token")

# 2. Setup House & Flock
s, b = req("POST", "/api/v1/farm/houses/", {"name": f"House {UNIQUE_SUFFIX}", "capacity": 1000}, token=admin_token)
house_id = b.get("id")

# Create Flock
s, b = req("POST", "/api/v1/farm/flocks/", {
    "house_id": house_id,
    "batch_number": f"BATCH-{UNIQUE_SUFFIX}",
    "bird_type": "Layers",
    "strain": "Isa Brown",
    "source": "Hatchery",
    "initial_quantity": 500,
    "current_quantity": 500,
    "arrival_date": "2023-01-01"
}, token=admin_token)
flock_id = b.get("id")

# 3. Setup Product Category and Product
s, b = req("POST", "/api/v1/inventory/product-categories/", {"name": f"Cat {UNIQUE_SUFFIX}", "description": "Desc"}, token=admin_token)
category_id = b.get("id")
s, b = req("POST", "/api/v1/inventory/products/", {
    "name": f"Layer Mash {UNIQUE_SUFFIX}",
    "category_id": category_id,
    "unit_of_measure": "bags",
    "reorder_level": 5.0
}, token=admin_token)
product_id = b.get("id")

# Add 50 stock to the product directly via Movement
req("POST", "/api/v1/inventory/movements/", {
    "product_id": product_id, "movement_type": "IN", "quantity": 50.0
}, token=admin_token)

print(f"[Setup] Flock {flock_id}, Product {product_id} with 50 bags in stock")

# TEST 1: Create Feed Record for 10 bags
print("\n[Test 1] Create FeedRecord (Used 10)")
s, b = req("POST", "/api/v1/farm/feed-records/", {
    "flock_id": flock_id,
    "product_id": product_id,
    "record_date": "2023-01-02",
    "quantity_used": 10.0,
    "cost_per_unit": 5.0
}, token=admin_token)
record_id = b.get("id")

if s == 201:
    print("-> PASS: Feed Record created")
else:
    print(f"-> FAIL: {s} - {b}")

s, p = req("GET", f"/api/v1/inventory/products/{product_id}", token=admin_token)
if p.get("current_stock") == "40.000":
    print("-> PASS: Product stock correctly dropped to 40")
else:
    print(f"-> FAIL: Expected 40 stock, got {p.get('current_stock')}")


# TEST 2: Update Feed Record to 8 bags (Delta: -2, should add 2 back)
print("\n[Test 2] Update FeedRecord (Used 10 -> 8)")
s, b = req("PUT", f"/api/v1/farm/feed-records/{record_id}", {
    "quantity_used": 8.0
}, token=admin_token)

s, p = req("GET", f"/api/v1/inventory/products/{product_id}", token=admin_token)
if p.get("current_stock") == "42.000":
    print("-> PASS: Product stock accurately rebounded to 42")
else:
    print(f"-> FAIL: Expected 42 stock, got {p.get('current_stock')}")


# TEST 3: Update Feed Record to 15 bags (Delta: +7, should deduct 7)
print("\n[Test 3] Update FeedRecord (Used 8 -> 15)")
s, b = req("PUT", f"/api/v1/farm/feed-records/{record_id}", {
    "quantity_used": 15.0
}, token=admin_token)

s, p = req("GET", f"/api/v1/inventory/products/{product_id}", token=admin_token)
if p.get("current_stock") == "35.000":
    print("-> PASS: Product stock accurately deducted to 35")
else:
    print(f"-> FAIL: Expected 35 stock, got {p.get('current_stock')}")


# TEST 4: Create Feed Record that exceeds stock (Try to use 100 bags when only 35 available)
print("\n[Test 4] Exceed Stock Limit")
s, b = req("POST", "/api/v1/farm/feed-records/", {
    "flock_id": flock_id,
    "product_id": product_id,
    "record_date": "2023-01-03",
    "quantity_used": 100.0,
    "cost_per_unit": 5.0
}, token=admin_token)
if s == 400:
    print("-> PASS: Properly blocked from exceeding stock.")
else:
    print(f"-> FAIL: Expected 400, got {s} - {b}")


# TEST 5: Delete Feed Record (restore 15 bags)
print("\n[Test 5] Delete FeedRecord")
s, b = req("DELETE", f"/api/v1/farm/feed-records/{record_id}", token=admin_token)

s, p = req("GET", f"/api/v1/inventory/products/{product_id}", token=admin_token)
if p.get("current_stock") == "50.000":
    print("-> PASS: Product stock fully restored to 50")
else:
    print(f"-> FAIL: Expected 50 stock, got {p.get('current_stock')}")

print("\nAll integration tests complete.")
